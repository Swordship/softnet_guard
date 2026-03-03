# import subprocess
# result = subprocess.run(['arp', '-a'] , capture_output= True, text=True)
# lines = result.stdout.splitlines()
# # for line in lines:
# #     if 'dynamic' in line:
# #         print(line)
# output = []
# for line in lines:
#     if 'dynamic' in line:
#         ip, mac = line.split()[:2]
#         output.append({"ip": ip, "mac": mac})
# print(output)
import subprocess
try:
    result = subprocess.run(['arp', '-a'] , capture_output= True, text=True)
    lines = result.stdout.splitlines()
except Exception as e:
    print(f"Error executing arp command: {e}")
    lines = []
output = []
for line in lines:
    if 'dynamic' in line:
        ip, mac = line.split()[:2]
        output.append({"ip": ip, "mac": mac})
print (output)