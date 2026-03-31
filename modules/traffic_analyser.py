import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import threading
from collections import defaultdict
from datetime import datetime
from database import db_manager

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
            self.stats[src]["bytes_sent"]      += size
            self.stats[src]["packet_count"]    += 1
            self.stats[src]["protocols"][proto] += 1
            self.stats[src]["destinations"].add(dst)
            self.stats[dst]["bytes_received"]  += size

    def flush(self):
        with self._lock:
            snap = dict(self.stats)
            self.stats.clear()
            return snap

BUFFER = TrafficBuffer()
_stop_event = threading.Event()

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
            if 53  in ports or 5353 in ports: return "DNS"
            if 67  in ports or 68   in ports: return "DHCP"
            if 123 in ports:                  return "NTP"
            return "UDP"
        if pkt.haslayer(ICMP): return "ICMP"
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

        if pkt.haslayer(DNS) and pkt.haslayer(DNSQR):
            domain = pkt[DNSQR].qname.decode("utf-8", errors="ignore").rstrip(".")
            if domain:
                db_manager.log_dns(source_ip=src, domain=domain)
                print(f"  [DNS] {src} → {domain}")
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
            print(f"  [TRAFFIC] {ip} → sent:{data['bytes_sent']} recv:{data['bytes_received']}")

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