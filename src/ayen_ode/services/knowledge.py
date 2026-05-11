"""KnowledgeMixin: mutations and hook management for the knowledge graph."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import dumps, loads, make_id, utc_now
from .hook_actions import execute_shared_hook_action
from .knowledge_queries import KnowledgeQueryMixin, _DEGREE_ORDER, _VALID_DEGREES

_VALID_TRIGGER_EVENTS = {"learn", "spread"}
_VALID_ACTIONS = {"stat_change", "log_note", "flag_entity"}


class KnowledgeMixin(KnowledgeQueryMixin):
    """Many-to-many knowledge graph: entity_id knows about knows_about_id at some degree."""

    # ------------------------------------------------------------------
    # Mutation methods
    # ------------------------------------------------------------------

    def learn(
        self,
        entity_id: str,
        target_id: str,
        degree: str,
        source_id: str | None = None,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Add or update a knowledge link. Fires learn hooks."""
        if degree not in _VALID_DEGREES:
            raise ValueError(f"degree must be one of: {sorted(_VALID_DEGREES)}")
        now = utc_now()
        knowledge_id = make_id("know")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, entity_id)
            self._resolve_entity(conn, wid, target_id)
            if source_id is not None:
                self._resolve_entity(conn, wid, source_id)
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
                (knowledge_id, wid, entity_id, target_id, degree, source_id, now, now),
            )
            conn.execute(
                """
                INSERT INTO knowledge_events
                    (event_id, world_id, entity_id, knows_about_id, event_type, degree, source_id, created_at)
                VALUES (?, ?, ?, ?, 'learn', ?, ?, ?)
                """,
                (make_id("kevt"), wid, entity_id, target_id, degree, source_id, now),
            )
            triggered = self._fire_knowledge_hooks(conn, wid, entity_id, target_id, "learn", degree)
            return {
                "world_id": wid,
                "entity_id": entity_id,
                "target_id": target_id,
                "degree": degree,
                "source_id": source_id,
                "triggered_hooks": triggered,
            }

    def spread(
        self,
        knowledge_target_id: str,
        from_entity: str,
        to_entity: str,
        degree_decay: int = 1,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Pass knowledge from one entity to another, degrading degree by degree_decay steps."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, knowledge_target_id)
            self._resolve_entity(conn, wid, from_entity)
            self._resolve_entity(conn, wid, to_entity)
            row = conn.execute(
                "SELECT degree FROM entity_knowledge WHERE world_id = ? AND entity_id = ? AND knows_about_id = ?",
                (wid, from_entity, knowledge_target_id),
            ).fetchone()
            if row is None:
                raise ValueError(
                    f"Entity '{from_entity}' has no knowledge of '{knowledge_target_id}'."
                )
            from_degree = row["degree"]
            if from_degree == "fabricated":
                new_degree = "fabricated"
            else:
                idx = _DEGREE_ORDER.index(from_degree) if from_degree in _DEGREE_ORDER else 0
                new_idx = max(0, idx - degree_decay)
                new_degree = _DEGREE_ORDER[new_idx]
        return self.learn(
            entity_id=to_entity,
            target_id=knowledge_target_id,
            degree=new_degree,
            source_id=from_entity,
            world=wid,
        )

    def forget(
        self,
        entity_id: str,
        target_id: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Remove a knowledge link."""
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            conn.execute(
                "DELETE FROM entity_knowledge WHERE world_id = ? AND entity_id = ? AND knows_about_id = ?",
                (wid, entity_id, target_id),
            )
            conn.execute(
                """
                INSERT INTO knowledge_events
                    (event_id, world_id, entity_id, knows_about_id, event_type, degree, source_id, created_at)
                VALUES (?, ?, ?, ?, 'forget', NULL, NULL, ?)
                """,
                (make_id("kevt"), wid, entity_id, target_id, now),
            )
            return {"world_id": wid, "entity_id": entity_id, "target_id": target_id, "forgotten": True}

    def update_degree(
        self,
        entity_id: str,
        target_id: str,
        new_degree: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Change the degree of an existing knowledge link."""
        if new_degree not in _VALID_DEGREES:
            raise ValueError(f"degree must be one of: {sorted(_VALID_DEGREES)}")
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            row = conn.execute(
                "SELECT degree FROM entity_knowledge WHERE world_id = ? AND entity_id = ? AND knows_about_id = ?",
                (wid, entity_id, target_id),
            ).fetchone()
            if row is None:
                raise ValueError(
                    f"No knowledge link from '{entity_id}' to '{target_id}'. Use learn() first."
                )
            old_degree = row["degree"]
            conn.execute(
                "UPDATE entity_knowledge SET degree = ?, updated_at = ? WHERE world_id = ? AND entity_id = ? AND knows_about_id = ?",
                (new_degree, now, wid, entity_id, target_id),
            )
            conn.execute(
                """
                INSERT INTO knowledge_events
                    (event_id, world_id, entity_id, knows_about_id, event_type, degree, source_id, created_at)
                VALUES (?, ?, ?, ?, 'update_degree', ?, NULL, ?)
                """,
                (make_id("kevt"), wid, entity_id, target_id, new_degree, now),
            )
            return {
                "world_id": wid,
                "entity_id": entity_id,
                "target_id": target_id,
                "old_degree": old_degree,
                "new_degree": new_degree,
            }

    # ------------------------------------------------------------------
    # Hook management
    # ------------------------------------------------------------------

    def register_knowledge_hook(
        self,
        trigger_event_type: str,
        action_type: str,
        action_params: dict[str, Any],
        trigger_entity_id: str | None = None,
        trigger_target_id: str | None = None,
        trigger_degree: str | None = None,
        label: str = "",
        world: str | None = None,
    ) -> dict[str, Any]:
        """Register a hook that fires when knowledge is learned or spread."""
        if trigger_event_type not in _VALID_TRIGGER_EVENTS:
            raise ValueError(f"trigger_event_type must be one of: {_VALID_TRIGGER_EVENTS}")
        if action_type not in _VALID_ACTIONS:
            raise ValueError(f"action_type must be one of: {_VALID_ACTIONS}")
        if trigger_degree is not None and trigger_degree not in _VALID_DEGREES:
            raise ValueError(f"trigger_degree must be one of: {sorted(_VALID_DEGREES)}")
        now = utc_now()
        hook_id = make_id("khook")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            if trigger_entity_id:
                self._resolve_entity(conn, wid, trigger_entity_id)
            if trigger_target_id:
                self._resolve_entity(conn, wid, trigger_target_id)
            conn.execute(
                """
                INSERT INTO knowledge_hooks
                    (hook_id, world_id, trigger_event_type, trigger_entity_id, trigger_target_id,
                     trigger_degree, action_type, action_params_json, label, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (hook_id, wid, trigger_event_type, trigger_entity_id, trigger_target_id,
                 trigger_degree, action_type, dumps(action_params), label.strip(), now),
            )
            return {
                "hook_id": hook_id,
                "world_id": wid,
                "trigger_event_type": trigger_event_type,
                "trigger_entity_id": trigger_entity_id,
                "trigger_target_id": trigger_target_id,
                "trigger_degree": trigger_degree,
                "action_type": action_type,
                "action_params": action_params,
                "label": label.strip(),
                "created_at": now,
            }

    def list_knowledge_hooks(self, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                "SELECT * FROM knowledge_hooks WHERE world_id = ? ORDER BY created_at ASC",
                (wid,),
            ).fetchall()
            return {
                "world_id": wid,
                "hooks": [
                    {
                        "hook_id": r["hook_id"],
                        "trigger_event_type": r["trigger_event_type"],
                        "trigger_entity_id": r["trigger_entity_id"],
                        "trigger_target_id": r["trigger_target_id"],
                        "trigger_degree": r["trigger_degree"],
                        "action_type": r["action_type"],
                        "action_params": loads(r["action_params_json"], {}),
                        "label": r["label"],
                        "created_at": r["created_at"],
                    }
                    for r in rows
                ],
            }

    def remove_knowledge_hook(self, hook_id: str, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            conn.execute(
                "DELETE FROM knowledge_hooks WHERE hook_id = ? AND world_id = ?",
                (hook_id, world_row["world_id"]),
            )
            return {"success": True, "hook_id": hook_id}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fire_knowledge_hooks(
        self,
        conn: sqlite3.Connection,
        world_id: str,
        entity_id: str,
        target_id: str,
        event_type: str,
        degree: str,
    ) -> list[dict[str, Any]]:
        """Match and execute hooks for a learn or spread event. Called within an open transaction."""
        fired_ids: set[str] = set()
        fired: list[dict[str, Any]] = []
        hooks = conn.execute(
            """
            SELECT * FROM knowledge_hooks
            WHERE world_id = ?
              AND trigger_event_type = ?
              AND (trigger_entity_id IS NULL OR trigger_entity_id = ?)
              AND (trigger_target_id IS NULL OR trigger_target_id = ?)
              AND (trigger_degree IS NULL OR trigger_degree = ?)
            ORDER BY created_at ASC
            """,
            (world_id, event_type, entity_id, target_id, degree),
        ).fetchall()
        for hook in hooks:
            if hook["hook_id"] in fired_ids:
                continue
            fired_ids.add(hook["hook_id"])
            result = execute_shared_hook_action(conn, world_id, hook, entity_id, self)
            fired.append({
                "hook_id": hook["hook_id"],
                "label": hook["label"],
                "action_type": hook["action_type"],
                "result": result,
            })
        return fired
