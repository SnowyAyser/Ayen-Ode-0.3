"""KnowledgeQueryMixin: read-only traversal of the knowledge graph."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import loads

_DEGREE_ORDER = ["unaware", "heard_rumor", "secondhand", "witnessed", "deeply_knows"]
_VALID_DEGREES = {*_DEGREE_ORDER, "fabricated"}


class KnowledgeQueryMixin:
    """Read-only query methods for the knowledge graph."""

    def get_knowledge(self, entity_id: str, world: str | None = None) -> dict[str, Any]:
        """Return everything this entity knows, with degrees and entity snapshots."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, entity_id)
            rows = conn.execute(
                """
                SELECT ek.*, e.* FROM entity_knowledge ek
                JOIN entities e ON e.entity_id = ek.knows_about_id
                WHERE ek.world_id = ? AND ek.entity_id = ?
                ORDER BY ek.degree DESC, e.name ASC
                """,
                (wid, entity_id),
            ).fetchall()
            return {
                "world_id": wid,
                "entity_id": entity_id,
                "knowledge": [self._knowledge_row(conn, r) for r in rows],
            }

    def get_known_by(self, target_id: str, world: str | None = None) -> dict[str, Any]:
        """Return everyone who knows about this entity, with their degrees."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, target_id)
            rows = conn.execute(
                """
                SELECT ek.entity_id AS knower_id, ek.knows_about_id, ek.degree, ek.source_id,
                       e.entity_id, e.world_id, e.entity_type, e.name, e.summary, e.status,
                       e.tags_json, e.timeline_notes_json, e.open_questions_json,
                       e.metadata_json, e.container_id, e.created_at, e.updated_at
                FROM entity_knowledge ek
                JOIN entities e ON e.entity_id = ek.entity_id
                WHERE ek.world_id = ? AND ek.knows_about_id = ?
                ORDER BY ek.degree DESC
                """,
                (wid, target_id),
            ).fetchall()
            return {
                "world_id": wid,
                "target_id": target_id,
                "known_by": [
                    {
                        "entity_id": r["knower_id"],
                        "knows_about_id": r["knows_about_id"],
                        "degree": r["degree"],
                        "source_id": r["source_id"],
                        "entity": self._entity_dict(conn, r),
                    }
                    for r in rows
                ],
            }

    def get_shared_knowledge(
        self,
        entity_a: str,
        entity_b: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Return what two entities both know about, with each one's degree."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, entity_a)
            self._resolve_entity(conn, wid, entity_b)
            rows = conn.execute(
                """
                SELECT a.knows_about_id, a.degree AS degree_a, b.degree AS degree_b,
                       e.entity_id, e.world_id, e.entity_type, e.name, e.summary, e.status,
                       e.tags_json, e.timeline_notes_json, e.open_questions_json,
                       e.metadata_json, e.container_id, e.created_at, e.updated_at
                FROM entity_knowledge a
                JOIN entity_knowledge b
                  ON a.knows_about_id = b.knows_about_id
                  AND a.world_id = b.world_id
                JOIN entities e ON e.entity_id = a.knows_about_id
                WHERE a.world_id = ? AND a.entity_id = ? AND b.entity_id = ?
                ORDER BY e.name ASC
                """,
                (wid, entity_a, entity_b),
            ).fetchall()
            return {
                "world_id": wid,
                "entity_a": entity_a,
                "entity_b": entity_b,
                "shared": [
                    {
                        "knows_about_id": r["knows_about_id"],
                        "degree_a": r["degree_a"],
                        "degree_b": r["degree_b"],
                        "entity": self._entity_dict(conn, r),
                    }
                    for r in rows
                ],
            }

    def get_knowledge_by_degree(
        self,
        entity_id: str,
        degree: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Return only what this entity knows at exactly this degree."""
        if degree not in _VALID_DEGREES:
            raise ValueError(f"degree must be one of: {sorted(_VALID_DEGREES)}")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, entity_id)
            rows = conn.execute(
                """
                SELECT ek.*, e.* FROM entity_knowledge ek
                JOIN entities e ON e.entity_id = ek.knows_about_id
                WHERE ek.world_id = ? AND ek.entity_id = ? AND ek.degree = ?
                ORDER BY e.name ASC
                """,
                (wid, entity_id, degree),
            ).fetchall()
            return {
                "world_id": wid,
                "entity_id": entity_id,
                "degree": degree,
                "knowledge": [self._knowledge_row(conn, r) for r in rows],
            }

    def get_all_knowledge_links(self, world: str | None = None) -> dict[str, Any]:
        """Return every knowledge link in the world as a flat list with resolved names."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            rows = conn.execute(
                """
                SELECT
                    ek.knowledge_id, ek.entity_id AS knower_id,
                    e1.name AS knower_name, e1.entity_type AS knower_type,
                    ek.knows_about_id AS target_id,
                    e2.name AS target_name, e2.entity_type AS target_type,
                    ek.degree, ek.created_at, ek.updated_at
                FROM entity_knowledge ek
                JOIN entities e1 ON e1.entity_id = ek.entity_id
                JOIN entities e2 ON e2.entity_id = ek.knows_about_id
                WHERE ek.world_id = ?
                ORDER BY e1.name ASC, e2.name ASC
                """,
                (wid,),
            ).fetchall()
            return {"world_id": wid, "links": [{k: r[k] for k in r.keys()} for r in rows]}

    def get_knowledge_chain(
        self,
        entity_id: str,
        target_id: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Trace how knowledge of target reached entity by following source_id hops."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            self._resolve_entity(conn, wid, entity_id)
            self._resolve_entity(conn, wid, target_id)
            chain: list[dict[str, Any]] = []
            visited: set[str] = set()
            current_entity = entity_id
            while current_entity is not None and current_entity not in visited:
                visited.add(current_entity)
                row = conn.execute(
                    "SELECT * FROM entity_knowledge WHERE world_id = ? AND entity_id = ? AND knows_about_id = ?",
                    (wid, current_entity, target_id),
                ).fetchone()
                if row is None:
                    break
                chain.append({
                    "entity_id": current_entity,
                    "degree": row["degree"],
                    "source_id": row["source_id"],
                })
                current_entity = row["source_id"]
            return {
                "world_id": wid,
                "entity_id": entity_id,
                "target_id": target_id,
                "chain": chain,
            }

    def get_knowledge_events(
        self,
        world: str | None = None,
        entity_id: str | None = None,
        target_id: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Return recent knowledge events, optionally filtered."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]
            query = "SELECT * FROM knowledge_events WHERE world_id = ?"
            params: list[Any] = [wid]
            if entity_id:
                query += " AND entity_id = ?"
                params.append(entity_id)
            if target_id:
                query += " AND knows_about_id = ?"
                params.append(target_id)
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return {
                "world_id": wid,
                "events": [
                    {
                        "event_id": r["event_id"],
                        "entity_id": r["entity_id"],
                        "knows_about_id": r["knows_about_id"],
                        "event_type": r["event_type"],
                        "degree": r["degree"],
                        "source_id": r["source_id"],
                        "created_at": r["created_at"],
                    }
                    for r in rows
                ],
            }

    def _knowledge_row(self, conn: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
        """Serialize a joined entity_knowledge + entities row."""
        target = conn.execute(
            "SELECT * FROM entities WHERE entity_id = ?", (row["knows_about_id"],)
        ).fetchone()
        return {
            "knows_about_id": row["knows_about_id"],
            "degree": row["degree"],
            "source_id": row["source_id"],
            "entity": self._entity_dict(conn, target) if target else None,
        }
