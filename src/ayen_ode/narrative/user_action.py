from typing import Any
import json
import logging

from ..config import HAIKU_MODEL

logger = logging.getLogger("ayen_ode.narrative.user_action")


def _clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def process_user_action(
    client: Any,
    service: Any,
    world_id: str,
    user_action: str,
    conversation_history: list[dict],
    player_entity_id: str | None = None,
) -> tuple[str, list[dict], dict, dict, dict]:
    """Process a user action and extract a simple JSON response of trigger states."""

    # Retrieve all database entities as possible subjects
    existing_entities = service.list_entities(world=world_id)
    entity_list = existing_entities.get("entities", [])
    
    known_subjects = [e["name"] for e in entity_list if e.get("name")]
    default_scene_subjects = [
        "old man",
        "self",
        "paladin guard",
        "paladin",
        "wooden chest",
        "chest",
        "stone archway",
        "door"
    ]
    known_subjects_lower = [k.lower() for k in known_subjects]
    for subj in default_scene_subjects:
        if subj.lower() not in known_subjects_lower:
            known_subjects.append(subj)
            known_subjects_lower.append(subj.lower())
        
    subjects_context = "\n".join(f"- {subject}" for subject in known_subjects)

    # Formulate recent history text for model context
    history_text = ""
    for m in conversation_history[-6:]:
        role = "Player" if m["role"] == "user" else "Narrator"
        history_text += f"[{role}]: {m['content']}\n"

    # Construct the instruction prompt
    system_prompt = (
        "You are an action-detection assistant. Check if the player's action indicates the general idea or intent of any of the actions below (it does not need to match the exact wording). If they did, output ONLY the corresponding JSON block (set fields to null if unspecified or unclear). If they did not perform any of these actions, return a plain text message starting with \"no_action_detected: \" explaining that no movement, identify, or door usage action was detected.\n\n"
        "Available Actions & JSON Syntax:\n"
        "1. Movement (player.move = true):\n"
        "{\n"
        '  "player.move": true,\n'
        '  "move.direction": "towards" | "away" | "north" | "south" | "east" | "west" | "forwards" | "back" or null,\n'
        '  "towards.subject": string or null (ONLY if it matches a subject from the list below, otherwise null. Defaults to "self" for relative/cardinal directions),\n'
        '  "move.distance_inches": integer or null (convert distance to inches, e.g. "3 feet" -> 36)\n'
        "}\n\n"
        "2. Identify/Inspect (player.identify = true):\n"
        "{\n"
        '  "player.identify": true,\n'
        '  "identify.target": string or null (ONLY if it matches a subject from the list below, otherwise null)\n'
        "}\n\n"
        "3. Use/Open Door (player.door_use = true):\n"
        "{\n"
        '  "player.door_use": true,\n'
        '  "door.target": string or null (ONLY if it matches a subject from the list below, otherwise null)\n'
        "}\n\n"
        "Available Subjects in the current scene:\n"
        f"{subjects_context}\n"
    )

    user_prompt = (
        f"Recent conversation history:\n{history_text}\n"
        f"Player action to analyze:\n{user_action}"
    )

    # Update progress status
    from .stages.utils import set_stage_progress, clear_stage_progress
    try:
        set_stage_progress(world_id, "Stage 1/1: Extracting Action JSON...")
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        raw_text = "".join(b.text for b in response.content if b.type == "text").strip()
        clean_text = _clean_json_text(raw_text)
        if clean_text.startswith("no_movement_detected:"):
            narrative_response = clean_text[len("no_movement_detected:"):].strip()
        elif clean_text.startswith("no_action_detected:"):
            narrative_response = clean_text[len("no_action_detected:"):].strip()
        else:
            try:
                parsed = json.loads(clean_text)
                if isinstance(parsed, dict):
                    # Validate and normalize/nullify towards.subject
                    if "towards.subject" in parsed and parsed["towards.subject"] is not None:
                        subj = str(parsed["towards.subject"]).strip().lower()
                        matched = None
                        for ks in known_subjects:
                            if ks.lower() == subj:
                                matched = ks
                                break
                        parsed["towards.subject"] = matched

                    # Validate and normalize/nullify identify.target
                    if "identify.target" in parsed and parsed["identify.target"] is not None:
                        tgt = str(parsed["identify.target"]).strip().lower()
                        matched = None
                        for ks in known_subjects:
                            if ks.lower() == tgt:
                                matched = ks
                                break
                        parsed["identify.target"] = matched

                    # Validate and normalize/nullify door.target
                    if "door.target" in parsed and parsed["door.target"] is not None:
                        tgt = str(parsed["door.target"]).strip().lower()
                        matched = None
                        for ks in known_subjects:
                            if ks.lower() == tgt:
                                matched = ks
                                break
                        parsed["door.target"] = matched

                    clean_text = json.dumps(parsed, indent=2)
            except Exception as e:
                logger.warning(f"Could not parse/validate action JSON: {e}")
            narrative_response = clean_text
    except Exception as e:
        logger.error(f"Failed action extraction: {e}")
        # Return fallback JSON indicating error
        narrative_response = json.dumps({
            "player.move": False,
            "move.direction": None,
            "towards.subject": None,
            "move.distance_inches": None,
            "player.identify": False,
            "identify.target": None,
            "player.door_use": False,
            "door.target": None
        }, indent=2)
    finally:
        clear_stage_progress(world_id)

    updated_history = conversation_history.copy()
    if narrative_response:
        updated_history.append({"role": "assistant", "content": narrative_response})

    # Return narrative response along with empty reports to preserve route/viewer compatibility
    return narrative_response, updated_history, {}, {}, {}
