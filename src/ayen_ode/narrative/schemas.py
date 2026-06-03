from typing import Any

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
