from typing import Any
from anthropic import Anthropic

from ..config import SONNET_MODEL
from ..services.base import STAT_NAMES_BY_ENTITY_TYPE
from ..narrative_utils import parse_investigation_response


def _extract_text(response: Any) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


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
    world_context_instruction = current_handoff.get('handoff_text', 'No context yet') + "\n" + context_instruction

    # Formulate recent history text for analytical stages
    history_text = ""
    for m in conversation_history[-6:]:
        role = "Player" if m["role"] == "user" else "Narrator"
        history_text += f"[{role}]: {m['content']}\n"

    from .stages.theme import analyze_theme
    from .stages.quests import evaluate_quests
    from .stages.mechanics import plan_mechanics
    from .stages.prose import generate_prose

    from .stages.utils import set_stage_progress, clear_stage_progress
    progress_key = f"{world_id}:investigate:{item_name.lower()}"

    try:
        # Stage 1: Thematic & Tone Analysis
        set_stage_progress(progress_key, "Stage 1/4: Analyzing Theme & Tone...")
        theme_report = analyze_theme(client, world_context_instruction, f"Investigating keyword: '{item_name}'", history_text)

        # Stage 2: Quest & Goal Evaluation
        set_stage_progress(progress_key, "Stage 2/4: Evaluating Quest Progress...")
        quest_report = evaluate_quests(client, world_context_instruction, f"Investigating keyword: '{item_name}'", history_text)

        # Stage 3: Compendium Card Attributes & Mechanics Generation
        set_stage_progress(progress_key, "Stage 3/4: Designing Compendium Card Details...")
        mechanics_report = plan_mechanics(
            client=client,
            world_context=world_context_instruction,
            player_action=f"Investigating keyword: '{item_name}'",
            history_text=history_text,
            theme_report=theme_report,
            quest_report=quest_report,
            mode="investigate",
            item_name=item_name,
            entity_type=entity_type,
            stat_names=stat_names
        )

        entity_details = mechanics_report.get("compendium_card", {})
        
        # Stage 4: Storyteller Narrative Prose Generation
        set_stage_progress(progress_key, "Stage 4/4: Weaving Narrative Discovery Prose...")
        narrative_text = generate_prose(
            client=client,
            world_context=world_context_instruction,
            player_action=f"Investigating keyword: '{item_name}'",
            history_text=history_text,
            theme_report=theme_report,
            quest_report=quest_report,
            mechanics_report=mechanics_report,
            mode="investigate",
            item_name=item_name
        )
    finally:
        clear_stage_progress(progress_key)
    
    # Run the Haiku relinker pass incrementally on the new compendium details to guarantee rich nested investigation links
    try:
        from ..relinker import relink_text_with_llm, get_all_linkable_entities
        already_investigated = get_all_linkable_entities(service, world_id)
        already_investigated[item_name] = entity_type
            
        if "summary" in entity_details and entity_details["summary"]:
            entity_details["summary"] = relink_text_with_llm(client, entity_details["summary"], already_investigated, use_llm=False)
            
        timeline_notes = entity_details.get("timeline_notes", [])
        for i in range(len(timeline_notes)):
            if timeline_notes[i]:
                timeline_notes[i] = relink_text_with_llm(client, timeline_notes[i], already_investigated, use_llm=False)
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
            # Trigger background history relinking
            try:
                import threading
                from ..relinker import relink_world_history_logs
                threading.Thread(
                    target=relink_world_history_logs,
                    args=(service, world_id),
                    daemon=True
                ).start()
            except Exception:
                pass
    else:
        entity = {
            "name": item_name,
            "entity_type": entity_type,
            "summary": entity_details.get("summary", ""),
            "tags": entity_details.get("tags", []),
            "timeline_notes": entity_details.get("timeline_notes", []),
        }

    # Relink the discovery narrative text as well
    try:
        from ..relinker import relink_text_with_llm, get_all_linkable_entities
        already_investigated = get_all_linkable_entities(service, world_id)
        if narrative_text:
            narrative_text = relink_text_with_llm(client, narrative_text, already_investigated)
    except Exception:
        pass

    # Run background pregeneration on narrative and card details to complete the recursive discovery loop!
    try:
        from ..relinker import auto_pre_generate_new_investigations
        if narrative_text:
            auto_pre_generate_new_investigations(client, service, world_id, narrative_text)
        summary = entity_details.get("summary", "")
        if summary:
            auto_pre_generate_new_investigations(client, service, world_id, summary)
        for note in entity_details.get("timeline_notes", []):
            if note:
                auto_pre_generate_new_investigations(client, service, world_id, note)
    except Exception:
        pass

    return {
        "narrative": narrative_text,
        "entity": entity,
        "stats": stats,
        "theme_report": theme_report,
        "quest_report": quest_report,
        "mechanics_report": mechanics_report,
    }
