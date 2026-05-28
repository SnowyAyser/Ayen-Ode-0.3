"""ContainmentMixin: unified containment tree — placement, movement, queries, and hooks."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import dumps, loads, make_id, utc_now
from .hook_actions import execute_shared_hook_action

_VALID_TRIGGER_EVENTS = {"enter", "exit", "move"}
_VALID_HOOK_ACTIONS = {"stat_change", "log_note", "flag_entity"}


class ContainmentMixin:
    """Containment tree: any entity can contain any other. Replaces spatial_placements."""

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def get_contents(self, entity_id: str, world: str | None = None) -> dict[str, Any]:
        """Return all entities directly inside this container."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            container = self._resolve_entity(conn, wid, entity_id)
            rows = conn.execute(
                "SELECT * FROM entities WHERE container_id = ? AND world_id = ? ORDER BY name ASC",
                (entity_id, wid),
            ).fetchall()
            return {
                "world_id": wid,
                "entity": self._entity_dict(conn, container),
                "contents": [self._entity_dict(conn, r) for r in rows],
            }

    def get_contents_recursive(self, entity_id: str, world: str | None = None) -> dict[str, Any]:
        """Return all entities nested at any depth inside this container."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, entity_id)
            rows = conn.execute(
                """
                WITH RECURSIVE nested(entity_id) AS (
                    SELECT entity_id FROM entities
                    WHERE container_id = ? AND world_id = ?
                    UNION ALL
                    SELECT e.entity_id FROM entities e
                    JOIN nested n ON e.container_id = n.entity_id
                    WHERE e.world_id = ?
                )
                SELECT e.* FROM entities e
                JOIN nested n ON e.entity_id = n.entity_id
                ORDER BY e.name ASC
                """,
                (entity_id, wid, wid),
            ).fetchall()
            return {
                "world_id": wid,
                "root_entity_id": entity_id,
                "entities": [self._entity_dict(conn, r) for r in rows],
            }

    def get_container_chain(self, entity_id: str, world: str | None = None) -> dict[str, Any]:
        """Walk upward from entity to root. Chain is ordered innermost → outermost."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, entity_id)
            rows = conn.execute(
                """
                WITH RECURSIVE chain(entity_id, container_id, depth) AS (
                    SELECT entity_id, container_id, 0 FROM entities WHERE entity_id = ?
                    UNION ALL
                    SELECT e.entity_id, e.container_id, c.depth + 1
                    FROM entities e
                    JOIN chain c ON e.entity_id = c.container_id
                )
                SELECT e.* FROM entities e
                JOIN chain c ON e.entity_id = c.entity_id
                ORDER BY c.depth ASC
                """,
                (entity_id,),
            ).fetchall()
            return {
                "world_id": wid,
                "chain": [self._entity_dict(conn, r) for r in rows],
            }

    def get_siblings(self, entity_id: str, world: str | None = None) -> dict[str, Any]:
        """Return everything sharing the same container as this entity."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            entity = self._resolve_entity(conn, wid, entity_id)
            parent_id = entity["container_id"]
            if parent_id is None:
                rows = conn.execute(
                    "SELECT * FROM entities WHERE container_id IS NULL AND world_id = ? AND entity_id != ? ORDER BY name ASC",
                    (wid, entity_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM entities WHERE container_id = ? AND world_id = ? AND entity_id != ? ORDER BY name ASC",
                    (parent_id, wid, entity_id),
                ).fetchall()
            return {
                "world_id": wid,
                "container_id": parent_id,
                "siblings": [self._entity_dict(conn, r) for r in rows],
            }

    # ------------------------------------------------------------------
    # Move
    # ------------------------------------------------------------------

    def move(
        self,
        entity_id: str,
        new_container_id: str | None,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Move entity into new_container_id (or None to make it a root entity).

        Validates: both entities must exist in the same world; no circular
        containment (new container cannot be a descendant of the moving entity).
        Logs the move and fires containment hooks.
        """
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            entity = self._resolve_entity(conn, wid, entity_id)
            moving_type = entity["entity_type"]
            if new_container_id is not None:
                dest_row = self._resolve_entity(conn, wid, new_container_id)
                dest_type = dest_row["entity_type"]
                if dest_type in ("character", "object") and moving_type != "object":
                    raise ValueError(
                        f"Containment violation: {dest_type.capitalize()} '{dest_row['name']}' can only contain objects, "
                        f"not {moving_type} '{entity['name']}'."
                    )
                if self._check_circular(conn, entity_id, new_container_id):
                    raise ValueError(
                        f"Circular containment: '{new_container_id}' is already inside '{entity_id}'."
                    )
            from_container_id = entity["container_id"]
            conn.execute(
                "UPDATE entities SET container_id = ?, updated_at = ? WHERE entity_id = ?",
                (new_container_id, now, entity_id),
            )
            if from_container_id is None:
                event_type = "place"
            elif new_container_id is None:
                event_type = "remove"
            else:
                event_type = "move"
            conn.execute(
                """
                INSERT INTO containment_events
                    (event_id, world_id, entity_id, from_container_id, to_container_id, event_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (make_id("cevt"), wid, entity_id, from_container_id, new_container_id, event_type, now),
            )
            triggered = self._fire_containment_hooks(
                conn, wid, entity_id, from_container_id, new_container_id
            )
            return {
                "world_id": wid,
                "entity_id": entity_id,
                "from_container_id": from_container_id,
                "to_container_id": new_container_id,
                "event_type": event_type,
                "triggered_hooks": triggered,
            }

    # ------------------------------------------------------------------
    # Hook management
    # ------------------------------------------------------------------

    def register_containment_hook(
        self,
        trigger_event_type: str,
        action_type: str,
        action_params: dict[str, Any],
        trigger_container_id: str | None = None,
        trigger_entity_id: str | None = None,
        label: str = "",
        world: str | None = None,
    ) -> dict[str, Any]:
        """Register a hook that fires when entities move in/out of a container."""
        if trigger_event_type not in _VALID_TRIGGER_EVENTS:
            raise ValueError(f"trigger_event_type must be one of: {_VALID_TRIGGER_EVENTS}")
        if action_type not in _VALID_HOOK_ACTIONS:
            raise ValueError(f"action_type must be one of: {_VALID_HOOK_ACTIONS}")
        now = utc_now()
        hook_id = make_id("hook")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            if trigger_container_id:
                self._resolve_entity(conn, wid, trigger_container_id)
            if trigger_entity_id:
                self._resolve_entity(conn, wid, trigger_entity_id)
            conn.execute(
                """
                INSERT INTO containment_hooks
                    (hook_id, world_id, trigger_event_type, trigger_container_id,
                     trigger_entity_id, action_type, action_params_json, label, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (hook_id, wid, trigger_event_type, trigger_container_id,
                 trigger_entity_id, action_type, dumps(action_params), label.strip(), now),
            )
            return {
                "hook_id": hook_id,
                "world_id": wid,
                "trigger_event_type": trigger_event_type,
                "trigger_container_id": trigger_container_id,
                "trigger_entity_id": trigger_entity_id,
                "action_type": action_type,
                "action_params": action_params,
                "label": label.strip(),
                "created_at": now,
            }

    def list_containment_hooks(
        self,
        world: str | None = None,
        container_id: str | None = None,
    ) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            query = "SELECT * FROM containment_hooks WHERE world_id = ?"
            params: list[Any] = [wid]
            if container_id:
                query += " AND trigger_container_id = ?"
                params.append(container_id)
            query += " ORDER BY created_at ASC"
            rows = conn.execute(query, params).fetchall()
            return {
                "world_id": wid,
                "hooks": [
                    {
                        "hook_id": r["hook_id"],
                        "trigger_event_type": r["trigger_event_type"],
                        "trigger_container_id": r["trigger_container_id"],
                        "trigger_entity_id": r["trigger_entity_id"],
                        "action_type": r["action_type"],
                        "action_params": loads(r["action_params_json"], {}),
                        "label": r["label"],
                        "created_at": r["created_at"],
                    }
                    for r in rows
                ],
            }

    def remove_containment_hook(self, hook_id: str, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            conn.execute(
                "DELETE FROM containment_hooks WHERE hook_id = ? AND world_id = ?",
                (hook_id, world_row["world_id"]),
            )
            return {"success": True, "hook_id": hook_id}

    def get_containment_events(
        self,
        world: str | None = None,
        entity_id: str | None = None,
        container_id: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Return recent containment move events, optionally filtered."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            query = "SELECT * FROM containment_events WHERE world_id = ?"
            params: list[Any] = [wid]
            if entity_id:
                query += " AND entity_id = ?"
                params.append(entity_id)
            if container_id:
                query += " AND (from_container_id = ? OR to_container_id = ?)"
                params.extend([container_id, container_id])
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return {
                "world_id": wid,
                "events": [
                    {
                        "event_id": r["event_id"],
                        "entity_id": r["entity_id"],
                        "from_container_id": r["from_container_id"],
                        "to_container_id": r["to_container_id"],
                        "event_type": r["event_type"],
                        "created_at": r["created_at"],
                    }
                    for r in rows
                ],
            }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_circular(
        self, conn: sqlite3.Connection, entity_id: str, new_container_id: str
    ) -> bool:
        """Return True if entity_id appears in the container chain above new_container_id."""
        visited: set[str] = set()
        current: str | None = new_container_id
        while current is not None:
            if current == entity_id:
                return True
            if current in visited:
                break
            visited.add(current)
            row = conn.execute(
                "SELECT container_id FROM entities WHERE entity_id = ?", (current,)
            ).fetchone()
            current = row["container_id"] if row else None
        return False

    def _fire_containment_hooks(
        self,
        conn: sqlite3.Connection,
        world_id: str,
        entity_id: str,
        from_container_id: str | None,
        to_container_id: str | None,
    ) -> list[dict[str, Any]]:
        """Match and execute hooks for a containment move. Called within an open transaction."""
        fired_ids: set[str] = set()
        fired: list[dict[str, Any]] = []

        checks: list[tuple[str, str | None]] = []
        if from_container_id is None:
            # Initial placement
            checks = [("enter", to_container_id)]
        elif to_container_id is None:
            # Removal from containment
            checks = [("exit", from_container_id)]
        else:
            # Full move: exit old, enter new, generic move event
            checks = [
                ("exit", from_container_id),
                ("enter", to_container_id),
                ("move", to_container_id),
                ("move", from_container_id),
            ]

        for trigger_event_type, container_id in checks:
            hooks = conn.execute(
                """
                SELECT * FROM containment_hooks
                WHERE world_id = ?
                  AND trigger_event_type = ?
                  AND (trigger_container_id IS NULL OR trigger_container_id = ?)
                  AND (trigger_entity_id IS NULL OR trigger_entity_id = ?)
                ORDER BY created_at ASC
                """,
                (world_id, trigger_event_type, container_id, entity_id),
            ).fetchall()
            for hook in hooks:
                if hook["hook_id"] in fired_ids:
                    continue
                fired_ids.add(hook["hook_id"])
                result = self._execute_containment_hook_action(conn, world_id, hook, entity_id)
                fired.append({
                    "hook_id": hook["hook_id"],
                    "label": hook["label"],
                    "action_type": hook["action_type"],
                    "result": result,
                })

        return fired

    def _execute_containment_hook_action(
        self,
        conn: sqlite3.Connection,
        world_id: str,
        hook: sqlite3.Row,
        triggering_entity_id: str,
    ) -> dict[str, Any]:
        return execute_shared_hook_action(conn, world_id, hook, triggering_entity_id, self)
