import psutil
print(psutil.net_io_counters())
print(psutil.net_connections(kind='inet')[:3])