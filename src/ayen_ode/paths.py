"""Central path resolution. Knows whether we're frozen (PyInstaller bundle) or
running from source, and points static assets / .env / data dir at the right
locations for each.

Source mode:
    bundle_dir   = <repo>
    user_data    = <repo>                           (writable: same dir)
    static_dir   = <repo>/static
    env_path     = <repo>/.env
    db_path      = <repo>/data/ayen_ode.db

Frozen mode (PyInstaller bundle):
    bundle_dir   = <_MEIPASS or exe-dir>            (read-only bundled assets)
    user_data    = %APPDATA%/Ayen-Ode/              (writable per-user dir)
    static_dir   = <bundle_dir>/static
    env_path     = %APPDATA%/Ayen-Ode/.env
    db_path      = %APPDATA%/Ayen-Ode/data/ayen_ode.db

Env-var overrides (apply in both modes):
    AYEN_ODE_USER_DATA   — override user_data_dir entirely
    AYEN_ODE_DB_PATH     — override db_path; relative paths resolve under user_data
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    """True when running from a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def bundle_dir() -> Path:
    """Directory containing read-only bundled resources (static/, .env.example).

    - Frozen onefile: sys._MEIPASS (temp extraction)
    - Frozen onedir:  directory of the EXE
    - Source run:     the repo root (paths.py lives at src/ayen_ode/paths.py)
    """
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def user_data_dir() -> Path:
    """Writable per-user dir. Frozen → %APPDATA%/Ayen-Ode; source → repo root."""
    override = os.environ.get("AYEN_ODE_USER_DATA", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    if is_frozen():
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA")
            if appdata:
                return Path(appdata) / "Ayen-Ode"
            return Path.home() / "AppData" / "Roaming" / "Ayen-Ode"
        if sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "Ayen-Ode"
        xdg = os.environ.get("XDG_CONFIG_HOME")
        if xdg:
            return Path(xdg) / "ayen-ode"
        return Path.home() / ".config" / "ayen-ode"
    # Source mode: keep .env and data/ next to the repo, matching the original layout.
    return Path(__file__).resolve().parent.parent.parent


def static_dir() -> Path:
    return bundle_dir() / "static"


def env_path() -> Path:
    return user_data_dir() / ".env"


def env_example_path() -> Path:
    """Read-only template. Always from the bundle, never from user_data."""
    return bundle_dir() / ".env.example"


def db_path_default() -> Path:
    """Default SQLite path, honouring AYEN_ODE_DB_PATH if set.

    Relative paths in AYEN_ODE_DB_PATH resolve against user_data_dir() so that
    a frozen build doesn't try to write into the bundle directory.
    """
    override = os.environ.get("AYEN_ODE_DB_PATH", "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = (user_data_dir() / p).resolve()
        return p
    return user_data_dir() / "data" / "ayen_ode.db"


def ensure_user_dir() -> Path:
    """Create user_data_dir if missing and seed .env from .env.example on first run.

    Called at startup from desktop.py and from config.load_settings().
    Safe to call multiple times — idempotent.
    """
    d = user_data_dir()
    d.mkdir(parents=True, exist_ok=True)
    env = env_path()
    if not env.exists():
        ex = env_example_path()
        if ex.exists():
            try:
                env.write_text(ex.read_text(encoding="utf-8"), encoding="utf-8")
            except OSError:
                pass
    return d
