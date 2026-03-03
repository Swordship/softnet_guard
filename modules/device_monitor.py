def scan ():
    import subprocess
    result = subprocess.run(['arp', '-a'] , capture_output= True, text=True)
    lines = result.stdout.splitlines()
    output = []
    for line in lines:
        if 'dynamic' in line:
            ip, mac = line.split()[:2]
            output.append({"ip": ip, "mac": mac})
    return output