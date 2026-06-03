import os
import sqlite3
from pathlib import Path
from typing import Any


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
    """Return a Turso connection when env vars are set AND libsql_experimental
    is importable. Otherwise fall back to local SQLite at `db_path`.

    The graceful fallback exists because libsql_experimental currently has no
    Python 3.12 Windows wheel (the source build segfaults during metadata gen),
    so frozen desktop builds ship without it. Without the fallback, any
    TURSO_DATABASE_URL leaking into the env would crash the EXE on startup.

    Used by both BaseService.connect() and SessionStore in server.py so all
    DB access goes to the same backend.
    """
    turso_url = os.getenv("TURSO_DATABASE_URL", "").strip()
    turso_token = os.getenv("TURSO_AUTH_TOKEN", "").strip()
    if turso_url and turso_token:
        try:
            import libsql_experimental  # noqa: F401  — probe for importability
            return _TursoConnection(turso_url, turso_token)
        except ImportError:
            import sys
            sys.stderr.write(
                "Ayen-Ode: TURSO_DATABASE_URL is set but libsql_experimental "
                "is not installed in this build. Falling back to local SQLite.\n"
            )
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn
