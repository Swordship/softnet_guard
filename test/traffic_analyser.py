import psutil
# print(psutil.net_io_counters())
# print(psutil.net_connections(kind='inet')[:3])
interfaces = psutil.net_if_addrs()
print(interfaces)