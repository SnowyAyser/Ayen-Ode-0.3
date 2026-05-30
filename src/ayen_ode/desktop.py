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


_mutex_handle = None
_lock_file = None


def check_single_instance() -> bool:
    """Ensure only one instance of the game runs at a time. Returns True if
    this is the only instance; False if another is already running."""
    global _mutex_handle, _lock_file
    if sys.platform == "win32":
        try:
            import ctypes
            # Global\\ prefix makes the mutex visible across all terminal server sessions
            MUTEX_NAME = "Global\\AyenOdeSingleInstanceMutex"
            kernel32 = ctypes.windll.kernel32
            # Keep a reference to the mutex handle so it isn't garbage collected!
            _mutex_handle = kernel32.CreateMutexW(None, True, MUTEX_NAME)
            last_error = kernel32.GetLastError()
            if last_error == 183: # ERROR_ALREADY_EXISTS
                return False
            return True
        except Exception:
            pass
    else:
        # Cross-platform fallback: lock file lock in the user data directory
        try:
            from . import paths
            lock_path = paths.user_data_dir() / "app.lock"
            # Keep lock file handle open
            _lock_file = open(lock_path, "w")
            import fcntl
            fcntl.flock(_lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except Exception:
            return False
    return True


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

    # Set up the persistent WebView2 user data folder as early as possible so
    # the runtime respects it on startup before any WebView2 code initializes.
    from . import paths
    webview_storage = paths.user_data_dir() / "webview_data"
    try:
        webview_storage.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(webview_storage)

    # Honour AYEN_ODE_PORT if already set (useful for tests / scripted launches);
    # otherwise try to bind to a static standard port (to preserve same-origin localStorage), falling back to ephemeral.
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
    from .server import app, investigation_worker, service, settings
    from .relinker import run_database_relinking

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

    # Read the persisted fullscreen preference from %APPDATA%/Ayen-Ode/.env.
    # We re-parse the file rather than relying on settings.* because settings
    # is loaded at server import time and doesn't expose this field.
    start_fullscreen = _read_fullscreen_preference()

    # Determine startup URL: auto-login redirect if preference is enabled
    auto_login_pref = False
    try:
        p_auto = paths.user_data_dir() / "auto_login.txt"
        if p_auto.exists():
            auto_login_pref = p_auto.read_text(encoding="utf-8").strip() == "true"
    except Exception:
        pass

    start_url = base_url + "/desktop-bootstrap" if auto_login_pref else base_url + "/"

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

    # Force Edge WebView2 and pywebview to write persistent local data to %APPDATA%/Ayen-Ode/webview_data
    # (or the repository root in source/dev mode) so localStorage (e.g. savedUsername) is remembered.
    webview_storage = paths.user_data_dir() / "webview_data"
    try:
        webview_storage.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    os.environ["WEBVIEW2_USER_DATA_FOLDER"] = str(webview_storage)

    # gui="edgechromium" forces the Edge WebView2 backend on Windows. On other
    # platforms pywebview picks the best available backend automatically.
    gui_backend = "edgechromium" if sys.platform == "win32" else None
    try:
        webview.start(
            gui=gui_backend,
            private_mode=False,
            storage_path=str(webview_storage),
            debug=False
        )
    finally:
        # Once the user closes the window, ask uvicorn to shut down so the
        # daemon thread doesn't keep the process alive on some platforms.
        try:
            server.should_exit = True
        except Exception:
            pass

    return 0


def _read_fullscreen_preference() -> bool:
    """Read AYEN_ODE_FULLSCREEN from %APPDATA%/Ayen-Ode/.env.

    The env var is set on this process by config.load_dotenv, but we read the
    file directly here because the dotenv call happens lazily and we need the
    answer at window-creation time."""
    from . import paths
    env_path = paths.env_path()
    if not env_path.exists():
        return False
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("AYEN_ODE_FULLSCREEN="):
                return s.split("=", 1)[1].strip() == "1"
    except OSError:
        pass
    return False


class DesktopApi:
    """Bridge exposed to the dashboard JS as `window.pywebview.api`.

    pywebview injects these methods on every page load. The dashboard calls
    them from the settings modal (toggle button) and from a keyboard handler
    (F11). We don't persist fullscreen state here — that's done by the user
    Save'ing in the settings panel, which writes AYEN_ODE_FULLSCREEN to .env
    via the /api/settings POST route.
    """

    def __init__(self) -> None:
        self._window = None  # type: ignore[var-annotated]

    def bind_window(self, window: object) -> None:
        self._window = window

    # --- methods callable from JS via window.pywebview.api.<name>() -------

    def toggle_fullscreen(self) -> bool:
        """Flip fullscreen state. Returns True so JS can await the call."""
        try:
            if self._window is not None:
                self._window.toggle_fullscreen()
        except Exception:
            pass
        return True

    def set_fullscreen(self, value: bool) -> bool:
        """Force fullscreen to a specific state, idempotent if already there.
        pywebview doesn't expose a direct setter, so we read current state
        from the window object and toggle iff different."""
        try:
            if self._window is None:
                return False
            current = bool(getattr(self._window, "fullscreen", False))
            if bool(value) != current:
                self._window.toggle_fullscreen()
        except Exception:
            pass
        return True

    def is_desktop(self) -> bool:
        """Sentinel the JS uses to detect 'are we in pywebview, not a browser?'.
        If window.pywebview is defined the answer is implicitly yes, but this
        gives a single explicit method to await."""
        return True

    def close_window(self) -> bool:
        """Close the application window and exit the process. Returns True so JS can await it."""
        try:
            if self._window is not None:
                self._window.destroy()
        except Exception:
            pass
        return True

    def get_saved_username(self) -> str:
        """Get the saved username from user_data_dir to bypass Same-Origin port isolation."""
        try:
            from . import paths
            p = paths.user_data_dir() / "saved_username.txt"
            if p.exists():
                username = p.read_text(encoding="utf-8").strip()
                print(f"[DesktopApi] get_saved_username read: {username}")
                return username
        except Exception as e:
            print(f"[DesktopApi] get_saved_username error: {e}")
        return ""

    def save_username(self, username: str) -> bool:
        """Save the username to user_data_dir to bypass Same-Origin port isolation."""
        try:
            from . import paths
            p = paths.user_data_dir() / "saved_username.txt"
            p.write_text(username.strip(), encoding="utf-8")
            print(f"[DesktopApi] save_username wrote: {username}")
            return True
        except Exception as e:
            print(f"[DesktopApi] save_username error: {e}")
        return False

    def get_auto_login(self) -> bool:
        """Get the auto-login preference from user_data_dir to bypass Same-Origin port isolation."""
        try:
            from . import paths
            p = paths.user_data_dir() / "auto_login.txt"
            if p.exists():
                val = p.read_text(encoding="utf-8").strip()
                print(f"[DesktopApi] get_auto_login read: {val}")
                return val == "true"
        except Exception as e:
            print(f"[DesktopApi] get_auto_login error: {e}")
        return False

    def save_auto_login(self, value: bool) -> bool:
        """Save the auto-login preference to user_data_dir to bypass Same-Origin port isolation."""
        try:
            from . import paths
            p = paths.user_data_dir() / "auto_login.txt"
            val = "true" if value else "false"
            p.write_text(val, encoding="utf-8")
            print(f"[DesktopApi] save_auto_login wrote: {val}")
            return True
        except Exception as e:
            print(f"[DesktopApi] save_auto_login error: {e}")
        return False
