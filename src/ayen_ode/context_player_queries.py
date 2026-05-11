"""PlayerQueryMixin: player-side queries for the world-state context packet."""

from __future__ import annotations

from typing import Any

from .context_scene_queries import SceneQueryMixin


class PlayerQueryMixin(SceneQueryMixin):
    """Queries 5–9: player state, entity histories, player journey, relationships, world bleed."""

    # ------------------------------------------------------------------
    # Query 5: Player state — knowledge, inventory, caused
    # ------------------------------------------------------------------

    def _query_player_state(
        self,
        conn: Any,
        world_id: str,
        player_entity_id: str | None,
    ) -> dict[str, Any]:
        empty: dict[str, Any] = {
            "entity": None,
            "stats": {},
            "knowledge_witnessed": [],
            "knowledge_rumor": [],
            "inventory": [],
            "caused": [],
        }
        if not player_entity_id:
            return empty

        player_row = conn.execute(
            "SELECT * FROM entities WHERE entity_id = ? AND world_id = ?",
            (player_entity_id, world_id),
        ).fetchone()
        if not player_row:
            return empty

        entity = self._fetch_entity_with_stats(conn, world_id, player_row)
        stats = self._service._entity_stats(conn, player_entity_id)

        def _knowledge_rows(degree: str) -> list[dict[str, Any]]:
            rows = conn.execute(
                "SELECT * FROM entity_knowledge WHERE world_id = ? AND entity_id = ? AND degree = ?",
                (world_id, player_entity_id, degree),
            ).fetchall()
            return [{"knows_about_id": r["knows_about_id"], "degree": r["degree"], "source_id": r["source_id"]} for r in rows]

        inventory_rows = conn.execute(
            "SELECT * FROM entities WHERE container_id = ? AND world_id = ? ORDER BY name ASC",
            (player_entity_id, world_id),
        ).fetchall()
        inventory = [self._fetch_entity_with_stats(conn, world_id, r) for r in inventory_rows]

        caused_rows = conn.execute(
            """SELECT * FROM consequence_records
               WHERE world_id = ? AND cause_id = ?
               ORDER BY created_at DESC LIMIT 20""",
            (world_id, player_entity_id),
        ).fetchall()

        return {
            "entity": entity,
            "stats": stats,
            "knowledge_witnessed": _knowledge_rows("witnessed"),
            "knowledge_rumor": _knowledge_rows("heard_rumor"),
            "inventory": inventory,
            "caused": [self._consequence_dict_raw(r) for r in caused_rows],
        }

    # ------------------------------------------------------------------
    # Query 6: Entity histories with compression
    # ------------------------------------------------------------------

    def _query_entity_histories(
        self,
        conn: Any,
        world_id: str,
        scene_ids: set[str],
        history_depth: int,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if not scene_ids:
            return result

        for entity_id in scene_ids:
            history_rows = conn.execute(
                """SELECT * FROM consequence_records
                   WHERE world_id = ? AND target_id = ?
                   ORDER BY created_at ASC""",
                (world_id, entity_id),
            ).fetchall()
            if not history_rows:
                result[entity_id] = {"full": [], "compressed": []}
                continue

            records = [self._consequence_dict_raw(r) for r in history_rows]
            consequence_ids = [r["consequence_id"] for r in records]
            downstream_counts = self._score_consequence_downstream(conn, world_id, consequence_ids)

            scored = sorted(records, key=lambda r: downstream_counts.get(r["consequence_id"], 0), reverse=True)
            full = scored[:3]
            compressed = [
                {"timestamp": r["created_at"], "effect_type": r["effect_type"], "detail": r["detail"]}
                for r in scored[3:]
            ]
            result[entity_id] = {"full": full, "compressed": compressed}

        return result

    # ------------------------------------------------------------------
    # Query 7: Player journey — causal chain where player is cause or target
    # ------------------------------------------------------------------

    def _query_player_journey(
        self,
        conn: Any,
        world_id: str,
        player_entity_id: str | None,
        scene_ids: set[str],
    ) -> list[dict[str, Any]]:
        if not player_entity_id:
            return []

        rows = conn.execute(
            """SELECT * FROM consequence_records
               WHERE world_id = ? AND (cause_id = ? OR target_id = ?)
               ORDER BY created_at ASC""",
            (world_id, player_entity_id, player_entity_id),
        ).fetchall()
        if not rows:
            return []

        all_records = [self._consequence_dict_raw(r) for r in rows]
        all_consequence_ids = {r["consequence_id"] for r in all_records}

        used_as_cause: set[str] = set()
        if all_consequence_ids:
            placeholders = ",".join("?" * len(all_consequence_ids))
            used_rows = conn.execute(
                f"""SELECT DISTINCT cause_id FROM consequence_records
                    WHERE world_id = ? AND cause_id IN ({placeholders})""",
                (world_id, *all_consequence_ids),
            ).fetchall()
            used_as_cause = {r["cause_id"] for r in used_rows}

        journey = []
        for rec in all_records:
            other_id = rec["target_id"] if rec["cause_id"] == player_entity_id else rec["cause_id"]
            is_scene_relevant = other_id in scene_ids
            is_unresolved = rec["consequence_id"] not in used_as_cause
            if is_scene_relevant or is_unresolved:
                rec["is_unresolved"] = is_unresolved
                journey.append(rec)

        return journey

    # ------------------------------------------------------------------
    # Query 8: Relationship histories — NPC knowledge events re: player
    # ------------------------------------------------------------------

    def _query_relationship_histories(
        self,
        conn: Any,
        world_id: str,
        scene: dict[str, Any],
        player_entity_id: str | None,
    ) -> dict[str, Any]:
        if not player_entity_id:
            return {}

        characters = [
            e for e in scene.get("contents", [])
            if e and e.get("entity_type") == "character"
        ]
        if not characters:
            return {}

        result: dict[str, Any] = {}
        for char in characters:
            cid = char["entity_id"]
            rows = conn.execute(
                """SELECT * FROM knowledge_events
                   WHERE world_id = ?
                     AND (
                       (entity_id = ? AND knows_about_id = ?)
                       OR (entity_id = ? AND knows_about_id = ?)
                     )
                   ORDER BY created_at ASC""",
                (world_id, cid, player_entity_id, player_entity_id, cid),
            ).fetchall()

            events = []
            for row in rows:
                direction = (
                    "character_about_player"
                    if row["entity_id"] == cid
                    else "player_about_character"
                )
                events.append({
                    "event_id": row["event_id"],
                    "entity_id": row["entity_id"],
                    "knows_about_id": row["knows_about_id"],
                    "event_type": row["event_type"],
                    "degree": row["degree"],
                    "source_id": row["source_id"],
                    "created_at": row["created_at"],
                    "direction": direction,
                })
            result[cid] = events

        return result

    # ------------------------------------------------------------------
    # Query 9: World bleed-in — cross-scene consequence records
    # ------------------------------------------------------------------

    def _query_world_bleed(
        self,
        conn: Any,
        world_id: str,
        scene_ids: set[str],
    ) -> list[dict[str, Any]]:
        if not scene_ids:
            return []
        placeholders = ",".join("?" * len(scene_ids))
        rows = conn.execute(
            f"""SELECT * FROM consequence_records
                WHERE world_id = ?
                  AND (cause_id IN ({placeholders}) OR target_id IN ({placeholders}))
                  AND NOT (cause_id IN ({placeholders}) AND target_id IN ({placeholders}))
                ORDER BY created_at DESC LIMIT 20""",
            (world_id, *scene_ids, *scene_ids, *scene_ids, *scene_ids),
        ).fetchall()
        return [self._consequence_dict_raw(r) for r in rows]

    # ------------------------------------------------------------------
    # Private helper
    # ------------------------------------------------------------------

    def _score_consequence_downstream(
        self,
        conn: Any,
        world_id: str,
        consequence_ids: list[str],
    ) -> dict[str, int]:
        """Batch-count how many downstream effects each consequence_id produced."""
        if not consequence_ids:
            return {}
        placeholders = ",".join("?" * len(consequence_ids))
        rows = conn.execute(
            f"""SELECT cause_id, COUNT(*) as cnt
                FROM consequence_records
                WHERE world_id = ? AND cause_id IN ({placeholders})
                GROUP BY cause_id""",
            (world_id, *consequence_ids),
        ).fetchall()
        return {r["cause_id"]: r["cnt"] for r in rows}
