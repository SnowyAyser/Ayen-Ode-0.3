"""Auth, health, and static-page route handlers."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse
from starlette.routing import Route

_STATIC_DIR = Path(__file__).parent.parent.parent.parent / "static"


def _client_ip(request: Request) -> str:
    """Resolve the real client IP, handling IPv4-mapped IPv6 and proxy headers."""
    ip = request.client.host if request.client else ""
    if not ip:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
    if ip.startswith("::ffff:"):
        ip = ip[7:]
    return ip


def make_auth_routes(service: Any, settings: Any, sessions: Any) -> list:
    async def health(_: Any) -> PlainTextResponse:
        return PlainTextResponse("Ayen-Ode server is running.")

    async def serve_login(_: Any) -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")

    async def serve_dashboard(_: Any) -> FileResponse:
        return FileResponse(_STATIC_DIR / "dashboard.html")

    async def serve_narrative(_: Any) -> FileResponse:
        return FileResponse(_STATIC_DIR / "narrative.html")

    async def serve_create_world(_: Any) -> FileResponse:
        return FileResponse(_STATIC_DIR / "create-world.html")

    async def serve_debug(_: Any) -> FileResponse:
        return FileResponse(_STATIC_DIR / "debug.html")

    async def whoami_handler(request: Request) -> JSONResponse:
        raw_host = request.client.host if request.client else None
        forwarded = request.headers.get("x-forwarded-for", "")
        detected = _client_ip(request)
        return JSONResponse({
            "detected_ip": detected,
            "raw_client_host": raw_host,
            "x_forwarded_for": forwarded,
        })

    async def login_handler(request: Request) -> JSONResponse:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        username = data.get("username", "")
        password = data.get("password", "")
        if username == settings.app_username and password == settings.app_password:
            token = sessions.create()
            return JSONResponse({"token": token})
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)

    async def logout_handler(request: Request) -> JSONResponse:
        auth_header = request.headers.get("authorization", "").strip()
        if auth_header.startswith("Bearer "):
            sessions.delete(auth_header[7:])
        return JSONResponse({"ok": True})

    async def settings_status_handler(_: Any) -> JSONResponse:
        # Re-read .env directly so the answer reflects the current file, not the
        # snapshot loaded at server start. Used by the dashboard banner.
        env_path = Path(__file__).parent.parent.parent.parent / ".env"
        api_key = ""
        if env_path.exists():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    s = line.strip()
                    if s.startswith("ANTHROPIC_API_KEY="):
                        api_key = s.split("=", 1)[1].strip()
                        break
            except OSError:
                pass
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
        configured = bool(api_key) and api_key != "sk-ant-..."
        return JSONResponse({
            "api_key_configured": configured,
            "stale": configured and api_key != settings.anthropic_api_key,
        })

    async def settings_launch_handler(request: Request) -> JSONResponse:
        # Localhost-only by design — the native window opens on the server's
        # desktop, so a remote client clicking this would do nothing useful and
        # could be abused to spawn subprocesses.
        ip = _client_ip(request)
        if ip not in {"127.0.0.1", "::1", "localhost"}:
            return JSONResponse({"error": "Settings window can only be opened from localhost"}, status_code=403)
        try:
            kwargs: dict[str, Any] = {
                "cwd": str(Path(__file__).parent.parent.parent.parent),
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "stdin": subprocess.DEVNULL,
                "close_fds": True,
            }
            if sys.platform == "win32":
                # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP — survives if the
                # server restarts, no inherited console.
                kwargs["creationflags"] = 0x00000008 | 0x00000200
            else:
                kwargs["start_new_session"] = True
            subprocess.Popen(
                [sys.executable, "-m", "ayen_ode.settings_window"],
                **kwargs,
            )
        except OSError as e:
            return JSONResponse({"error": f"Could not launch settings window: {e}"}, status_code=500)
        return JSONResponse({"ok": True})

    async def restart_handler(request: Request) -> JSONResponse:
        # Localhost-only — same policy as settings/launch.
        ip = _client_ip(request)
        if ip not in {"127.0.0.1", "::1", "localhost"}:
            return JSONResponse(
                {"error": "Restart can only be triggered from localhost"}, status_code=403
            )
        # Exit cleanly after a short delay so the response has time to be sent.
        # start.bat loops on exit-code 0 and restarts the process automatically.
   