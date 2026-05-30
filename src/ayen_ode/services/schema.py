"""Database schema SQL and migration helpers."""

from __future__ import annotations

import sqlite3


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS worlds (
    world_id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    premise TEXT NOT NULL,
    theme_tone TEXT NOT NULL DEFAULT '',
    player_role TEXT NOT NULL DEFAULT '',
    current_state_summary TEXT NOT NULL DEFAULT '',
    active_tensions_json TEXT NOT NULL DEFAULT '[]',
    last_system_handoff TEXT NOT NULL DEFAULT '',
    original_opening_scene TEXT NOT NULL DEFAULT '',
    game_time_seconds INTEGER NOT NULL DEFAULT 0,
    game_time_label   TEXT    NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS world_handoffs (
    handoff_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    handoff_text TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,
    name TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    tags_json TEXT NOT NULL DEFAULT '[]',
    timeline_notes_json TEXT NOT NULL DEFAULT '[]',
    open_questions_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    container_id TEXT REFERENCES entities(entity_id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entity_links (
    link_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_id_a TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    entity_id_b TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    relation TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE(world_id, entity_id_a, entity_id_b)
);

CREATE TABLE IF NOT EXISTS entity_stats (
    entity_id TEXT PRIMARY KEY REFERENCES entities(entity_id) ON DELETE CASCADE,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    stats_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stat_ledger (
    ledger_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    changes_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    source_event_id TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_log (
    sync_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_id TEXT,
    sync_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS investigation_state (
    state_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_id TEXT REFERENCES entities(entity_id) ON DELETE CASCADE,
    item_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    investigated_at TEXT
);

CREATE TABLE IF NOT EXISTS world_currencies (
    currency_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL UNIQUE REFERENCES worlds(world_id) ON DELETE CASCADE,
    currency_type TEXT NOT NULL DEFAULT 'investigation_points',
    current_balance INTEGER NOT NULL DEFAULT 5,
    max_balance INTEGER NOT NULL DEFAULT 5,
    last_regen_at TEXT NOT NULL,
    regen_rate INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS investigation_jobs (
    job_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    cost INTEGER NOT NULL DEFAULT 1,
    context TEXT,
    entity_id TEXT REFERENCES entities(entity_id) ON DELETE SET NULL,
    result_json TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS containment_events (
    event_id          TEXT PRIMARY KEY,
    world_id          TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_id         TEXT NOT NULL,
    from_container_id TEXT,
    to_container_id   TEXT,
    event_type        TEXT NOT NULL DEFAULT 'move',
    created_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS containment_hooks (
    hook_id              TEXT PRIMARY KEY,
    world_id             TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    trigger_event_type   TEXT NOT NULL,
    trigger_container_id TEXT,
    trigger_entity_id    TEXT,
    action_type          TEXT NOT NULL,
    action_params_json   TEXT NOT NULL DEFAULT '{}',
    label                TEXT NOT NULL DEFAULT '',
    created_at           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entity_knowledge (
    knowledge_id   TEXT PRIMARY KEY,
    world_id       TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_id      TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    knows_about_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    degree         TEXT NOT NULL DEFAULT 'heard_rumor',
    source_id      TEXT REFERENCES entities(entity_id) ON DELETE SET NULL,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    UNIQUE(world_id, entity_id, knows_about_id)
);

CREATE TABLE IF NOT EXISTS knowledge_events (
    event_id       TEXT PRIMARY KEY,
    world_id       TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_id      TEXT NOT NULL,
    knows_about_id TEXT NOT NULL,
    event_type     TEXT NOT NULL,
    degree         TEXT,
    source_id      TEXT,
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_hooks (
    hook_id            TEXT PRIMARY KEY,
    world_id           TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    trigger_event_type TEXT NOT NULL,
    trigger_entity_id  TEXT,
    trigger_target_id  TEXT,
    trigger_degree     TEXT,
    action_type        TEXT NOT NULL,
    action_params_json TEXT NOT NULL DEFAULT '{}',
    label              TEXT NOT NULL DEFAULT '',
    created_at         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consequence_records (
    consequence_id TEXT PRIMARY KEY,
    world_id       TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    cause_id       TEXT NOT NULL,
    effect_type    TEXT NOT NULL,
    target_id      TEXT NOT NULL,
    detail         TEXT NOT NULL DEFAULT '',
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consequence_hooks (
    hook_id             TEXT PRIMARY KEY,
    world_id            TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    trigger_effect_type TEXT,
    trigger_cause_id    TEXT,
    trigger_target_id   TEXT,
    action_type         TEXT NOT NULL,
    action_params_json  TEXT NOT NULL DEFAULT '{}',
    label               TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    last_used  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS world_quests (
    quest_id          TEXT PRIMARY KEY,
    world_id          TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    tier              INTEGER NOT NULL DEFAULT 2,
    title             TEXT NOT NULL,
    description       TEXT NOT NULL DEFAULT '',
    completion_tags_json TEXT NOT NULL DEFAULT '[]',
    progress_tags_json   TEXT NOT NULL DEFAULT '[]',
    significance_score   INTEGER NOT NULL DEFAULT 0,
    status            TEXT NOT NULL DEFAULT 'active',
    parent_quest_id   TEXT REFERENCES world_quests(quest_id),
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    completed_at      TEXT
);

CREATE TABLE IF NOT EXISTS world_debts (
    debt_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    debtor_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    creditor_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    resource_type TEXT NOT NULL,
    quantity TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    evidence TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS intake_logs (
    log_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    narrative_text TEXT NOT NULL,
    thought_process TEXT NOT NULL,
    tools_attempted_json TEXT NOT NULL,
    tools_executed_json TEXT NOT NULL,
    game_time_label TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pregenerated_investigations (
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (world_id, entity_name)
);
"""


def run_migrations(conn: sqlite3.Connection) -> None:
    entity_cols = {row[1] for row in conn.execute("PRAGMA table_info(entities)").fetchall()}
    if "container_id" not in entity_cols:
        conn.execute("ALTER TABLE entities ADD COLUMN container_id TEXT REFERENCES entities(entity_id)")
    for tbl in ["spatial_placements", "spatial_relationships"]:
        try:
            conn.execute(f"DROP TABLE IF EXISTS {tbl}")
        except Exception:
            pass
    world_cols = {row[1] for row in conn.execute("PRAGMA table_info(worlds)").fetchall()}
    if "game_time_seconds" not in world_cols:
        conn.execute("ALTER TABLE worlds ADD COLUMN game_time_seconds INTEGER NOT NULL DEFAULT 0")
    if "game_time_label" not in world_cols:
        conn.execute("ALTER TABLE worlds ADD COLUMN game_time_label TEXT NOT NULL DEFAULT ''")
    if "narrative_turn_count" not in world_cols:
        conn.execute("ALTER TABLE worlds ADD COLUMN narrative_turn_count INTEGER NOT NULL DEFAULT 0")
    if "original_opening_scene" not in world_cols:
        conn.execute("ALTER TABLE worlds ADD COLUMN original_opening_scene TEXT NOT NULL DEFAULT ''")
        # Backfill original_opening_scene from the oldest handoff for existing worlds
        conn.execute(
            """
            UPDATE worlds
            SET original_opening_scene = COALESCE(
                (
                    SELECT handoff_text
                    FROM world_handoffs
                    WHERE world_handoffs.world_id = worlds.world_id
                    ORDER BY created_at ASC
                    LIMIT 1
                ),
                ''
            )
            WHERE original_opening_scene = ''
            """
        )

    job_cols = {row[1] for row in conn.execute("PRAGMA table_info(investigation_jobs)").fetchall()}
    if "cost" not in job_cols:
        conn.execute("ALTER TABLE investigation_jobs ADD COLUMN cost INTEGER NOT NULL DEFAULT 1")
    if "context" not in job_cols:
        conn.execute("ALTER TABLE investigation_jobs ADD COLUMN context TEXT")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pregenerated_investigations (
            world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
            entity_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (world_id, entity_name)
        );
        """
    )
