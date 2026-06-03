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
        return e.code, e.read().decode("utf-8")

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
        return e.code, e.read().decode("utf-8")

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

    # Log in
    print("[Client] Logging in...")
    status, body = http_post("http://127.0.0.1:54321/api/login", {"username": "SnowyAyser", "password": "1437"})
    token = body.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    world_id = "world_98335cf915584b91"
    
    # 1. Dispatch Reset (simulates user clicking Reset)
    print(f"[Client] Resetting world {world_id}...")
    status, reset_body = http_post(f"http://127.0.0.1:54321/api/worlds/{world_id}/reset", {}, headers=headers)
    print(f"[Client] Reset response: {status}")

    # 2. Immediately try to enter the world (fetches /api/world and currencies in parallel)
    print("[Client] Immediately fetching /api/world and currencies in parallel to simulate Entrance...")
    
    def fetch_world():
        print("[Client Thread 1] Fetching /api/world...")
        try:
            status, body = http_get(f"http://127.0.0.1:54321/api/world?world_id={world_id}", headers=headers)
            print(f"[Client Thread 1] /api/world Response: {status} (length: {len(str(body))})")
        except Exception as e:
            print(f"[Client Thread 1] /api/world failed: {e}")

    def fetch_currencies():
        print("[Client Thread 2] Fetching /api/worlds/.../currencies...")
        try:
            status, body = http_get(f"http://127.0.0.1:54321/api/worlds/{world_id}/currencies", headers=headers)
            print(f"[Client Thread 2] /api/worlds/.../currencies Response: {status} (body: {body})")
        except Exception as e:
            print(f"[Client Thread 2] /api/worlds/.../currencies failed: {e}")

    t1 = threading.Thread(target=fetch_world)
    t2 = threading.Thread(target=fetch_currencies)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    print("[Client] Completed concurrent fetches.")

if __name__ == "__main__":
    run_test()
