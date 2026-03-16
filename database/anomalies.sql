-- SQL script to create the 'anomailes' table in the database
-- if it does not already exist. This table will store
-- information about detected anomalies in the network traffic,
-- including timestamps, device IP addresses, anomaly types,
-- anomaly scores, descriptions, severity levels, and resolution status.
-- CREATE table if not exists anomailes (
-- id integer PRIMARY KEY AUTOINCREMENT,
-- timestamp text not null,
-- device_ip text not null,
-- anomaly_type text not null ,
-- anomaly_score real not null,
-- description text not null,
-- severity text not null CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
-- resolved integer not null
-- );
CREATE TABLE IF NOT EXISTS anomalies (
id INTEGER PRIMARY KEY AUTOINCREMENT,
occurred_at TEXT NOT NULL, -- ISO8601
device_id INTEGER NOT NULL,
anomaly_type TEXT NOT NULL,
anomaly_score REAL NOT NULL DEFAULT 0.0,
description TEXT,
severity TEXT NOT NULL DEFAULT 'LOW' CHECK(severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
resolved INTEGER NOT NULL DEFAULT 0 CHECK(resolved IN (0,1)),
created_at TEXT NOT NULL DEFAULT (datetime('now')),
updated_at TEXT NOT NULL DEFAULT (datetime('now')),
FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE
);