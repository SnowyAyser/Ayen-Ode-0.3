"""Background worker thread for Ayen-Ode investigation jobs."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone

from .config import load_settings
from .narrative import investigate_entity
from .service import AyenOdeService
from .services.base import utc_now

settings = load_settings()
service = AyenOdeService(settings.db_path)


def investigation_worker() -> None:
    """Background worker that processes investigation jobs one at a time."""
    while True:
        try:
            with service.connect() as conn:
                conn.execute(
                    """UPDATE investigation_jobs SET status = 'processing'
                       WHERE job_id = (
                           SELECT job_id FROM investigation_jobs
                           WHERE status = 'queued' ORDER BY priority ASC, created_at ASC LIMIT 1
                       )"""
                )
                claimed = conn.execute("SELECT changes()").fetchone()[0]
                job = (
                    conn.execute(
                        "SELECT * FROM investigation_jobs WHERE status = 'processing'"
                        " ORDER BY priority ASC, created_at ASC LIMIT 1"
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
            priority = dict(job).get("priority", 1)

            created_at = job["created_at"]
            start_time = time.time()
            try:
                if created_at.endswith("Z"):
                    created_at = created_at[:-1] + "+00:00"
                created_dt = datetime.fromisoformat(created_at)
                elapsed = (datetime.now(timezone.utc) - created_dt).total_seconds()
            except Exception:
                elapsed = 0.0

            import getpass
            try:
                username = getpass.getuser()
            except Exception:
                username = os.environ.get("USERNAME") or os.environ.get("USER", "")
            skip_pacing = (
                os.environ.get("SKIP_INVESTIGATION_PACING") == "1"
                or (username and username.lower() == "zgreiniman")
            )
            pacing_duration = 0.0 if skip_pacing else 60.0

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
                    remaining = pacing_duration - elapsed
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
                    remaining = pacing_duration - elapsed_after
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
                        "theme_report": result.get("theme_report"),
                        "quest_report": result.get("quest_report"),
                        "mechanics_report": result.get("mechanics_report"),
                    },
                )
                service.restore_investigation_points(cost, world=world_id)
            except Exception as e:
                import traceback
                print(f"FAILED processing investigation '{entity_name}': {e}")
                traceback.print_exc()
                with service.connect() as conn:
                    conn.execute(
                        "UPDATE investigation_jobs SET status = 'failed' WHERE job_id = ?",
                        (job_id,),
                    )
                service.restore_investigation_points(cost, world=world_id)
        except Exception as e:
            print(f"Investigation worker error: {e}")
            time.sleep(1)
