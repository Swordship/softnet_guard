import subprocess
def scan ():
    try:
        result = subprocess.run(['arp', '-a'] , capture_output= True, text=True)
        lines = result.stdout.splitlines()
    except Exception as e:
        print(f"Error executing arp command: {e}")
        return []
    output = []
    for line in lines:
        if 'dynamic' in line:
            ip, mac = line.split()[:2]
            output.append({"ip": ip, "mac": mac})
    return output
if __name__ == "__main__":
    print(scan())