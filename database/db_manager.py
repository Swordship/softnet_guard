import sqlite3

DB_PATH = "softnet_guard.db"

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"[DB ERROR] Could not connect: {e}")
        return None
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("Database connection successful.")
        conn.close()
    else:
        print("Database connection failed.")