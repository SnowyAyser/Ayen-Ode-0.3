"""Quest goal detection: generate the overarching goal and scan for new goals during play."""

from __future__ import annotations

import json
import re
from typing import Any

from .config import HAIKU_MODEL
from .services.base import loads as _loads


# ---------------------------------------------------------------------------
# Overarching goal generation (Tier 1) — called once at world creation
# ---------------------------------------------------------------------------

_OVERARCHING_GOAL_PROMPT = """You are a narrative director for an RPG. A new world has just been created.

World details:
- Name: {name}
- Premise: {premise}
- Theme / Tone: {theme_tone}
- Player Role: {player_role}

Generate the single overarching narrative goal for this world — the central arc the player is part of.
This is a long-horizon objective that shapes the whole story. It should feel open-ended and discoverable,
not a direct instruction. The player should be able to pursue it in their own way.

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "title": "Short arc title, max 10 words",
  "description": "2-3 sentences. What is at stake? What mystery or conflict defines this world?",
  "completion_tags": ["tag_one", "tag_two", "tag_three", "tag_four"]
}}

Rules for completion_tags:
- 3-5 tags total
- snake_case, short, narrative — e.g. "architect_unmasked", "evidence_secured", "alliance_formed"
- They represent major milestones toward resolving the arc
- Do NOT use generic words like "complete", "done", "finish"
"""

_GOAL_SCAN_PROMPT = """You are a quest detector for a narrative RPG. Analyse the recent world events
and identify goals or objectives that are developing — things the player should be aware of.

EXISTING TRACKED QUESTS (do not create duplicates):
{existing_quests}

RECENT WORLD EVENTS (last 10 consequence records):
{recent_consequences}

SIGNIFICANT STAT CHANGES (recent):
{stat_changes}

PLAYER ENTITY ID: {player_entity_id}

For each potential goal, assign a significance score 0-100:
  - Player is a direct cause or target: +30
  - Causal chain spans 3+ records: +20
  - effect_type is triggered_event or relationship_changed: +15 each
  - Connects to the overarching goal themes: +10
  - Event is self-contained / already resolved: -30

Only output goals scoring 40+. Scores 40-69 need player confirmation. Scores 70+ auto-create.

Return ONLY valid JSON, no markdown:
{{
  "new_goals": [
    {{
      "title": "Short goal title, max 8 words",
      "description": "1-2 sentences. What is developing and why does it matter?",
      "completion_tags": ["tag_one", "tag_two"],
      "significance_score": 75,
      "connects_to_overarching": true
    }}
  ],
  "progress_updates": [
    {{"quest_id": "quest_xxx", "tag": "tag_name"}}
  ],
  "completed_quests": ["quest_id"]
}}

Rules:
- completion_tags: 2-4 per goal, snake_case, narrative phrases
- progress_updates: mark a tag if recent events clearly imply it was achieved
- completed_quests: only if the quest's goal is fully resolved in the narrative
- Return empty arrays if nothing qualifies
"""


def _extract_json(text: str) -> dict:
    """Extract the first JSON object from a response that may have stray text."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_overarching_goal(
    client: Any,
    service: Any,
    world_id: str,
    name: str,
    premise: str,
    theme_tone: str,
    player_role: str,
) -> dict[str, Any] | None:
    """Generate and persist the Tier 1 overarching quest for a newly created world.

    Uses Haiku for speed. Returns the created quest dict or None on failure.
    Failures are silent — world creation must not be blocked by this.
    """
    try:
        prompt = _OVERARCHING_GOAL_PROMPT.format(
            name=name,
            premise=premise,
            theme_tone=theme_tone or "unspecified",
            player_role=player_role or "unspecified",
        )
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in response.content if b.type == "text")
        data = _extract_json(text)
        if not data.get("title") or not data.get("completion_tags"):
            return None
        quest = service.create_quest(
            title=data["title"],
            description=data.get("description", ""),
            completion_tags=data["completion_tags"],
            tier=1,
            significance_score=100,
            status="active",
            world=world_id,
        )
        return quest
    except Exception:
        return None


def scan_for_goals(
    client: Any,
    service: Any,
    world_id: str,
    player_entity_id: str,
) -> dict[str, Any]:
    """Scan recent events and update the quest tracker.

    Reads consequence records and stat changes from DB. Calls Haiku once.
    Returns a summary of what was created/updated/completed.
    Silent on failure.

    Scoring thresholds:
        < 40  → dropped silently
        40-69 → created as pending_player (surfaced to player for decision)
        70+   → created as active Tier 2 goal
    """
    result: dict[str, Any] = {"created": [], "updated": [], "completed": []}
    try:
        # --- Gather context from DB ---
        existing_data = service.get_active_quests_summary(world=world_id)
        existing_quests = existing_data.get("quests", [])

        existing_lines = []
        for q in existing_quests:
            tags_str = ", ".join(q["completion_tags"])
            existing_lines.append(
                f"  [{q['quest_id']}] (tier {q['tier']}) {q['title']} — tags: {tags_str}"
            )
        existing_summary = "\n".join(existing_lines) or "  None yet."

        # Last 10 consequence records + stat ledger (one DB connection)
        csq_lines = []
        stat_lines = []
        try:
            with service.connect() as conn:
                world_row = service._resolve_world(conn, world_id)
                wid = world_row["world_id"]
                csq_rows = conn.execute(
                    """SELECT cause_id, effect_type, target_id, detail
                    FROM consequence_records WHERE world_id = ?
                    ORDER BY created_at DESC LIMIT 10""",
                    (wid,),
                ).fetchall()
                for r in csq_rows:
                    csq_lines.append(
                        f"  cause={r['cause_id']} effect={r['effect_type']} "
                        f"target={r['target_id']} detail={r['detail']!r}"
                    )
                ledger_rows = conn.execute(
                    """SELECT entity_id, changes_json, reason FROM stat_ledger
                    WHERE world_id = ? ORDER BY created_at DESC LIMIT 8""",
                    (wid,),
                ).fetchall()
        except Exception:
            ledger_rows = []
        csq_summary = "\n".join(csq_lines) or "  No recent events."

        # Stat ledger — filter to significant changes
        try:
            for row in ledger_rows:
                changes = _loads(row["changes_json"], {})
                significant = {k: v for k, v in changes.items() if abs(v) >= 10}
                if significant:
                    stat_lines.append(
                        f"  entity={row['entity_id']} changes={significant} reason={row['reason']!r}"
                    )
            stat_summary = "\n".join(stat_lines) or "  No significant stat changes."
        except Exception:
            stat_summary = "  Unavailable."

        # --- Haiku call ---
        prompt = _GOAL_SCAN_PROMPT.format(
            existing_quests=existing_summary,
            recent_consequences=csq_summary,
            stat_changes=stat_summary,
            player_entity_id=player_entity_id,
        )
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in response.content if b.type == "text")
        data = _extract_json(text)

        # --- Process new goals ---
        for goal in data.get("new_goals", []):
            score = int(goal.get("significance_score", 0))
            if score < 40:
                continue
            status = "active" if score >= 70 else "pending_player"
            tier = 2 if score >= 70 else 3
            quest = service.create_quest(
                title=goal.get("title", "Unnamed goal"),
                description=goal.get("description", ""),
                completion_tags=goal.get("completion_tags", []),
                tier=tier,
                significance_score=score,
                status=status,
                world=world_id,
            )
            result["created"].append(quest)

        # --- Process progress updates ---
        for update in data.get("progress_updates", []):
            quest_id = update.get("quest_id", "")
            tag = update.get("tag", "")
            if not quest_id or not tag:
                continue
            try:
                updated = service.mark_quest_tag(quest_id, tag, world=world_id)
                result["updated"].append(updated)
            except Exception:
                pass

        # --- Process completed quests ---
        for quest_id in data.get("completed_quests", []):
            try:
                service.complete_quest(quest_id, world=world_id)
                result["completed"].append(quest_id)
            except Exception:
                pass

    except Exception:
        pass

    return result
