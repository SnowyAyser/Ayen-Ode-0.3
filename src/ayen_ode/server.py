"""HTTP server for Ayen-Ode state and narrative."""

from __future__ import annotations

import json
import os
import secrets
import threading
import time
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from . import paths
from .config import load_settings
from .narrative import investigate_entity
from .routes import make_all_routes
from .routes.auth import _client_ip
from .service import AyenOdeService
from .services.base import make_db_connection, utc_now


settings = load_settings()
service = AyenOdeService(settings.db_path)

# Reset any stuck processing jobs back to queued on server start/import
try:
    with service.connect() as conn:
        conn.execute("UPDATE investigation_jobs SET status = 'queued' WHERE status = 'processing'")
        conn.commit()
except Exception as e:
    print(f"Error resetting stuck processing jobs: {e}")



# utc_now is imported from services.base — the local alias keeps call sites unchanged.
_utc_now = utc_now


# --- Session Store ---


class SessionStore:
    def __init__(self, db_path: Path):
        self._db_path = db_path

    def _conn(self):
        return make_db_connection(self._db_path)

    def create(self) -> str:
        token = secrets.token_hex(32)
        now = _utc_now()
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO sessions (token, created_at, last_used) VALUES (?, ?, ?)",
                (token, now, now),
            )
            conn.commit()
        finally:
            conn.close()
        return token

    def validate(self, token: str) -> bool:
        conn = self._conn()
        try:
            row = conn.execute("SELECT token FROM sessions WHERE token = ?", (token,)).fetchone()
            if row:
                conn.execute("UPDATE sessions SET last_used = ? WHERE token = ?", (_utc_now(), token))
                conn.commit()
                return True
            return False
        finally:
            conn.close()

    def delete(self, token: str) -> None:
        conn = self._conn()
        try:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
        finally:
            conn.close()


sessions = SessionStore(settings.db_path)


# --- App Assembly ---

_PUBLIC_PATHS = {
    "/", "/health", "/dashboard.html", "/narrative.html", "/create-world.html",
    "/debug.html", "/desktop-bootstrap", "/api/local-ai/status",
}

static_dir = paths.static_dir()

starlette_app = Starlette(
    routes=make_all_routes(service, settings, sessions) + [
        Mount("/static", app=StaticFiles(directory=static_dir), name="static"),
    ],
)

cors_app = CORSMiddleware(
    starlette_app,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["content-type", "authorization"],
    expose_headers=[],
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path == "/api/whoami":
            return await call_next(request)

        if settings.allowed_ips:
            client_ip = _client_ip(request)
            if client_ip not in settings.allowed_ips:
                return PlainTextResponse(f"Forbidden — your IP: {client_ip}", status_code=403)

        if (
            path in _PUBLIC_PATHS
            or path.startswith("/static")
            or (path == "/api/login" and request.method == "POST")
        ):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "").strip()
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        token = auth_header[7:]
        if not sessions.validate(token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        return await call_next(request)


class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


app = CacheControlMiddleware(AuthMiddleware(cors_app))


# --- Background Workers ---


from .worker import investigation_worker

# Automatically start background worker threads on server boot/import
threading.Thread(target=investigation_worker, daemon=True).start()


# --- Entry Point ---


def main() -> None:
    import uvicorn

    # Reload is force-disabled in frozen builds (PyInstaller bundles can't
    # re-exec a Python script for the reloader child process).
    reload_enabled = (not paths.is_frozen()) and os.getenv("AYEN_ODE_RELOAD", "1") == "1"

    uvicorn.run(
        "ayen_ode.server:app",
        host=settings.host,
        port=settings.port,
        reload=reload_enabled,
        reload_dirs=[str(Path(__file__).resolve().parent)],
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
