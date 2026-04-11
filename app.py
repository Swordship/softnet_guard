import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request
from database import db_manager
from modules import device_monitor
from modules import anomaly_detector
import threading

app = Flask(__name__, template_folder="dashboard/templates")

# ── API Routes ────────────────────────────────
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
               SUM(t.bytes_sent) as total_sent,
               SUM(t.bytes_received) as total_received,
               SUM(t.packet_count) as total_packets
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
    conn = db_manager.get_connection()
    if not conn:
        return jsonify([])
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM alerts
        ORDER BY occurred_at DESC LIMIT 20
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

# ── Helper ────────────────────────────────────
def get_stats():
    devices = db_manager.get_all_devices()
    total   = len(devices)
    active  = len([d for d in devices if d["status"] == "Active"])
    return {
        "total_devices": total,
        "active_devices": active,
        "inactive_devices": total - active
    }

# ── Background threads ────────────────────────
def start_background_tasks():
    # Device scanner — runs every 60 seconds
    def scan_loop():
        import time
        while True:
            try:
                device_monitor.scan_network()
            except Exception as e:
                print(f"[Scanner] Error: {e}")
            time.sleep(60)

    t = threading.Thread(target=scan_loop, daemon=True)
    t.start()
    print("[App] Background scanner started.")

if __name__ == "__main__":
    db_manager.initialize_db()
    start_background_tasks()
    print("\n  Dashboard → http://127.0.0.1:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000)