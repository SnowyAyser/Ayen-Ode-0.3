import json
import logging
from typing import Any
from .parser import text_needs_relinking, relink_text_with_llm
from .pregenerator import auto_pre_generate_new_investigations

logger = logging.getLogger("ayen_ode.relinker.db_relinker")


def run_database_relinking(service: Any, settings: Any) -> None:
    logger.info("Starting background keyword relinking pass...")
    try:
        client = settings.anthropic_client if settings else None
        
        # 1. Fetch investigated entities and all logs/entries in a brief, closed connection
        with service.connect() as conn:
            entities = conn.execute("SELECT name, entity_type FROM entities").fetchall()
            already_investigated = {row["name"]: row["entity_type"] for row in entities}
            logs = conn.execute("SELECT log_id, world_id, narrative_text FROM intake_logs").fetchall()
            handoffs = conn.execute("SELECT handoff_id, world_id, handoff_text FROM world_handoffs").fetchall()
            entity_rows = conn.execute(
                "SELECT entity_id, world_id, name, summary, timeline_notes_json, open_questions_json FROM entities"
            ).fetchall()

        # 2. Process Intake Logs that ACTUALLY need relinking
        logs_updated = 0
        for log in logs:
            log_id = log["log_id"]
            world_id = log["world_id"]
            old_text = log["narrative_text"]
            if text_needs_relinking(old_text, already_investigated):
                new_text = relink_text_with_llm(client, old_text, already_investigated)
                if new_text != old_text:
                    with service.connect() as conn:
                        conn.execute(
                            "UPDATE intake_logs SET narrative_text = ? WHERE log_id = ?",
                            (new_text, log_id)
                        )
                    auto_pre_generate_new_investigations(client, service, world_id, new_text)
                    logs_updated += 1
        if logs_updated > 0:
            logger.info(f"Relinked narrative text in {logs_updated} intake logs.")
                
        # 3. Process World Handoffs that ACTUALLY need relinking
        handoffs_updated = 0
        for handoff in handoffs:
            handoff_id = handoff["handoff_id"]
            world_id = handoff["world_id"]
            old_text = handoff["handoff_text"]
            if text_needs_relinking(old_text, already_investigated):
                new_text = relink_text_with_llm(client, old_text, already_investigated)
                if new_text != old_text:
                    with service.connect() as conn:
                        conn.execute(
                            "UPDATE world_handoffs SET handoff_text = ? WHERE handoff_id = ?",
                            (new_text, handoff_id)
                        )
                    auto_pre_generate_new_investigations(client, service, world_id, new_text)
                    handoffs_updated += 1
        if handoffs_updated > 0:
            logger.info(f"Relinked handoff text in {handoffs_updated} world handoffs.")
            
        # 4. Process Compendium Entries that ACTUALLY need relinking
        entities_updated = 0
        for row in entity_rows:
            entity_id = row["entity_id"]
            world_id = row["world_id"]
            name = row["name"]
            old_summary = row["summary"]
            timeline_notes = json.loads(row["timeline_notes_json"] or "[]")
            open_questions = json.loads(row["open_questions_json"] or "[]")
            
            # Check if any component of this entity card needs relinking
            needs_summary = text_needs_relinking(old_summary, already_investigated)
            needs_timeline = any(text_needs_relinking(note, already_investigated) for note in timeline_notes)
            needs_questions = any(text_needs_relinking(q, already_investigated) for q in open_questions)
            
            if needs_summary or needs_timeline or needs_questions:
                new_summary = relink_text_with_llm(client, old_summary, already_investigated, use_llm=False) if needs_summary else old_summary
                summary_changed = (new_summary != old_summary)
                
                new_timeline = []
                timeline_changed = False
                for note in timeline_notes:
                    if text_needs_relinking(note, already_investigated):
                        new_note = relink_text_with_llm(client, note, already_investigated, use_llm=False)
                        new_timeline.append(new_note)
                        if new_note != note:
                            timeline_changed = True
                    else:
                        new_timeline.append(note)
                        
                new_questions = []
                questions_changed = False
                for q in open_questions:
                    if text_needs_relinking(q, already_investigated):
                        new_q = relink_text_with_llm(client, q, already_investigated, use_llm=False)
                        new_questions.append(new_q)
                        if new_q != q:
                            questions_changed = True
                    else:
                        new_questions.append(q)
                        
                if summary_changed or timeline_changed or questions_changed:
                    with service.connect() as conn:
                        conn.execute(
                            """
                            UPDATE entities
                            SET summary = ?, timeline_notes_json = ?, open_questions_json = ?
                            WHERE entity_id = ?
                            """,
                            (
                                new_summary,
                                json.dumps(new_timeline),
                                json.dumps(new_questions),
                                entity_id
                            )
                        )
                    # Gather and scan all newly updated text components of this compendium entry
                    parts = [new_summary] + new_timeline + new_questions
                    combined_text = "\n".join(parts)
                    auto_pre_generate_new_investigations(client, service, world_id, combined_text)
                    entities_updated += 1
        if entities_updated > 0:
            logger.info(f"Relinked {entities_updated} compendium entries.")
            
        logger.info("Database keyword relinking pass completed successfully.")
    except Exception as e:
        logger.warning(f"Error during background relinking pass: {e}")
