"""ConsequenceQueryMixin: read-only traversal of the causal chain."""

from __future__ import annotations

import re
from typing import Any
import sqlite3

from .base import loads

_VALID_EFFECT_TYPES = {
    "created",
    "destroyed",
    "moved",
    "transformed",
    "state_changed",
    "triggered_event",
    "relationship_changed",
}

_DETAIL_PATTERN = re.compile(r"^(.+?):\s*(.+?)\s*→\s*(.+?)\s*$")


def _parse_detail(detail: str) -> tuple[str, str, str] | None:
    """Return (key, from_val, to_val) if detail matches 'key: old → new', else None."""
    m = _DETAIL_PATTERN.match(detail)
    if m:
        return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    return None


def _consequence_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "consequence_id": row["consequence_id"],
        "world_id": row["world_id"],
        "cause_id": row["cause_id"],
        "effect_type": row["effect_type"],
        "target_id": row["target_id"],
        "detail": row["detail"],
        "created_at": row["created_at"],
    }


class ConsequenceQueryMixin:
    """Read-only traversal methods for the causal graph."""

    def get_effects(self, cause_id: str, world: str | None = None) -> dict[str, Any]:
        """Return everything that resulted from this cause."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                "SELECT * FROM consequence_records WHERE world_id = ? AND cause_id = ? ORDER BY created_at ASC, consequence_id ASC",
                (wid, cause_id),
            ).fetchall()
            return {
                "world_id": wid,
                "cause_id": cause_id,
                "effects": [_consequence_dict(r) for r in rows],
            }

    def get_causes(self, target_id: str, world: str | None = None) -> dict[str, Any]:
        """Return every causal record that contributed to this entity's current state."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                "SELECT * FROM consequence_records WHERE world_id = ? AND target_id = ? ORDER BY created_at ASC, consequence_id ASC",
                (wid, target_id),
            ).fetchall()
            return {
                "world_id": wid,
                "target_id": target_id,
                "causes": [_consequence_dict(r) for r in rows],
            }

    def get_chain_forward(
        self,
        event_id: str,
        depth: int = 3,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Trace ripple effects outward N levels from event_id. Cycle-safe."""
        depth = max(1, min(depth, 10))
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            levels: list[dict[str, Any]] = []
            frontier: set[str] = {event_id}
            seen_causes: set[str] = {event_id}
            for level_num in range(1, depth + 1):
                if not frontier:
                    break
                placeholders = ",".join("?" * len(frontier))
                rows = conn.execute(
                    f"SELECT * FROM consequence_records WHERE world_id = ? AND cause_id IN ({placeholders}) ORDER BY created_at ASC, consequence_id ASC",
                    (wid, *frontier),
                ).fetchall()
                if not rows:
                    break
                records = [_consequence_dict(r) for r in rows]
                levels.append({"level": level_num, "records": records})
                new_frontier: set[str] = set()
                for r in records:
                    tid = r["target_id"]
                    if tid not in seen_causes:
                        new_frontier.add(tid)
                        seen_causes.add(tid)
                frontier = new_frontier
            return {
                "world_id": wid,
                "root_id": event_id,
                "depth_requested": depth,
                "levels": levels,
            }

    def get_chain_backward(
        self,
        entity_id: str,
        depth: int = 3,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Trace backward N levels to root causes. Cycle-safe."""
        depth = max(1, min(depth, 10))
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            levels: list[dict[str, Any]] = []
            frontier: set[str] = {entity_id}
            seen_targets: set[str] = {entity_id}
            for level_num in range(1, depth + 1):
                if not frontier:
                    break
                placeholders = ",".join("?" * len(frontier))
                rows = conn.execute(
                    f"SELECT * FROM consequence_records WHERE world_id = ? AND target_id IN ({placeholders}) ORDER BY created_at ASC, consequence_id ASC",
                    (wid, *frontier),
                ).fetchall()
                if not rows:
                    break
                records = [_consequence_dict(r) for r in rows]
                levels.append({"level": level_num, "records": records})
                new_frontier: set[str] = set()
                for r in records:
                    cid = r["cause_id"]
                    if cid not in seen_targets:
                        new_frontier.add(cid)
                        seen_targets.add(cid)
                frontier = new_frontier
            return {
                "world_id": wid,
                "root_id": entity_id,
                "depth_requested": depth,
                "levels": levels,
            }

    def get_history(self, entity_id: str, world: str | None = None) -> dict[str, Any]:
        """Full ordered timeline of every consequence where this entity is the target."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                "SELECT * FROM consequence_records WHERE world_id = ? AND target_id = ? ORDER BY created_at ASC, rowid ASC",
                (wid, entity_id),
            ).fetchall()
            return {
                "world_id": wid,
                "entity_id": entity_id,
                "history": [_consequence_dict(r) for r in rows],
            }

    def get_state_at(
        self,
        entity_id: str,
        timestamp: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Reconstruct entity state at a point in time by replaying consequences up to timestamp."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                """
                SELECT * FROM consequence_records
                WHERE world_id = ? AND target_id = ? AND created_at <= ?
                ORDER BY created_at ASC, rowid ASC
                """,
                (wid, entity_id, timestamp),
            ).fetchall()
            records = [_consequence_dict(r) for r in rows]
            state: dict[str, str] = {}
            for r in records:
                parsed = _parse_detail(r["detail"])
                if parsed:
                    key, _from, to = parsed
                    state[key] = to
            return {
                "world_id": wid,
                "entity_id": entity_id,
                "as_of": timestamp,
                "records": records,
                "reconstructed_state": state,
            }

    def get_consequence_events(
        self,
        world: str | None = None,
        cause_id: str | None = None,
        target_id: str | None = None,
        effect_type: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Return recent consequence records, optionally filtered."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            query = "SELECT * FROM consequence_records WHERE world_id = ?"
            params: list[Any] = [wid]
            if cause_id:
                query += " AND cause_id = ?"
                params.append(cause_id)
            if target_id:
                query += " AND target_id = ?"
                params.append(target_id)
            if effect_type:
                query += " AND effect_type = ?"
                params.append(effect_type)
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return {
                "world_id": wid,
                "records": [_consequence_dict(r) for r in rows],
            }

    def get_unresolved_threads(
        self,
        world: str | None = None,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Return consequence records that have no downstream effects yet."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                """
                SELECT cr.*
                FROM consequence_records cr
                WHERE cr.world_id = ?
                  AND cr.consequence_id NOT IN (
                      SELECT DISTINCT cause_id FROM consequence_records
                      WHERE world_id = ? AND cause_id IS NOT NULL
                  )
                ORDER BY cr.created_at DESC LIMIT ?
                """,
                (wid, wid, limit),
            ).fetchall()
            return {
                "world_id": wid,
                "unresolved_threads": [_consequence_dict(r) for r in rows],
            }
