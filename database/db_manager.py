import sqlite3
import os
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
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("Database connection successful.")
        conn.close()
    else:
        print("Database connection failed.")