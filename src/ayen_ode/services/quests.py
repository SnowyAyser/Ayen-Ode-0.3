"""QuestsMixin: create, read, and progress the layered quest system."""

from __future__ import annotations

from typing import Any

from .base import dumps, loads, make_id, utc_now


class QuestsMixin:
    """Manages world_quests: overarching (tier 1), active (tier 2), threads (tier 3).

    Status lifecycle:
        active          — visible and being tracked
        pending_player  — score 40-69, awaiting player promote/dismiss
        completed       — all tags matched (or manually completed)
        dismissed       — player or system discarded it
    """

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_quest(
        self,
        title: str,
        description: str,
        completion_tags: list[str],
        tier: int = 2,
        significance_score: int = 0,
        parent_quest_id: str | None = None,
        status: str = "active",
        world: str | None = None,
    ) -> dict[str, Any]:
        """Insert a new quest row. Returns the quest dict."""
        if tier not in (1, 2, 3):
            raise ValueError("tier must be 1, 2, or 3")
        if status not in ("active", "pending_player", "completed", "dismissed"):
            raise ValueError(f"Invalid status: {status}")
        now = utc_now()
        quest_id = make_id("quest")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            conn.execute(
                """
                INSERT INTO world_quests
                    (quest_id, world_id, tier, title, description,
                     completion_tags_json, progress_tags_json,
                     significance_score, status, parent_quest_id,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, '[]', ?, ?, ?, ?, ?)
                """,
                (
                    quest_id, wid, tier, title.strip(), description.strip(),
                    dumps(completion_tags), significance_score,
                    status, parent_quest_id, now, now,
                ),
            )
            return self._quest_dict_from_id(conn, quest_id)

    def mark_quest_tag(
        self,
        quest_id: str,
        tag: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Mark a completion tag as achieved. Auto-completes if all tags are matched."""
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            row = conn.execute(
                "SELECT * FROM world_quests WHERE quest_id = ? AND world_id = ?",
                (quest_id, wid),
            ).fetchone()
            if not row:
                raise ValueError(f"Quest not found: {quest_id}")
            if row["status"] not in ("active", "pending_player"):
                return self._quest_dict(row)

            completion_tags = loads(row["completion_tags_json"], [])
            progress_tags = loads(row["progress_tags_json"], [])
            if tag in completion_tags and tag not in progress_tags:
                progress_tags.append(tag)

            all_done = set(completion_tags).issubset(set(progress_tags))
            new_status = "completed" if all_done else row["status"]
            completed_at = now if all_done else row["completed_at"]

            conn.execute(
                """
                UPDATE world_quests
                SET progress_tags_json = ?, status = ?, updated_at = ?, completed_at = ?
                WHERE quest_id = ?
                """,
                (dumps(progress_tags), new_status, now, completed_at, quest_id),
            )
            return self._quest_dict_from_id(conn, quest_id)

    def complete_quest(self, quest_id: str, world: str | None = None) -> dict[str, Any]:
        """Force-complete a quest regardless of tag state."""
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            conn.execute(
                "UPDATE world_quests SET status = 'completed', updated_at = ?, completed_at = ? WHERE quest_id = ? AND world_id = ?",
                (now, now, quest_id, wid),
            )
            return self._quest_dict_from_id(conn, quest_id)

    def dismiss_quest(self, quest_id: str, world: str | None = None) -> dict[str, Any]:
        """Dismiss a quest (player or system chose to drop it)."""
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            conn.execute(
                "UPDATE world_quests SET status = 'dismissed', updated_at = ? WHERE quest_id = ? AND world_id = ?",
                (now, quest_id, wid),
            )
            return self._quest_dict_from_id(conn, quest_id)

    def promote_quest(self, quest_id: str, world: str | None = None) -> dict[str, Any]:
        """Promote a pending_player thread to an active Tier 2 goal."""
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            conn.execute(
                "UPDATE world_quests SET status = 'active', tier = 2, updated_at = ? WHERE quest_id = ? AND world_id = ?",
                (now, quest_id, wid),
            )
            return self._quest_dict_from_id(conn, quest_id)

    def increment_world_turn_count(self, world: str | None = None) -> int:
        """Increment narrative_turn_count for the world. Returns new count."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            conn.execute(
                "UPDATE worlds SET narrative_turn_count = narrative_turn_count + 1 WHERE world_id = ?",
                (wid,),
            )
            row = conn.execute(
                "SELECT narrative_turn_count FROM worlds WHERE world_id = ?", (wid,)
            ).fetchone()
            return row["narrative_turn_count"] if row else 0

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_quest(self, quest_id: str, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            row = conn.execute(
                "SELECT * FROM world_quests WHERE quest_id = ? AND world_id = ?",
                (quest_id, wid),
            ).fetchone()
            if not row:
                raise ValueError(f"Quest not found: {quest_id}")
            return {"quest": self._quest_dict(row)}

    def list_quests(
        self,
        tier: int | None = None,
        status: str | None = None,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Return quests for the world, optionally filtered by tier and/or status."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            sql = "SELECT * FROM world_quests WHERE world_id = ?"
            params: list[Any] = [wid]
            if tier is not None:
                sql += " AND tier = ?"
                params.append(tier)
            if status is not None:
                sql += " AND status = ?"
                params.append(status)
            sql += " ORDER BY tier ASC, created_at ASC"
            rows = conn.execute(sql, params).fetchall()
            return {"world_id": wid, "quests": [self._quest_dict(r) for r in rows]}

    def check_quest_progress(self, quest_id: str, world: str | None = None) -> dict[str, Any]:
        """Return progress breakdown: matched/total count, percentage, tag lists."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            row = conn.execute(
                "SELECT * FROM world_quests WHERE quest_id = ? AND world_id = ?",
                (quest_id, wid),
            ).fetchone()
            if not row:
                raise ValueError(f"Quest not found: {quest_id}")
            completion_tags = loads(row["completion_tags_json"], [])
            progress_tags = loads(row["progress_tags_json"], [])
            matched = [t for t in completion_tags if t in progress_tags]
            remaining = [t for t in completion_tags if t not in progress_tags]
            total = len(completion_tags)
            return {
                "quest_id": quest_id,
                "title": row["title"],
                "matched": len(matched),
                "total": total,
                "percentage": int((len(matched) / total) * 100) if total else 0,
                "matched_tags": matched,
                "remaining_count": len(remaining),
                "status": row["status"],
            }

    def get_active_quests_summary(self, world: str | None = None) -> dict[str, Any]:
        """Return a concise summary of all active+pending quests for prompt injection."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                """SELECT * FROM world_quests
                WHERE world_id = ? AND status IN ('active', 'pending_player')
                ORDER BY tier ASC, created_at ASC""",
                (wid,),
            ).fetchall()
            return {
                "world_id": wid,
                "quests": [self._quest_dict(r) for r in rows],
            }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _quest_dict(self, row: Any) -> dict[str, Any]:
        return {
            "quest_id": row["quest_id"],
            "world_id": row["world_id"],
            "tier": row["tier"],
            "title": row["title"],
            "description": row["description"],
            "completion_tags": loads(row["completion_tags_json"], []),
            "progress_tags": loads(row["progress_tags_json"], []),
            "significance_score": row["significance_score"],
            "status": row["status"],
            "parent_quest_id": row["parent_quest_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "completed_at": row["completed_at"],
        }

    def _quest_dict_from_id(self, conn: Any, quest_id: str) -> dict[str, Any]:
        row = conn.execute(
            "SELECT * FROM world_quests WHERE quest_id = ?", (quest_id,)
        ).fetchone()
        return self._quest_dict(row) if row else {}
