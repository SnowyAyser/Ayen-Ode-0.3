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


def relink_text_with_llm(client: Any, text: str, already_investigated: list[str]) -> str:
    if not text.strip():
        return text

    investigated_list_str = "\n".join(f"- {name}" for name in already_investigated)
    
    prompt = f"""You are an assistant for a narrative RPG engine.
Your task is to analyze the provided text and wrap any keywords (characters, locations, objects, factions, events) that represent discoverable lore or entities in `<investigate item='NAME' cost='1'>KEYWORD</investigate>` tags so the player can click and investigate them.

Already investigated entities (DO NOT wrap these in investigate tags, as they are already known):
{investigated_list_str}

Rules:
1. ONLY wrap items that are NOT in the already investigated list. If a keyword is in the already investigated list, leave it as plain text (do not wrap it in tags).
2. If an item is already wrapped in `<investigate>` tags, preserve it exactly as-is.
3. Be highly selective: only wrap named entities (such as specific characters, cities, factions) or new, made-up words/terms/fantasy jargon, complex world-specific vocabulary/lore, or novel ideas/concepts introduced by the game that are not simple enough to understand on their own and need explanation. Do NOT wrap common nouns (like 'sword', 'tower', 'star', 'plinth', 'event', 'skeleton', 'lights'), abstract concepts, or generic/common words.
4. Ensure target entity names in the item attribute are clean and exact (e.g. item='old merchant', item='desert ruins').
5. If a sub-entity name or a person/place (e.g., 'Kal-Dorum' or 'Kal Dorum') is mentioned within a longer text or as part of another entity name (e.g., 'the Verge of Kal-Dorum'), but that specific sub-entity does NOT have its own standalone entry in the already investigated list, you MUST wrap it in an `<investigate>` tag (e.g., `<investigate item='Kal-Dorum' cost='1'>Kal-Dorum</investigate>`) so it can be investigated independently!
6. Return ONLY the final relinked text. Do not include any explanations, formatting wrappers, markdown fences, or conversational filler. Keep all other text exactly unchanged.

Input text:
{text}
"""
    try:
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.warning(f"Error calling Anthropic API during relinking: {e}")
        return text


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


def auto_pre_generate_new_investigations(client: Any, service: Any, world_id: str, text: str) -> None:
    """Scan text for investigate tags, and background-pregenerate any new entities."""
    if not client:
        return

    items = extract_investigate_tags(text)
    if not items:
        return

    import threading
    from .narrative import investigate_entity

    def pregen_worker(name: str, etype: str):
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
            entities = conn.execute("SELECT DISTINCT name FROM entities").fetchall()
            already_investigated = [row["name"] for row in entities]
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
