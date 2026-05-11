"""ConsequenceMixin: mutation and hook management for the causal chain."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import dumps, loads, make_id, utc_now
from .consequence_queries import ConsequenceQueryMixin, _VALID_EFFECT_TYPES
from .hook_actions import execute_shared_hook_action

_VALID_ACTIONS = {
    "stat_change",
    "log_note",
    "flag_entity",
    "containment_move",
    "knowledge_learn",
}

_KNOWLEDGE_DEGREES = {
    "unaware", "heard_rumor", "secondhand", "witnessed", "deeply_knows", "fabricated",
}


class ConsequenceMixin(ConsequenceQueryMixin):
    """Directed causal graph: every effect points back to its cause.

    Containment answers WHERE. Knowledge answers WHO KNOWS WHAT.
    Consequence answers WHY and WHAT HAPPENED.

    Hooks connect the three systems: a consequence of type 'moved' can fire
    containment_move; 'relationship_changed' can fire knowledge_learn.
    """

    # ------------------------------------------------------------------
    # Mutation methods
    # ------------------------------------------------------------------

    def record_consequence(
        self,
        cause_id: str,
        effect_type: str,
        target_id: str,
        detail: str = "",
        world: str | None = None,
    ) -> dict[str, Any]:
        """Log a single causal link and fire any matching hooks."""
        if effect_type not in _VALID_EFFECT_TYPES:
            raise ValueError(f"effect_type must be one of: {sorted(_VALID_EFFECT_TYPES)}")
        now = utc_now()
        consequence_id = make_id("csq")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            conn.execute(
                """
                INSERT INTO consequence_records
                    (consequence_id, world_id, cause_id, effect_type, target_id, detail, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (consequence_id, wid, cause_id, effect_type, target_id, detail.strip(), now),
            )
            triggered = self._fire_consequence_hooks(
                conn, wid, cause_id, effect_type, target_id, consequence_id
            )
            return {
                "consequence_id": consequence_id,
                "world_id": wid,
                "cause_id": cause_id,
                "effect_type": effect_type,
                "target_id": target_id,
                "detail": detail.strip(),
                "created_at": now,
                "triggered_hooks": triggered,
            }

    def record_chain(
        self,
        cause_id: str,
        effects: list[dict[str, Any]],
        world: str | None = None,
    ) -> dict[str, Any]:
        """Batch record multiple effects from a single cause."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
        results = []
        for effect in effects:
            r = self.record_consequence(
                cause_id=cause_id,
                effect_type=effect["effect_type"],
                target_id=effect["target_id"],
                detail=effect.get("detail", ""),
                world=wid,
            )
            results.append(r)
        return {
            "world_id": wid,
            "cause_id": cause_id,
            "recorded": len(results),
            "consequences": results,
        }

    # ------------------------------------------------------------------
    # Hook management
    # ------------------------------------------------------------------

    def register_consequence_hook(
        self,
        action_type: str,
        action_params: dict[str, Any],
        trigger_effect_type: str | None = None,
        trigger_cause_id: str | None = None,
        trigger_target_id: str | None = None,
        label: str = "",
        world: str | None = None,
    ) -> dict[str, Any]:
        """Register a hook that fires whenever a consequence is recorded."""
        if trigger_effect_type is not None and trigger_effect_type not in _VALID_EFFECT_TYPES:
            raise ValueError(f"trigger_effect_type must be one of: {sorted(_VALID_EFFECT_TYPES)}")
        if action_type not in _VALID_ACTIONS:
            raise ValueError(f"action_type must be one of: {sorted(_VALID_ACTIONS)}")
        now = utc_now()
        hook_id = make_id("cshook")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            if trigger_cause_id:
                self._resolve_entity(conn, wid, trigger_cause_id)
            if trigger_target_id:
                self._resolve_entity(conn, wid, trigger_target_id)
            conn.execute(
                """
                INSERT INTO consequence_hooks
                    (hook_id, world_id, trigger_effect_type, trigger_cause_id, trigger_target_id,
                     action_type, action_params_json, label, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    hook_id, wid, trigger_effect_type, trigger_cause_id, trigger_target_id,
                    action_type, dumps(action_params), label.strip(), now,
                ),
            )
            return {
                "hook_id": hook_id,
                "world_id": wid,
                "trigger_effect_type": trigger_effect_type,
                "trigger_cause_id": trigger_cause_id,
                "trigger_target_id": trigger_target_id,
                "action_type": action_type,
                "action_params": action_params,
                "label": label.strip(),
                "created_at": now,
            }

    def list_consequence_hooks(self, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                "SELECT * FROM consequence_hooks WHERE world_id = ? ORDER BY created_at ASC",
                (wid,),
            ).fetchall()
            return {
                "world_id": wid,
                "hooks": [
                    {
                        "hook_id": r["hook_id"],
                        "trigger_effect_type": r["trigger_effect_type"],
                        "trigger_cause_id": r["trigger_cause_id"],
                        "trigger_target_id": r["trigger_target_id"],
                        "action_type": r["action_type"],
                        "action_params": loads(r["action_params_json"], {}),
                        "label": r["label"],
                        "created_at": r["created_at"],
                    }
                    for r in rows
                ],
            }

    def remove_consequence_hook(self, hook_id: str, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            conn.execute(
                "DELETE FROM consequence_hooks WHERE hook_id = ? AND world_id = ?",
                (hook_id, world_row["world_id"]),
            )
            return {"success": True, "hook_id": hook_id}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fire_consequence_hooks(
        self,
        conn: sqlite3.Connection,
        world_id: str,
        cause_id: str,
        effect_type: str,
        target_id: str,
        consequence_id: str,
    ) -> list[dict[str, Any]]:
        """Match and execute consequence hooks. Called within an open transaction."""
        fired_ids: set[str] = set()
        fired: list[dict[str, Any]] = []
        hooks = conn.execute(
            """
            SELECT * FROM consequence_hooks
            WHERE world_id = ?
              AND (trigger_effect_type IS NULL OR trigger_effect_type = ?)
              AND (trigger_cause_id IS NULL OR trigger_cause_id = ?)
              AND (trigger_target_id IS NULL OR trigger_target_id = ?)
            ORDER BY created_at ASC
            """,
            (world_id, effect_type, cause_id, target_id),
        ).fetchall()
        for hook in hooks:
            if hook["hook_id"] in fired_ids:
                continue
            fired_ids.add(hook["hook_id"])
            result = self._execute_consequence_hook_action(
                conn, world_id, hook, cause_id, effect_type, target_id, consequence_id
            )
            fired.append({
                "hook_id": hook["hook_id"],
                "label": hook["label"],
                "action_type": hook["action_type"],
                "result": result,
            })
        return fired

    def _execute_consequence_hook_action(
        self,
        conn: sqlite3.Connection,
        world_id: str,
        hook: sqlite3.Row,
        cause_id: str,
        effect_type: str,
        target_id: str,
        consequence_id: str,
    ) -> dict[str, Any]:
        action_type = hook["action_type"]

        if action_type in {"stat_change", "log_note", "flag_entity"}:
            return execute_shared_hook_action(
                conn, world_id, hook, target_id, self,
                source_event_id=consequence_id,
                default_reason=f"Consequence {consequence_id}",
            )

        try:
            return self._execute_bridge_action(
                conn, world_id, hook, cause_id, target_id, consequence_id
            )
        except Exception as exc:
            return {"error": f"Hook action failed: {exc}"}

    def _execute_bridge_action(
        self,
        conn: sqlite3.Connection,
        world_id: str,
        hook: sqlite3.Row,
        cause_id: str,
        target_id: str,
        consequence_id: str,
    ) -> dict[str, Any]:
        """Dispatch containment_move and knowledge_learn bridge actions."""
        params = loads(hook["action_params_json"], {})
        action_type = hook["action_type"]
        if action_type == "containment_move":
            return self._execute_containment_move_action(conn, world_id, params, target_id)
        if action_type == "knowledge_learn":
            return self._execute_knowledge_learn_action(conn, world_id, params, target_id, cause_id)
        return {"error": f"Unknown action_type: {action_type}"}

    def _execute_containment_move_action(
        self,
        conn: sqlite3.Connection,
        world_id: str,
        params: dict[str, Any],
        target_id: str,
    ) -> dict[str, Any]:
        now = utc_now()
        entity_id = params.get("entity_id") or target_id
        new_container_id = params.get("new_container_id")
        entity_row = conn.execute(
            "SELECT * FROM entities WHERE entity_id = ? AND world_id = ?",
            (entity_id, world_id),
        ).fetchone()
        if not entity_row:
            return {"error": f"Entity not found: {entity_id}"}
        from_container_id = entity_row["container_id"]
        if new_container_id is not None:
            tgt_row = conn.execute(
                "SELECT entity_id FROM entities WHERE entity_id = ? AND world_id = ?",
                (new_container_id, world_id),
            ).fetchone()
            if not tgt_row:
                return {"error": f"Container entity not found: {new_container_id}"}
            if self._check_circular(conn, entity_id, new_container_id):
                return {"error": "Circular containment detected — move skipped"}
        conn.execute(
            "UPDATE entities SET container_id = ?, updated_at = ? WHERE entity_id = ?",
            (new_container_id, now, entity_id),
        )
        event_type = (
            "place" if from_container_id is None
            else "remove" if new_container_id is None
            else "move"
        )
        conn.execute(
            """
            INSERT INTO containment_events
                (event_id, world_id, entity_id, from_container_id, to_container_id, event_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (make_id("cevt"), world_id, entity_id, from_container_id, new_container_id, event_type, now),
        )
        return {
            "entity_id": entity_id,
            "from_container_id": from_container_id,
            "to_container_id": new_container_id,
            "event_type": event_type,
        }

    def _execute_knowledge_learn_action(
        self,
        conn: sqlite3.Connection,
        world_id: str,
        params: dict[str, Any],
        target_id: str,
        cause_id: str,
    ) -> dict[str, Any]:
        now = utc_now()
        learner_id = params.get("entity_id") or target_id
        knows_about_id = params.get("target_id")
        degree = params.get("degree", "heard_rumor")
        source_id = params.get("source_id") or cause_id
        if not knows_about_id:
            return {"error": "knowledge_learn requires 'target_id' in action_params"}
        if degree not in _KNOWLEDGE_DEGREES:
            return {"error": f"Invalid degree '{degree}'"}
        learner_row = conn.execute(
            "SELECT entity_id FROM entities WHERE entity_id = ? AND world_id = ?",
            (learner_id, world_id),
        ).fetchone()
        target_row = conn.execute(
            "SELECT entity_id FROM entities WHERE entity_id = ? AND world_id = ?",
            (knows_about_id, world_id),
        ).fetchone()
        if not learner_row:
            return {"error": f"Learner entity not found: {learner_id}"}
        if not target_row:
            return {"error": f"Knowledge target not found: {knows_about_id}"}
        knowledge_id = make_id("know")
        conn.execute(
            """
            INSERT INTO entity_knowledge
                (knowledge_id, world_id, entity_id, knows_about_id, degree, source_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(world_id, entity_id, knows_about_id) DO UPDATE SET
                degree = excluded.degree,
                source_id = excluded.source_id,
                updated_at = excluded.updated_at
            """,
            (knowledge_id, world_id, learner_id, knows_about_id, degree, source_id, now, now),
        )
        conn.execute(
            """
            INSERT INTO knowledge_events
                (event_id, world_id, entity_id, knows_about_id, event_type, degree, source_id, created_at)
            VALUES (?, ?, ?, ?, 'learn', ?, ?, ?)
            """,
            (make_id("kevt"), world_id, learner_id, knows_about_id, degree, source_id, now),
        )
        return {
            "entity_id": learner_id,
            "knows_about_id": knows_about_id,
            "degree": degree,
            "source_id": source_id,
        }
