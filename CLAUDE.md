# CLAUDE.md — Ayen-Ode Project Navigation

> **AI ASSISTANTS: Read this document before working in this codebase.**
> After making any structural or significant code changes, **update this file** to keep it accurate.
> Future AI sessions depend on this document being current.

---

## What This Project Is

Ayen-Ode is a narrative RPG engine. It manages deterministic game state —
worlds, entities, hidden stats, a containment tree, and investigation jobs —
so the AI storyteller can focus on narrative while the server enforces rules
and consistency. Narration is driven by the Anthropic Claude API.

- **Backend**: Python 3.11+, Starlette, SQLite (local) or Turso/libSQL (cloud)
- **Frontend**: Static HTML/JS served by the same process
- **Deployment**: Render.com (see `render.yaml`)
- **Version**: 0.3.2

---

## Read This First

- **Project location must NOT be inside OneDrive / iCloud / Dropbox / Google Drive.** Sync corrupts `.venv` and SQLite. Use `C:\dev\` or `~/dev/`. The setup script refuses to run inside synced folders.
- The **database** is the authoritative source for all live game state. By default this is `data/ayen_ode.db` (local SQLite). When `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` are set in `.env`, all reads/writes go to Turso instead — the local file is ignored.
- `world/` contains human-readable lore reference files — these do **not** drive the server.
- `worlds/` (different!) holds per-world campaign operational files.
- `server.py` is the HTTP layer. It delegates all logic to `AyenOdeService` from `service.py`.
- `service.py` is a one-line re-export shim — the real implementation is in `services/`.
- Always run `pytest tests/` before and after changes to the service layer.
- The quest system (`world_quests` table, `QuestsMixin`, `quests.py`) tracks layered narrative goals. Tier 1 is generated at world creation; Tier 2/3 are detected every 3 narrative turns by a Haiku scan.

---

## Directory Structure

```
Ayen-Ode-0.3/
│
├── src/ayen_ode/               # Python package — the running server
│   ├── __init__.py                 # Package version string
│   ├── __main__.py                 # Entry point: python -m ayen_ode
│   ├── config.py                   # Settings (env vars) + Anthropic client init; SONNET_MODEL + HAIKU_MODEL constants
│   ├── server.py                   # App setup: SessionStore, AuthMiddleware, investigation worker, main()
│   ├── narrative.py                # Claude API driver: world init, action processing, investigation; imports intake + quests
│   ├── intake.py                   # Post-narration intake pass: _run_intake_pass() + tool schemas (incl. mark_quest_progress)
│   ├── quests.py                   # Quest goal detection: generate_overarching_goal() + scan_for_goals() — Haiku calls
│   ├── context_assembler.py        # Thin orchestrator: ContextAssembler(PlayerQueryMixin) — __init__, assemble(), to_prompt_text()
│   ├── context_scene_queries.py    # SceneQueryMixin: queries 1–4 (scene, actor awareness, recent history, open threads)
│   ├── context_player_queries.py   # PlayerQueryMixin(SceneQueryMixin): queries 5–9 (player state, histories, journey, bleed-in)
│   ├── service.py                  # Re-export shim → from .services import AyenOdeService
│   ├── settings_window.py          # Native tkinter settings UI: edits .env fields (API key, username, password, port)
│   ├── routes/                     # HTTP route handlers split by domain
│   │   ├── __init__.py             # make_all_routes() — assembles all route lists from sub-modules
│   │   ├── auth.py                 # health, static page serves, whoami, login, logout; _client_ip() helper
│   │   ├── worlds.py               # World CRUD, init, switch, reset, delete, currency handlers
│   │   ├── entities.py             # Entity CRUD, stats, linking handlers
│   │   ├── containment.py          # Containment tree, move, hooks, events handlers
│   │   ├── knowledge.py            # Knowledge graph, hooks, events handlers
│   │   └── consequence.py          # Consequence, hooks, investigation, narrative action, context-packet handlers
│       └── quests.py               # Quest routes: GET /quests, POST /promote, /dismiss, /check
│   ├── narrative_utils.py              # Parsing helpers: parse_investigation_response, sanitize_entity_details
│   └── services/                   # Domain-split service modules (see Services Layer below)
│       ├── quests.py               # QuestsMixin: create/read/progress/complete/dismiss world_quests rows
│       ├── __init__.py             # Assembles AyenOdeService from mixins
│       ├── base.py                 # BaseService: connect(), initialize(), shared private helpers; imports schema
│       ├── schema.py               # _SCHEMA_SQL DDL constant + run_migrations(conn) — extracted from base.py
│       ├── hook_actions.py         # execute_shared_hook_action(): stat_change, log_note, flag_entity branches
│       ├── worlds.py               # WorldsMixin: world CRUD, handoffs, archive, reset, time tracking
│       ├── entities.py             # EntitiesMixin: entity CRUD, linking, comparison
│       ├── stats.py                # StatsMixin: stat reads, apply_stat_change, reconciliation
│       ├── containment.py          # ContainmentMixin: containment tree, move, hooks, events
│       ├── knowledge_queries.py    # KnowledgeQueryMixin: all read-only knowledge query methods (JOIN-based, no N+1)
│       ├── knowledge.py            # KnowledgeMixin(KnowledgeQueryMixin): learn, spread, forget, hooks
│       ├── consequence_queries.py  # ConsequenceQueryMixin: all read-only consequence query methods
│       ├── consequence.py          # ConsequenceMixin(ConsequenceQueryMixin): record, hooks, chain traversal
│       ├── investigation.py        # InvestigationMixin: jobs, state history, points currency
│       └── sync.py                 # SyncMixin: canon sync log, world summary sync
│
├── tests/
│   ├── test_state_service.py       # Unit tests: world switching, stat changes, reconciliation
│   ├── test_containment.py         # Unit tests: containment tree, move, hooks, circular detection
│   ├── test_knowledge.py           # Unit tests: knowledge graph, spread, degree, chain, hooks
│   ├── test_consequence.py         # Unit tests: causal chain, forward/backward traversal, cross-system hooks
│   └── test_context_assembler.py   # Unit tests: context packet assembly, compression, filtering
│
├── static/                         # Browser UI files served by the server at /
│   ├── index.html                  # Login page (API key input)
│   ├── dashboard.html              # World management dashboard
│   ├── narrative.html              # In-game narrative play UI (HTML only; JS in narrative*.js files)
│   ├── narrative.js                # State vars, storage, world load, entity render, form submit, bootstrap
│   ├── narrative-investigation.js  # Investigation panel, polling, queue, timer, points display
│   ├── narrative-entity.js         # Entity detail panel, compendium list, entity link detection
│   ├── narrative-worlds.js         # World switcher modal
│   ├── narrative-quests.js         # Quest panel: load, render, promote/dismiss threads, check progress
│   ├── debug.html                  # Dev debug panel HTML shell (JS in debug*.js files)
│   ├── debug.js                    # State, api wrapper, badge helpers, tab switcher, polling, live feed, init
│   ├── debug-panels.js             # Entity inspector, containment tree, knowledge table, consequence list renderers
│   ├── app.js                      # Shared auth + API fetch wrapper (loaded first on every page)
│   ├── clover-loader.html          # Animated loading screen (standalone page)
│   └── clover-loader.js            # Clover trail animation script
│
├── world/                          # Human-readable lore content (NOT live state)
│   ├── README.md                   # Explains world/ vs worlds/ distinction
│   ├── stat-framework.md           # Stat model definitions (6 stats per entity type, 0–100)
│   ├── stat-ledger.md              # Human-readable stat change snapshot
│   ├── reference-map.md            # Entity relationship reference map
│   ├── story-framework.md          # Active campaign control sheet
│   ├── characters/                 # Character reference files
│   ├── factions/                   # Faction reference files
│   ├── locations/                  # Location reference files
│   ├── objects/                    # Object reference files
│   └── events/                     # Event reference files
│
├── worlds/                         # Per-world operational files (one folder per world slug)
│   └── README.md                   # Conventions for world folders
│
├── docs/                           # Technical documentation
│   ├── DATA_MODEL.md               # Database schema reference (13 tables)
│   ├── ACTIONS.md                  # Endpoint/action reference
│   └── DEPLOYMENT.md               # Render.com deployment guide
│
├── data/                           # SQLite database files (gitignored)
│   └── ayen_ode.db                 # Live game state
│
├── examples/
│   └── local-tool-flow.md          # Example local tool invocation flow
│
├── world-registry.md               # Human-readable world registry (server is authoritative)
├── .env.example                    # Template for required environment variables
├── pyproject.toml                  # Package config, dependencies, pytest config
├── render.yaml                     # Render.com deployment descriptor
├── README.md                       # Quickstart + troubleshooting
└── scripts/                        # setup.ps1 (Windows) + setup.sh (POSIX)
```

---

## Services Layer

`AyenOdeService` is assembled from mixin classes. Each mixin handles one domain.
All private helpers (`_resolve_world`, `_entity_stats`, `connect()`, etc.) live in `BaseService`
and are accessible on `self` throughout all mixins via Python's MRO.

| Domain | File | Key Public Methods |
|--------|------|--------------------|
| Worlds | `services/worlds.py` | `list_worlds`, `create_world`, `switch_world`, `archive_world`, `delete_world`, `reset_world`, `save_world_handoff`, `get_world_handoff`, `get_world_time`, `advance_world_time` |
| Entities | `services/entities.py` | `list_entities`, `get_entity`, `create_entity`, `update_entity`, `link_entities`, `compare_entities` |
| Stats | `services/stats.py` | `get_entity_stats`, `apply_stat_change`, `reconcile_linked_stats` |
| Containment | `services/containment.py` | `get_contents`, `get_contents_recursive`, `get_container_chain`, `get_siblings`, `move`, `register_containment_hook`, `list_containment_hooks`, `remove_containment_hook`, `get_containment_events` |
| Knowledge Queries | `services/knowledge_queries.py` | `get_knowledge`, `get_known_by`, `get_shared_knowledge`, `get_knowledge_by_degree`, `get_all_knowledge_links`, `get_knowledge_chain` — read-only; all JOIN-based (no N+1) |
| Knowledge | `services/knowledge.py` | `learn`, `spread`, `forget`, `update_degree`, `register_knowledge_hook`, `list_knowledge_hooks`, `remove_knowledge_hook`, `get_knowledge_events` — `KnowledgeMixin(KnowledgeQueryMixin)` |
| Consequence Queries | `services/consequence_queries.py` | `get_effects`, `get_causes`, `get_chain_forward`, `get_chain_backward`, `get_history`, `get_state_at`, `get_consequence_events`, `get_unresolved_threads` — read-only |
| Consequence | `services/consequence.py` | `record_consequence`, `record_chain`, `register_consequence_hook`, `list_consequence_hooks`, `remove_consequence_hook` — `ConsequenceMixin(ConsequenceQueryMixin)` |
| Investigation | `services/investigation.py` | `initialize_world_currency`, `get_investigation_balance`, `spend_investigation_points`, `create_investigation_job`, `complete_investigation_job`, `get_investigation_queue` |
| Sync | `services/sync.py` | `sync_canon_record`, `sync_world_summary` |
| Quests | `services/quests.py` | `create_quest`, `get_quest`, `list_quests`, `mark_quest_tag`, `complete_quest`, `dismiss_quest`, `promote_quest`, `check_quest_progress`, `get_active_quests_summary`, `increment_world_turn_count` |
| Base | `services/base.py` | `__init__`, `connect()`, `initialize()`, `_resolve_world`, `_resolve_entity`, `_entity_stats`, `_world_dict`, `_entity_dict`, `_normalize_stats` |
| Schema | `services/schema.py` | `_SCHEMA_SQL` (DDL constant), `run_migrations(conn)` — imported by `base.py`; not part of public API |
| Hook Actions | `services/hook_actions.py` | `execute_shared_hook_action(conn, world_id, hook, default_entity_id, service)` — shared executor for `stat_change`, `log_note`, `flag_entity` hook action types |

---

## Key Architecture Facts

```
HTTP request
    │
    â–¼
server.py (app setup: SessionStore, AuthMiddleware, worker, main)
    │  routes assembled by make_all_routes() from routes/ package
    â–¼
routes/
    ├── auth.py        (health, static serves, login/logout, _client_ip)
    ├── worlds.py      (world CRUD, init, switch, reset)
    ├── entities.py    (entity CRUD, stats, linking)
    ├── containment.py (tree, move, hooks, events)
    ├── knowledge.py   (graph, hooks, events)
    └── consequence.py (records, hooks, investigate, narrative action, context-packet)
    │  all import AyenOdeService from service.py
    â–¼
service.py (re-export shim)
    │  from .services import AyenOdeService
    â–¼
services/__init__.py (assembles class from mixins)
    │
    ├── WorldsMixin        (worlds.py)
    ├── EntitiesMixin      (entities.py)
    ├── StatsMixin         (stats.py)
    ├── ContainmentMixin   (containment.py) â† delegates shared hook actions to hook_actions.py
    ├── KnowledgeMixin     (knowledge.py)   â† inherits KnowledgeQueryMixin (knowledge_queries.py)
    ├── ConsequenceMixin   (consequence.py) â† inherits ConsequenceQueryMixin (consequence_queries.py)
    ├── InvestigationMixin (investigation.py)
    ├── SyncMixin          (sync.py)
    └── BaseService        (base.py) ← DB init, helpers; DDL in schema.py
            │
            ▼
        make_db_connection() — returns _TursoConnection (remote) or sqlite3 (local)
            │
            ├── Turso (libsql://ayen-ode-zgreiniman.aws-eu-west-1.turso.io)
            │       when TURSO_DATABASE_URL + TURSO_AUTH_TOKEN are set in .env
            └── SQLite (data/ayen_ode.db)
                    fallback when Turso env vars are absent
```

**narrative.py** runs separately — it calls the Claude API (claude-sonnet-4-6) and then calls back
into `service` to persist entity data. The background investigation worker thread is started in
`server.py` and also calls `narrative.investigate_entity()`. The worker uses an atomic
`UPDATE...WHERE...subquery` to claim jobs (no race condition) and sleeps outside the connection block.

**Context assembly**: Before every narrative call in `process_user_action()`, `ContextAssembler`
(`context_assembler.py`) runs 9 queries in a single DB transaction and returns a structured
world-state packet. The assembler class inherits `PlayerQueryMixin` (from `context_player_queries.py`)
which inherits `SceneQueryMixin` (from `context_scene_queries.py`). Queries 1–4 live in
`SceneQueryMixin`: scene, actor awareness, recent history, open threads. Queries 5–9 live in
`PlayerQueryMixin`: player state, entity histories, player journey, relationship histories, world bleed-in.
When `player_entity_id` is None the assembler is skipped and the legacy handoff-based context
is used as fallback.

**Post-narration intake**: After Claude narrates, `_run_intake_pass()` (in `intake.py`) makes a
second call with `claude-haiku-4-5-20251001` to extract concrete state changes (consequences,
knowledge, moves, and time advancement) from the narration text and write them to the DB.
The intake model always calls `advance_time(seconds, label)` to accumulate in-game time.
Intake failures are always silent.

**In-game time**: Each world tracks `game_time_seconds` (cumulative, since world creation) and
`game_time_label` (Claude's human-readable current-time string, e.g. "Late afternoon, Day 3").
The intake pass advances both after every narrative turn. The narrative response JSON always
includes `game_time: {seconds, label}`. The client shows the label above the input form.
`POST /api/worlds/{world_id}/skip-time` advances time manually but blocks if there are active
investigation jobs or open consequence threads.

**Player entity convention**: The player's entity_id is their username. The client sends
`player_entity_id` in the `/api/narrative` request body.

**Debug endpoint**: `GET /api/worlds/{world_id}/context-packet` returns the assembled packet
without triggering an AI call. Useful for inspecting scene state during development.

**Auth**: All routes except static files require a `Bearer <ANTHROPIC_API_KEY>` token header.

**Stat types**: Each entity type has exactly 6 stats (0–100 integers). See `services/base.py`
`STAT_NAMES_BY_ENTITY_TYPE` for the full mapping.

**Containment model**: Every entity has a nullable `container_id` column on the `entities` table
pointing to its direct parent entity. Null means root-level. Any entity type can be a container —
this unifies location ("character is in this room") and inventory ("potion is on this character")
in one field. Moves are validated for circular containment, logged to `containment_events`, and
fire hooks from `containment_hooks`. REST endpoints live under
`/api/worlds/{world_id}/entities/{entity_id}/contents` (and siblings) and
`/api/worlds/{world_id}/containment/*`.

**Three relational systems — the complete world state**:
- **Containment** answers WHERE (physical reality) — `container_id` + `containment_events`
- **Knowledge** answers WHO KNOWS WHAT (information reality) — `entity_knowledge` + `knowledge_events`
- **Consequence** answers WHY and WHAT HAPPENED (causal reality) — `consequence_records` + `consequence_hooks`

The three systems connect through consequence hooks. A `consequence_hook` with `action_type="containment_move"` will automatically update the containment tree when a consequence of type `moved` is recorded. A hook with `action_type="knowledge_learn"` will write to the knowledge graph when a `relationship_changed` consequence fires. All three hook actions run in the same SQLite transaction as the triggering `record_consequence` call.

**Consequence data model**: `consequence_records` has five fields — `cause_id`, `effect_type`, `target_id`, `detail`, `created_at`. `effect_type` is one of: `created`, `destroyed`, `moved`, `transformed`, `state_changed`, `triggered_event`, `relationship_changed`. `detail` uses the convention `"key: old → new"` (e.g. `"status: alive → dead"`) so that `get_state_at` can reconstruct a per-key state snapshot. REST endpoints live under `/api/worlds/{world_id}/consequences/*` and `/api/worlds/{world_id}/entities/{entity_id}/history` (and `state-at`).

---

## Running the Project

One command (idempotent — safe to re-run):

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

```bash
# macOS / Linux / WSL
./scripts/setup.sh
```

The script: detects Python 3.11+, creates `.venv`, runs `pip install -e .`,
copies `.env.example` → `.env` and prompts for `ANTHROPIC_API_KEY` on first
run, creates `data/`, then launches the server on `http://localhost:8000`.

Manual equivalents (if not using the script):

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e .   # Windows; .venv/bin/python on Unix
cp .env.example .env                            # then edit ANTHROPIC_API_KEY
.venv/Scripts/python.exe -m ayen_ode            # or `ayen-ode` (console script)

# Tests
.venv/Scripts/python.exe -m pytest tests/

# Health check
curl http://localhost:8000/health
```

Reload watches only `src/ayen_ode/` (not `.venv` or `data/`). Disable
entirely with `AYEN_ODE_RELOAD=0`.

**Cloud database (Turso):** Add these two lines to `.env` to store all game data in Turso
instead of a local SQLite file. Once set, any machine with the same `.env` shares the same
game world.

```
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your-auth-token
```

A `test_turso.py` script at the project root can be run to verify the connection works before
starting the server: `python test_turso.py`

---

## Development Workflow

When adding or changing features, follow these steps:

### Before writing code
- Ask detailed questions about how the feature should look, feel, and behave
- Ask about edge cases and error scenarios
- Ask how it connects to existing features
- Summarize your understanding and wait for confirmation before starting

### During implementation
- Break work into small named steps; present the step list before starting
