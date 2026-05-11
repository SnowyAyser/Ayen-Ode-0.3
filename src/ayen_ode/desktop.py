"""Desktop launcher: starts the Starlette server bound to a random localhost
port, then opens a native window pointed at it. No browser, no internet IP.

The window is created via pywebview, which uses Microsoft Edge WebView2 on
Windows 10/11 (pre-installed on Windows 11; the installer ensures it on Win10).

Entry flow:
    1. Pick a free port on 127.0.0.1.
    2. Seed %APPDATA%/Ayen-Ode/ on first run.
    3. Import .server (this loads config, builds the service, builds the app).
    4. Spawn the investigation worker thread.
    5. Spawn uvicorn in a thread; wait for /health.
    6. Open a pywebview window pointing at /desktop-bootstrap, which sets the
       session token in localStorage and redirects to the dashboard — so the
       user never sees the username/password login screen.
    7. When the window closes, exit the process.

If the embedded server exits with code 42 (a /api/restart request), this
process exits with the same code so a supervisor script can relaunch us.
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import urllib.request


def _pick_free_port() -> int:
    """Ask the OS for a free port on loopback, then release it. There's a small
    race between this call and uvicorn binding it, but in practice it's safe
    for a single-process launcher."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(url: str, timeout: float = 30.0) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as r:
                if 200 <= r.status < 500:
                    return True
        except Exception:
            pass
        time.sleep(0.1)
    return False


def _redirect_streams_to_log(log_path) -> None:
    """When running as a windowed (console=False) frozen build, sys.stdout and
    sys.stderr are bound to NUL. Redirect them to a rotating log file in the
    user-data dir so tracebacks aren't silently lost. Best-effort: any failure
    here is swallowed, since logging must not break startup."""
    try:
        # Keep two generations: app.log (current) + app.log.1 (previous run).
        if log_path.exists():
            backup = log_path.with_suffix(log_path.suffix + ".1")
            try:
                if backup.exists():
                    backup.unlink()
                log_path.rename(backup)
            except OSError:
                pass
        f = open(log_path, "a", encoding="utf-8", buffering=1)
        sys.stdout = f
        sys.stderr = f
    except OSError:
        pass


def run_desktop() -> int:
    """Run the desktop app. Returns an exit code; caller is responsible for
    propagating it to sys.exit()."""

    # Force desktop mode before anything imports config — this gates the
    # /desktop-bootstrap route and tells the server to disable reload.
    os.environ["AYEN_ODE_DESKTOP"] = "1"
    os.environ["AYEN_ODE_RELOAD"] = "0"

    # Honour AYEN_ODE_PORT if already set (useful for tests / scripted launches);
    # otherwise grab a free ephemeral port on loopback.
    preset = os.environ.get("AYEN_ODE_PORT", "").strip()
    if preset.isdigit():
        port = int(preset)
    else:
        port = _pick_free_port()
        os.environ["AYEN_ODE_PORT"] = str(port)
    os.environ["AYEN_ODE_HOST"] = "127.0.0.1"

    # Make sure %APPDATA%/Ayen-Ode/.env exists before config.py reads it.
    from . import paths
    paths.ensure_user_dir()

    # In windowed frozen builds, route stdout/stderr to a log file so unhandled
    # exceptions aren't lost. Skipped in source mode (devs see them in the terminal).
    if paths.is_frozen():
        _redirect_streams_to_log(paths.user_data_dir() / "app.log")

    # Write the chosen port to a file so external scripts (and the user, if
    # they want to use the API from another tool) can discover it.
    try:
        (paths.user_data_dir() / "runtime.json").write_text(
            f'{{"port": {port}, "url": "http://127.0.0.1:{port}"}}',
            encoding="utf-8",
        )
    except OSError:
        pass

    # Import server lazily so the env tweaks above take effect first.
    from .server import app, investigation_worker

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

    # Show the window. webview.start() blocks until all windows close.
    import webview

    webview.create_window(
        title="Ayen-Ode",
        url=base_url + "/desktop-bootstrap",
        width=1280,
        height=820,
        min_size=(960, 640),
        background_color="#0f172a",
        text_select=True,
    )

    # gui="edgechromium" forces the Edge WebView2 backend on Windows. On other
    # platforms pywebview picks the best available backend automatically.
    gui_backend = "edgechromium" if sys.platform == "win32" else None
    try:
        webview.start(gui=gui_backend)
    finally:
        # Once the user closes the window, ask uvicorn to shut down so the
        # daemon thread doesn't keep the process alive on some platforms.
        try:
            server.should_exit = True
        except Exception:
            pass

    return 0


def run_settings_window() -> int:
    """Launch the native tkinter settings window. Invoked when the EXE is
    started with --settings (or `python -m ayen_ode.settings_window` in source
    mode)."""
    from .settings_window import main as _settings_main
    try:
        _settings_main()
    except SystemExit as e:
        return int(e.code or 0)
    return 0
