import subprocess
import time
import os
import sys
from pathlib import Path

appdata_dir = Path(os.environ.get("APPDATA")) / "Ayen-Ode"
cache_dir = appdata_dir / "webview_data"
log_path = appdata_dir / "app.log"
exe_path = Path("C:/GitHub/Ayen-Ode-0.3/dist/Ayen-Ode.exe")

# 1. Clean WebView2 cache and clean the log file so we only see the fresh execution
print("Purging WebView2 cache...")
if cache_dir.exists():
    import shutil
    try:
        shutil.rmtree(str(cache_dir))
        print("Cache deleted successfully!")
    except Exception as e:
        print(f"Warning: could not delete cache folder: {e}")

print("Cleaning app.log...")
if log_path.exists():
    try:
        log_path.unlink()
        print("Old app.log deleted successfully!")
    except OSError:
        pass

# 2. Start the newly compiled executable
print("\nSpawning recompiled Ayen-Ode.exe...")
proc = subprocess.Popen(
    [str(exe_path)],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd="C:/GitHub/Ayen-Ode-0.3"
)

# 3. Wait for the app to initialize, load the WebView2 control, render, and execute all JS
print("Waiting 15 seconds to let the GUI load, evaluate all JS, and trigger any onerror logs...")
for i in range(15):
    time.sleep(1.0)
    print(f"  {i+1}/15 seconds elapsed...")

# 4. Terminate the app
print("\nTerminating application process...")
proc.terminate()
proc.wait()
print("Process terminated.")

# 5. Read the log file to check for frontend errors
print("\n=================== READING FRESH APP.LOG ===================")
if not log_path.exists():
    print("No app.log was written. The app might not have booted.")
    sys.exit(1)

log_content = log_path.read_text(encoding="utf-8")
print(log_content)
print("=============================================================")

if "[FRONTEND ERROR]" in log_content:
    print("\nFAIL: Javascript errors were detected during frontend load!")
    sys.exit(1)
else:
    print("\nSUCCESS: No Javascript errors detected! All assets parsed and evaluated successfully!")
    sys.exit(0)
