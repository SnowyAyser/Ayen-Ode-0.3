"""EntitiesMixin: entity CRUD, linking, and comparison."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import (
    VALID_ENTITY_TYPES,
    dumps,
    loads,
    make_id,
    normalize_list,
    utc_now,
)


class EntitiesMixin:
    """Entity CRUD, linking, comparison. Stats read via get_entity_stats (StatsMixin)."""

    # --- Queries ---

    def list_entities(
        self,
        world: str | None = None,
        entity_type: str | None = None,
        include_archived: bool = False,
    ) -> dict[str, Any]:
        if entity_type and entity_type not in VALID_ENTITY_TYPES:
            raise ValueError(f"Unsupported entity_type: {entity_type}")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            query = "SELECT * FROM entities WHERE world_id = ?"
            params: list[Any] = [world_row["world_id"]]
            if entity_type:
                query += " AND entity_type = ?"
                params.append(entity_type)
            if not include_archived:
                query += " AND status != 'archived'"
            query += " ORDER BY name ASC"
            rows = conn.execute(query, params).fetchall()
            return {
                "world": self._world_dict(world_row),
                "entities": [self._entity_dict(conn, row) for row in rows],
            }

    def get_entity(self, entity_id: str, world: str | None = None) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            entity = self._resolve_entity(conn, world_row["world_id"], entity_id)
            return {
                "world": self._world_dict(world_row),
                "entity": self._entity_dict(conn, entity),
            }

    # --- Mutations ---

    def create_entity(
        self,
        name: str,
        entity_type: str,
        summary: str = "",
        world: str | None = None,
        status: str = "active",
        tags: list[str] | None = None,
        timeline_notes: list[str] | None = None,
        open_questions: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        stats: dict[str, int] | None = None,
        container_id: str | None = None,
    ) -> dict[str, Any]:
        if entity_type not in VALID_ENTITY_TYPES:
            raise ValueError(f"Unsupported entity_type: {entity_type}")
        if not name.strip():
            raise ValueError("Entity name is required.")
        normalized_stats = self._normalize_stats(entity_type, stats or {})
        now = utc_now()
        entity_id = make_id("entity")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            clean_name = name.strip()
            variants = [clean_name]
            if clean_name.lower().endswith("s"):
                if clean_name.lower().endswith("es"):
                    variants.append(clean_name[:-2])
                variants.append(clean_name[:-1])
            else:
                variants.append(clean_name + "s")
                variants.append(clean_name + "es")

            existing = None
            for var in variants:
                existing = conn.execute(
                    "SELECT * FROM entities WHERE world_id = ? AND LOWER(name) = LOWER(?)",
                    (world_row["world_id"], var),
                ).fetchone()
                if existing:
                    break

            if existing:
                return {
                    "world": self._world_dict(world_row),
                    "entity": self._entity_dict(conn, existing),
                    "stats": self._entity_stats(conn, existing["entity_id"]),
                }
            conn.execute(
                """
                INSERT INTO entities (
                    entity_id, world_id, entity_type, name, summary, status, tags_json,
                    timeline_notes_json, open_questions_json, metadata_json, container_id,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity_id,
                    world_row["world_id"],
                    entity_type,
                    name.strip(),
                    summary.strip(),
                    status.strip() or "active",
                    dumps(normalize_list(tags)),
                    dumps(normalize_list(timeline_notes)),
                    dumps(normalize_list(open_questions)),
                    dumps(metadata or {}),
                    container_id,
                    now,
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO entity_stats (entity_id, world_id, stats_json, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (entity_id, world_row["world_id"], dumps(normalized_stats), now),
            )
            entity = self._resolve_entity(conn, world_row["world_id"], entity_id)
            return {
                "world": self._world_dict(world_row),
                "entity": self._entity_dict(conn, entity),
                "stats": normalized_stats,
            }

    def update_entity(
        self,
        entity_id: str,
        world: str | None = None,
        name: str | None = None,
        summary: str | None = None,
        status: str | None = None,
        tags: list[str] | None = None,
        timeline_notes: list[str] | None = None,
        open_questions: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        stats: dict[str, int] | None = None,
        container_id: str | None = None,
    ) -> dict[str, Any]:
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            entity = self._resolve_entity(conn, world_row["world_id"], entity_id)
            updates: list[str] = ["updated_at = ?"]
            params: list[Any] = [now]
            if name is not None:
                if not name.strip():
                    raise ValueError("Entity name cannot be blank.")
                updates.append("name = ?")
                params.append(name.strip())
            if summary is not None:
                updates.append("summary = ?")
                params.append(summary.strip())
            if status is not None:
                updates.append("status = ?")
                params.append(status.strip())
            if tags is not None:
                updates.append("tags_json = ?")
                params.append(dumps(normalize_list(tags)))
            if timeline_notes is not None:
                updates.append("timeline_notes_json = ?")
                params.append(dumps(normalize_list(timeline_notes)))
            if open_questions is not None:
                updates.append("open_questions_json = ?")
                params.append(dumps(normalize_list(open_questions)))
            if metadata is not None:
                updates.append("metadata_json = ?")
                params.append(dumps(metadata))
            if container_id is not None:
                updates.append("container_id = ?")
                params.append(container_id)
            params.append(entity["entity_id"])
            conn.execute(f"UPDATE entities SET {', '.join(updates)} WHERE entity_id = ?", params)

            if stats is not None:
                normalized_stats = self._normalize_stats(entity["entity_type"], stats)
                conn.execute(
                    "UPDATE entity_stats SET stats_json = ?, updated_at = ? WHERE entity_id = ?",
                    (dumps(normalized_stats), now, entity["entity_id"]),
                )

            updated = self._resolve_entity(conn, world_row["world_id"], entity_id)
            return {
                "world": self._world_dict(world_row),
                "entity": self._entity_dict(conn, updated),
                "stats": self._entity_stats(conn, updated["entity_id"]),
            }

    # --- Relations ---

    def link_entities(
        self,
        entity_id_a: str,
        entity_id_b: str,
        world: str | None = None,
        relation: str = "",
    ) -> dict[str, Any]:
        if entity_id_a == entity_id_b:
            raise ValueError("Cannot link an entity to itself.")
        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            a = self._resolve_entity(conn, world_row["world_id"], entity_id_a)
            b = self._resolve_entity(conn, world_row["world_id"], entity_id_b)
            left, right = sorted([a["entity_id"], b["entity_id"]])
            conn.execute(
                """
                INSERT OR IGNORE INTO entity_links (
                    link_id, world_id, entity_id_a, entity_id_b, relation, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (make_id("link"), world_row["world_id"], left, right, relation.strip(), now),
            )
            return {
                "world": self._world_dict(world_row),
                "linked_entity_ids": [a["entity_id"], b["entity_id"]],
                "relation": relation.strip(),
            }

    def compare_entities(
        self,
        entity_id_a: str,
        entity_id_b: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            a = self._resolve_entity(conn, world_row["world_id"], entity_id_a)
            b = self._resolve_entity(conn, world_row["world_id"], entity_id_b)
            stats_a = self._entity_stats(conn, a["entity_id"])
            stats_b = self._entity_stats(conn, b["entity_id"])
            keys = sorted(set(stats_a) | set(stats_b))
            differences = []
            for key in keys:
                value_a = stats_a.get(key)
                value_b = stats_b.get(key)
                if value_a is None or value_b is None:
                    relation = "missing"
                    delta = None
                else:
                    delta = value_a - value_b
                    relation = "equal" if delta == 0 else ("a_higher" if delta > 0 else "b_higher")
                differences.append(
                    {
                        "stat": key,
                        "entity_a_value": value_a,
                        "entity_b_value": value_b,
                        "delta_a_minus_b": delta,
                        "relation": relation,
                    }
                )
            return {
                "world": self._world_dict(world_row),
                "entity_a": self._entity_dict(conn, a),
                "entity_b": self._entity_dict(conn, b),
                "differences": differences,
                "exact_values_visible": True,
            }
