import subprocess
result = subprocess.run(["cmd", "/c", "dir"])
print(result.stdout) 