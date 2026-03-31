CREATE TABLE IF NOT EXISTS traffic_stats (
id INTEGER PRIMARY KEY AUTOINCREMENT,
observed_at TEXT NOT NULL,
device_id INTEGER NOT NULL,
packet_count INTEGER NOT NULL DEFAULT 0,
bytes_sent INTEGER NOT NULL DEFAULT 0,
bytes_received INTEGER NOT NULL DEFAULT 0,
destination_ip TEXT,
protocol TEXT,
port INTEGER,
created_at TEXT NOT NULL DEFAULT (datetime('now')),
FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_traffic_device ON traffic_stats(device_id);
CREATE INDEX IF NOT EXISTS idx_traffic_observed_at ON traffic_stats(observed_at);