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
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from starlette.routing import Route

from .. import paths


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


def _is_loopback(ip: str) -> bool:
    return ip in {"127.0.0.1", "::1", "localhost"}


def make_auth_routes(service: Any, settings: Any, sessions: Any) -> list:
    static_dir = paths.static_dir()

    async def health(_: Any) -> PlainTextResponse:
        return PlainTextResponse("Ayen-Ode server is running.")

    async def serve_login(_: Any) -> FileResponse:
        return FileResponse(static_dir / "index.html")

    async def serve_dashboard(_: Any) -> FileResponse:
        return FileResponse(static_dir / "dashboard.html")

    async def serve_narrative(_: Any) -> FileResponse:
        return FileResponse(static_dir / "narrative.html")

    async def serve_create_world(_: Any) -> FileResponse:
        return FileResponse(static_dir / "create-world.html")

    async def serve_debug(_: Any) -> FileResponse:
        return FileResponse(static_dir / "debug.html")

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
        env_path = paths.env_path()
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
        if not _is_loopback(ip):
            return JSONResponse({"error": "Settings window can only be opened from localhost"}, status_code=403)
        try:
            kwargs: dict[str, Any] = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "stdin": subprocess.DEVNULL,
                "close_fds": True,
            }
            if sys.platform == "win32":
                kwargs["creationflags"] = 0x00000008 | 0x00000200  # DETACHED | NEW_PROCESS_GROUP
            else:
                kwargs["start_new_session"] = True

            if paths.is_frozen():
                # In a PyInstaller bundle, sys.executable IS the app EXE.
                # Re-launch ourselves with the --settings flag (handled in desktop_launcher).
                subprocess.Popen([sys.executable, "--settings"], **kwargs)
            else:
                kwargs["cwd"] = str(paths.bundle_dir())
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
        if not _is_loopback(ip):
            return JSONResponse(
                {"error": "Restart can only be triggered from localhost"}, status_code=403
            )

        def _delayed_exit() -> None:
            time.sleep(0.4)
            # Exit code 42 signals the desktop launcher (if running) to relaunch.
            # In source mode start.bat loops on exit-code 0; we use 42 for explicit restart.
            os._exit(42 if paths.is_frozen() else 0)

        threading.Thread(target=_delayed_exit, daemon=True).start()
        return JSONResponse({"ok": True})

    async def desktop_bootstrap_handler(request: Request) -> Any:
        """Serve a one-shot HTML page that sets the session token in localStorage
        and redirects to the dashboard. Only available in desktop mode and only
        accessible from loopback.

        Used by the pywebview launcher so the user never sees the login screen.
        The token is a fresh session created server-side; nothing crosses the
        URL boundary except the HTML response.
        """
        if os.environ.get("AYEN_ODE_DESKTOP") != "1":
            return PlainTextResponse("Not in desktop mode", status_code=404)
        if not _is_loopback(_client_ip(request)):
            return PlainTextResponse("Forbidden", status_code=403)
        token = sessions.create()
        # token is hex from secrets.token_hex(32) — safe to inline without escaping.
        html = (
            "<!doctype html><html><head><meta charset=\"utf-8\"><title>Ayen-Ode</title>"
            "<style>html,body{margin:0;background:#0f172a;color:#94a3b8;"
            "font-family:Segoe UI,system-ui,sans-serif;height:100%;"
            "display:flex;align-items:center;justify-content:center;}</style></head>"
            "<body><div>Loading Ayen-Ode…</div><script>"
            f"try{{localStorage.setItem('apiKey','{token}');}}catch(e){{}}"
            "location.replace('/dashboard.html');"
            "</script></body></html>"
        )
        return HTMLResponse(html)

    return [
        Route("/health", health, methods=["GET"]),
        Route("/", serve_login, methods=["GET"]),
        Route("/dashboard.html", serve_dashboard, methods=["GET"]),
        Route("/narrative.html", serve_narrative, methods=["GET"]),
        Route("/create-world.html", serve_create_world, methods=["GET"]),
        Route("/debug.html", serve_debug, methods=["GET"]),
        Route("/desktop-bootstrap", desktop_bootstrap_handler, methods=["GET"]),
        Route("/api/whoami", whoami_handler, methods=["GET"]),
        Route("/api/login", login_handler, methods=["POST"]),
        Route("/api/logout", logout_handler, methods=["POST"]),
        Route("/api/settings/status", settings_status_handler, methods=["GET"]),
        Route("/api/settings/launch", settings_launch_handler, methods=["POST"]),
        Route("/api/restart", restart_handler, methods=["POST"]),
    ]
