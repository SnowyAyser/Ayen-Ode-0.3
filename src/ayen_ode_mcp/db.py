import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path("data/ayen_ode.db")


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def tx(conn):
    try:
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db(conn):
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS worlds (
    world_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    premise TEXT NOT NULL,
    theme_tone TEXT,
    player_role TEXT,
    current_state_summary TEXT,
    active_tensions TEXT DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_world ON worlds ((status='active')) WHERE status='active';

CREATE TABLE IF NOT EXISTS world_handoffs (
    world_id INTEGER PRIMARY KEY,
    handoff TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(world_id) REFERENCES worlds(world_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS entities (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    world_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    name TEXT NOT NULL,
    summary TEXT,
    status TEXT DEFAULT 'active',
    tags TEXT DEFAULT '[]',
    linked_entity_ids TEXT DEFAULT '[]',
    timeline_notes TEXT DEFAULT '[]',
    open_questions TEXT DEFAULT '[]',
    payload TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(world_id) REFERENCES worlds(world_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS entity_links (
    world_id INTEGER NOT NULL,
    a_entity_id INTEGER NOT NULL,
    b_entity_id INTEGER NOT NULL,
    relation TEXT DEFAULT 'linked',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(world_id, a_entity_id, b_entity_id)
);
CREATE TABLE IF NOT EXISTS entity_stats (
    world_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    stats_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(world_id, entity_id)
);
CREATE TABLE IF NOT EXISTS sync_log (
    sync_id INTEGER PRIMARY KEY AUTOINCREMENT,
    world_id INTEGER NOT NULL,
    entity_id INTEGER,
    sync_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""
    )
