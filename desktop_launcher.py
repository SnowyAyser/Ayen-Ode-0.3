"""PyInstaller entry point for the Ayen-Ode desktop app.

This script is what the EXE actually runs. It starts the embedded server and
opens a native pywebview window — the entire desktop UX, including settings
and fullscreen toggle, lives inside that window.

Keep this file tiny and dependency-free at import time so PyInstaller's
bootstrap is fast and predictable.
"""

from __future__ import annotations

import multiprocessing


def main() -> int:
    # Required first thing on Windows for any frozen app that might spawn a
    # multiprocessing child (anthropic SDK, watchfiles, etc.). Harmless on
    # other platforms.
    multiprocessing.freeze_support()

    from ayen_ode.desktop import run_desktop
    return run_desktop()


if __name__ == "__main__":
    raise SystemExit(main())
