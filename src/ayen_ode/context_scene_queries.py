"""SceneQueryMixin: scene-side queries for the world-state context packet.

All methods share the conn passed from ContextAssembler.assemble().
Never call service methods that open their own connect() inside these methods.
"""

from __future__ import annotations

from typing import Any


class SceneQueryMixin:
    """Queries 1–4: physical scene, actor awareness, recent history, open threads."""

    # ------------------------------------------------------------------
    # Shared helpers (used by both scene and player queries)
    # ------------------------------------------------------------------

    def _consequence_dict_raw(self, row: Any) -> dict[str, Any]:
        """Serialize a consequence_records row to a plain dict."""
        return {
            "consequence_id": row["consequence_id"],
            "world_id": row["world_id"],
            "cause_id": row["cause_id"],
            "effect_type": row["effect_type"],
            "target_id": row["target_id"],
            "detail": row["detail"],
            "created_at": row["created_at"],
        }

    def _fetch_entity_with_stats(
        self,
        conn: Any,
        world_id: str,
        row: Any,
    ) -> dict[str, Any]:
        """Serialize an entity row and merge in its stats."""
        if row is None:
            return {}
        entity = self._service._entity_dict(conn, row)
        entity["stats"] = self._service._entity_stats(conn, row["entity_id"])
        return entity

    # ------------------------------------------------------------------
    # Query 1: Scene — physical reality
    # ------------------------------------------------------------------

    def _query_scene(
        self,
        conn: Any,
        world_id: str,
        player_entity_id: str | None,
    ) -> dict[str, Any]:
        empty = {
            "current_container": None,
            "contents": [],
            "adjacent_containers": [],
            "container_chain": [],
        }
        if not player_entity_id:
            return empty

        player_row = conn.execute(
            "SELECT * FROM entities WHERE entity_id = ? AND world_id = ?",
            (player_entity_id, world_id),
        ).fetchone()
        if not player_row:
            return empty

        container_id = player_row["container_id"]
        if not container_id:
            return empty

        container_row = conn.execute(
            "SELECT * FROM entities WHERE entity_id = ? AND world_id = ?",
            (container_id, world_id),
        ).fetchone()
        if not container_row:
            return empty

        current_container = self._fetch_entity_with_stats(conn, world_id, container_row)

        content_rows = conn.execute(
            "SELECT * FROM entities WHERE container_id = ? AND world_id = ? ORDER BY name ASC",
            (container_id, world_id),
        ).fetchall()
        contents = [self._fetch_entity_with_stats(conn, world_id, r) for r in content_rows]

        parent_id = container_row["container_id"]
        adjacent_containers = []
        if parent_id:
            sibling_rows = conn.execute(
                """SELECT * FROM entities
                   WHERE container_id = ? AND world_id = ? AND entity_id != ?
                   ORDER BY name ASC""",
                (parent_id, world_id, container_id),
            ).fetchall()
            for sib_row in sibling_rows:
                sib_entity = self._fetch_entity_with_stats(conn, world_id, sib_row)
                sib_contents_rows = conn.execute(
                    "SELECT * FROM entities WHERE container_id = ? AND world_id = ? ORDER BY name ASC",
                    (sib_row["entity_id"], world_id),
                ).fetchall()
                sib_contents = [self._fetch_entity_with_stats(conn, world_id, r) for r in sib_contents_rows]
                adjacent_containers.append({"container": sib_entity, "contents": sib_contents})

        chain_rows = conn.execute(
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
            (container_id,),
        ).fetchall()
        container_chain = [self._fetch_entity_with_stats(conn, world_id, r) for r in chain_rows]

        return {
            "current_container": current_container,
            "contents": contents,
            "adjacent_containers": adjacent_containers,
            "container_chain": container_chain,
        }

    # ------------------------------------------------------------------
    # Query 2: Actor awareness — who knows what about scene entities
    # ------------------------------------------------------------------

    def _query_actor_awareness(
        self,
        conn: Any,
        world_id: str,
        scene: dict[str, Any],
        scene_ids: set[str],
    ) -> dict[str, Any]:
        if not scene_ids:
            return {}

        characters = [
            e for e in scene.get("contents", [])
            if e and e.get("entity_type") == "character"
        ]
        if not characters:
            return {}

        placeholders = ",".join("?" * len(scene_ids))
        result: dict[str, Any] = {}

        for char in characters:
            cid = char["entity_id"]
            rows = conn.execute(
                f"""SELECT * FROM entity_knowledge
                    WHERE world_id = ? AND entity_id = ?
                      AND knows_about_id IN ({placeholders})
                    ORDER BY updated_at DESC""",
                (world_id, cid, *scene_ids),
            ).fetchall()

            scene_knowledge = []
            for row in rows:
                target_row = conn.execute(
                    "SELECT * FROM entities WHERE entity_id = ? AND world_id = ?",
                    (row["knows_about_id"], world_id),
                ).fetchone()
                scene_knowledge.append({
                    "knows_about_id": row["knows_about_id"],
                    "degree": row["degree"],
                    "source_id": row["source_id"],
                    "entity": self._fetch_entity_with_stats(conn, world_id, target_row) if target_row else None,
                })

            result[cid] = {
                "entity": char,
                "scene_relevant_knowledge": scene_knowledge,
            }

        return result

    # ------------------------------------------------------------------
    # Query 3: Recent history — consequence records targeting scene entities
    # ------------------------------------------------------------------

    def _query_recent_history(
        self,
        conn: Any,
        world_id: str,
        scene_ids: set[str],
        limit: int,
    ) -> list[dict[str, Any]]:
        if not scene_ids:
            return []
        placeholders = ",".join("?" * len(scene_ids))
        rows = conn.execute(
            f"""SELECT * FROM consequence_records
                WHERE world_id = ? AND target_id IN ({placeholders})
                ORDER BY created_at DESC LIMIT ?""",
            (world_id, *scene_ids, limit),
        ).fetchall()
        return [self._consequence_dict_raw(r) for r in rows]

    # ------------------------------------------------------------------
    # Query 4: Open threads — unresolved consequences
    # ------------------------------------------------------------------

    def _query_open_threads(
        self,
        conn: Any,
        world_id: str,
        limit: int,
    ) -> list[dict[str, Any]]:
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
            (world_id, world_id, limit),
        ).fetchall()
        return [self._consequence_dict_raw(r) for r in rows]
