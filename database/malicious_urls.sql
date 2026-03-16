-- SQL script to create the 'MALICIOUS_URL' table in the database
-- if it does not already exist. This table will store
-- information about detected malicious URLs in the network traffic,
-- including timestamps, device IP addresses, threat types,
-- URLs, blocked status, and severity levels. The threat types
-- are categorized as 'malware', 'phishing', and 'social_engineering'.
-- CREATE table if not exists MALICIOUS_URL (
-- ID integer PRIMARY KEY AUTOINCREMENT,
-- timestamp text not null,
-- device_ip text not null,
-- threat_type text not null CHECK(threat_type IN ('malware','phishing','social_engineering')),
-- url text not null,
-- blocked integer not null ,
-- severity text not null CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
-- );
CREATE TABLE IF NOT EXISTS malicious_urls (
id INTEGER PRIMARY KEY AUTOINCREMENT,
detected_at TEXT NOT NULL,
device_id INTEGER NOT NULL,
threat_type TEXT NOT NULL CHECK(threat_type IN ('malware','phishing','social_engineering')),
url TEXT NOT NULL,
blocked INTEGER NOT NULL DEFAULT 0 CHECK(blocked IN (0,1)),
severity TEXT NOT NULL DEFAULT 'HIGH' CHECK(severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
created_at TEXT NOT NULL DEFAULT (datetime('now')),
FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_mal_urls_url ON malicious_urls(url);