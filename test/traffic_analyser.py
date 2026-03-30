import psutil
# print(psutil.net_io_counters())
# print(psutil.net_connections(kind='inet')[:3])
interfaces = psutil.net_if_addrs()
print(interfaces)
# import psutil
# from socket import AF_INET
# import ipaddress
# def get_local_network():
#     for name, addrs in psutil.net_if_addrs().items():
#         for addr in addrs:
#             if addr.family == AF_INET:
#                 ip = addr.address
#                 # Skip APIPA and loopback addresses
#                 if ip.startswith("169.254.") or ip == "127.0.0.1":
#                     continue
#                 # Return the first valid interface found
#                 network = ipaddress.IPv4Interface(f"{ip}/{addr.netmask}").network
#                 return str(network)
#     return None  # is not found , return none here 
                
# if __name__ == "__main__":
#     print(get_local_network())