import sys
import os
import time
import threading
import json
import urllib.request
import urllib.error
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

def start_server():
    print("[Server] Booting server on port 54321 pointing to AppData...")
    os.environ["PORT"] = "54321"
    os.environ["AYEN_ODE_PORT"] = "54321"
    os.environ["AYEN_ODE_RELOAD"] = "0"
    # Force use of AppData directory
    os.environ["AYEN_ODE_USER_DATA"] = r"C:\Users\zgreiniman\AppData\Roaming\Ayen-Ode"
    
    from ayen_ode.server import main
    main()

def http_post(url, data_dict, headers=None):
    if headers is None:
        headers = {}
    data = json.dumps(data_dict).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            body = json.loads(body)
        except Exception:
            pass
        return e.code, body

def http_get(url, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, method="GET")
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            body = json.loads(body)
        except Exception:
            pass
        return e.code, body

def run_test():
    # Start server in thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # Wait for server to boot
    print("[Client] Waiting for server to boot...")
    for _ in range(10):
        try:
            req = urllib.request.Request("http://127.0.0.1:54321/static/index.html")
            with urllib.request.urlopen(req, timeout=1) as response:
                if response.status == 200:
                    print("[Client] Server is UP!")
                    break
        except Exception:
            pass
        time.sleep(0.5)
    else:
        print("[Client] Server failed to boot.")
        return

    # Let's log in using real credentials
    print("[Client] Logging in...")
    try:
        status, body = http_post("http://127.0.0.1:54321/api/login", {"username": "SnowyAyser", "password": "1437"})
        print(f"[Client] Login response: {status} - {body}")
        token = body.get("token")
    except Exception as e:
        print(f"[Client] Login failed: {e}")
        return

    # Let's find the active world (the shattered plane)
    headers = {"Authorization": f"Bearer {token}"}
    print("[Client] Listing worlds in AppData...")
    status, body = http_get("http://127.0.0.1:54321/api/worlds", headers=headers)
    worlds = body.get("worlds", [])
    if not worlds:
        print("[Client] No worlds found in database.")
        return
        
    for w in worlds:
        print(f"  - {w['name']} (ID: {w['world_id']})")
        
    world = worlds[0]
    world_id = world["world_id"]
    world_name = world["name"]
    print(f"[Client] Selected world: {world_name} (ID: {world_id})")

    # Let's hit the reset endpoint!
    print(f"[Client] Hitting reset endpoint for {world_id}...")
    try:
        status, body = http_post(f"http://127.0.0.1:54321/api/worlds/{world_id}/reset", {}, headers=headers)
        print(f"[Client] Reset response code: {status}")
        print(f"[Client] Reset response body: {body}")
    except Exception as e:
        print(f"[Client] Reset request failed: {e}")

if __name__ == "__main__":
    run_test()
