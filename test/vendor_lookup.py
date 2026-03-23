import requests
def get_vendor(mac_address: str) -> str:
    try:
        mac_prefix = mac_address[:8]
        response = requests.get(f"https://api.macvendors.com/{mac_prefix}")
        if response.status_code == 200:
            return response.text  # ← return not print!
        return "Unknown"
    except requests.RequestException:
        return "request error"
    
if __name__ == "__main__":
    print (get_vendor("b8:1e:a4:e3:4e:17"))
    print (get_vendor("9c:8c:6e:5a:2f:bc"))
    print(get_vendor("52:7f:f4:68:40:ba"))