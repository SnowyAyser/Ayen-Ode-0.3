from typing import Any
from .utils import run_stage_with_retry

def analyze_theme(client: Any, world_context: str, player_action: str, history_text: str) -> dict[str, Any]:
    """Stage 1: Analyze player action tone and emotional/environmental subtext, grounded in database themes."""
    default_val = {
        "theme_conclusions": [
            {
                "motif": "Neutral Storytelling",
                "observation": "Narrate the consequences with standard atmospheric descriptions.",
                "evidence": "No active theme constraints provided in database context."
            }
        ]
    }
    
    prompt = f"""You are a literary analyst and theme manager for the RPG Ayen-Ode.
Analyze the player's action and recent context to plan the atmospheric subtext and tone for the upcoming narration.

Why this is needed: To preserve absolute thematic consistency (such as paranoia, decay, isolation) as designated in the world database.

World Database Context:
\"\"\"{world_context}\"\"\"

Recent Conversation History:
\"\"\"{history_text}\"\"\"

Player's Action:
\"{player_action}\"

TASK:
Identify which themes, tones, or emotional motifs from the World Context are active in this action. 
Write highly focused instructions on how these themes should be reinforced in the storytelling prose.

CRITICAL EVIDENCE RULE:
For every theme or motif you identify, you MUST provide explicit evidence or a database citation citing the exact lines, premise, theme_tone, or history details that justify its inclusion. No hallucinations or hand-waving.

Response MUST be a valid, parsed JSON block matching this exact structure:
{{
    "theme_conclusions": [
        {{
            "motif": "Active Theme Name (e.g. Paranoia / Decay)",
            "observation": "Specific guidelines for the storyteller on how this tone should manifest in physical descriptions or NPC dialogue.",
            "evidence": "Direct quote or detail from World Context/History proving this theme is active."
        }}
    ]
}}
"""
    return run_stage_with_retry(client, prompt, default_val)
