CREATE TABLE IF NOT EXISTS dns_queries (
id INTEGER PRIMARY KEY AUTOINCREMENT,
queried_at TEXT NOT NULL,
device_id INTEGER NOT NULL,
domain TEXT NOT NULL,
query_type TEXT DEFAULT 'A',
response TEXT,
created_at TEXT NOT NULL DEFAULT (datetime('now')),
FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_dns_domain ON dns_queries(domain);