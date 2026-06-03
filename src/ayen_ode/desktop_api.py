from __future__ import annotations

import sys
from . import paths


class DesktopApi:
    """Bridge exposed to the dashboard JS as `window.pywebview.api`."""

    def __init__(self) -> None:
        self._window = None  # type: ignore[var-annotated]

    def bind_window(self, window: object) -> None:
        self._window = window

    # --- methods callable from JS via window.pywebview.api.<name>() -------

    def toggle_fullscreen(self) -> bool:
        """Flip fullscreen state."""
        try:
            if self._window is not None:
                self._window.toggle_fullscreen()
        except Exception:
            pass
        return True

    def set_fullscreen(self, value: bool) -> bool:
        """Force fullscreen to a specific state."""
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
        """Sentinel the JS uses to detect desktop mode."""
        return True

    def close_window(self) -> bool:
        """Close the application window and exit the process."""
        try:
            if self._window is not None:
                self._window.destroy()
        except Exception:
            pass
        return True

    def get_saved_username(self) -> str:
        """Get the saved username from user_data_dir to bypass Same-Origin port isolation."""
        try:
            p = paths.user_data_dir() / "saved_username.txt"
            if p.exists():
                return p.read_text(encoding="utf-8").strip()
        except Exception:
            pass
        return ""

    def save_username(self, username: str) -> bool:
        """Save the username to user_data_dir to bypass Same-Origin port isolation."""
        try:
            p = paths.user_data_dir() / "saved_username.txt"
            p.write_text(username.strip(), encoding="utf-8")
            return True
        except Exception:
            pass
        return False

    def get_auto_login(self) -> bool:
        """Get the auto-login preference from user_data_dir."""
        try:
            p = paths.user_data_dir() / "auto_login.txt"
            if p.exists():
                val = p.read_text(encoding="utf-8").strip()
                return val == "true"
        except Exception:
            pass
        return False

    def save_auto_login(self, value: bool) -> bool:
        """Save the auto-login preference to user_data_dir."""
        try:
            p = paths.user_data_dir() / "auto_login.txt"
            val = "true" if value else "false"
            p.write_text(val, encoding="utf-8")
            return True
        except Exception:
            pass
        return False

    def get_configured_credentials(self) -> dict[str, str]:
        """Get the plain username and password configured in settings."""
        try:
            from .server import settings
            return {
                "username": settings.app_username or "",
                "password": settings.app_password or ""
            }
        except Exception:
            return {"username": "", "password": ""}
