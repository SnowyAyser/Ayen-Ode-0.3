import os
import sys
import logging
from pathlib import Path

# Add src directory to path so we can import ayen_ode modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ayen_ode.config import load_settings
from ayen_ode.server import service
from ayen_ode.service import AyenOdeService
from ayen_ode.relinker import run_database_relinking

def main():
    # Setup console logging so we can see the relinker output
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    print("=" * 60)
    print("Ayen-Ode: Deep Database Keyword Relinking Process")
    print("=" * 60)
    
    settings = load_settings()
    
    # 1. Relink the local development database
    print(f"Processing local developer database: {settings.db_path}")
    run_database_relinking(service, settings)
    
    # 2. Relink the active AppData desktop database (if it exists)
    appdata = os.environ.get("APPDATA")
    if appdata:
        appdata_db = Path(appdata) / "Ayen-Ode" / "data" / "ayen_ode.db"
        if appdata_db.exists():
            print("-" * 60)
            print(f"Detected active AppData desktop database: {appdata_db}")
            print("Running relinker on active desktop game save...")
            appdata_service = AyenOdeService(appdata_db)
            run_database_relinking(appdata_service, settings)
        else:
            print("-" * 60)
            print("Active AppData desktop database not found (fresh install or separate profile).")
            
    print("=" * 60)
    print("Relinking process complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
