import logging
from typing import Any
from .parser import text_needs_relinking, relink_text_programmatically, get_all_linkable_entities

logger = logging.getLogger("ayen_ode.relinker.history_relinker")


def relink_world_history_logs(service: Any, world_id: str) -> None:
    """Traverse and update world history logs (intake_logs and world_handoffs) programmatically."""
    logger.info(f"Starting history relinking for world_id: {world_id}")
    try:
        # 1. Fetch entities and logs for this world
        already_investigated = get_all_linkable_entities(service, world_id)
        with service.connect() as conn:
            logs = conn.execute(
                "SELECT log_id, narrative_text FROM intake_logs WHERE world_id = ?",
                (world_id,)
            ).fetchall()
            
            handoffs = conn.execute(
                "SELECT handoff_id, handoff_text FROM world_handoffs WHERE world_id = ?",
                (world_id,)
            ).fetchall()

        # 2. Relink Intake Logs
        logs_updated = 0
        for log in logs:
            log_id = log["log_id"]
            old_text = log["narrative_text"]
            if text_needs_relinking(old_text, already_investigated):
                new_text = relink_text_programmatically(old_text, already_investigated)
                if new_text != old_text:
                    with service.connect() as conn:
                        conn.execute(
                            "UPDATE intake_logs SET narrative_text = ? WHERE log_id = ?",
                            (new_text, log_id)
                        )
                    logs_updated += 1

        if logs_updated > 0:
            logger.info(f"Relinked narrative_text in {logs_updated} intake logs for world {world_id}.")

        # 3. Relink World Handoffs
        handoffs_updated = 0
        for handoff in handoffs:
            handoff_id = handoff["handoff_id"]
            old_text = handoff["handoff_text"]
            if text_needs_relinking(old_text, already_investigated):
                new_text = relink_text_programmatically(old_text, already_investigated)
                if new_text != old_text:
                    with service.connect() as conn:
                        conn.execute(
                            "UPDATE world_handoffs SET handoff_text = ? WHERE handoff_id = ?",
                            (new_text, handoff_id)
                        )
                    handoffs_updated += 1

        if handoffs_updated > 0:
            logger.info(f"Relinked handoff_text in {handoffs_updated} world handoffs for world {world_id}.")

        logger.info(f"History relinking for world_id: {world_id} completed successfully.")
    except Exception as e:
        logger.warning(f"Error during history relinking for world_id {world_id}: {e}")
