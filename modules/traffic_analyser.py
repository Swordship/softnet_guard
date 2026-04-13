import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import threading
import requests
from collections import defaultdict
from datetime import datetime
from database import db_manager
from dotenv import load_dotenv
load_dotenv()

# ── In-memory buffer ──────────────────────────
class TrafficBuffer:
    def __init__(self):
        self._lock = threading.Lock()
        self.stats = defaultdict(lambda: {
            "bytes_sent": 0, "bytes_received": 0,
            "packet_count": 0,
            "protocols": defaultdict(int),
            "destinations": set()
        })

    def record(self, src, dst, size, proto):
        with self._lock:
            self.stats[src]["bytes_sent"]       += size
            self.stats[src]["packet_count"]     += 1
            self.stats[src]["protocols"][proto] += 1
            self.stats[src]["destinations"].add(dst)
            self.stats[dst]["bytes_received"]   += size

    def flush(self):
        with self._lock:
            snap = dict(self.stats)
            self.stats.clear()
            return snap

BUFFER     = TrafficBuffer()
_stop_event = threading.Event()

# ── Already-checked domains cache (avoid repeat API calls) ──
_checked_domains = set()

# ── Google Safe Browsing check ────────────────
def check_domain_safety(domain, source_ip):
    """Check domain against Google Safe Browsing API. Create alert if malicious."""
    if not domain or domain in _checked_domains:
        return
    _checked_domains.add(domain)

    API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    if not API_KEY:
        return

    url = f"https://{domain}"
    try:
        payload = {
            "client": {"clientId": "softnet-guard", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
        r = requests.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}",
            json=payload, timeout=5
        )
        result = r.json()

        if result.get("matches"):
            threat = result["matches"][0].get("threatType", "MALWARE")
            msg    = f"Malicious domain visited: {domain} (Threat: {threat})"
            print(f"  🚨 [ALERT] {source_ip} visited {domain} → {threat}")

            # Find device_id for the source IP
            device_id = db_manager.get_device_id_by_ip(source_ip)

            # Save to malicious_urls table
            conn = db_manager.get_connection()
            if conn:
                try:
                    current_time = datetime.now().isoformat()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO malicious_urls
                        (detected_at, device_id, threat_type, url, blocked, severity)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        current_time,
                        device_id,
                        threat.lower()[:20],
                        url,
                        0,
                        "HIGH"
                    ))
                    conn.commit()
                finally:
                    conn.close()

            # Create alert
            db_manager.create_alert(
                alert_type = "MALICIOUS_URL",
                severity   = "HIGH",
                device_id  = device_id,
                message    = msg
            )

    except Exception as e:
        pass  # API failure — silent, don't crash capture


# ── Protocol detection ────────────────────────
def detect_protocol(pkt) -> str:
    try:
        from scapy.all import TCP, UDP, ICMP, DNS
        if pkt.haslayer(DNS):
            return "DNS"
        if pkt.haslayer(TCP):
            ports = {pkt[TCP].dport, pkt[TCP].sport}
            if 443 in ports: return "HTTPS"
            if 80  in ports: return "HTTP"
            if 22  in ports: return "SSH"
            if 53  in ports: return "DNS"
            return "TCP"
        if pkt.haslayer(UDP):
            ports = {pkt[UDP].dport, pkt[UDP].sport}
            if 53 in ports or 5353 in ports: return "DNS"
            if 67 in ports or 68   in ports: return "DHCP"
            if 123 in ports:                 return "NTP"
            return "UDP"
        if pkt.haslayer(ICMP):
            return "ICMP"
    except Exception:
        pass
    return "OTHER"


# ── Packet handler ────────────────────────────
def on_packet(pkt):
    try:
        from scapy.all import IP, DNS, DNSQR
        if not pkt.haslayer(IP):
            return

        src   = pkt[IP].src
        dst   = pkt[IP].dst
        size  = len(pkt)
        proto = detect_protocol(pkt)
        BUFFER.record(src, dst, size, proto)

        # DNS query detected — log and check for malicious domain
        if pkt.haslayer(DNS) and pkt.haslayer(DNSQR):
            domain = pkt[DNSQR].qname.decode("utf-8", errors="ignore").rstrip(".")
            if domain:
                print(f"  [DNS] {src} → {domain}")
                # Log to DB (best effort — may fail if IP not in devices)
                db_manager.log_dns(source_ip=src, domain=domain)
                # Check safety in background thread (don't slow down capture)
                t = threading.Thread(
                    target=check_domain_safety,
                    args=(domain, src),
                    daemon=True
                )
                t.start()

    except Exception:
        pass


# ── Flush worker ──────────────────────────────
def flush_worker(interval=60):
    while not _stop_event.is_set():
        time.sleep(interval)
        snap = BUFFER.flush()
        for ip, data in snap.items():
            if data["packet_count"] == 0:
                continue
            top_proto = max(data["protocols"], key=data["protocols"].get) \
                        if data["protocols"] else "UNKNOWN"
            db_manager.log_traffic(
                ip             = ip,
                bytes_sent     = data["bytes_sent"],
                bytes_received = data["bytes_received"],
                packet_count   = data["packet_count"],
                protocol       = top_proto,
                dest_ip        = next(iter(data["destinations"]), None)
            )
            print(f"  [TRAFFIC] {ip} → "
                  f"sent:{data['bytes_sent']} "
                  f"recv:{data['bytes_received']}")


# ── Main capture ──────────────────────────────
def start_capture(duration=None):
    try:
        from scapy.all import sniff
    except ImportError:
        print("[ERROR] Scapy not installed.")
        return

    _stop_event.clear()
    t = threading.Thread(target=flush_worker, args=(60,), daemon=True)
    t.start()

    print(f"\n[Capture] Started at {datetime.now().strftime('%H:%M:%S')}")
    print("[Capture] Listening for packets... (Ctrl+C to stop)\n")

    try:
        sniff(prn=on_packet, store=False, timeout=duration)
    except KeyboardInterrupt:
        print("\n[Capture] Stopped by user.")
    except PermissionError:
        print("\n[ERROR] Run VS Code as Administrator!")
    finally:
        _stop_event.set()


if __name__ == "__main__":
    start_capture()