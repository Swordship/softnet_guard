import subprocess
result = subprocess.run(['arp', '-a'] , capture_output= True, text=True)
lines = result.stdout.splitlines()
for line in lines:
    if 'dynamic' in line:
        print(line)