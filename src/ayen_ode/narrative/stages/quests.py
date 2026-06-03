from typing import Any
from .utils import run_stage_with_retry

def evaluate_quests(client: Any, world_context: str, player_action: str, history_text: str) -> dict[str, Any]:
    """Stage 2: Evaluate player active goals, quest logs, and outstanding debts grounded in DB evidence."""
    default_val = {
        "quest_progressions": [],
        "debt_implications": []
    }
    
    prompt = f"""You are a narrative designer and quest director for the RPG Ayen-Ode.
Evaluate the player's action against their active goals and outstanding debts to check for progressions or violations.

Why this is needed: To ensure player narrative commitments and world obligations are progressed accurately and factually.

World Database Context:
\"\"\"{world_context}\"\"\"

Recent Conversation History:
\"\"\"{history_text}\"\"\"

Player's Action:
\"{player_action}\"

TASK:
1. Examine active goals/quests. Analyze if the player's action progresses, triggers, or completes any of them.
2. Examine outstanding debts/obligations. Analyze if a debtor character owes a resource,Cow, Favor, or Money and how this subtext influences the encounter.

CRITICAL EVIDENCE RULE:
For every claim, quest progress, or debt impact, you MUST provide explicit evidence citing the exact goals list, active debts, or logs from the World Context/History. No hallucinations.

Response MUST be a valid, parsed JSON block matching this exact structure:
{{
    "quest_progressions": [
        {{
            "goal_name": "Active Goal/Quest Name",
            "status_change": "progressed / completed / failed / unchanged",
            "reasoning": "Detailed logic of how the player's action directly impacted this goal.",
            "evidence": "Exact database citation or quote of this goal from the World Context."
        }}
    ],
    "debt_implications": [
        {{
            "creditor": "Creditor Entity Name",
            "debtor": "Debtor Entity Name",
            "subtext_impact": "How this debt influences the tone, desperation, or servility of the debtor NPC in dialogue.",
            "evidence": "Exact database citation of the debt description from the World Context."
        }}
    ]
}}
"""
    return run_stage_with_retry(client, prompt, default_val)
