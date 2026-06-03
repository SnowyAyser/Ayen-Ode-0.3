"""Desktop launcher: starts the Starlette server bound to a random localhost
port, then opens a native window pointed at it. No browser, no internet IP.
"""

from __future__ import annotations

import os
import sys
import threading
import time

# Re-export key variables/functions for launchers and backwards compatibility
from .desktop_helpers import (
    check_single_instance,
    _read_fullscreen_preference,
    _pick_free_port,
    _wait_for_server,
    _redirect_streams_to_log,
    set_window_icon,
)
from .desktop_api import DesktopApi

# Explicit AppUserModelID to force Windows taskbar/Alt-Tab to group our windows with custom icon
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SnowyAyser.AyenOde.0.3")
    except Exception:
        pass


def run_desktop() -> int:
    """Run the desktop app. Returns an exit code; caller is responsible for
    propagating it to sys.exit()."""

    # Force desktop mode before anything imports config
    os.environ["AYEN_ODE_DESKTOP"] = "1"
    os.environ["AYEN_ODE_RELOAD"] = "0"

    from . import paths
    webview_storage = paths.user_data_dir() / "webview_data"
    try:
        webview_storage.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(webview_storage)

    preset = os.environ.get("AYEN_ODE_PORT", "").strip()
    if preset.isdigit():
        port = int(preset)
    else:
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", 54224))
                port = 54224
        except Exception:
            port = _pick_free_port()
        os.environ["AYEN_ODE_PORT"] = str(port)
    os.environ["AYEN_ODE_HOST"] = "127.0.0.1"

    paths.ensure_user_dir()

    if paths.is_frozen() or sys.executable.lower().endswith("pythonw.exe"):
        _redirect_streams_to_log(paths.user_data_dir() / "app.log")

    try:
        (paths.user_data_dir() / "runtime.json").write_text(
            f'{{"port": {port}, "url": "http://127.0.0.1:{port}"}}',
            encoding="utf-8",
        )
    except OSError:
        pass

    # Import server dynamically
    from .server import app, investigation_worker, service, settings
    
    threading.Thread(target=investigation_worker, daemon=True).start()

    import uvicorn

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
        proxy_headers=False,
        lifespan="on",
    )
    server = uvicorn.Server(config)

    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    base_url = f"http://127.0.0.1:{port}"
    if not _wait_for_server(base_url + "/health", timeout=30.0):
        sys.stderr.write("Ayen-Ode: server failed to start within 30 seconds\n")
        return 1

    import webview

    start_fullscreen = _read_fullscreen_preference()

    # Point the window directly at the login screen
    start_url = base_url + "/"

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
                
                if hwnd is None and hasattr(window.native, "Handle"):
                    try:
                        hwnd = int(window.native.Handle.ToInt64())
                    except Exception:
                        pass
                if hwnd is None and hasattr(window.native, "Handle"):
                    try:
                        hwnd = int(window.native.Handle.ToInt32())
                    except Exception:
                        pass
                if hwnd is None and hasattr(window.native, "hwnd"):
                    try:
                        hwnd = int(window.native.hwnd)
                    except Exception:
                        pass
                if hwnd is None:
                    try:
                        import re
                        m = re.search(r"with\s+(\d+)\s+handle", str(window.native))
                        if m:
                            hwnd = int(m.group(1))
                    except Exception:
                        pass
                if hwnd is None:
                    try:
                        hwnd = int(window.native)
                    except Exception:
                        pass
                        
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

    webview_storage = paths.user_data_dir() / "webview_data"
    try:
        webview_storage.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(webview_storage)

    gui_backend = "edgechromium" if sys.platform == "win32" else None
    try:
        webview.start(
            gui=gui_backend,
            private_mode=False,
            storage_path=str(webview_storage),
            debug=False
        )
    finally:
        try:
            server.should_exit = True
        except Exception:
            pass

    return 0
