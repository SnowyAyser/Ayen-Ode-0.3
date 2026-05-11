"""Post-narration intake pass: extract state changes from narration and write to DB."""

from __future__ import annotations

from typing import Any

from .config import HAIKU_MODEL


# --- Tool Schemas ---

_INTAKE_TOOL_SCHEMAS = [
    {
        "name": "mark_quest_progress",
        "description": (
            "Mark a quest completion tag as achieved based on what happened in this narration. "
            "Only call this when the narration clearly shows that a tracked goal milestone was reached. "
            "Use the quest_id and the exact tag string from the quest context provided."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "quest_id": {
                    "type": "string",
                    "description": "The quest_id of the quest being updated",
                },
                "tag": {
                    "type": "string",
                    "description": "The completion tag that was achieved (must match exactly)",
                },
            },
            "required": ["quest_id", "tag"],
        },
    },
    {
        "name": "record_consequence",
        "description": (
            "Record a causal consequence extracted from the narration. "
            "Use when the narration implies that one entity caused a change in another."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cause_id": {"type": "string", "description": "entity_id of the cause"},
                "effect_type": {
                    "type": "string",
                    "enum": [
                        "created", "destroyed", "moved", "transformed",
                        "state_changed", "triggered_event", "relationship_changed",
                    ],
                },
                "target_id": {"type": "string", "description": "entity_id of the target"},
                "detail": {
                    "type": "string",
                    "description": "State change in 'key: old → new' format, e.g. 'status: alive → wounded'",
                },
            },
            "required": ["cause_id", "effect_type", "target_id"],
        },
    },
    {
        "name": "learn_knowledge",
        "description": "Record that an entity learned about another entity as a result of this scene.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string"},
                "target_id": {"type": "string"},
                "degree": {
                    "type": "string",
                    "enum": ["heard_rumor", "secondhand", "witnessed", "deeply_knows"],
                },
            },
            "required": ["entity_id", "target_id", "degree"],
        },
    },
    {
        "name": "move_entity",
        "description": "Record that an entity physically moved to a new container as narrated.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string"},
                "new_container_id": {
                    "type": "string",
                    "description": "entity_id of the destination container",
                },
            },
            "required": ["entity_id", "new_container_id"],
        },
    },
    {
        "name": "advance_time",
        "description": (
            "Record how many in-game seconds elapsed during this action. "
            "Call exactly once per narration turn. "
            "Estimate duration: a brief exchange ≈120s, a short conversation ≈600s, "
            "a fight ≈120s, travel across a room ≈30s, city travel ≈3600s, "
            "a long journey ≈28800s, sleeping ≈28800s."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "integer",
                    "description": "In-game seconds elapsed for this action",
                },
                "label": {
                    "type": "string",
                    "description": (
                        "Human-readable current time after this action, "
                        "using world-appropriate terms "
                        "(e.g. 'Late afternoon, Day 3' or 'The Third Hour of Sundering, Week 2'). "
                        "Omit if the world has no established calendar yet."
                    ),
                },
            },
            "required": ["seconds"],
        },
    },
]

# --- System Prompt ---

_INTAKE_SYSTEM_PROMPT = """You are a state extractor. You will be given a narrative passage from a story.
Your job is to extract concrete, factual state changes that occurred in the passage and record them
using the provided tools.

Rules:
- Only record things explicitly stated or directly implied in the narration — never infer
- Use entity IDs exactly as provided in the entity roster — do not guess or fabricate IDs
- If you cannot identify the cause or target entity_id with certainty, skip that record
- record_consequence: use for causal events (one entity caused a change in another)
- learn_knowledge: use when a character clearly learns something about another entity
- move_entity: use when a character or object physically relocates
- mark_quest_progress: call ONLY when the narration clearly shows a tracked quest milestone was achieved.
  Use the exact quest_id and tag from the ACTIVE QUESTS list. Do not guess or fabricate IDs or tags.
- It is acceptable to call zero tools if nothing concrete changed
- Always call advance_time exactly once to record how many in-game seconds this action took

Do not produce any narrative text. Only call tools."""


# --- Intake Pass ---


def _run_intake_pass(
    client: Any,
    service: Any,
    world_id: str,
    player_entity_id: str,
    narration_text: str,
) -> None:
    """Post-narration event intake: extract state changes from narration and write to DB.

    Uses a small fast model. Failures are silent — intake errors never surface to the player.
    """
    try:
        existing = service.list_entities(world=world_id)
        seen_ids: set[str] = set()
        unique_entities = []
        for e in existing.get("entities", []):
            eid = e.get("entity_id")
            if eid and eid not in seen_ids:
                seen_ids.add(eid)
                unique_entities.append(e)
        entity_lines = "\n".join(
            f"  {e['name']} ({e.get('entity_type', '?')}) → id: {e['entity_id']}"
            for e in unique_entities
        )

        # Build active quest context for mark_quest_progress
        quest_lines = ""
        try:
            quest_data = service.get_active_quests_summary(world=world_id)
            quest_context_parts = []
            for q in quest_data.get("quests", []):
                remaining = [t for t in q["completion_tags"] if t not in q["progress_tags"]]
                if remaining:
                    quest_context_parts.append(
                        f"  [{q['quest_id']}] {q['title']!r} — remaining tags: {remaining}"
                    )
            if quest_context_parts:
                quest_lines = "ACTIVE QUESTS (for mark_quest_progress only):\n" + "\n".join(quest_context_parts) + "\n\n"
        except Exception:
            pass

        user_message = (
            f"{quest_lines}"
            f"Known entities in this world:\n{entity_lines}\n\n"
            f"Narration to analyze:\n{narration_text}"
        )

        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=1024,
            system=_INTAKE_SYSTEM_PROMPT,
            tools=_INTAKE_TOOL_SCHEMAS,
            tool_choice={"type": "auto"},
            messages=[{"role": "user", "content": user_message}],
        )

        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                name = block.name
                inp = block.input
                if name == "advance_time":
                    service.advance_world_time(
                        seconds=int(inp.get("seconds", 0)),
                        label=inp.get("label", ""),
                        world=world_id,
                    )
                elif name == "record_consequence":
                    service.record_consequence(
                        cause_id=inp["cause_id"],
                        effect_type=inp["effect_type"],
                        target_id=inp["target_id"],
                        detail=inp.get("detail", ""),
                        world=world_id,
                    )
                elif name == "learn_knowledge":
                    service.learn(
                        entity_id=inp["entity_id"],
                        target_id=inp["target_id"],
                        degree=inp.get("degree", "heard_rumor"),
                        world=world_id,
                    )
                elif name == "move_entity":
                    service.move(
                        entity_id=inp["entity_id"],
                        new_container_id=inp.get("new_container_id"),
                        world=world_id,
                    )
                elif name == "mark_quest_progress":
                    service.mark_quest_tag(
                        quest_id=inp["quest_id"],
                        tag=inp["tag"],
                        world=world_id,
                    )
            except Exception:
                pass

    except Exception:
        pass
