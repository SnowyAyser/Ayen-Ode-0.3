import json
import logging
import re
from typing import Any
from .config import HAIKU_MODEL

logger = logging.getLogger("ayen_ode.relinker")


def text_needs_relinking(text: str, already_investigated: list[str]) -> bool:
    if not text or not text.strip():
        return False
    text_lower = text.lower()
    for name in already_investigated:
        name_clean = name.strip()
        if not name_clean:
            continue
        # Fast case-insensitive substring check first before compiling regex
        if name_clean.lower() in text_lower:
            # Check if this name is already linkified in the text
            # (An entity is considered linkified if its tag attributes are present)
            tag_attr1 = f"item='{name_clean}'".lower()
            tag_attr2 = f'item="{name_clean}"'.lower()
            tag_attr3 = f"npc='{name_clean}'".lower()
            tag_attr4 = f'npc="{name_clean}"'.lower()
            tag_attr5 = f"location='{name_clean}'".lower()
            tag_attr6 = f'location="{name_clean}"'.lower()
            tag_attr7 = f"faction='{name_clean}'".lower()
            tag_attr8 = f'faction="{name_clean}"'.lower()
            tag_attr9 = f"event='{name_clean}'".lower()
            tag_attr10 = f'event="{name_clean}"'.lower()
            
            if (tag_attr1 in text_lower or tag_attr2 in text_lower or 
                tag_attr3 in text_lower or tag_attr4 in text_lower or
                tag_attr5 in text_lower or tag_attr6 in text_lower or
                tag_attr7 in text_lower or tag_attr8 in text_lower or
                tag_attr9 in text_lower or tag_attr10 in text_lower):
                continue
                
            # If not linkified, verify it's a whole word match (to prevent partial matches)
            try:
                pattern = r'\b' + re.escape(name_clean) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            except Exception:
                pass
    return False


def relink_text_programmatically(text: str, already_investigated: dict[str, str] | list[str]) -> str:
    if not text.strip() or not already_investigated:
        return text

    # Convert list/dict already_investigated to a uniform lowercase name -> type dict
    if isinstance(already_investigated, list):
        existing_entities = {name.strip().lower(): "object" for name in already_investigated if name.strip()}
    else:
        existing_entities = {name.strip().lower(): etype for name, etype in already_investigated.items() if name.strip()}

    # Sort names by length descending to match longer multi-word phrases first
    sorted_names = sorted(existing_entities.keys(), key=len, reverse=True)

    # Split text into segments inside and outside investigate tags
    tag_pattern = re.compile(r"(<investigate\s+[^>]*?>.*?</investigate>)", re.DOTALL)
    parts = tag_pattern.split(text)

    type_attr_map = {
        "character": "npc",
        "location": "location",
        "faction": "faction",
        "object": "item",
        "event": "event"
    }

    for i in range(len(parts)):
        # Only modify segments outside existing investigate tags
        if not parts[i].startswith("<investigate"):
            segment = parts[i]
            for name in sorted_names:
                etype = existing_entities[name]
                attr = type_attr_map.get(etype, "item")
                
                # Match whole words case-insensitively
                pattern = re.compile(r"\b(" + re.escape(name) + r")\b", re.IGNORECASE)
                replacement = f"<investigate {attr}='{name}' cost='1'>\\1</investigate>"
                segment = pattern.sub(replacement, segment)
            parts[i] = segment

    return "".join(parts)


def relink_text_with_llm(client: Any, text: str, already_investigated: dict[str, str] | list[str]) -> str:
    """Fallback wrapper that maps to programmatic relinker to bypass AI calls entirely."""
    return relink_text_programmatically(text, already_investigated)


_INV_RE = re.compile(r"<investigate\s+([^>]*?)>(.*?)</investigate>", re.DOTALL)


def extract_investigate_tags(text: str) -> list[tuple[str, str]]:
    """Extract list of (item_name, entity_type) from <investigate> tags in the text."""
    if not text:
        return []
    results = []
    for m in _INV_RE.finditer(text):
        attrs = m.group(1)
        display = m.group(2).strip()
        item_name = ""
        entity_type = "object"
        
        # Parse name using our robust, quote-flexible regexes
        item_matches = list(re.finditer(r"(item|npc|location|faction|event)=(['\"])(.*?)\2", attrs))
        if not item_matches:
            item_matches = list(re.finditer(r"(item|npc|location|faction|event)=([^\s'\">]+)", attrs))
            for am in item_matches:
                item_name = am.group(2)
                t = am.group(1)
                if t == "npc":        entity_type = "character"
                elif t == "location": entity_type = "location"
                elif t == "faction":  entity_type = "faction"
                elif t == "event":    entity_type = "event"
        else:
            for am in item_matches:
                item_name = am.group(3)
                t = am.group(1)
                if t == "npc":        entity_type = "character"
                elif t == "location": entity_type = "location"
                elif t == "faction":  entity_type = "faction"
                elif t == "event":    entity_type = "event"
        
        name = (item_name or display).strip()
        if name:
            results.append((name, entity_type))
    return results


def get_name_variants(name: str) -> list[str]:
    name_clean = name.strip().lower()
    variants = [name_clean]
    if name_clean.endswith("s"):
        if name_clean.endswith("es"):
            variants.append(name_clean[:-2])
        variants.append(name_clean[:-1])
    else:
        variants.append(name_clean + "s")
        variants.append(name_clean + "es")
    return list(set(variants))


import threading

_pending_pregenerations = set()
_pending_pregenerations_lock = threading.Lock()


def clear_pending_pregenerations(world_id: str) -> None:
    """Remove all pending pre-generation keys for a given world (e.g. after reset)."""
    with _pending_pregenerations_lock:
        to_remove = {k for k in _pending_pregenerations if k[0] == world_id}
        _pending_pregenerations -= to_remove

def auto_pre_generate_new_investigations(client: Any, service: Any, world_id: str, text: str) -> None:
    """Scan text for investigate tags, and background-pregenerate any new entities."""
    if not client:
        return

    items = extract_investigate_tags(text)
    if not items:
        return

    from .narrative import investigate_entity

    def pregen_worker(name: str, etype: str):
        key = (world_id, name.strip().lower())
        with _pending_pregenerations_lock:
            if key in _pending_pregenerations:
                return
            _pending_pregenerations.add(key)
        try:
            variants = get_name_variants(name)
            placeholders = ",".join("?" for _ in variants)

            # 1. Check if already investigated (in entities table, singular/plural variants)
            with service.connect() as conn:
                already_exists = conn.execute(
                    f"SELECT 1 FROM entities WHERE world_id = ? AND LOWER(name) IN ({placeholders})",
                    [world_id] + variants
                ).fetchone()
                if already_exists:
                    return

                # 2. Check if already pre-generated (in pregenerated_investigations table, singular/plural variants)
                already_pregenerated = conn.execute(
                    f"SELECT 1 FROM pregenerated_investigations WHERE world_id = ? AND LOWER(entity_name) IN ({placeholders})",
                    [world_id] + variants
                ).fetchone()
                if already_pregenerated:
                    return

            logger.info(f"Auto-pregenerating new investigation in background: {name} ({etype})")
            
            # Query Claude for this new investigation, save_to_db=False (stores to pregenerated_investigations cache)
            investigate_entity(
                client,
                service,
                world_id,
                name,
                etype,
                [],
                save_to_db=False,
                context=f"Discovered in previous narrative or compendium card."
            )
        except Exception as e:
            logger.warning(f"Error auto-pregenerating {name}: {e}")
        finally:
            with _pending_pregenerations_lock:
                _pending_pregenerations.discard(key)

    for name, etype in items:
        threading.Thread(target=pregen_worker, args=(name, etype), daemon=True).start()


def run_database_relinking(service: Any, settings: Any) -> None:
    api_key = settings.anthropic_api_key
    if not api_key or api_key == "missing-api-key":
        logger.info("Skipping keyword relinking: ANTHROPIC_API_KEY is not set or missing.")
        return

    logger.info("Starting background keyword relinking pass...")
    try:
        client = settings.anthropic_client
        
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
                new_summary = relink_text_with_llm(client, old_summary, already_investigated) if needs_summary else old_summary
                summary_changed = (new_summary != old_summary)
                
                new_timeline = []
                timeline_changed = False
                for note in timeline_notes:
                    if text_needs_relinking(note, already_investigated):
                        new_note = relink_text_with_llm(client, note, already_investigated)
                        new_timeline.append(new_note)
                        if new_note != note:
                            timeline_changed = True
                    else:
                        new_timeline.append(note)
                        
                new_questions = []
                questions_changed = False
                for q in open_questions:
                    if text_needs_relinking(q, already_investigated):
                        new_q = relink_text_with_llm(client, q, already_investigated)
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


def pre_generate_scene_investigations_sync(client: Any, service: Any, world_id: str, text: str) -> None:
    """Extract tags and pre-generate all of them concurrently, waiting for completion."""
    if not client:
        return

    items = extract_investigate_tags(text)
    if not items:
        return

    import concurrent.futures
    from .narrative import investigate_entity
    from .services.base import utc_now

    def worker(name: str, etype: str):
        try:
            variants = get_name_variants(name)
            placeholders = ",".join("?" for _ in variants)

            # Check if already exists or pregenerated
            with service.connect() as conn:
                already_exists = conn.execute(
                    f"SELECT 1 FROM entities WHERE world_id = ? AND LOWER(name) IN ({placeholders})",
                    [world_id] + variants
                ).fetchone()
                if already_exists:
                    return

                already_pregenerated = conn.execute(
                    f"SELECT 1 FROM pregenerated_investigations WHERE world_id = ? AND LOWER(entity_name) IN ({placeholders})",
                    [world_id] + variants
                ).fetchone()
                if already_pregenerated:
                    return

            logger.info(f"Synchronously pre-generating: {name} ({etype})")
            result = investigate_entity(
                client,
                service,
                world_id,
                name,
                etype,
                [],
                save_to_db=False,
                context="Pre-generated during world loading."
            )
            now = utc_now()
            with service.connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO pregenerated_investigations"
                    " (world_id, entity_name, entity_type, result_json, created_at)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (world_id, name.strip(), etype.strip(), json.dumps(result), now),
                )
        except Exception as e:
            logger.warning(f"Failed pre-generating {name}: {e}")

    # Use a ThreadPoolExecutor to run all of them concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, name, etype) for name, etype in items]
        concurrent.futures.wait(futures)
