"""StatsMixin: hidden stat reads, changes, and linked-entity reconciliation."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import clamp_stat, dumps, make_id, utc_now


class StatsMixin:
    """Read/write hidden stats and propagate changes to linked entities."""

    def get_entity_stats(
        self,
        entity_id: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            entity = self._resolve_entity(conn, world_row["world_id"], entity_id)
            return {
                "world": self._world_dict(world_row),
                "entity": self._entity_dict(conn, entity),
                "stats": self._entity_stats(conn, entity["entity_id"]),
                "exact_values_visible": True,
            }

    def apply_stat_change(
        self,
        entity_id: str,
        changes: dict[str, int],
        reason: str,
        world: str | None = None,
        source_event_id: str | None = None,
        include_reconciliation_suggestions: bool = True,
    ) -> dict[str, Any]:
        if not reason.strip():
            raise ValueError("A reason is required for stat changes.")
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            entity = self._resolve_entity(conn, world_row["world_id"], entity_id)
            before = self._entity_stats(conn, entity["entity_id"])
            normalized_changes = self._normalize_stat_deltas(entity["entity_type"], changes)
            after = dict(before)
            for key, delta in normalized_changes.items():
                after[key] = clamp_stat(after.get(key, 50) + delta)
            conn.execute(
                "UPDATE entity_stats SET stats_json = ?, updated_at = ? WHERE entity_id = ?",
                (dumps(after), now, entity["entity_id"]),
            )
            conn.execute(
                """
                INSERT INTO stat_ledger (
                    ledger_id, world_id, entity_id, changes_json, reason, source_event_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    make_id("stat"),
                    world_row["world_id"],
                    entity["entity_id"],
                    dumps(normalized_changes),
                    reason.strip(),
                    source_event_id,
                    now,
                ),
            )
            suggestions = []
            if include_reconciliation_suggestions:
                suggestions = self._reconciliation_suggestions(conn, world_row["world_id"], entity, normalized_changes)
            return {
                "world": self._world_dict(world_row),
                "entity": self._entity_dict(conn, entity),
                "before": before,
                "changes_applied_as_deltas": normalized_changes,
                "after": after,
                "reconciliation_suggestions": suggestions,
            }

    def reconcile_linked_stats(
        self,
        entity_id: str,
        changes: dict[str, int],
        reason: str = "",
        world: str | None = None,
        apply: bool = False,
    ) -> dict[str, Any]:
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            source = self._resolve_entity(conn, world_row["world_id"], entity_id)
            deltas = self._normalize_stat_deltas(source["entity_type"], changes)
            suggestions = self._reconciliation_suggestions(conn, world_row["world_id"], source, deltas)
            applied: list[dict[str, Any]] = []
            if apply:
                for suggestion in suggestions:
                    if not suggestion["suggested_deltas"]:
                        continue
                    target = self._resolve_entity(conn, world_row["world_id"], suggestion["entity_id"])
                    before = self._entity_stats(conn, target["entity_id"])
                    after = dict(before)
                    for key, delta in suggestion["suggested_deltas"].items():
                        after[key] = clamp_stat(after.get(key, 50) + delta)
                    conn.execute(
                        "UPDATE entity_stats SET stats_json = ?, updated_at = ? WHERE entity_id = ?",
                        (dumps(after), now, target["entity_id"]),
                    )
                    conn.execute(
                        """
                        INSERT INTO stat_ledger (
                            ledger_id, world_id, entity_id, changes_json, reason, source_event_id, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, NULL, ?)
                        """,
                        (
                            make_id("stat"),
                            world_row["world_id"],
                            target["entity_id"],
                            dumps(suggestion["suggested_deltas"]),
                            reason.strip() or f"Reconciled from linked entity {source['name']}.",
                            now,
                        ),
                    )
                    applied.append(
                        {
                            "entity_id": target["entity_id"],
                            "before": before,
                            "after": after,
                            "deltas": suggestion["suggested_deltas"],
                        }
                    )
            return {
                "world": self._world_dict(world_row),
                "source_entity": self._entity_dict(conn, source),
                "source_deltas": deltas,
                "suggestions": suggestions,
                "applied": applied,
            }
