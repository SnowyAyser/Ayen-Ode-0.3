"""Entry point for the Ayen-Ode desktop app.

Launches the high-fidelity WebView2 wrapper engine with an integrated 
premium animated splash screen and background updater.
"""

from __future__ import annotations

import os
import sys
import time
import socket
import threading
import multiprocessing
import urllib.request
from pathlib import Path

# Ensure src/ is in sys.path early so imports resolve correctly
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ayen_ode.desktop_helpers import (
    check_single_instance,
    _read_fullscreen_preference,
    set_window_icon,
)
from ayen_ode.desktop_api import DesktopApi

try:
    import tkinter as tk
    from ayen_ode.splash_app import SplashApp
except ImportError:
    tk = None
    SplashApp = None


class DummyStream:
    """Safe dummy stream to replace None standard streams under windowless pythonw.exe."""
    def write(self, data): pass
    def flush(self): pass
    def isatty(self): return False
    @property
    def encoding(self): return "utf-8"
    @property
    def errors(self): return "strict"
    def writable(self): return True
    def seekable(self): return False
    def readable(self): return False


# Defensive stream replacement for windowless environment compatibility
if sys.stdout is None:
    sys.stdout = DummyStream()
if sys.stderr is None:
    sys.stderr = DummyStream()
if sys.stdin is None:
    sys.stdin = DummyStream()

# Redirect stdout and stderr early to a rotating app.log file under pythonw.exe
if sys.executable.lower().endswith("pythonw.exe") or isinstance(sys.stdout, DummyStream):
    try:
        from ayen_ode import paths
        paths.ensure_user_dir()
        log_path = paths.user_data_dir() / "app.log"
        
        if log_path.exists():
            backup = log_path.with_suffix(log_path.suffix + ".1")
            try:
                if backup.exists():
                    backup.unlink()
                log_path.rename(backup)
            except OSError:
                pass
                
        log_file = open(log_path, "a", encoding="utf-8", buffering=1)
        sys.stdout = log_file
        sys.stderr = log_file
    except Exception:
        pass

# Thread-safe flags
server_ready = False
server_failed = False
update_triggered = False
chosen_port = 54224


def _log_boot_error(msg: str, exc: Exception | None = None):
    """Write startup errors securely to AppData/Ayen-Ode/boot.log for developer diagnostics."""
    try:
        import traceback
        from ayen_ode import paths
        paths.ensure_user_dir()
        boot_log = paths.user_data_dir() / "boot.log"
        with open(boot_log, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
            if exc is not None:
                traceback.print_exc(file=f)
    except Exception:
        pass


def bg_boot_thread():
    global server_ready, server_failed, update_triggered, chosen_port
    
    # 1. Background Update Check (Only for frozen Windows EXE)
    try:
        from ayen_ode.updater import check_and_update
        if check_and_update():
            update_triggered = True
            return
    except Exception as e:
        _log_boot_error("Background updater exception", e)
        
    # 2. Single Instance Check (Done in main thread)
    pass

    # 3. Server Startup
    try:
        os.environ["AYEN_ODE_DESKTOP"] = "1"
        os.environ["AYEN_ODE_RELOAD"] = "0"
        
        from ayen_ode import paths
        paths.ensure_user_dir()
        
        preset = os.environ.get("AYEN_ODE_PORT", "").strip()
        if preset.isdigit():
            port = int(preset)
        else:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("127.0.0.1", 54224))
                    port = 54224
            except Exception:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("127.0.0.1", 0))
                    port = s.getsockname()[1]
            os.environ["AYEN_ODE_PORT"] = str(port)
            
        chosen_port = port
        os.environ["AYEN_ODE_HOST"] = "127.0.0.1"
        
        webview_storage = paths.user_data_dir() / "webview_data"
        webview_storage.mkdir(parents=True, exist_ok=True)
        os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(webview_storage)
        
        from ayen_ode.server import app
        
        import uvicorn
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
            lifespan="on",
        )
        server = uvicorn.Server(config)
        
        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()
        
        base_url = f"http://127.0.0.1:{port}"
        health_url = base_url + "/health"
        
        end_time = time.monotonic() + 30.0
        while time.monotonic() < end_time:
            try:
                with urllib.request.urlopen(health_url, timeout=1.0) as r:
                    if 200 <= r.status < 500:
                        server_ready = True
                        break
            except Exception:
                pass
            time.sleep(0.1)
        else:
            _log_boot_error("Uvicorn server failed to respond to /health in 30s")
            server_failed = True
            
    except Exception as e:
        _log_boot_error("Background server boot exception", e)
        server_failed = True


def launch_webview():
    global chosen_port
    try:
        from ayen_ode import paths
        webview_storage = paths.user_data_dir() / "webview_data"
        os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(webview_storage)
        
        base_url = f"http://127.0.0.1:{chosen_port}"
        start_fullscreen = _read_fullscreen_preference()
        
        # Point directly to the login screen so checkbox-based auto-entry can run
        start_url = base_url + "/"
        
        import webview
        api = DesktopApi()
        window = webview.create_window(
            title="Ayen-Ode",
            url=start_url,
            width=1280,
            height=820,
            min_size=(960, 640),
            background_color="#0f172a",
            text_select=True,
            fullscreen=start_fullscreen,
            js_api=api,
        )
        api.bind_window(window)
        
        def on_shown():
            try:
                icon_path = paths.static_dir() / "clover.ico"
                if not icon_path.exists():
                    icon_path = paths.static_dir() / "icon_v2.ico"
                if sys.platform == "win32" and icon_path.exists():
                    hwnd = None
                    
                    for attr in ("Handle", "hwnd"):
                        val = getattr(window.native, attr, None)
                        if val is not None:
                            try:
                                hwnd = int(val.ToInt64() if hasattr(val, "ToInt64") else (val.ToInt32() if hasattr(val, "ToInt32") else val))
                                break
                            except Exception: pass
                    if hwnd is None:
                        try:
                            import re
                            m = re.search(r"with\s+(\d+)\s+handle", str(window.native))
                            hwnd = int(m.group(1)) if m else int(window.native)
                        except Exception: pass
                            
                    if hwnd:
                        set_window_icon(hwnd, icon_path)
                        
                        def retries():
                            time.sleep(0.2)
                            set_window_icon(hwnd, icon_path)
                            time.sleep(0.3)
                            set_window_icon(hwnd, icon_path)
                            
                        threading.Thread(target=retries, daemon=True).start()
            except Exception:
                pass
                
        window.events.shown += on_shown
        
        gui_backend = "edgechromium" if sys.platform == "win32" else None
        webview.start(
            gui=gui_backend,
            private_mode=False,
            storage_path=str(webview_storage),
            debug=False
        )
    except Exception as e:
        _log_boot_error("WebView launch execution exception", e)
        raise


def main() -> int:
    multiprocessing.freeze_support()
    
    # 1. Single Instance Check early before showing splash GUI
    try:
        if not check_single_instance():
            msg = "You can't have more than one instance of the game open at a time."
            _log_boot_error(msg)
            if sys.platform == "win32":
                try:
                    import ctypes
                    # MB_ICONERROR (0x10) | MB_SETFOREGROUND (0x10000) | MB_TOPMOST (0x40000)
                    ctypes.windll.user32.MessageBoxW(None, msg, "Ayen-Ode", 0x10 | 0x10000 | 0x40000)
                except Exception:
                    pass
            return 1
    except Exception as e:
        _log_boot_error("Early single-instance check exception", e)
        return 1

    try:
        from ayen_ode import paths
        boot_log = paths.user_data_dir() / "boot.log"
        if boot_log.exists():
            boot_log.unlink()
    except Exception:
        pass
        
    try:
        _log_boot_error("--- INITIALIZING BOOT LOADER ---")
        
        t = threading.Thread(target=bg_boot_thread, daemon=True)
        t.start()
        
        if tk is not None and SplashApp is not None:
            try:
                root = tk.Tk()
                app = SplashApp(root)
                root.mainloop()
            except Exception as e:
                _log_boot_error("Tkinter window failed, falling back to headless sleep wait", e)
                while not server_ready and not server_failed and not update_triggered:
                    time.sleep(0.1)
        else:
            _log_boot_error("Tkinter module not available, starting in headless fallback mode")
            while not server_ready and not server_failed and not update_triggered:
                time.sleep(0.1)
                
        if update_triggered:
            _log_boot_error("Boot aborted: Update triggered successfully")
            os._exit(0)
        elif server_ready:
            _log_boot_error("Server is ready, spawning pywebview desktop...")
            try:
                launch_webview()
            finally:
                _log_boot_error("pywebview window closed, exiting boot loader")
                os._exit(0)
        else:
            _log_boot_error("Boot failed: Server startup failed or was aborted")
            os._exit(1)
            
    except Exception as e:
        _log_boot_error("Fatal exception in main boot loader process", e)
        os._exit(1)


if __name__ == "__main__":
    raise SystemExit(main())
