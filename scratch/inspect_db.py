import os
import sqlite3
from pathlib import Path

def inspect_db(path):
    print(f"\n==========================================")
    print(f"DATABASE: {path}")
    if not os.path.exists(path):
        print("Does not exist.")
        return
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        
        # Check tables
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f"Tables: {', '.join(tables)}")
        
        # Check worlds
        worlds = conn.execute("SELECT world_id, name, original_opening_scene, last_system_handoff FROM worlds").fetchall()
        print(f"Worlds count: {len(worlds)}")
        for w in worlds:
            print(f"  - ID: {w['world_id']}")
            print(f"    Name: {w['name']}")
            print(f"    Original Opening Scene length: {len(w['original_opening_scene']) if w['original_opening_scene'] else 0}")
            print(f"    Last System Handoff length: {len(w['last_system_handoff']) if w['last_system_handoff'] else 0}")
            
            # Check handoffs count
            handoffs = conn.execute("SELECT COUNT(*) FROM world_handoffs WHERE world_id = ?", (w['world_id'],)).fetchone()[0]
            print(f"    Handoffs count: {handoffs}")
            
            # Check entities count
            entities = conn.execute("SELECT COUNT(*) FROM entities WHERE world_id = ?", (w['world_id'],)).fetchone()[0]
            print(f"    Entities count: {entities}")
            
            # Check investigation_jobs
            jobs = conn.execute("SELECT COUNT(*), status FROM investigation_jobs WHERE world_id = ? GROUP BY status", (w['world_id'],)).fetchall()
            print(f"    Jobs: {dict(jobs)}")
            
            # Check pregenerated_investigations
            pregens = conn.execute("SELECT COUNT(*) FROM pregenerated_investigations WHERE world_id = ?", (w['world_id'],)).fetchone()[0]
            print(f"    Pregenerated cache count: {pregens}")
            
        conn.close()
    except Exception as e:
        print(f"Error inspecting: {e}")

# Inspect local repo database
inspect_db("c:/GItHub/Ayen-Ode-0.3/data/ayen_ode.db")

# Inspect APPDATA database
appdata = os.environ.get("APPDATA")
if appdata:
    inspect_db(os.path.join(appdata, "Ayen-Ode", "data", "ayen_ode.db"))
