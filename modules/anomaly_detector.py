import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pickle
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
from database import db_manager

MODEL_PATH  = "isolation_forest.pkl"
SCALER_PATH = "scaler.pkl"

FEATURE_NAMES = [
    "packet_count", "bytes_sent", "bytes_received", "bytes_total",
    "bytes_per_packet", "send_receive_ratio", "protocol_diversity",
    "unique_destinations", "dns_query_count", "http_ratio",
    "https_ratio", "dns_ratio", "is_high_port"
]

# ── Train Model ───────────────────────────────
def train_model():
    print("[Model] Generating normal traffic training data...")
    rng = np.random.default_rng(42)

    # Normal home network traffic patterns
    # Train ONLY on normal data — Isolation Forest is unsupervised
    X = rng.uniform(
        low= [10,  500,   2000,  3000,  200, 0.02, 0.5, 1,  0, 0.0, 0.3, 0.0, 0],
        high=[600, 50000, 200000,250000,1500, 0.45, 2.5, 10, 25, 0.3, 0.9, 0.2, 1],
        size=(5000, 13)
    )

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    model.fit(X_scaled)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    print("[Model] Training complete! Files saved.")
    return model, scaler

# ── Load Model ────────────────────────────────
def load_model():
    if not os.path.exists(MODEL_PATH):
        print("[Model] No model found — training now...")
        return train_model()
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    return model, scaler

# ── Score a feature vector ────────────────────
def score_vector(vector, model, scaler):
    X = np.array(vector).reshape(1, -1)
    X_scaled = scaler.transform(X)
    raw = model.decision_function(X_scaled)[0]
    # Convert to 0-1 scale using tanh
    return float(max(0.0, min(1.0, (1.0 - float(np.tanh(raw * 8.0))) / 2.0)))

# ── Classify anomaly type ─────────────────────
def classify_anomaly(vector):
    packet_count    = vector[0]
    bytes_total     = vector[3]
    unique_dests    = vector[7]
    dns_count       = vector[8]
    protocol_div    = vector[6]

    if bytes_total > 50 * 1024 * 1024:
        return "BANDWIDTH_ANOMALY"
    if unique_dests > 20:
        return "CONNECTION_ANOMALY"
    if dns_count > 100:
        return "DNS_ANOMALY"
    if protocol_div > 2.5:
        return "PROTOCOL_ANOMALY"
    return "TEMPORAL_ANOMALY"

# ── Get severity from score ───────────────────
def get_severity(score):
    if score >= 0.80: return "CRITICAL"
    if score >= 0.65: return "HIGH"
    if score >= 0.50: return "MEDIUM"
    if score >= 0.35: return "LOW"
    return "NORMAL"
def run_detection_once():
    """Score all devices from recent traffic and create alerts if anomalous."""
    model, scaler = load_model()
    
    conn = db_manager.get_connection()
    if not conn:
        return
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    
    # Get traffic data per device from last 60 minutes
    cursor.execute("""
        SELECT device_id,
               SUM(packet_count)   as packet_count,
               SUM(bytes_sent)     as bytes_sent,
               SUM(bytes_received) as bytes_received,
               COUNT(DISTINCT destination_ip) as unique_destinations
        FROM traffic_stats
        WHERE observed_at >= datetime('now', '-60 minutes')
        GROUP BY device_id
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("[Detector] No traffic data yet.")
        return

    for row in rows:
        # Build 13-feature vector
        bs   = float(row["bytes_sent"] or 0)
        br   = float(row["bytes_received"] or 0)
        pc   = float(row["packet_count"] or 1)
        bt   = bs + br
        bpp  = bt / pc
        srr  = bs / (bt + 1)

        vector = [
            pc, bs, br, bt, bpp, srr,
            1.0, float(row["unique_destinations"] or 1),
            0, 0.0, 0.65, 0.08, 0
        ]

        score    = score_vector(vector, model, scaler)
        severity = get_severity(score)

        print(f"[Detector] device_id={row['device_id']} score={score:.3f} → {severity}")

        if severity in ("MEDIUM", "HIGH", "CRITICAL"):
            anomaly_type = classify_anomaly(vector)
            msg = f"Anomaly detected: {anomaly_type} (score={score:.2f})"
            db_manager.create_alert(
                alert_type = anomaly_type,
                severity   = severity,
                device_id  = row["device_id"],
                message    = msg
            )
            print(f"  [ALERT] {msg}")
if __name__ == "__main__":
    train_model()
    print("[Test] Model trained and saved successfully!")