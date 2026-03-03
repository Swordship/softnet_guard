import subprocess
result = subprocess.run(['arp', '-a'] , capture_output= True, text=True)
print(result.stdout)