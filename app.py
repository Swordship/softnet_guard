import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request
from database import db_manager
from modules import device_monitor
from modules import anomaly_detector
import threading
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, template_folder="dashboard/templates")

@app.route("/")
def dashboard():
    devices = db_manager.get_all_devices()
    stats   = get_stats()
    return render_template("dashboard.html", devices=devices, stats=stats)

@app.route("/api/devices")
def api_devices():
    return jsonify(db_manager.get_all_devices())

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

@app.route("/api/scan", methods=["POST"])
def api_scan():
    devices = device_monitor.scan_network()
    return jsonify({"scanned": len(devices), "devices": devices})

@app.route("/api/traffic")
def api_traffic():
    conn = db_manager.get_connection()
    if not conn:
        return jsonify([])
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.ip_address, d.host_name,
               SUM(t.bytes_sent)     as total_sent,
               SUM(t.bytes_received) as total_received,
               SUM(t.packet_count)   as total_packets
        FROM traffic_stats t
        JOIN devices d ON t.device_id = d.id
        GROUP BY t.device_id
        ORDER BY total_packets DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/alerts")
def api_alerts():
    return jsonify(db_manager.get_alerts())

@app.route("/api/check-url", methods=["POST"])
def api_check_url():
    import requests as req
    data    = request.get_json()
    url     = data.get("url", "").strip()
    API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    if not url.startswith("http"):
        url = "http://" + url
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
        r = req.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}",
            json=payload, timeout=5
        )
        result = r.json()
        if result.get("matches"):
            threat = result["matches"][0].get("threatType", "MALWARE")
            return jsonify({"safe": False, "threat_type": threat, "url": url})
        return jsonify({"safe": True, "url": url})
    except Exception as e:
        return jsonify({"safe": True, "url": url, "note": str(e)})

def get_stats():
    devices  = db_manager.get_all_devices()
    total    = len(devices)
    active   = len([d for d in devices if d["status"] == "Active"])
    return {
        "total_devices":    total,
        "active_devices":   active,
        "inactive_devices": total - active
    }

def start_background_tasks():
    def scan_loop():
        import time
        while True:
            try:
                device_monitor.scan_network()
                anomaly_detector.run_detection_once()
            except Exception as e:
                print(f"[Scanner] Error: {e}")
            time.sleep(60)
    t = threading.Thread(target=scan_loop, daemon=True)
    t.start()
    print("[App] Background tasks started.")

if __name__ == "__main__":
    db_manager.initialize_db()
    start_background_tasks()
    print("\n  Dashboard → http://127.0.0.1:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000)