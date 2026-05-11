"""BaseService: DB initialization, connection manager, and shared private helpers."""

from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import re
import sqlite3
import uuid

from .schema import _SCHEMA_SQL, run_migrations


# ---------------------------------------------------------------------------
# Turso / libSQL remote connection support
# ---------------------------------------------------------------------------

class _DictRow:
    """Row object supporting both named-key and integer-index access.

    libsql_experimental returns plain tuples; this wrapper makes them
    behave like sqlite3.Row so the rest of the codebase needs no changes.
    """
    __slots__ = ("_keys", "_values", "_map")

    def __init__(self, keys: list[str], values: tuple) -> None:
        self._keys = keys
        self._values = tuple(values)
        self._map: dict[str, Any] = dict(zip(keys, values))

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, int):
            return self._values[key]
        return self._map[key]

    def __iter__(self):
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __bool__(self) -> bool:
        return True  # a fetched row always exists

    def keys(self) -> list[str]:
        return self._keys


class _WrappedCursor:
    """Cursor wrapper that converts libsql rows into _DictRow objects."""

    def __init__(self, cursor: Any) -> None:
        self._cur = cursor
        # Capture description immediately — some drivers clear it after fetch
        self._desc = cursor.description

    @property
    def description(self) -> Any:
        return self._desc

    def _wrap(self, row: Any) -> Any:
        if row is None or self._desc is None:
            return row
        keys = [d[0] for d in self._desc]
        return _DictRow(keys, row)

    def fetchone(self) -> Any:
        return self._wrap(self._cur.fetchone())

    def fetchall(self) -> list:
        rows = self._cur.fetchall()
        if self._desc is None:
            return rows
        keys = [d[0] for d in self._desc]
        return [_DictRow(keys, r) for r in rows]


class _TursoConnection:
    """sqlite3-compatible wrapper around a libsql_experimental remote connection."""

    def __init__(self, url: str, token: str) -> None:
        import libsql_experimental as libsql  # type: ignore[import]
        self._conn = libsql.connect(url, auth_token=token)

    def execute(self, sql: str, params: Any = ()) -> _WrappedCursor:
        cur = self._conn.execute(sql, params)
        return _WrappedCursor(cur)

    def executemany(self, sql: str, params: Any) -> None:
        self._conn.executemany(sql, params)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        try:
            self._conn.rollback()
        except Exception:
            pass

    def close(self) -> None:
        self._conn.close()


def make_db_connection(db_path: Path) -> Any:
    """Return a Turso connection when env vars are set, otherwise local SQLite.

    Used by both BaseService.connect() and SessionStore in server.py so that
    all DB access goes to the same backend.
    """
    turso_url = os.getenv("TURSO_DATABASE_URL", "").strip()
    turso_token = os.getenv("TURSO_AUTH_TOKEN", "").strip()
    if turso_url and turso_token:
        return _TursoConnection(turso_url, turso_token)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

VALID_WORLD_STATUSES = {"active", "paused", "archived", "draft"}
VALID_ENTITY_TYPES = {"character", "faction", "location", "object", "event"}

STAT_NAMES_BY_ENTITY_TYPE: dict[str, set[str]] = {
    "character": {"force", "influence", "will", "perception", "resilience", "volatility"},
    "faction": {"power", "cohesion", "reach", "resources", "secrecy", "instability"},
    "location": {"security", "prosperity", "corruption", "danger", "stability", "mystique"},
    "object": {"potency", "rarity", "durability", "risk", "control", "significance"},
    "event": {"scale", "urgency", "fallout", "visibility", "disruption", "momentum"},
}


# ---------------------------------------------------------------------------
# Module-level utility functions
# ---------------------------------------------------------------------------

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "world"


def clamp_stat(value: int) -> int:
    return max(0, min(100, int(value)))


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def loads(value: str | None, fallback: Any) -> Any:
    if value is None or value == "":
        return fallback
    return json.loads(value)


def normalize_list(value: list[Any] | None) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Expected a list value.")
    return value


# ---------------------------------------------------------------------------
# BaseService
# ---------------------------------------------------------------------------

class BaseService:
    """DB initialization, connection manager, and private helpers shared by all mixins."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path).resolve()
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[Any]:
        conn = make_db_connection(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            # Execute each DDL statement individually — compatible with both
            # local SQLite and remote Turso (which may not support executescript).
            for stmt in [s.strip() for s in _SCHEMA_SQL.split(";") if s.strip()]:
                conn.execute(stmt)
            run_migrations(conn)

    # -----------------------------------------------------------------------
    # Private helpers — shared across all domain mixins via MRO
    # -----------------------------------------------------------------------

    def _unique_slug(self, conn: sqlite3.Connection, name: str) -> str:
        base = slugify(name)
        candidate = base
        suffix = 2
        while conn.execute("SELECT 1 FROM worlds WHERE slug = ?", (candidate,)).fetchone():
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    def _active_world_row(self, conn: sqlite3.Connection) -> sqlite3.Row | None:
        return conn.execute("SELECT * FROM worlds WHERE status = 'active' LIMIT 1").fetchone()

    def _require_active_world(self, conn: sqlite3.Connection) -> sqlite3.Row:
        row = self._active_world_row(conn)
        if not row:
            raise ValueError("No active world exists yet. Create or switch to a world first.")
        return row

    def _get_world_row(self, conn: sqlite3.Connection, world_id: str) -> sqlite3.Row:
        row = conn.execute("SELECT * FROM worlds WHERE world_id = ?", (world_id,)).fetchone()
        if not row:
            raise ValueError(f"World not found: {world_id}")
        return row

    def _resolve_world(self, conn: sqlite3.Connection, world: str | None) -> sqlite3.Row:
        if not world:
            return self._require_active_world(conn)
        row = conn.execute(
            "SELECT * FROM worlds WHERE world_id = ? OR slug = ?",
            (world, world),
        ).fetchone()
        if not row:
            raise ValueError(f"World not found: {world}")
        return row

    def _resolve_entity(self, conn: sqlite3.Connection, world_id: str, entity_id: str) -> sqlite3.Row:
        row = conn.execute(
            "SELECT * FROM entities WHERE world_id = ? AND entity_id = ?",
            (world_id, entity_id),
        ).fetchone()
        if not row:
            raise ValueError("Entity not found in the selected world.")
        return row

    def _entity_stats(self, conn: sqlite3.Connection, entity_id: str) -> dict[str, int]:
        row = conn.execute("SELECT stats_json FROM entity_stats WHERE entity_id = ?", (entity_id,)).fetchone()
        return loads(row["stats_json"], {}) if row else {}

    def _linked_entity_ids(self, conn: sqlite3.Connection, world_id: str, entity_id: str) -> list[str]:
        rows = conn.execute(
            """
            SELECT entity_id_a, entity_id_b
            FROM entity_links
            WHERE world_id = ? AND (entity_id_a = ? OR entity_id_b = ?)
            ORDER BY created_at ASC
            """,
            (world_id, entity_id, entity_id),
        ).fetchall()
        linked = []
        for row in rows:
            linked.append(row["entity_id_b"] if row["entity_id_a"] == entity_id else row["entity_id_a"])
        return linked

    def _world_dict(self, row: sqlite3.Row | Mapping[str, Any] | None) -> dict[str, Any] | None:
        """Serialize a worlds table row to a public-facing dict."""
        if row is None:
            return None
        return {
            "world_id": row["world_id"],
            "slug": row["slug"],
            "name": row["name"],
            "status": row["status"],
            "premise": row["premise"],
            "theme_tone": row["theme_tone"],
            "player_role": row["player_role"],
            "current_state_summary": row["current_state_summary"],
            "active_tensions": loads(row["active_tensions_json"], []),
            "last_system_handoff": row["last_system_handoff"],
            "game_time_seconds": row["game_time_seconds"],
            "game_time_label": row["game_time_label"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _entity_dict(self, conn: Any, row: Any) -> dict[str, Any]:
        """Serialize an entities table row to a public-facing dict.

        Fetches linked_entity_ids in the same connection to avoid extra round-trips.
        """
        return {
            "entity_id": row["entity_id"],
            "world_id": row["world_id"],
            "entity_type": row["entity_type"],
            "name": row["name"],
            "summary": row["summary"],
            "status": row["status"],
            "tags": loads(row["tags_json"], []),
            "timeline_notes": loads(row["timeline_notes_json"], []),
            "open_questions": loads(row["open_questions_json"], []),
            "metadata": loads(row["metadata_json"], {}),
            "container_id": row["container_id"],
            "linked_entity_ids": self._linked_entity_ids(conn, row["world_id"], row["entity_id"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _normalize_stats(self, entity_type: str, stats: dict[str, Any]) -> dict[str, int]:
        """Filter a stats dict to valid names for entity_type and clamp values 0-100."""
        valid = STAT_NAMES_BY_ENTITY_TYPE.get(entity_type, set())
        return {k: clamp_stat(int(v)) for k, v in stats.items() if k in valid}

    def _normalize_stat_deltas(self, entity_type: str, deltas: dict[str, Any]) -> dict[str, int]:
        """Filter stat deltas to valid names for entity_type. Values are signed, not clamped."""
        valid = STAT_NAMES_BY_ENTITY_TYPE.get(entity_type, set())
        return {k: int(v) for k, v in deltas.items() if k in valid}

    def _reconciliation_suggestions(
        self,
        conn: Any,
        world_id: str,
        source: Any,
        deltas: dict[str, int],
    ) -> list[dict[str, Any]]:
        """Suggest proportional stat adjustments for entities linked to source.

        Each linked entity receives a suggestion of half the source delta for any
        stat name that is also valid for the linked entity's type. Entities with no
        overlapping stats produce an empty suggested_deltas entry (included so the
        caller can enumerate all linked entities uniformly).
        """
        linked_ids = self._linked_entity_ids(conn, world_id, source["entity_id"])
        suggestions: list[dict[str, Any]] = []
        for eid in linked_ids:
            linked_row = conn.execute(
                "SELECT entity_id, entity_type, name FROM entities WHERE entity_id = ?",
                (eid,),
            ).fetchone()
            if not linked_row:
                continue
            valid = STAT_NAMES_BY_ENTITY_TYPE.get(linked_row["entity_type"], set())
            suggested: dict[str, int] = {}
            for stat, delta in deltas.items():
                if stat in valid:
                    half = delta // 2
                    if half != 0:
                        suggested[stat] = half
            suggestions.append({
                "entity_id": linked_row["entity_id"],
                "entity_name": linked_row["name"],
                "entity_type": linked_row["entity_type"],
                "suggested_deltas": suggested,
            })
        return suggestions
