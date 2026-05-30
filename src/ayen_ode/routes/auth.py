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
            try:
                from ..relinker import run_database_relinking
                threading.Thread(target=run_database_relinking, args=(service, settings), daemon=True).start()
            except Exception:
                pass
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

    # Settings live inside the dashboard now (see static/dashboard.html).
    # The old subprocess-Tk path is gone; settings_window.py is kept only for
    # devs who want `python -m ayen_ode.settings_window` in source mode.
    # The two routes below back the in-window modal.

    # Whitelist of keys the user can edit through the in-window settings panel.
    # Anything else in a POST body is dropped on the floor.
    _EDITABLE_KEYS = (
        "ANTHROPIC_API_KEY",
        "APP_USERNAME",
        "APP_PASSWORD",
        "ALLOWED_IPS",
        "AYEN_ODE_PORT",
        "AYEN_ODE_FULLSCREEN",  # 1/0 — persisted fullscreen preference for the next launch
    )

    def _parse_env(text: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            out[k.strip()] = v.strip()
        return out

    def _mask(value: str) -> str:
        if not value or value == "sk-ant-...":
            return ""
        if len(value) <= 8:
            return "•" * len(value)
        return value[:7] + "…" + value[-4:]

    async def settings_get_handler(request: Request) -> JSONResponse:
        """Return current user-editable settings from %APPDATA%/Ayen-Ode/.env.
        The API key and password are masked — write-only from the client's
        perspective. The fullscreen flag is reported verbatim as "1" or "0"."""
        ip = _client_ip(request)
        if not _is_loopback(ip):
            return JSONResponse({"error": "Settings only available from localhost"}, status_code=403)
        env_path = paths.env_path()
        values: dict[str, str] = {}
        if env_path.exists():
            try:
                values = _parse_env(env_path.read_text(encoding="utf-8"))
            except OSError:
                pass
        api_key = values.get("ANTHROPIC_API_KEY", "")
        api_key_set = bool(api_key) and api_key != "sk-ant-..."
        return JSONResponse({
            "anthropic_api_key_masked": _mask(api_key) if api_key_set else "",
            "anthropic_api_key_set": api_key_set,
            "anthropic_api_key_stale": api_key_set and api_key != settings.anthropic_api_key,
            "app_username": values.get("APP_USERNAME", ""),
            "app_password_set": bool(values.get("APP_PASSWORD", "")),
            "allowed_ips": values.get("ALLOWED_IPS", ""),
            "ayen_ode_port": values.get("AYEN_ODE_PORT", ""),
            "fullscreen": values.get("AYEN_ODE_FULLSCREEN", "") == "1",
        })

    async def settings_post_handler(request: Request) -> JSONResponse:
        """Write a subset of settings to %APPDATA%/Ayen-Ode/.env.

        Empty string values are ignored (so leaving a field blank doesn't wipe
        an existing secret). To explicitly clear a value, send the sentinel
        `__clear__`. Comments and key order in .env are preserved by
        settings_window.write_env, which we reuse."""
        ip = _client_ip(request)
        if not _is_loopback(ip):
            return JSONResponse({"error": "Settings only editable from localhost"}, status_code=403)
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        if not isinstance(data, dict):
            return JSONResponse({"error": "Expected a JSON object"}, status_code=400)

        to_write: dict[str, str] = {}
        for key in _EDITABLE_KEYS:
            if key not in data:
                continue
            val = data[key]
            if not isinstance(val, (str, bool, int)):
                continue
            if isinstance(val, bool):
                val = "1" if val else "0"
            elif isinstance(val, int):
                val = str(val)
            val = val.strip()
            if val == "":
                continue  # don't clobber existing values with empty
            if val == "__clear__":
                val = ""
            to_write[key] = val

        if not to_write:
            return JSONResponse({"ok": True, "wrote": []})

        try:
            from ..settings_window import write_env
            write_env(to_write)
        except OSError as e:
            return JSONResponse({"error": f"Could not write .env: {e}"}, status_code=500)

        return JSONResponse({"ok": True, "wrote": sorted(to_write.keys())})

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

    async def frontend_error_log_handler(request: Request) -> JSONResponse:
        try:
            data = await request.json()
            message = data.get("message", "Unknown error")
            source = data.get("source", "unknown")
            lineno = data.get("lineno", 0)
            colno = data.get("colno", 0)
            stack = data.get("stack", "")
            
            import sys
            sys.stderr.write(
                f"\n[FRONTEND ERROR] {message}\n"
                f"  Source: {source} (line {lineno}, col {colno})\n"
                f"  Stack: {stack}\n\n"
            )
            return JSONResponse({"success": True})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

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
        try:
            from ..relinker import run_database_relinking
            threading.Thread(target=run_database_relinking, args=(service, settings), daemon=True).start()
        except Exception:
            pass
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
        Route("/api/settings", settings_get_handler, methods=["GET"]),
        Route("/api/settings", settings_post_handler, methods=["POST"]),
        Route("/api/restart", restart_handler, methods=["POST"]),
        Route("/api/logs/error", frontend_error_log_handler, methods=["POST"]),
    ]
