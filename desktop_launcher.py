"""PyInstaller entry point for the Ayen-Ode desktop app.

This script is what the EXE actually runs. It dispatches to one of two modes:

    ayen-ode.exe              -> open the native window + run the embedded server
    ayen-ode.exe --settings   -> open the tkinter settings window (edit .env)

Keep this file tiny and dependency-free at import time so PyInstaller's
bootstrap is fast and predictable.
"""

from __future__ import annotations

import multiprocessing
import sys


def main() -> int:
    # Required first thing on Windows for any frozen app that might spawn a
    # multiprocessing child (anthropic SDK, watchfiles, etc.). Harmless on
    # other platforms.
    multiprocessing.freeze_support()

    if "--settings" in sys.argv[1:]:
        from ayen_ode.desktop import run_settings_window
        return run_settings_window()

    from ayen_ode.desktop import run_desktop
    return run_desktop()


if __name__ == "__main__":
    raise SystemExit(main())
