"""Self-update check for the packaged desktop build.

When Ayen-Ode runs as the bundled ``Ayen-Ode.exe`` it compares a hash of the
on-disk source tree against the hash recorded at the last build
(``.build_hash``). If the source is newer, it spawns a detached helper
(``scripts/update_and_launch.ps1``) that waits for this process to exit,
rebuilds the exe, and relaunches the fresh build.

Running from source (``python -m ayen_ode.desktop_launcher``) is a no-op here —
``Play-Ayen-Ode.bat`` already handles the rebuild in that case.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

_CREATE_NEW_CONSOLE = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
_CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _repo_root() -> Optional[Path]:
    """Find the project root (the folder holding scripts/ and src/)."""
    start = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve()
    for parent in [start.parent, *start.parents]:
        if (parent / "scripts" / "build_exe.ps1").exists() and (parent / "src").exists():
            return parent
    return None


def _source_hash(root: Path) -> Optional[str]:
    script = root / "scripts" / "source_hash.ps1"
    if not script.exists():
        return None
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(script), "-RepoRoot", str(root)],
            capture_output=True, text=True, timeout=120,
            creationflags=_CREATE_NO_WINDOW,
        )
    except Exception:
        return None
    out = (result.stdout or "").strip()
    if not out or out in ("ERROR", "EMPTY"):
        return None
    return out


def check_and_update() -> bool:
    """Start a self-update if the source is newer than this build.

    Returns ``True`` when an update has been launched and the caller should
    exit immediately (the helper will relaunch the rebuilt exe). Returns
    ``False`` when the app is up to date or updating is not possible, in which
    case the caller should continue launching normally.
    """
    # Only the packaged Windows exe self-updates; source runs use the .bat.
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return False

    root = _repo_root()
    if root is None:
        return False

    # Without the build venv we can't recompile — just launch what we have.
    if not (root / ".venv-build" / "Scripts" / "python.exe").exists():
        return False

    current = _source_hash(root)
    if current is None:
        return False

    hash_file = root / ".build_hash"
    stored = ""
    if hash_file.exists():
        try:
            stored = hash_file.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception:
            stored = ""

    if current == stored:
        return False  # up to date

    helper = root / "scripts" / "update_and_launch.ps1"
    if not helper.exists():
        return False

    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(helper), "-RepoRoot", str(root),
             "-WaitPid", str(os.getpid())],
            creationflags=_CREATE_NEW_CONSOLE,
            close_fds=True,
        )
    except Exception:
        return False
    return True
