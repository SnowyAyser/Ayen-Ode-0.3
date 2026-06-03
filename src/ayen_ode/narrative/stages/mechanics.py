from typing import Any
from .utils import run_stage_with_retry

def plan_mechanics(
    client: Any,
    world_context: str,
    player_action: str,
    history_text: str,
    theme_report: dict[str, Any],
    quest_report: dict[str, Any],
    mode: str = "consequence",
    item_name: str = "",
    entity_type: str = "",
    stat_names: str = ""
) -> dict[str, Any]:
    """Stage 3: Plan database mechanical tool updates or generate detailed compendium card structures."""
    
    if mode == "investigate":
        # Compendium Card Generation Mode
        default_val = {
            "compendium_card": {
                "summary": f"A mysterious {entity_type} discovered in the world.",
                "tags": [entity_type],
                "timeline_notes": ["Discovered by traveler."],
                "stats": {}
            },
            "evidence": "Discovered in context."
        }
        
        prompt = f"""You are a system database designer for the narrative RPG Ayen-Ode.
A player has investigated: "{item_name}" ({entity_type})
We need to generate a new Compendium Card entry for this entity in the database.

Why this is needed: To synchronize character/location/item attributes and record their histories based strictly on actual facts.

World Context & History:
\"\"\"{world_context}\"\"\"

Recent Conversation History:
\"\"\"{history_text}\"\"\"

Theme Analysis Guidelines:
{theme_report}

Quest Progress Reports:
{quest_report}

TASK:
Generate detailed Compendium Card attributes for "{item_name}" ({entity_type}).
- summary: Brief 1-2 sentence description.
- tags: List of 2-3 short descriptive tags.
- timeline_notes: Initial bullet note describing its state.
- stats: Numeric stats (values 1 to 100) using only these allowed stat names for {entity_type}: [{stat_names}]

CRITICAL EVIDENCE RULE:
You MUST provide an explicit database citation showing exactly what details in the World Context or History justify these card properties (summary, notes, stats). No hallucinations.

Response MUST be a valid, parsed JSON block matching this exact structure:
{{
    "compendium_card": {{
        "summary": "1-2 sentence description of {item_name}",
        "tags": ["tag1", "tag2"],
        "timeline_notes": ["Initial history log entry for {item_name}"],
        "stats": {{
            "StatName": 50
        }}
    }},
    "evidence": "Direct quote or database fact justifying the card summary and stats."
}}
"""
        return run_stage_with_retry(client, prompt, default_val)
        
    else:
        # Player Action Consequence Tool Planning Mode
        default_val = {
            "tool_calls": [],
            "consequence_facts": [
                {
                    "fact": "The action completes with immediate narrative consequences.",
                    "evidence": "Player action executed in the world."
                }
            ]
        }
        
        prompt = f"""You are a database mechanics planner for the narrative RPG Ayen-Ode.
Plan the physical consequences of the player's action and any required SQLite tool calls.

Why this is needed: To mathematically and factually synchronize entity relationships and stats in the SQLite database.

World Context:
\"\"\"{world_context}\"\"\"

Recent Conversation History:
\"\"\"{history_text}\"\"\"

Theme Analysis Guidelines:
{theme_report}

Quest Progress Reports:
{quest_report}

Player's Action:
\"{player_action}\"

TASK:
1. Identify which existing entities in the World Context should receive stat changes or timeline notes as a direct consequence of the action.
2. Outline the exact physical "consequence facts" (i.e. what actually happens) that must be narrated.

CRITICAL EVIDENCE RULE:
For every tool call or consequence fact, you MUST provide explicit evidence or a database citation from the World Context proving why this change or fact is valid.

Response MUST be a valid, parsed JSON block matching this exact structure:
{{
    "tool_calls": [
        {{
            "tool_name": "add_timeline_note / apply_stat_change",
            "input": {{
                "entity_name": "Exact name of the target database entity (e.g. Stranger)",
                "note": "Description of the timeline event (if add_timeline_note)",
                "stat_name": "Allowed stat name (if apply_stat_change)",
                "change": -10
            }},
            "evidence": "Direct quote or database detail proving this stat shift or note is justified."
        }}
    ],
    "consequence_facts": [
        {{
            "fact": "Consequences to narrate: How the environment or nearby NPCs physically react.",
            "evidence": "Exact context or history quote justifying this reaction."
        }}
    ]
}}
"""
        return run_stage_with_retry(client, prompt, default_val)
