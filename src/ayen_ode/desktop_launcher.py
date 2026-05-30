"""Entry point for the Ayen-Ode desktop app.

Launches the high-fidelity WebView2 wrapper engine directly.
"""

from __future__ import annotations

import multiprocessing


def main() -> int:
    multiprocessing.freeze_support()

    # If a newer source version exists, rebuild and relaunch before starting.
    # No-op when running from source; only the packaged exe self-updates.
    from ayen_ode.updater import check_and_update
    if check_and_update():
        return 0

    from ayen_ode.desktop import check_single_instance
    if not check_single_instance():
        msg = "You can't have more than one instance of the game open at a time."
        import sys
        if sys.stderr is not None:
            try:
                sys.stderr.write(msg + "\n")
            except Exception:
                pass
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    None, 
                    msg, 
                    "Ayen-Ode", 
                    0x00000010 | 0x00000000  # MB_ICONERROR | MB_OK
                )
            except Exception:
                pass
        return 1

    from ayen_ode.desktop import run_desktop
    return run_desktop()


if __name__ == "__main__":
    raise SystemExit(main())
