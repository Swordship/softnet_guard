-- SQL script to create the 'MALICIOUS_URL' table in the database
-- if it does not already exist. This table will store
-- information about detected malicious URLs in the network traffic,
-- including timestamps, device IP addresses, threat types,
-- URLs, blocked status, and severity levels. The threat types
-- are categorized as 'malware', 'phishing', and 'social_engineering'.
CREATE table if not exists MALICIOUS_URL (
ID integer PRIMARY KEY AUTOINCREMENT,
timestamp text not null,
device_ip text not null,
threat_type text not null CHECK(threat_type IN ('malware','phishing','social_engineering')),
url text not null,
blocked integer not null ,
severity text not null CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);