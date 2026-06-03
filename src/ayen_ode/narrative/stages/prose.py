from typing import Any

def generate_prose(
    client: Any,
    world_context: str,
    player_action: str,
    history_text: str,
    theme_report: dict[str, Any],
    quest_report: dict[str, Any],
    mechanics_report: dict[str, Any],
    mode: str = "consequence",
    item_name: str = ""
) -> str:
    """Stage 4: Generate high-quality, atmospheric reactionary second-person plain-text story prose."""
    if not client:
        return "The world rolls on silently."
        
    from ...config import SONNET_MODEL
    
    if mode == "investigate":
        action_desc = f"A player has investigated: \"{item_name}\""
        card_details = mechanics_report.get("compendium_card", {})
        consequence_block = (
            f"Discovery Facts to Weave In:\n"
            f"- summary: {card_details.get('summary', '')}\n"
            f"- timeline: {', '.join(card_details.get('timeline_notes', []))}\n"
        )
    else:
        action_desc = f"Player Action: \"{player_action}\""
        facts = [c.get("fact", "") for c in mechanics_report.get("consequence_facts", [])]
        consequence_block = "Consequences/Facts to Physically Narrate:\n" + "\n".join(f"- {f}" for f in facts)
        
    prompt = f"""You are the narrator and world-master for the narrative RPG Ayen-Ode.
Write an atmospheric, literary narrative scene translating our evidence-grounded plans into immersive prose.

CRITICAL ROLEPLAY CONSTRAINT (STRICTLY ENFORCED):
- Write exclusively in the second-person ("you") but be purely REACTIONARY.
- You must NEVER speak, think, emote, react, make decisions, write dialogue, or write physical actions on behalf of the player character (the "you"). 
- The player character is completely silent and passive in your responses. Keep them entirely under the player's own control.
- STRICTLY FORBIDDEN: Do not write physical actions or reactions for the player character in the narrative (e.g., do NOT write "You nod...", "You smile...", "You shrug...", "You turn...", "You walk...").
- STRICTLY FORBIDDEN: Do not write emotional or mental states for the player character (e.g., do NOT write "You feel...", "You absorb their words...", "You think...", "You notice with a sigh...", "You are filled with...").
- You may ONLY describe:
  1. The immediate surroundings, environment, and physical reactions of the world.
  2. The dialogue, behaviors, movements, gestures, and reactions of OTHER characters/NPCs.

World Context:
\"\"\"{world_context}\"\"\"

Recent Conversation History:
\"\"\"{history_text}\"\"\"

{action_desc}

CREATIVE DIRECTOR'S BRIEF (MUST ADHERE TO):
Theme & Tone Directives:
{theme_report}

Quest Progress Outcomes:
{quest_report}

{consequence_block}

LITERARY STYLE & IMMERSION RULES:
- Write high-quality, atmospheric literary narrative prose in second-person ("you"). Avoid writing a dry, gamified text-adventure or game-guide simulation.
- STRICTLY FORBIDDEN: Never output hand-holding hints, tutorial instructions, leading advice, or video-game-like mechanical suggestions directing what to do next (e.g., do NOT write "It might be worth investigating further", "You could look closer at...", "Perhaps you should ask...", "Choose your path carefully").
- STRICTLY FORBIDDEN: Never output suggested actions, choices, player commands, options, prompt questions, or call-to-actions anywhere in the response (e.g., do NOT write "What do you do?", "Scrutinize the man's eyes", "Choose to either...", or list options). The narrator must ONLY write the narrative story block, ending on a natural storytelling description, leaving all decisions, actions, and questions entirely silent and up to the player.
- Write pure story prose in plain text. Never output any HTML, XML, <investigate> tags, or any other markup. The game engine automatically identifies and links proper nouns in a separate post-processing step.

Write the story narrative block in plain text. Do not break character. Do not output any JSON or schema details here.
"""
    try:
        response = client.messages.create(
            model=SONNET_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in response.content if b.type == "text").strip()
    except Exception as e:
        print(f"Error generating prose storyteller response: {e}")
        return "The surroundings remain eerie and still."
