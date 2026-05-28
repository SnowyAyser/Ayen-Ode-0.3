"""Post-narration intake pass: extract state changes from narration and write to DB."""

from __future__ import annotations

import re
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
                    "description": "State change in 'key: old -> new' format, e.g. 'status: alive -> wounded'",
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
    {
        "name": "record_debt",
        "description": "Record a new financial, material, or moral debt between two entities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "debtor_id": {"type": "string", "description": "Entity ID who owes the resource"},
                "creditor_id": {"type": "string", "description": "Entity ID who is owed the resource"},
                "resource_type": {"type": "string", "description": "Type of resource, e.g. gold, cows, life, favor"},
                "quantity": {"type": "string", "description": "Amount or scale, e.g. 50, 3, 1, major"},
                "detail": {"type": "string", "description": "Brief description of the debt context"},
                "evidence": {"type": "string", "description": "Direct quote from narration establishing the debt"}
            },
            "required": ["debtor_id", "creditor_id", "resource_type", "quantity", "detail", "evidence"]
        }
    },
    {
        "name": "update_debt_status",
        "description": "Satisfy or default an active debt.",
        "input_schema": {
            "type": "object",
            "properties": {
                "debt_id": {"type": "string", "description": "The unique ID of the debt being updated"},
                "status": {"type": "string", "enum": ["satisfied", "defaulted"]},
                "detail": {"type": "string", "description": "Brief description of how the debt was resolved or defaulted"}
            },
            "required": ["debt_id", "status"]
        }
    },
    {
        "name": "update_character_motivation",
        "description": "Add or remove a motivation tag on a character card.",
        "input_schema": {
            "type": "object",
            "properties": {
                "character_id": {"type": "string"},
                "action": {"type": "string", "enum": ["add", "remove"]},
                "motivation": {"type": "string", "description": "Motivation keyword (e.g. gold, revenge, survival, escape)"}
            },
            "required": ["character_id", "action", "motivation"]
        }
    }
]

# --- System Prompt ---

_INTAKE_SYSTEM_PROMPT = """You are a state extractor. You will be given a narrative passage from a story.
Your job is to extract concrete, factual state changes that occurred in the passage and record them
using the provided tools.

ANALYSIS & CHAIN-OF-THOUGHT:
Before invoking any tools, you must write a brief analysis of the dialogue and description inside a single `<analysis_thought>` tag in your text response.
Analyze:
- Did any dialogue or description imply an obligation or debt (financial, moral, cows, gold, life, favors) was created or resolved?
- Did any character's core motivations or desires shift in dialogue?
- Did any physical movements or consequences occur?
Then, invoke the appropriate tools based on your analysis.

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

Do not produce any other narrative text except the <analysis_thought> block. Only call tools."""


# --- Intake Pass ---


def _run_intake_pass(
    client: Any,
    service: Any,
    world_id: str,
    player_entity_id: str,
    narration_text: str,
) -> None:
    """Post-narration event intake: extract state changes from narration and write to DB.

    Uses a small fast model. Logs all attempts and execution results inside intake_logs.
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

        thought_process = ""
        tools_attempted = []
        tools_executed = []

        for block in response.content:
            if block.type == "text":
                match = re.search(r"<analysis_thought>(.*?)</analysis_thought>", block.text, re.DOTALL)
                if match:
                    thought_process += match.group(1).strip()
                else:
                    thought_process += block.text.strip()
            elif block.type == "tool_use":
                tools_attempted.append({
                    "name": block.name,
                    "input": block.input,
                    "id": block.id
                })

        for tool in tools_attempted:
            name = tool["name"]
            inp = tool["input"]
            res = None
            try:
                if name == "advance_time":
                    res = service.advance_world_time(
                        seconds=int(inp.get("seconds", 0)),
                        label=inp.get("label", ""),
                        world=world_id,
                    )
                elif name == "record_consequence":
                    res = service.record_consequence(
                        cause_id=inp["cause_id"],
                        effect_type=inp["effect_type"],
                        target_id=inp["target_id"],
                        detail=inp.get("detail", ""),
                        world=world_id,
                    )
                elif name == "learn_knowledge":
                    res = service.learn(
                        entity_id=inp["entity_id"],
                        target_id=inp["target_id"],
                        degree=inp.get("degree", "heard_rumor"),
                        world=world_id,
                    )
                elif name == "move_entity":
                    res = service.move(
                        entity_id=inp["entity_id"],
                        new_container_id=inp.get("new_container_id"),
                        world=world_id,
                    )
                elif name == "mark_quest_progress":
                    res = service.mark_quest_tag(
                        quest_id=inp["quest_id"],
                        tag=inp["tag"],
                        world=world_id,
                    )
                elif name == "record_debt":
                    res = service.record_debt(
                        debtor_id=inp["debtor_id"],
                        creditor_id=inp["creditor_id"],
                        resource_type=inp["resource_type"],
                        quantity=inp["quantity"],
                        detail=inp["detail"],
                        evidence=inp["evidence"],
                        world=world_id,
                    )
                elif name == "update_debt_status":
                    res = service.update_debt_status(
                        debt_id=inp["debt_id"],
                        status=inp["status"],
                        detail=inp.get("detail", ""),
                        world=world_id,
                    )
                elif name == "update_character_motivation":
                    character_id = inp["character_id"]
                    action = inp["action"]
                    motivation = inp["motivation"].strip().lower()
                    mot_tag = f"motivation:{motivation}"
                    
                    # Fetch current details
                    entity_res = service.get_entity(character_id, world=world_id)
                    current_tags = entity_res.get("entity", {}).get("tags") or []
                    
                    if action == "add":
                        if mot_tag not in current_tags:
                            new_tags = current_tags + [mot_tag]
                            service.update_entity(entity_id=character_id, world=world_id, tags=new_tags)
                    elif action == "remove":
                        if mot_tag in current_tags:
                            new_tags = [t for t in current_tags if t != mot_tag]
                            service.update_entity(entity_id=character_id, world=world_id, tags=new_tags)
                    
                    res = {"success": True, "character_id": character_id, "action": action, "tag": mot_tag}
                else:
                    raise ValueError(f"Unknown tool name: {name}")

                tools_executed.append({
                    "name": name,
                    "input": inp,
                    "status": "success",
                    "result": res
                })
            except Exception as e:
                tools_executed.append({
                    "name": name,
                    "input": inp,
                    "status": "error",
                    "error": str(e)
                })

        # Save logging entry to database
        try:
            game_time = service.get_world_time(world=world_id)
            time_label = game_time.get("label", "Unknown Time")
            service.log_intake_run(
                narrative_text=narration_text,
                thought_process=thought_process or "No chain of thought analysis outputted.",
                tools_attempted=tools_attempted,
                tools_executed=tools_executed,
                game_time_label=time_label,
                world=world_id
            )
        except Exception:
            pass

    except Exception:
        pass
