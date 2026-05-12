import sqlite3
import json

def read_db():
    conn = sqlite3.connect('data/purple_team.db')
    cursor = conn.cursor()
    
    print("TABLES:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(tables)
    
    for table in tables:
        t_name = table[0]
        print(f"\nDATA FROM {t_name}:")
        cursor.execute(f"SELECT * FROM {t_name} LIMIT 10;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    
    conn.close()

if __name__ == "__main__":
    read_db()
