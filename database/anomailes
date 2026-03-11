-- SQL script to create the 'anomailes' table in the database
-- if it does not already exist. This table will store
-- information about detected anomalies in the network traffic,
-- including timestamps, device IP addresses, anomaly types,
-- anomaly scores, descriptions, severity levels, and resolution status.
CREATE table if not exists anomailes (
ID integer PRIMARY KEY AUTOINCREMENT,
timestamp text not null,
device_ip text not null,
anomaly_type text not null ,
anomaly_score real not null,
description text not null,
severity text not null CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
resolved integer not null
);