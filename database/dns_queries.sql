-- SQL script to create the 'dns_queries' table in the database
-- if it does not already exist. This table will store
-- information about DNS queries made by devices on the network,
-- including timestamps, device IP addresses, queried domains,
-- query types, and responses received. This information can be
-- useful for monitoring and analyzing DNS traffic for potential security threats or anomalies.
-- CREATE table if not exists dns_queries (
-- id integer PRIMARY KEY AUTOINCREMENT,
-- timestamp text not null,
-- device_ip text not null,
-- domain text not null,
-- queries_type text null ,
-- response text null
-- );
CREATE TABLE IF NOT EXISTS dns_queries (
id INTEGER PRIMARY KEY AUTOINCREMENT,
queried_at TEXT NOT NULL,
device_id INTEGER NOT NULL,
domain TEXT NOT NULL,
query_type TEXT,
response TEXT,
created_at TEXT NOT NULL DEFAULT (datetime('now')),
FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_dns_domain ON dns_queries(domain);