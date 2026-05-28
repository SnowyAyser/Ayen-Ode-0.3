"""Entry point for the Ayen-Ode desktop app.

Launches the high-fidelity WebView2 wrapper engine directly.
"""

from __future__ import annotations

import multiprocessing


def main() -> int:
    multiprocessing.freeze_support()
    from ayen_ode.desktop import run_desktop
    return run_desktop()


if __name__ == "__main__":
    raise SystemExit(main())
