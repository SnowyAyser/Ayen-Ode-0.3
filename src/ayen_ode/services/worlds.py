"""WorldsMixin: world lifecycle, handoffs, and status management."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import dumps, loads, make_id, normalize_list, utc_now


class WorldsMixin:
    """World CRUD, handoffs, status transitions, archive, reset."""

    def list_worlds(self, include_archived: bool = False) -> dict[str, Any]:
        with self.connect() as conn:
            if include_archived:
                rows = conn.execute("SELECT * FROM worlds ORDER BY created_at ASC").fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM worlds WHERE status != 'archived' ORDER BY created_at ASC"
                ).fetchall()
            return {"worlds": [self._world_dict(row) for row in rows]}

    def create_world(
        self,
        name: str,
        premise: str,
        theme_tone: str = "",
        player_role: str = "",
        activate_now: bool = True,
    ) -> dict[str, Any]:
        if not name.strip():
            raise ValueError("World name is required.")
        if not premise.strip():
            raise ValueError("World premise is required.")

        now = utc_now()
        world_id = make_id("world")

        with self.connect() as conn:
            active_exists = self._active_world_row(conn) is not None
            status = "active" if activate_now or not active_exists else "draft"
            slug = self._unique_slug(conn, name)

            if status == "active":
                conn.execute(
                    "UPDATE worlds SET status = 'paused', updated_at = ? WHERE status = 'active'",
                    (now,),
                )

            conn.execute(
                """
                INSERT INTO worlds (
                    world_id, slug, name, status, premise, theme_tone, player_role,
                    current_state_summary, active_tensions_json, last_system_handoff,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, '', '[]', '', ?, ?)
                """,
                (
                    world_id,
                    slug,
                    name.strip(),
                    status,
                    premise.strip(),
                    theme_tone.strip(),
                    player_role.strip(),
                    now,
                    now,
                ),
            )
            row = self._get_world_row(conn, world_id)
            return {
                "world": self._world_dict(row),
                "activated": status == "active",
                "note": "First world was activated automatically." if not active_exists else "",
            }

    def get_active_world(self) -> dict[str, Any]:
        with self.connect() as conn:
            row = self._active_world_row(conn)
            return {"world": self._world_dict(row) if row else None}

    def switch_world(self, world: str) -> dict[str, Any]:
        now = utc_now()
        with self.connect() as conn:
            target = self._resolve_world(conn, world)
            if target["status"] == "archived":
                raise ValueError("Archived worlds cannot be activated.")

            previous = self._active_world_row(conn)
            if previous and previous["world_id"] == target["world_id"]:
                return {
                    "previous_world": self._world_dict(previous),
                    "active_world": self._world_dict(target),
                    "restored_handoff": target["last_system_handoff"],
                    "current_state_summary": target["current_state_summary"],
                    "changed": False,
                }

            if previous:
                conn.execute(
                    "UPDATE worlds SET status = 'paused', updated_at = ? WHERE world_id = ?",
                    (now, previous["world_id"]),
                )
            conn.execute(
                "UPDATE worlds SET status = 'active', updated_at = ? WHERE world_id = ?",
                (now, target["world_id"]),
            )
            active = self._get_world_row(conn, target["world_id"])
            return {
                "previous_world": self._world_dict(previous) if previous else None,
                "active_world": self._world_dict(active),
                "restored_handoff": active["last_system_handoff"],
                "current_state_summary": active["current_state_summary"],
                "changed": True,
            }

    def get_world_status(self, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            counts = conn.execute(
                """
                SELECT entity_type, COUNT(*) AS count
                FROM entities
                WHERE world_id = ?
                GROUP BY entity_type
                """,
                (row["world_id"],),
            ).fetchall()
            return {
                "world": self._world_dict(row),
                "entity_counts": {count["entity_type"]: count["count"] for count in counts},
            }

    def archive_world(self, world: str) -> dict[str, Any]:
        now = utc_now()
        with self.connect() as conn:
            target = self._resolve_world(conn, world)
            was_active = target["status"] == "active"
            conn.execute(
                "UPDATE worlds SET status = 'archived', updated_at = ? WHERE world_id = ?",
                (now, target["world_id"]),
            )
            replacement = None
            if was_active:
                replacement = conn.execute(
                    """
                    SELECT * FROM worlds
                    WHERE status != 'archived'
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """
                ).fetchone()
                if replacement:
                    conn.execute(
                        "UPDATE worlds SET status = 'active', updated_at = ? WHERE world_id = ?",
                        (now, replacement["world_id"]),
                    )
                    replacement = self._get_world_row(conn, replacement["world_id"])
            archived = self._get_world_row(conn, target["world_id"])
            return {
                "archived_world": self._world_dict(archived),
                "replacement_active_world": self._world_dict(replacement) if replacement else None,
            }

    def delete_world(self, world: str) -> dict[str, Any]:
        """Permanently delete a world and all its data."""
        now = utc_now()
        with self.connect() as conn:
            target = self._resolve_world(conn, world)
            world_id = target["world_id"]
            was_active = target["status"] == "active"
            conn.execute("DELETE FROM worlds WHERE world_id = ?", (world_id,))
            replacement = None
            if was_active:
                replacement = conn.execute(
                    "SELECT * FROM worlds WHERE status != 'archived' ORDER BY updated_at DESC LIMIT 1"
                ).fetchone()
                if replacement:
                    conn.execute(
                        "UPDATE worlds SET status = 'active', updated_at = ? WHERE world_id = ?",
                        (now, replacement["world_id"]),
                    )
                    replacement = self._get_world_row(conn, replacement["world_id"])
            return {
                "deleted_world_id": world_id,
                "replacement_active_world": self._world_dict(replacement) if replacement else None,
            }

    def reset_world(self, world: str) -> dict[str, Any]:
        """Wipe all world progress and restore the original opening scene."""
        now = utc_now()
        with self.connect() as conn:
            target = self._resolve_world(conn, world)
            world_id = target["world_id"]
            
            # Retrieve the original opening scene from original_opening_scene column if populated
            original_text = ""
            try:
                original_text = target["original_opening_scene"]
            except (IndexError, KeyError):
                pass
                
            # Fallback and backfill from oldest handoff if column was empty
            if not original_text:
                original = conn.execute(
                    "SELECT handoff_text FROM world_handoffs WHERE world_id = ? ORDER BY created_at ASC LIMIT 1",
                    (world_id,),
                ).fetchone()
                original_text = original["handoff_text"] if original else ""
                if original_text:
                    conn.execute(
                        "UPDATE worlds SET original_opening_scene = ? WHERE world_id = ?",
                        (original_text, world_id),
                    )

            # Wipe all playthrough progress (entity cascade handles entity_links, entity_stats, stat_ledger)
            conn.execute("DELETE FROM entities WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM world_handoffs WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM investigation_state WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM investigation_jobs WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM world_currencies WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM sync_log WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM intake_logs WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM containment_events WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM entity_knowledge WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM knowledge_events WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM consequence_records WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM world_quests WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM world_debts WHERE world_id = ?", (world_id,))
            conn.execute("DELETE FROM pregenerated_investigations WHERE world_id = ?", (world_id,))

            # Reset game time
            conn.execute(
                "UPDATE worlds SET game_time_seconds = 0, game_time_label = '', narrative_turn_count = 0 WHERE world_id = ?",
                (world_id,),
            )

            # Restore the original opening scene as the only handoff
            if original_text:
                conn.execute(
                    "INSERT INTO world_handoffs (handoff_id, world_id, handoff_text, created_at) VALUES (?, ?, ?, ?)",
                    (make_id("handoff"), world_id, original_text, now),
                )
            conn.execute(
                "UPDATE worlds SET last_system_handoff = ?, updated_at = ? WHERE world_id = ?",
                (original_text, now, world_id),
            )
            # Reinitialize investigation currency
            conn.execute(
                """
                INSERT INTO world_currencies
                    (currency_id, world_id, currency_type, current_balance, max_balance, last_regen_at, regen_rate)
                VALUES (?, ?, 'investigation_points', 5, 5, ?, 0)
                """,
                (make_id("currency"), world_id, now),
            )
            return {
                "reset_world_id": world_id,
                "world": self._world_dict(self._get_world_row(conn, world_id)),
                "original_opening_scene": original_text,
            }

    def set_original_opening_scene(self, world_id: str, scene_text: str) -> None:
        """Store the raw original opening scene (including LLM investigation tags) permanently."""
        with self.connect() as conn:
            conn.execute(
                "UPDATE worlds SET original_opening_scene = ? WHERE world_id = ?",
                (scene_text.strip(), world_id),
            )

    def save_world_handoff(
        self,
        handoff_text: str,
        world: str | None = None,
        current_state_summary: str | None = None,
        active_tensions: list[str] | None = None,
    ) -> dict[str, Any]:
        if not handoff_text.strip():
            raise ValueError("handoff_text is required.")
        now = utc_now()
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            updates = ["last_system_handoff = ?", "updated_at = ?"]
            params: list[Any] = [handoff_text.strip(), now]
            if current_state_summary is not None:
                updates.append("current_state_summary = ?")
                params.append(current_state_summary.strip())
            if active_tensions is not None:
                updates.append("active_tensions_json = ?")
                params.append(dumps(normalize_list(active_tensions)))
            params.append(row["world_id"])
            conn.execute(f"UPDATE worlds SET {', '.join(updates)} WHERE world_id = ?", params)
            conn.execute(
                """
                INSERT INTO world_handoffs (handoff_id, world_id, handoff_text, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (make_id("handoff"), row["world_id"], handoff_text.strip(), now),
            )
            saved = self._get_world_row(conn, row["world_id"])
            return {
                "world": self._world_dict(saved),
                "handoff": saved["last_system_handoff"],
                "saved_at": now,
            }

    def get_world_time(self, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            return {
                "world_id": row["world_id"],
                "seconds": row["game_time_seconds"],
                "label": row["game_time_label"],
            }

    def advance_world_time(
        self,
        seconds: int,
        label: str = "",
        world: str | None = None,
    ) -> dict[str, Any]:
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            conn.execute(
                "UPDATE worlds SET game_time_seconds = game_time_seconds + ?, game_time_label = ? WHERE world_id = ?",
                (max(0, int(seconds)), label.strip(), row["world_id"]),
            )
            updated = conn.execute(
                "SELECT game_time_seconds, game_time_label FROM worlds WHERE world_id = ?",
                (row["world_id"],),
            ).fetchone()
            return {
                "world_id": row["world_id"],
                "seconds": updated["game_time_seconds"],
                "label": updated["game_time_label"],
            }

    def get_world_handoff(self, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            latest = conn.execute(
                """
                SELECT handoff_text, created_at
                FROM world_handoffs
                WHERE world_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (row["world_id"],),
            ).fetchone()
            return {
                "world": self._world_dict(row),
                "handoff": latest["handoff_text"] if latest else row["last_system_handoff"],
                "saved_at": latest["created_at"] if latest else None,
            }
