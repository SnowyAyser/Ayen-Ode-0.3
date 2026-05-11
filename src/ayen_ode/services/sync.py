"""SyncMixin: canon sync log and world summary sync."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import dumps, loads, make_id, normalize_list, utc_now


class SyncMixin:
    """Canon sync log and world summary sync (Notion integration deferred in v1)."""

    def sync_canon_record(
        self,
        sync_type: str,
        payload: dict[str, Any],
        world: str | None = None,
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        return self._log_sync(sync_type=f"canon:{sync_type}", payload=payload, world=world, entity_id=entity_id)

    def sync_world_summary(
        self,
        summary: str,
        world: str | None = None,
        active_tensions: list[str] | None = None,
        source: str = "client",
    ) -> dict[str, Any]:
        now = utc_now()
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            conn.execute(
                """
                UPDATE worlds
                SET current_state_summary = ?, active_tensions_json = ?, updated_at = ?
                WHERE world_id = ?
                """,
                (
                    summary.strip(),
                    dumps(normalize_list(active_tensions)),
                    now,
                    row["world_id"],
                ),
            )
            updated = self._get_world_row(conn, row["world_id"])
        sync = self._log_sync(
            sync_type="world_summary",
            payload={"summary": summary.strip(), "active_tensions": active_tensions or [], "source": source},
            world=updated["world_id"],
        )
        return {"world": self._world_dict(updated), "sync": sync}

    def _log_sync(
        self,
        sync_type: str,
        payload: dict[str, Any],
        world: str | None = None,
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        now = utc_now()
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            sync_id = make_id("sync")
            conn.execute(
                """
                INSERT INTO sync_log (sync_id, world_id, entity_id, sync_type, payload_json, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'logged', ?)
                """,
                (sync_id, row["world_id"], entity_id, sync_type, dumps(payload), now),
            )
            return {
                "sync_id": sync_id,
                "world_id": row["world_id"],
                "entity_id": entity_id,
                "sync_type": sync_type,
                "status": "logged",
                "created_at": now,
                "note": "Logged only. Notion/canon automation is intentionally deferred in v1.",
            }
