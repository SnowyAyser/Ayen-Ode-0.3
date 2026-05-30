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
    "/debug.html", "/desktop-bootstrap",
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
            cost = dict(job).get("cost", 1)

            from datetime import datetime, timezone
            created_at = job["created_at"]
            try:
                if created_at.endswith("Z"):
                    created_at = created_at[:-1] + "+00:00"
                created_dt = datetime.fromisoformat(created_at)
                elapsed = (datetime.now(timezone.utc) - created_dt).total_seconds()
            except Exception:
                elapsed = 0.0

            try:
                # Check if we have pre-generated cached data in SQLite database
                cached_result = None
                clean_name = entity_name.strip()
                variants = [clean_name]
                if clean_name.lower().endswith("s"):
                    if clean_name.lower().endswith("es"):
                        variants.append(clean_name[:-2])
                    variants.append(clean_name[:-1])
                else:
                    variants.append(clean_name + "s")
                    variants.append(clean_name + "es")

                with service.connect() as conn:
                    for var in variants:
                        row_cached = conn.execute(
                            "SELECT result_json FROM pregenerated_investigations"
                            " WHERE world_id = ? AND LOWER(entity_name) = LOWER(?)",
                            (world_id, var),
                        ).fetchone()
                        if row_cached:
                            cached_result = json.loads(row_cached[0])
                            break

                if cached_result:
                    # 1. Consume the cached JSON directly
                    result = cached_result
                    
                    # Trigger background auto-pregeneration for any new investigate tags inside the compendium card content
                    try:
                        from .relinker import auto_pre_generate_new_investigations
                        parts = []
                        if "narrative" in result:
                            parts.append(result["narrative"])
                        entity_data = result.get("entity", {})
                        if "summary" in entity_data:
                            parts.append(entity_data["summary"])
                        for note in entity_data.get("timeline_notes", []):
                            parts.append(note)
                        for q in entity_data.get("open_questions", []):
                            parts.append(q)
                        combined_text = "\n".join(parts)
                        auto_pre_generate_new_investigations(settings.anthropic_client, service, world_id, combined_text)
                    except Exception as ex:
                        print(f"Failed to auto-pregenerate tags from compendium card: {ex}")

                    # 2. Sleep for the remaining pacing countdown relative to created_at
                    remaining = 60.0 - elapsed
                    if remaining > 0:
                        time.sleep(remaining)
                else:
                    # 3. Fallback: Query Claude immediately if not cached (fallback path)
                    job_context = dict(job).get("context")
                    result = investigate_entity(
                        settings.anthropic_client, service, world_id, entity_name, entity_type, [], save_to_db=False, context=job_context
                    )
                    
                    # Trigger background auto-pregeneration for any new investigate tags inside the compendium card content
                    try:
                        from .relinker import auto_pre_generate_new_investigations
                        parts = []
                        if "narrative" in result:
                            parts.append(result["narrative"])
                        entity_data = result.get("entity", {})
                        if "summary" in entity_data:
                            parts.append(entity_data["summary"])
                        for note in entity_data.get("timeline_notes", []):
                            parts.append(note)
                        for q in entity_data.get("open_questions", []):
                            parts.append(q)
                        combined_text = "\n".join(parts)
                        auto_pre_generate_new_investigations(settings.anthropic_client, service, world_id, combined_text)
                    except Exception as ex:
                        print(f"Failed to auto-pregenerate tags from compendium card: {ex}")

                    try:
                        elapsed_after = (datetime.now(timezone.utc) - created_dt).total_seconds()
                    except Exception:
                        elapsed_after = time.time() - start_time
                    remaining = 60.0 - elapsed_after
                    if remaining > 0:
                        time.sleep(remaining)

                # --- 4. Persist to SQLite DB since the investigation is now officially complete! ---
                entity_data = result.get("entity", {})
                entity_result = service.create_entity(
                    name=entity_name,
                    entity_type=entity_type,
                    summary=entity_data.get("summary", ""),
                    world=world_id,
                    tags=entity_data.get("tags", []),
                    timeline_notes=entity_data.get("timeline_notes", []),
                    stats=result.get("stats", {}),
                )
                entity = entity_result.get("entity", {})
                entity_id = entity.get("entity_id")

                if entity_id:
                    service.record_investigation(
                        item_name=entity_name,
                        world=world_id,
                        entity_id=entity_id,
                    )
                    try:
                        from .relinker import run_database_relinking
                        threading.Thread(target=run_database_relinking, args=(service, settings), daemon=True).start()
                    except Exception:
                        pass

                service.complete_investigation_job(
                    job_id,
                    entity_id,
                    {
                        "narrative": result.get("narrative", ""),
                        "entity": entity,
                        "stats": result.get("stats", {}),
                    },
                )
                service.restore_investigation_points(cost, world=world_id)
            except Exception as e:
                with service.connect() as conn:
                    conn.execute(
                        "UPDATE investigation_jobs SET status = 'failed' WHERE job_id = ?",
                        (job_id,),
                    )
                service.restore_investigation_points(cost, world=world_id)
        except Exception as e:
            print(f"Investigation worker error: {e}")
            time.sleep(1)


# --- Entry Point ---


def main() -> None:
    import uvicorn
    from .relinker import run_database_relinking

    worker_thread = threading.Thread(target=investigation_worker, daemon=True)
    worker_thread.start()

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
