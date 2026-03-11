-- SQL script to create the 'dns_queries' table in the database
-- if it does not already exist. This table will store
-- information about DNS queries made by devices on the network,
-- including timestamps, device IP addresses, queried domains,
-- query types, and responses received. This information can be
-- useful for monitoring and analyzing DNS traffic for potential security threats or anomalies.
CREATE table if not exists dns_queries (
ID integer PRIMARY KEY AUTOINCREMENT,
timestamp text not null,
device_ip text not null,
domain text not null,
queries_type text null ,
response text null
);