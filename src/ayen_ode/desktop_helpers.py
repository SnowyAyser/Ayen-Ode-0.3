import os
import sys
import time
import socket
import urllib.request
from pathlib import Path
from typing import Any

_mutex_handle = None
_lock_file = None


def check_single_instance() -> bool:
    """Ensure only one instance of the game runs at a time. Returns True if
    this is the only instance; False if another is already running."""
    global _mutex_handle, _lock_file
    
    max_attempts = 15
    delay = 0.1
    
    for attempt in range(max_attempts):
        if sys.platform == "win32":
            try:
                import ctypes
                # Global\\ prefix makes the mutex visible across all terminal server sessions
                MUTEX_NAME = "Global\\AyenOdeSingleInstanceMutex"
                kernel32 = ctypes.windll.kernel32
                # Keep a reference to the mutex handle so it isn't garbage collected!
                _mutex_handle = kernel32.CreateMutexW(None, True, MUTEX_NAME)
                last_error = kernel32.GetLastError()
                if last_error != 183: # NOT ERROR_ALREADY_EXISTS
                    return True
                # If it already exists, close the handle so we don't leak it on retries
                kernel32.CloseHandle(_mutex_handle)
                _mutex_handle = None
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
                if _lock_file:
                    try:
                        _lock_file.close()
                    except Exception:
                        pass
                    _lock_file = None
        
        if attempt < max_attempts - 1:
            time.sleep(delay)
            
    return False


def _pick_free_port() -> int:
    """Ask the OS for a free port on loopback, then release it."""
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


def _redirect_streams_to_log(log_path: Path) -> None:
    """Redirect stdout/stderr to a rotating log file in user-data dir."""
    try:
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


def set_window_icon(hwnd: Any, icon_path: Path) -> None:
    if not hwnd or not icon_path.exists():
        return
    try:
        import ctypes
        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x00000010
        hicon = ctypes.windll.user32.LoadImageW(
            None,
            str(icon_path),
            IMAGE_ICON,
            0, 0,
            LR_LOADFROMFILE
        )
        if hicon:
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
            
            try:
                if sys.maxsize > 2**32:
                    ctypes.windll.user32.SetClassLongPtrW(hwnd, -14, hicon) # GCLP_HICON = -14
                    ctypes.windll.user32.SetClassLongPtrW(hwnd, -34, hicon) # GCLP_HICONSM = -34
                else:
                    ctypes.windll.user32.SetClassLongW(hwnd, -14, hicon)
                    ctypes.windll.user32.SetClassLongW(hwnd, -34, hicon)
            except Exception:
                pass
    except Exception:
        pass


def _read_fullscreen_preference() -> bool:
    """Read AYEN_ODE_FULLSCREEN from %APPDATA%/Ayen-Ode/.env."""
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
