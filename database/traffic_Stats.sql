-- SQL script to create the 'traffic_stats' table in the database 
-- if it does not already exist. This table will store
-- information about network traffic statistics for devices connected to the network,
-- including timestamps, device IP addresses, packets sent and received,
-- bytes sent and received, destination IP addresses, and ports used.
-- CREATE table if not exists traffic_stats (
-- ID integer PRIMARY KEY AUTOINCREMENT,
-- timestamp text not null,
-- device_ip text not null,
-- packets_sent integer not null ,
-- packets_recived  integer not null,
-- bytes_sent integer not null,
-- bytes_recived integer not null,
-- destination_ip text null,
-- protocol text not null,
-- port integer null
-- );
CREATE TABLE IF NOT EXISTS traffic_stats (
id INTEGER PRIMARY KEY AUTOINCREMENT,
observed_at TEXT NOT NULL,
device_id INTEGER NOT NULL,
packets_sent INTEGER NOT NULL DEFAULT 0,
packets_received INTEGER NOT NULL DEFAULT 0,
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