import sqlite3
import os
from pathlib import Path

repo_db = Path("c:/GitHub/Ayen-Ode-0.3/data/ayen_ode.db")
appdata_db = Path(os.environ.get("APPDATA")) / "Ayen-Ode" / "data" / "ayen_ode.db"

for name, db_path in [("Repo DB", repo_db), ("AppData DB", appdata_db)]:
    print(f"\n=================== {name}: {db_path} ===================")
    if not db_path.exists():
        print("Database file does not exist!")
        continue

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    try:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for t in tables:
            tname = t['name']
            count = conn.execute(f"SELECT COUNT(*) FROM {tname}").fetchone()[0]
            print(f"Table: {tname}, Rows: {count}")

        print("\n--- Worlds ---")
        worlds = conn.execute("SELECT world_id, slug, name, status, created_at FROM worlds").fetchall()
        for w in worlds:
            print(dict(w))
    except Exception as e:
        print("Error inspecting DB:", e)
    finally:
        conn.close()
