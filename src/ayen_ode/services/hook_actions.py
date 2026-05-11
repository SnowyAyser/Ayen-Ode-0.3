"""Shared hook action executor for containment, knowledge, and consequence systems.

stat_change, log_note, and flag_entity appear identically in all three hook
systems. This module provides a single implementation so they stay in sync.
containment_move and knowledge_learn are consequence-specific bridges and live
in consequence.py.
"""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import (
    STAT_NAMES_BY_ENTITY_TYPE,
    clamp_stat,
    dumps,
    loads,
    make_id,
    utc_now,
)


def execute_shared_hook_action(
    conn: sqlite3.Connection,
    world_id: str,
    hook: sqlite3.Row,
    default_entity_id: str,
    service: Any,
    *,
    source_event_id: str | None = None,
    default_reason: str | None = None,
) -> dict[str, Any]:
    """Execute stat_change, log_note, or flag_entity hook actions.

    Always returns a dict — never raises, so callers can safely append results.

    Args:
        default_entity_id: Entity to use when action_params doesn't specify one.
            Pass the triggering entity for containment/knowledge hooks, or the
            consequence target_id for consequence hooks.
        source_event_id: Written to stat_ledger.source_event_id.
            Pass None for containment/knowledge, consequence_id for consequence.
        default_reason: Fallback reason for stat_ledger when params has no "reason".
            Defaults to "Triggered by hook <hook_id>".
    """
    try:
        return _do_execute(conn, world_id, hook, default_entity_id, service, source_event_id, default_reason)
    except Exception as exc:
        return {"error": f"Hook action failed: {exc}"}


def _do_execute(
    conn: sqlite3.Connection,
    world_id: str,
    hook: sqlite3.Row,
    default_entity_id: str,
    service: Any,
    source_event_id: str | None,
    default_reason: str | None,
) -> dict[str, Any]:
    now = utc_now()
    params = loads(hook["action_params_json"], {})
    action_type = hook["action_type"]

    if action_type == "stat_change":
        target_id = params.get("entity_id") or default_entity_id
        stat = params.get("stat", "")
        delta = int(params.get("delta", 0))
        reason = params.get("reason") or default_reason or f"Triggered by hook {hook['hook_id']}"
        entity = conn.execute(
            "SELECT entity_type FROM entities WHERE entity_id = ? AND world_id = ?",
            (target_id, world_id),
        ).fetchone()
        if not entity or not stat:
            return {"error": f"Invalid stat_change params: entity={target_id} stat={stat}"}
        allowed = STAT_NAMES_BY_ENTITY_TYPE.get(entity["entity_type"], set())
        if stat not in allowed:
            return {"error": f"Stat '{stat}' not valid for entity_type '{entity['entity_type']}'"}
        before = service._entity_stats(conn, target_id)
        after = dict(before)
        after[stat] = clamp_stat(after.get(stat, 50) + delta)
        conn.execute(
            "UPDATE entity_stats SET stats_json = ?, updated_at = ? WHERE entity_id = ?",
            (dumps(after), now, target_id),
        )
        conn.execute(
            """
            INSERT INTO stat_ledger
                (ledger_id, world_id, entity_id, changes_json, reason, source_event_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (make_id("stat"), world_id, target_id, dumps({stat: delta}), reason, source_event_id, now),
        )
        return {
            "entity_id": target_id,
            "stat": stat,
            "delta": delta,
            "before": before.get(stat),
            "after": after.get(stat),
        }

    if action_type == "log_note":
        note = params.get("note", "")
        entity_id = params.get("entity_id") or default_entity_id
        row = conn.execute(
            "SELECT timeline_notes_json FROM entities WHERE entity_id = ? AND world_id = ?",
            (entity_id, world_id),
        ).fetchone()
        if not row:
            return {"error": f"Entity not found: {entity_id}"}
        notes = loads(row["timeline_notes_json"], [])
        notes.append({"note": note, "at": now})
        conn.execute(
            "UPDATE entities SET timeline_notes_json = ? WHERE entity_id = ?",
            (dumps(notes), entity_id),
        )
        return {"note": note}

    if action_type == "flag_entity":
        target_id = params.get("entity_id") or default_entity_id
        flag = params.get("flag", "")
        value = params.get("value", True)
        row = conn.execute(
            "SELECT metadata_json FROM entities WHERE entity_id = ? AND world_id = ?",
            (target_id, world_id),
        ).fetchone()
        if not row or not flag:
            return {"error": f"Invalid flag_entity params: entity={target_id} flag={flag}"}
        meta = loads(row["metadata_json"], {})
        meta[flag] = value
        conn.execute(
            "UPDATE entities SET metadata_json = ? WHERE entity_id = ?",
            (dumps(meta), target_id),
        )
        return {"entity_id": target_id, "flag": flag, "value": value}

    return {"error": f"Unknown action_type: {action_type}"}
