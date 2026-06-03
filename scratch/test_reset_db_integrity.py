import sqlite3
import os

db_path = r"C:\Users\zgreiniman\AppData\Roaming\Ayen-Ode\data\ayen_ode.db"
print(f"Checking SQLite integrity of: {db_path}")
if not os.path.exists(db_path):
    print("Database does not exist.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    res = conn.execute("PRAGMA integrity_check").fetchone()[0]
    print(f"Integrity check result: {res}")
    
    # Check foreign key consistency
    fks = conn.execute("PRAGMA foreign_key_check").fetchall()
    print(f"Foreign key check errors count: {len(fks)}")
    for fk in fks:
        print(f"  FK Error: {fk}")
        
    conn.close()
except Exception as e:
    print(f"Error checking: {e}")
