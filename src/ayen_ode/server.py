"""HTTP server for Ayen-Ode state and narrative."""

from __future__ import annotations

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

from .config import load_settings
from .narrative import investigate_entity
from .routes import make_all_routes
from .routes.auth import _client_ip
from .service import AyenOdeService
from .services.base import make_db_connection, utc_now


settings = load_settings()
service = AyenOdeService(settings.db_path)


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

_PUBLIC_PATHS = {"/", "/health", "/dashboard.html", "/narrative.html", "/create-world.html", "/debug.html"}

static_dir = Path(__file__).parent.parent.parent / "static"

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


app = AuthMiddleware(cors_app)


# --- Background Worker ---


def investigation_worker() -> None:
    """Background worker that processes investigation jobs one at a time."""
    while True:
        try:
            with service.connect() as conn:
                conn.execute(
                    """UPDATE investigation_jobs SET status = 'processing'
                       WHERE job_id = (
                           SELECT job_id FROM investigation_jobs
                           WHERE status = 'queued' ORDER BY created_at ASC LIMIT 1
                       )"""
                )
                claimed = conn.execute("SELECT changes()").fetchone()[0]
                job = (
                    conn.execute(
                        "SELECT * FROM investigation_jobs WHERE status = 'processing'"
                        " ORDER BY created_at ASC LIMIT 1"
                    ).fetchone()
                    if claimed
                    else None
                )

            if not job:
                time.sleep(1)
                continue

            job_id = job["job_id"]
            world_id = job["world_id"]
            entity_name = job["entity_name"]
            entity_type = job["entity_type"]

            try:
                result = investigate_entity(
                    settings.anthropic_client, service, world_id, entity_name, entity_type, []
                )
                entity_id = result.get("entity", {}).get("entity_id")
                service.complete_investigation_job(
                    job_id,
                    entity_id,
                    {
                        "narrative": result.get("narrative", ""),
                        "entity": result.get("entity", {}),
                        "stats": result.get("stats", {}),
                    },
                )
                service.restore_investigation_points(1, world=world_id)
            except Exception as e:
                with service.connect() as conn:
                    conn.execute(
                        "UPDATE investigation_jobs SET status = 'failed' WHERE job_id = ?",
                        (job_id,),
                    )
                service.restore_investigation_points(1, world=world_id)
        except Exception as e:
            print(f"Investigation worker error: {e}")
            time.sleep(1)


# --- Entry Point ---


def main() -> None:
    import uvicorn

    worker_thread = threading.Thread(target=investigation_worker, daemon=True)
    worker_thread.start()

    uvicorn.run(
        "ayen_ode.server:app",
        host=settings.host,
        port=settings.port,
        reload=os.getenv("AYEN_ODE_RELOAD", "1") == "1",
        reload_dirs=[str(Path(__file__).resolve().parent)],
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
