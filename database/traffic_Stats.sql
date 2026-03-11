-- SQL script to create the 'traffic_stats' table in the database 
-- if it does not already exist. This table will store
-- information about network traffic statistics for devices connected to the network,
-- including timestamps, device IP addresses, packets sent and received,
-- bytes sent and received, destination IP addresses, and ports used.
CREATE table if not exists traffic_stats (
ID integer PRIMARY KEY AUTOINCREMENT,
timestamp text not null,
device_ip text not null,
packets_sent integer not null ,
packets_recived  integer not null,
bytes_sent integer not null,
bytes_recived integer not null,
destination_ip text null,
protocol text not null,
port integer null
);
