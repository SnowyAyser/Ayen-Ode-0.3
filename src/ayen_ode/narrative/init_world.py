from typing import Any
from anthropic import Anthropic

from ..config import SONNET_MODEL
from ..quests import generate_overarching_goal


def _extract_text(response: Any) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


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
2. Do NOT register entities via tools — they will be created on-demand when the player investigates

LITERARY STYLE & IMMERSION RULES:
- Write high-quality, atmospheric literary narrative prose in second-person ("you"). Avoid writing a dry, gamified text-adventure or game-guide simulation.
- STRICTLY FORBIDDEN: Never output hand-holding hints, tutorial instructions, leading advice, or video-game-like mechanical suggestions directing what to do next (e.g., do NOT write "It might be worth investigating further", "You could look closer at...", "Perhaps you should ask...", "Choose your path carefully").
- STRICTLY FORBIDDEN: Never output suggested actions, choices, player commands, options, prompt questions, or call-to-actions anywhere in the response (e.g., do NOT write "What do you do?", "Scrutinize the man's eyes", "Choose to either...", or list options). The narrator must ONLY write the narrative story block, ending on a natural storytelling description, leaving all decisions, actions, and questions entirely silent and up to the player.
- Write pure story prose in plain text. Never output any HTML, XML, <investigate> tags, or any other markup. The game engine automatically identifies and links proper nouns in a separate post-processing step.

Write the opening scene in plain text. Do not use any tools."""

    response = client.messages.create(
        model=SONNET_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    initial_scene = _extract_text(response)

    # Run bidirectional relinker on the initial scene to linkify proper nouns instantly
    try:
        from ..relinker import relink_text_with_llm
        initial_scene = relink_text_with_llm(client, initial_scene, {})
    except Exception:
        pass

    service.set_original_opening_scene(world_id, initial_scene)
    service.initialize_world_currency(world=world_id, initial_balance=5, max_balance=5)
    service.save_world_handoff(
        handoff_text=initial_scene,
        world=world_id,
        current_state_summary=f"World just created. {premise}",
        active_tensions=[],
    )

    try:
        from ..relinker import auto_pre_generate_new_investigations
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
