-- SQL script to create the 'device' table in the database 
-- if it does not already exist. This table will store 
-- information about devices connected to the network, 
-- including their IP and MAC addresses, device type, host name, 
-- vendor, timestamps for when they were first and last seen,
-- their current status, and whether they are authorized to access the network.
CREATE table if not exists device (
ID integer PRIMARY KEY AUTOINCREMENT,
ip_address text not null,
mac_address text not null,
device_type text null,
host_name text null,
vendor text null,
first_seen text not null ,
last_seen text not null,
status text not null,
is_authorized integer not null
);
