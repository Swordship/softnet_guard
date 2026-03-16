import datetime
import sqlite3
import os
from time import timezone
DB_PATH = "softnet_guard.db"

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"[DB ERROR] Could not connect: {e}")
        return None
def initialize_db():
    conn = get_connection()
    if not conn:
        return
    
    sql_folder = os.path.dirname(__file__)
    
    try:
        for filename in os.listdir(sql_folder):
            if filename.endswith(".sql"):
                file_path = os.path.join(sql_folder, filename)
                with open(file_path, 'r') as sql_file:
                    sql_script = sql_file.read()
                    conn.executescript(sql_script)
                    print(f"Executed {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to read or execute SQL files: {e}")
    finally:
        conn.close()
def insert_device(ip_address, mac_address, host_name=None, vendor=None, device_type=None):
    conn = get_connection()
    if not conn:
        return False
    current_time = datetime.now(timezone.utc).isoformat()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO devices (ip_address, mac_address, host_name, vendor, device_type ,first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?) on conflict(mac_address) DO UPDATE SET 
                    ip_address=excluded.ip_address, 
                    host_name=excluded.host_name,
                    vendor=excluded.vendor,
                    device_type=excluded.device_type,
                    last_seen = excluded.last_seen
        """, (ip_address, mac_address, host_name, vendor, device_type,current_time,current_time))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to insert device: {e}")
        return False
    finally:
        conn.close()
if __name__ == "__main__":
    initialize_db()