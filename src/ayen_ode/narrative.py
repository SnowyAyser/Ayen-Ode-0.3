"""Narrative generation and conversation handling via Anthropic API."""

from __future__ import annotations

import json
import re
from typing import Any
from anthropic import Anthropic

from .config import SONNET_MODEL
from .context_assembler import ContextAssembler
from .intake import _run_intake_pass
from .quests import generate_overarching_goal, scan_for_goals
from .services.base import STAT_NAMES_BY_ENTITY_TYPE
from .narrative_utils import parse_investigation_response


def _extract_text(response: Any) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


# --- Tool Schemas ---

_ENTITY_TOOL_SCHEMAS = [
    {
        "name": "register_entity",
        "description": (
            "Register a new entity introduced in the narrative. "
            "Call this for each distinct character, location, faction, object, or event "
            "that appears or is named in the scene."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "entity_type": {
                    "type": "string",
                    "enum": ["character", "faction", "location", "object", "event"],
                },
                "summary": {
                    "type": "string",
                    "description": "Brief description of this entity (1-2 sentences)",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Descriptive tags e.g. 'merchant', 'antagonist', 'ruined'",
                },
                "stats": {
                    "type": "object",
                    "description": (
                        "Hidden stats as 0-100 integers. "
                        "Characters: force, influence, will, perception, resilience, volatility. "
                        "Factions: power, cohesion, reach, resources, secrecy, instability. "
                        "Locations: security, prosperity, corruption, danger, stability, mystique. "
                        "Objects: potency, rarity, durability, risk, control, significance. "
                        "Events: scale, urgency, fallout, visibility, disruption, momentum."
                    ),
                    "additionalProperties": {"type": "integer"},
                },
            },
            "required": ["name", "entity_type", "summary"],
        },
    },
    {
        "name": "add_timeline_note",
        "description": "Add a timeline note to an existing entity after a significant story event.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "The entity's ID"},
                "note": {"type": "string", "description": "The timeline event to record"},
            },
            "required": ["entity_id", "note"],
        },
    },
    {
        "name": "apply_stat_change",
        "description": "Apply stat changes to an entity when narrative events meaningfully affect them.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string"},
                "changes": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                    "description": "Signed stat deltas e.g. {\"will\": -10, \"resilience\": 5}",
                },
                "reason": {"type": "string"},
            },
            "required": ["entity_id", "changes", "reason"],
        },
    },
]


# --- Tool Execution ---


def _execute_entity_tool(service: Any, world_id: str, tool_name: str, tool_input: dict) -> None:
    """Execute a single entity tool call from Claude. Failures are silent to not break narrative."""
    try:
        if tool_name == "register_entity":
            service.create_entity(
                name=tool_input["name"],
                entity_type=tool_input["entity_type"],
                summary=tool_input.get("summary", ""),
                world=world_id,
                tags=tool_input.get("tags"),
                stats=tool_input.get("stats"),
            )
        elif tool_name == "add_timeline_note":
            entity_id = tool_input["entity_id"]
            existing = service.get_entity(entity_id, world=world_id)
            current_notes = existing.get("entity", {}).get("timeline_notes") or []
            service.update_entity(
                entity_id=entity_id,
                world=world_id,
                timeline_notes=current_notes + [tool_input["note"]],
            )
        elif tool_name == "apply_stat_change":
            service.apply_stat_change(
                entity_id=tool_input["entity_id"],
                changes=tool_input["changes"],
                reason=tool_input["reason"],
                world=world_id,
            )
    except Exception:
        pass


# --- Public API ---


def initialize_world(
    client: Anthropic,
    service: Any,
    world_id: str,
    name: str,
    premise: str,
    theme_tone: str,
    player_role: str,
) -> str:
    """Generate initial scene for a new world (entities created on-demand via investigation)."""

    prompt = f"""You are the world-builder and narrator for a narrative RPG called Ayen-Ode.

A new world has been created:
- Name: {name}
- Premise: {premise}
- Theme/Tone: {theme_tone}
- Player Role: {player_role}

Your task:
1. Write an immersive, evocative opening scene (2-3 paragraphs) — vivid, atmospheric, do NOT offer choices
2. Use <investigate> tags to mark items the player can click to learn more about
3. Highlight characters, locations, objects, factions, and events with investigation tags.
   CRITICAL: Be highly selective with <investigate> tags. Only wrap items that are named entities (e.g. specific characters, specific cities/locations, unique factions) or new, made-up words/terms/fantasy jargon, complex world-specific vocabulary/lore, or novel ideas/concepts introduced by the game that are not simple enough to understand on their own and need explanation. Do NOT wrap simple common nouns (like 'sword', 'tower', 'event', 'stars', 'rocks', 'skeleton', 'plinth', 'lights'), abstract concepts, or generic descriptors.
4. Do NOT register entities via tools — they will be created on-demand when the player investigates

CRITICAL FORMATTING RULES:
- Use ONLY <investigate> tags for clickable items. NEVER output raw HTML, <button>, <span>, or any other HTML tags.
- Attribute for objects/items: item='name'
- Attribute for characters/NPCs: npc='name'
- Attribute for locations: location='name'
- Attribute for factions: faction='name'
- Attribute for events: event='name'
- Always include cost='1' (or cost='2' for major entities)

Correct example:
"You stand in the <investigate item='town square' cost='1'>bustling town square</investigate>, where <investigate npc='old merchant' cost='1'>an elderly merchant</investigate> tends his stall."

Incorrect (never do this):
"You stand in the <button class='...'>town square</button>"

Write the opening scene with <investigate> tags only. Do not use any tools."""

    response = client.messages.create(
        model=SONNET_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    initial_scene = _extract_text(response)

    service.set_original_opening_scene(world_id, initial_scene)
    service.initialize_world_currency(world=world_id, initial_balance=5, max_balance=5)
    service.save_world_handoff(
        handoff_text=initial_scene,
        world=world_id,
        current_state_summary=f"World just created. {premise}",
        active_tensions=[],
    )

    try:
        from .relinker import auto_pre_generate_new_investigations
        auto_pre_generate_new_investigations(client, service, world_id, initial_scene)
    except Exception:
        pass

    # Generate the overarching (Tier 1) goal — silent on failure
    generate_overarching_goal(
        client=client,
        service=service,
        world_id=world_id,
        name=name,
        premise=premise,
        theme_tone=theme_tone,
        player_role=player_role,
    )

    return initial_scene


def process_user_action(
    client: Anthropic,
    service: Any,
    world_id: str,
    user_action: str,
    conversation_history: list[dict],
    player_entity_id: str | None = None,
) -> tuple[str, list[dict]]:
    """Process a user action and generate narrative with investigation tags."""

    investigation_state = service.get_investigation_state(world=world_id)
    currency = service.get_investigation_balance(world=world_id)

    seen_names: set[str] = set()
    investigated_items = []
    for inv in investigation_state.get("investigations", []):
        name = inv["item_name"]
        if name not in seen_names:
            seen_names.add(name)
            investigated_items.append(name)
    investigated_context = "\n".join(f"- {item}" for item in investigated_items) or "None yet."
    investigation_block = (
        f"Investigation Points: {currency.get('balance', 0)}/{currency.get('max_balance', 0)}\n"
        f"Already Investigated (don't re-introduce):\n{investigated_context}"
    )

    if player_entity_id is not None:
        assembler = ContextAssembler(service)
        packet = assembler.assemble(world_id=world_id, player_entity_id=player_entity_id)
        world_context_block = (
            "WORLD STATE (read this exactly — do not infer or add to it):\n"
            + assembler.to_prompt_text(packet)
        )
    else:
        existing_entities = service.list_entities(world=world_id)
        current_handoff = service.get_world_handoff(world_id)
        entity_list = existing_entities.get("entities", [])
        entity_context = (
            "\n".join(
                f"- {e['name']} ({e.get('entity_type', e.get('type', '?'))}) [id: {e.get('entity_id', '')}]"
                for e in entity_list
            )
            or "None yet."
        )
        world_context_block = (
            f"Current World Context:\n{current_handoff.get('handoff_text', 'No context yet')}\n\n"
            f"Known Entities (use these IDs for tools):\n{entity_context}"
        )

    context = investigation_block + "\n\n" + world_context_block

    system_prompt = f"""You are the narrator and world-master for the narrative RPG Ayen-Ode.

INVESTIGATION SYSTEM:
- Players can investigate items by clicking them
- Mark investigable items with <investigate> tags in your narrative
- CRITICAL: Be highly selective with <investigate> tags. Only wrap items that are named entities (e.g. specific characters, specific cities/locations, unique factions) or new, made-up words/terms/fantasy jargon, complex world-specific vocabulary/lore, or novel ideas/concepts introduced by the game that are not simple enough to understand on their own and need explanation. Do NOT wrap simple common nouns (like 'sword', 'tower', 'event', 'stars', 'rocks', 'skeleton', 'plinth', 'lights'), abstract concepts, or generic descriptors.
- NEVER output raw HTML, <button>, <span>, or any other HTML tags — ONLY use <investigate> tags
- Correct format: <investigate item='item name' cost='1'>display text</investigate>
- Attribute by type: item='name' for objects, npc='name' for characters, location='name' for places, faction='name' for factions, event='name' for events
- Cost is typically 1 (or 2 for major entities)
- Do NOT create entities upfront — they are created on-demand when investigated
- Reference already-investigated items naturally in the story without tagging them again

Your role:
- Ground your response in what the player just did — that action is the focus
- Show the immediate, natural consequences of that action: how the world reacts, how nearby entities respond
- Keep the response proportional (1-3 paragraphs); shorter actions earn shorter responses
- Do not inject new plot threads, arriving characters, or unrelated events unless they are a direct consequence of the player's action
- Leave space for the player to act next — end on a settled beat, not a cliffhanger you manufactured
- Mark interesting items, NPCs, locations, factions, and events for investigation

For already-investigated entities, use tools to maintain continuity:
- Call add_timeline_note on known entities to record significant events
- Call apply_stat_change when narrative events meaningfully shift their stats

ACTIVE DEBTS & OBLIGATIONS:
- Adhere strictly to any active debts listed in the world context.
- If a character owes another entity a resource (e.g., money, cows, favors, or a life), enforce this subtext in dialogue and actions. Debtors might act defensive, desperate, servile, or attempt to bargain or settle their obligations.

Do not break character or reference mechanics in the narrative text itself.

{context}"""

    messages = conversation_history.copy()
    messages.append({"role": "user", "content": user_action})

    response = client.messages.create(
        model=SONNET_MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=messages,
        tools=_ENTITY_TOOL_SCHEMAS,
        tool_choice={"type": "auto"},
    )

    narrative_response = ""
    for block in response.content:
        if block.type == "text":
            narrative_response += block.text
        elif block.type == "tool_use":
            _execute_entity_tool(service, world_id, block.name, block.input)

    # Relink keywords in the new story response incrementally
    if narrative_response:
        try:
            from .relinker import relink_text_with_llm, auto_pre_generate_new_investigations
            with service.connect() as conn:
                entities = conn.execute("SELECT name, entity_type FROM entities").fetchall()
                already_investigated = {row["name"]: row["entity_type"] for row in entities}
            narrative_response = relink_text_with_llm(client, narrative_response, already_investigated)
            auto_pre_generate_new_investigations(client, service, world_id, narrative_response)
        except Exception:
            pass

    if narrative_response and player_entity_id is not None:
        _run_intake_pass(client, service, world_id, player_entity_id, narrative_response)

    # Increment turn counter and run goal scan every 3 turns
    if player_entity_id is not None:
        try:
            turn_count = service.increment_world_turn_count(world=world_id)
            if turn_count % 3 == 0:
                scan_for_goals(client, service, world_id, player_entity_id)
        except Exception:
            pass

    updated_history = messages.copy()
    if narrative_response:
        updated_history.append({"role": "assistant", "content": narrative_response})

    return narrative_response, updated_history


def investigate_entity(
    client: Anthropic,
    service: Any,
    world_id: str,
    item_name: str,
    entity_type: str,
    conversation_history: list[dict],
    save_to_db: bool = True,
    context: str | None = None,
) -> dict[str, Any]:
    """Generate entity details on-demand when investigated, weave into narrative."""

    current_handoff = service.get_world_handoff(world_id)
    stat_names = ", ".join(sorted(STAT_NAMES_BY_ENTITY_TYPE.get(entity_type, set())))

    context_instruction = ""
    if context:
        context_instruction = f'\nNarrative Context:\nThis keyword/entity appeared in the following specific message or compendium entry:\n"""\n{context.strip()}\n"""\nUse this established context to guide your description, aligning facts, events, and tone.\n'

    prompt = f"""You are the narrator for a narrative RPG. A player has investigated: {item_name}

World Context:
{current_handoff.get('handoff_text', 'No context yet')}
{context_instruction}
TASK:
1. Write a brief discovery narrative (1-2 paragraphs) about what the player learns when investigating "{item_name}"
2. After the narrative, provide details for the Compendium using this JSON format:
```json
{{
    "summary": "Brief 1-2 sentence description",
    "tags": ["tag1", "tag2"],
    "timeline_notes": ["initial note about this {entity_type}"],
    "stats": {{
        "stat1": 45,
        "stat2": 65
    }}
}}
```

CRITICAL FORMATTING RULES:
- If your discovery narrative or any Compendium details ("summary", "timeline_notes") introduce other characters, locations, objects, or events that the player can investigate further, you MUST wrap them in `<investigate item='entity name' cost='1'>display text</investigate>` tags!
  CRITICAL: Be highly selective with <investigate> tags. Only wrap items that are named entities (e.g. specific characters, specific cities/locations, unique factions) or new, made-up words/terms/fantasy jargon, complex world-specific vocabulary/lore, or novel ideas/concepts introduced by the game that are not simple enough to understand on their own and need explanation. Do NOT wrap simple common nouns (like 'sword', 'tower', 'event', 'stars', 'rocks', 'skeleton', 'plinth', 'lights'), abstract concepts, or generic descriptors.
- Use ONLY `<investigate>` tags for clickable items. NEVER output raw HTML, `<button>`, or any other HTML tags.

Entity type: {entity_type}
Stat types for {entity_type}: {stat_names}

Write naturally, in character. The discovery should feel organic to the world."""

    response = client.messages.create(
        model=SONNET_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = _extract_text(response)
    entity_details = parse_investigation_response(response_text, entity_type)
    
    # Run the Haiku relinker pass incrementally on the new compendium details to guarantee rich nested investigation links
    try:
        from .relinker import relink_text_with_llm
        with service.connect() as conn:
            entities = conn.execute("SELECT name, entity_type FROM entities").fetchall()
            already_investigated = {row["name"]: row["entity_type"] for row in entities}
            
        if "summary" in entity_details and entity_details["summary"]:
            entity_details["summary"] = relink_text_with_llm(client, entity_details["summary"], already_investigated)
            
        timeline_notes = entity_details.get("timeline_notes", [])
        for i in range(len(timeline_notes)):
            if timeline_notes[i]:
                timeline_notes[i] = relink_text_with_llm(client, timeline_notes[i], already_investigated)
    except Exception:
        pass

    stats = entity_details.get("stats", {})

    if save_to_db:
        entity_result = service.create_entity(
            name=item_name,
            entity_type=entity_type,
            summary=entity_details.get("summary", ""),
            world=world_id,
            tags=entity_details.get("tags", []),
            timeline_notes=entity_details.get("timeline_notes", []),
            stats=stats,
        )
        entity = entity_result.get("entity", {})
        entity_id = entity.get("entity_id")
        if entity_id:
            service.record_investigation(
                item_name=item_name,
                world=world_id,
                entity_id=entity_id,
            )
    else:
        entity = {
            "name": item_name,
            "entity_type": entity_type,
            "summary": entity_details.get("summary", ""),
            "tags": entity_details.get("tags", []),
            "timeline_notes": entity_details.get("timeline_notes", []),
        }

    # Extract just the narrative portion (before the JSON block)
    narrative_text = response_text.split("```")[0].strip()

    # Relink the discovery narrative text as well
    try:
        from .relinker import relink_text_with_llm
        with service.connect() as conn:
            entities = conn.execute("SELECT name, entity_type FROM entities").fetchall()
            already_investigated = {row["name"]: row["entity_type"] for row in entities}
        if narrative_text:
            narrative_text = relink_text_with_llm(client, narrative_text, already_investigated)
    except Exception:
        pass

    return {
        "narrative": narrative_text,
        "entity": entity,
        "stats": stats,
    }


