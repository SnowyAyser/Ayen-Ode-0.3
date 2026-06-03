# CLAUDE.md — Ayen-Ode Project Navigation

> **AI ASSISTANTS: Read this document before working in this codebase.**
> After making any structural or significant code changes, **update this file** to keep it accurate.
> Future AI sessions depend on this document being current.

---

## What This Project Is

Ayen-Ode is a narrative RPG engine. It manages deterministic game state — worlds, entities, hidden stats, a containment tree, investigation jobs, and quest tracking — so an AI narrator can focus on storytelling while the server enforces rules and consistency.

**Narration is driven by local Qwen 2.5:14b via Ollama** (running at `localhost:11434`). The Anthropic API key field in Settings is optional and unused by default; `LocalAIClient` in `local_ai.py` mimics the Anthropic SDK interface but routes calls to Ollama.

- **Backend**: Python 3.11+, Starlette, SQLite (local) or Turso/libSQL (cloud)
- **Frontend**: Static HTML/Tailwind CSS/JS served by the Starlette server
- **Desktop wrapper**: pywebview (Edge WebView2 on Windows) pointing at `http://127.0.0.1:{port}/`
- **Deployment**: Render.com (see `render.yaml`) — the HTML/JS frontend is the same for both desktop and web

---

## Entry Point and Boot Sequence

```
Play-Ayen-Ode.bat
  └─ pythonw.exe -m ayen_ode.desktop_launcher
       │
       ├─ (background thread) bg_boot_thread()
       │    ├─ updater.check_and_update()             # EXE builds: compare source hash → spawn update
       │    ├─ desktop_helpers.check_single_instance() # Windows mutex
       │    ├─ uvicorn.Server(app).run()               # Starlette on 127.0.0.1:{port}
       │    └─ sets server_ready = True
       │
       ├─ (main thread) SplashApp (tkinter animated splash)
       │    └─ polls server_ready / server_failed / update_triggered every 100 ms
       │
       └─ When server_ready: launch_webview()
            └─ webview.create_window(url="http://127.0.0.1:{port}/")
                 → user sees index.html (login) or auto-redirects to /desktop-bootstrap
```

**Preferred port:** 54224 (fixed if free, otherwise random ephemeral). Written to
`%APPDATA%/Ayen-Ode/runtime.json`.

**Auto-login flow (desktop):** If the user checked "Auto Login on Startup",
`index.html` immediately redirects to `/desktop-bootstrap`. That route creates a
fresh session token server-side, injects it into `localStorage` via an inline
HTML page, and redirects to `/dashboard.html`. The user never sees the login form.

---

## Package / Module Map

```
src/ayen_ode/
│
│  ── Desktop layer ────────────────────────────────────────────────────────────
├── desktop_launcher.py        # ← PRIMARY ENTRY POINT (desktop mode)
│                              #   starts uvicorn + pywebview + splash
├── splash_app.py              # Animated tkinter loading screen (boot-time only)
├── desktop_api.py             # pywebview JS bridge:
│                              #   save_username / get_saved_username
│                              #   save_auto_login / get_auto_login
│                              #   get_configured_credentials
│                              #   close_window, toggle_fullscreen, set_fullscreen
├── desktop_helpers.py         # Single-instance mutex, set_window_icon, stream redirect
├── updater.py                 # Self-update: compare source hash, spawn build script
│
│  ── Orphaned customtkinter UI (NOT used by launcher) ─────────────────────────
├── desktop_gui.py             # ⚠ SHIM ONLY — re-exports desktop.AyenOdeApp / run()
├── desktop/                   # ⚠ ORPHANED ctk UI package
│   ├── app.py                 #   AyenOdeApp root
│   ├── colors.py              #   Shared colour constants (S950–S100, A950–A100, etc.)
│   ├── widgets.py             #   Shared widget helpers (_btn, _label, _panel, etc.)
│   ├── login.py               #   LoginFrame
│   ├── dashboard.py           #   DashboardFrame
│   ├── settings.py            #   SettingsDialog (ctk)
│   ├── create_world.py        #   CreateWorldFrame wizard
│   ├── narrative_layout.py    #   NarrativeFrame (layout orchestrator)
│   ├── narrative_view.py      #   NarrativeView (story text + input)
│   ├── quest_panel.py         #   QuestPanel
│   ├── compendium_panel.py    #   CompendiumPanel
│   └── investigation_overlay.py
│
│  ── Config & AI ──────────────────────────────────────────────────────────────
├── config.py                  # load_settings() → Settings dataclass
│                              #   SONNET_MODEL = HAIKU_MODEL = "qwen2.5:14b"
│                              #   client = LocalAIClient(api_key=...)
├── local_ai.py                # Ollama adapter: MessagesAdapter.create() mimics
│                              #   anthropic.messages.create(); auto-starts Ollama;
│                              #   auto-pulls qwen2.5:14b if not installed
├── paths.py                   # Resolves AppData dir, db path, static dir, .env path;
│                              #   is_frozen() detects PyInstaller bundle
├── settings_window.py         # Plain-tkinter settings UI — kept for devs
│                              #   (python -m ayen_ode.settings_window).
│                              #   write_env() is reused by routes/auth.py.
│                              #   NOT invoked by the launcher.
│
│  ── Server ────────────────────────────────────────────────────────────────────
├── server.py                  # Starlette app assembly: routes, middleware (Auth,
│                              #   CacheControl, CORS), SessionStore; starts
│                              #   investigation_worker + check_and_pull_qwen_model threads
├── service.py                 # Re-export shim → from .services import AyenOdeService
├── worker.py                  # Background investigation job processor:
│                              #   pregenerated_investigations cache first, then Qwen fallback;
│                              #   priority queue; 60s pacing (waivable for dev user)
│
│  ── Narrative ─────────────────────────────────────────────────────────────────
├── narrative/
│   ├── __init__.py            # Exports: initialize_world, process_user_action,
│   │                          #   investigate_entity
│   ├── init_world.py          # Generate opening scene for a new world
│   ├── user_action.py         # process_user_action() → narration string
│   ├── investigator.py        # investigate_entity() → entity data + narrative
│   └── stages/
│       ├── prose.py           # Narration generation stage
│       ├── mechanics.py       # Mechanics extraction stage
│       ├── quests.py          # Quest update stage
│       ├── theme.py           # Theme consistency stage
│       └── utils.py           # Shared stage helpers
├── intake.py                  # Post-narration pass (Qwen): extracts state changes —
│                              #   consequences, knowledge, moves, time advancement
├── quests.py                  # Quest goal detection: scan_for_goals(),
│                              #   generate_overarching_goal()
│
│  ── Context assembly ──────────────────────────────────────────────────────────
├── context_assembler.py       # ContextAssembler: 9-query world-state packet assembled
│                              #   before each narrative call
├── context_scene_queries.py   # Queries 1–4: scene, actor awareness, history, threads
├── context_player_queries.py  # Queries 5–9: player state, entity histories, journey
├── narrative_utils.py         # parse_investigation_response, sanitize_entity_details
│
│  ── Relinker ──────────────────────────────────────────────────────────────────
├── relinker/                  # Auto-link <investigate> tags in stored narration text
│   ├── __init__.py            # Exports: relink_text_*, auto_pre_generate_*, etc.
│   ├── parser.py              # Detect / rewrite investigate tags programmatically
│   ├── pregenerator.py        # Queue + execute background pre-generation
│   ├── db_relinker.py         # Batch-relink stored narration rows in the DB
│   └── history_relinker.py    # Relink world handoff history logs
│
│  ── Routes ────────────────────────────────────────────────────────────────────
├── routes/
│   ├── __init__.py            # make_all_routes() assembles all route lists
│   ├── auth.py                # health, static page serves, login, logout,
│   │                          #   /desktop-bootstrap, /api/settings GET/POST,
│   │                          #   /api/restart, /api/local-ai/status,
│   │                          #   /api/settings/status, frontend error log
│   ├── worlds.py              # World CRUD, create-and-init, switch, reset, delete,
│   │                          #   currency handlers
│   ├── entities.py            # Entity CRUD, stats, linking
│   ├── containment.py         # Containment tree, move, hooks, events
│   ├── knowledge.py           # Knowledge graph, hooks, events
│   ├── consequence.py         # Consequence records, hooks, context-packet,
│   │                          #   narrative action endpoint
│   ├── consequence_handlers.py # Split consequence handler logic
│   ├── consequence_narrative.py # Narrative-specific consequence routes
│   ├── quests.py              # Quest routes: list, promote, dismiss, check
│   └── arch.py                # Architecture / admin routes
│
│  ── Services ──────────────────────────────────────────────────────────────────
└── services/
    ├── __init__.py            # Assembles AyenOdeService from all mixins
    ├── base.py                # BaseService: connect(), initialize(), shared helpers
    ├── schema.py              # _SCHEMA_SQL DDL + run_migrations(conn)
    ├── db_conn.py             # make_db_connection() — SQLite or Turso
    ├── worlds.py              # WorldsMixin
    ├── entities.py            # EntitiesMixin
    ├── stats.py               # StatsMixin
    ├── containment.py         # ContainmentMixin
    ├── knowledge_queries.py   # KnowledgeQueryMixin (read-only)
    ├── knowledge.py           # KnowledgeMixin
    ├── consequence_queries.py # ConsequenceQueryMixin (read-only)
    ├── consequence.py         # ConsequenceMixin
    ├── investigation.py       # InvestigationMixin
    ├── quests.py              # QuestsMixin
    ├── sync.py                # SyncMixin
    ├── hook_actions.py        # execute_shared_hook_action()
    └── arch.py                # Architecture mixin

static/
├── index.html                 # Login page — auto-login, pywebview bridge polling,
│                              #   credential auto-fill, clover animation
├── dashboard.html             # World dashboard — world list, forge CTA, settings modal,
│                              #   local-AI download progress panel
├── create-world.html          # 4-step world creation wizard (name→tone→premise→role)
│                              #   animated step transitions, starfield background
├── narrative.html             # In-game narrative shell (JS split into modules below)
├── narrative-core.js          # Core state, world load, entity render, bootstrap
├── narrative-actions.js       # Form submit, send action, streaming
├── narrative-dom.js           # DOM helpers and rendering utilities
├── narrative-investigation.js # Investigation panel (combined legacy file)
├── narrative-investigation-api.js  # Investigation API call wrappers
├── narrative-investigation-ui.js   # Investigation UI rendering
├── narrative-settings.js      # Settings popover + skip-time picker for narrative page
├── narrative-entity.js        # Entity detail panel, compendium list, entity link detection
├── narrative-worlds.js        # World switcher modal
├── narrative-quests.js        # Quest panel: load, render, promote/dismiss threads
├── app.js                     # Shared: checkAuth(), apiCall(), setToken(), getToken()
├── clover-loader.js           # CloverLoader.createLoader() — clover trail animation
├── debug.html / debug.js / debug-panels.js / debug-intake.js  # Dev debug panel
└── clover-loader.html         # Standalone loading page
```

---

## Data Model

### Storage locations

| What | Where |
|------|-------|
| Database | `%APPDATA%/Ayen-Ode/data/ayen_ode.db` (desktop / frozen)<br>`<repo>/data/ayen_ode.db` (source mode) |
| Settings / API key | `%APPDATA%/Ayen-Ode/.env` |
| Auto-login flag | `%APPDATA%/Ayen-Ode/auto_login.txt` + `localStorage.autoLogin` |
| Saved username | `%APPDATA%/Ayen-Ode/saved_username.txt` + `localStorage.savedUsername` |
| Session tokens | `sessions` table in SQLite |
| Runtime port | `%APPDATA%/Ayen-Ode/runtime.json` |
| Boot/error log | `%APPDATA%/Ayen-Ode/boot.log` (cleared each launch) |
| App log | `%APPDATA%/Ayen-Ode/app.log` + `app.log.1` (rolling) |
| Cloud DB (opt-in) | Turso — set `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` in `.env` |

### Key DB tables

**`worlds`**
```
world_id TEXT PK, slug TEXT UNIQUE, name TEXT, status TEXT,
premise TEXT, theme_tone TEXT, player_role TEXT,
current_state_summary TEXT, active_tensions_json TEXT,
last_system_handoff TEXT, original_opening_scene TEXT,
game_time_seconds INT, game_time_label TEXT,
created_at TEXT, updated_at TEXT
```
`status` (`active` / `paused` / `archived` / `draft`) is written by the service layer
but **not shown in the UI**. See §Deliberately Gone.

**`entities`** — characters, locations, factions, objects, events per world.
`container_id` (nullable FK to `entities`) implements the physical containment tree.

**`investigation_jobs`** — queued/processing/complete/failed jobs.
`priority INT`, `cost INT`, `result_json TEXT` (entity + narrative + stats).

**`pregenerated_investigations`** — cache keyed on `(world_id, entity_name)`.
Worker reads this before calling the AI.

**`world_currencies`** — investigation points per world (`current_balance`, `max_balance`).

**Other tables**: `entity_links`, `entity_stats`, `stat_ledger`, `world_handoffs`,
`investigation_state`, `containment_events/hooks`, `entity_knowledge`,
`knowledge_events/hooks`, `consequence_records/hooks`, `world_quests`, `sessions`, `sync_log`.

---

## Main User Flows

### App launch → Dashboard
```
Play-Ayen-Ode.bat
  → splash screen (tkinter) while uvicorn boots on 127.0.0.1:54224
  → pywebview opens http://127.0.0.1:54224/
  → index.html
       if localStorage.autoLogin === 'true': → /desktop-bootstrap
         → server creates session, injects token in localStorage → /dashboard.html
       else: show login form
         → POST /api/login { username, password } → { token } → /dashboard.html
  → dashboard polls GET /api/local-ai/status every 2s
       if ollama_running=false or model_installed=false:
         show blocking download-progress overlay; disable Forge + world buttons
       when model_installed=true: dismiss overlay, enable buttons
  → GET /api/worlds → render world cards
```

### Forge a new world
```
Click "Forge a new world" link (id="forgeWorldLink") → /create-world.html
  4 animated steps: Name → Tone (preset chips) → Premise → Your Role
  Final step: POST /api/worlds/create { name, premise, theme_tone, player_role }
    → service.create_world() inserts row
    → narrative.initialize_world() calls Qwen → opening scene
    → navigate to /narrative.html?world_id={id}&fresh=1
```

### Enter an existing world
```
Dashboard world card → "Enter →" button → enterWorldWithTransition(worldId)
  → animated overlay: clover spinner + world name floats to centre
  → ~1.5s later: navigate to /narrative.html?world_id={id}&fresh=1
```

### Narrative loop
```
narrative.html
  → GET /api/worlds/{id} + handoff → display opening scene
  → player types action → Enter (or click Act)
  → POST /api/narrative { world_id, user_action, player_entity_id, history }
       server: ContextAssembler.assemble() → 9-query world-state packet
       narrative.process_user_action() → Qwen → narration string
       intake._run_intake_pass() → Qwen → writes consequences/knowledge/time to DB
       returns: { narration, game_time, ... }
  → <investigate item='X' npc|location|...='Y' cost='N'>display</investigate>
       rendered as clickable amber underline links
  → click link: spend N points → POST create investigation_job
       worker.py claims job (atomic UPDATE…subquery, no race)
       checks pregenerated_investigations cache → use if present
       else: narrative.investigate_entity() → Qwen → entity data
       service.create_entity() → complete job, restore points
```

### Settings
```
Dashboard header gear icon → openSettingsModal()
  → GET /api/settings (loopback-only, reads .env, masks secrets)
  → populate form: API key (write-only), username, password, IPs, port, fullscreen
  → POST /api/settings { key: value, ... }
       server: write_env() from settings_window.py → %APPDATA%/Ayen-Ode/.env
       optional: POST /api/restart → process relaunches with updated config
```
The narrative page has a smaller gear in the input bar that opens the same modal
(via `narrative-settings.js` `settingsBtn` / `settingsPopover`).

---

## Conventions

### File Length Limits
- **Strict Limit**: All files in the codebase MUST NOT exceed 300 lines of code.
- If a file grows past 300 lines, it must be split up into smaller, modular submodules.

### Colours (desktop/ package)
Defined in `desktop/colors.py`. Always import from there — never hardcode hex in
customtkinter code.

| Range | Semantic use |
|-------|-------------|
| S950 → S100 | slate-950 → slate-100 — page bg → primary text |
| A950 → A100 | amber-950 → amber-100 — invest pill bg → Act btn text |
| P600 | purple-600 — quest panel accent |
| RED / GRN | #ef4444 / #22c55e — error / success |
| TYPE_COLORS dict | entity-type dots: character=blue, location=green, faction=violet, object=orange, event=red |

The HTML/JS frontend uses Tailwind class names directly; `colors.py` is ctk-only.

### Widget helpers (desktop/ package — `desktop/widgets.py`)
```python
_btn(parent, text, cmd, *, w=None, h=32, bg=S800, hbg=S700, fg=S300)
_label(parent, text, color=S400, size=12, **kw)
_entry(parent, var, *, w=340, ph="", show="")
_panel(parent, *, w=None, r=12, **kw)         # card frame: S900 bg, S800 border
_divider(parent)                               # 1px S800 horizontal rule
_center(win, w, h)                             # centre a Toplevel on screen
_bind_click_recursive(widget, handler)         # bind <Button-1> on widget + all children
_split_investigate(text)                       # parse <investigate ...> spans from narration
```

### Auth / sessions
- All API routes except `_PUBLIC_PATHS` require `Authorization: Bearer <token>`.
- Token lives in `localStorage` as `apiKey`; `app.js` exposes `getToken()` / `setToken()`.
- `/api/settings` and `/api/restart` are additionally loopback-only (`_is_loopback(ip)`).

### AI client
Use `settings.anthropic_client` (a `LocalAIClient`). Interface:
`client.messages.create(model, max_tokens, system, messages, tools, tool_choice)`.
Never instantiate a new client inline; never import `anthropic` directly.

### Model names
```python
from .config import SONNET_MODEL, HAIKU_MODEL   # both = "qwen2.5:14b"
```
Always import from `config.py`. Never hardcode model strings.

---

## Things Deliberately Gone — Do Not Reintroduce

### 1. Active / inactive world concept in the UI

The `worlds.status` DB column still exists and `WorldsMixin.create_world` still writes it.
`switch_world` and `get_active_world` still exist on the service.

**The UI does not expose any of this.** There are no "active" / "ACTIVE" badges, no "Set
Active" or "Switch" buttons, and no prominent featured-active-world section. Every world
card shows the same actions. Do not add these back. To change which world a player is in,
navigate directly to `/narrative.html?world_id={id}`.

> **Known residue to clean up:** `dashboard.html:renderWorlds()` still checks
> `w.status === 'active'` to conditionally render an "active" badge and show
> "Enter →" vs "Switch". This should be removed — all worlds should show "Enter →".
> `loadData()` also calls `renderActiveWorld()` which references a `#activeWorldCard`
> element that no longer exists in the HTML, causing a silent TypeError.

### 2. Anthropic Claude as the AI narrator

All narrative calls go through `LocalAIClient` → Ollama → Qwen 2.5:14b. The
`ANTHROPIC_API_KEY` setting is optional and unused by the narrator. Do not add
`anthropic` imports to `narrative/`, `intake.py`, or `quests.py`.

### 3. Customtkinter desktop UI as the primary interface

`desktop_launcher.py` does not call `desktop_gui.run()` or anything in `desktop/`.
The real UI is the HTML/JS frontend served by Starlette and displayed inside pywebview.
Do not re-add customtkinter frames to the boot path.

### 4. Subprocess settings window

`/api/settings/launch` (old route that spawned a subprocess to open `settings_window.py`)
is gone. Settings are handled entirely in the web modal (`settingsModal` in `dashboard.html`
backed by `GET/POST /api/settings`).

---

## Running the Project

```powershell
# Desktop app (normal)
Play-Ayen-Ode.bat          # or double-click "Play Ayen-Ode.lnk"

# Server only — no desktop window (web/dev mode)
.venv\Scripts\python.exe -m ayen_ode

# Tests
.venv\Scripts\python.exe -m pytest tests\

# Standalone settings editor (dev only)
.venv\Scripts\python.exe -m ayen_ode.settings_window

# One-time setup (idempotent)
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

**Ollama must be installed and running** for narrative calls to work. The server
auto-starts Ollama and auto-pulls `qwen2.5:14b` on first boot, but that is a
~9 GB download. The dashboard shows a full-screen blocking progress panel until
the model is ready — "Forge a new world" and all world action buttons are disabled
until `model_installed=true`.

**Cloud database (optional):** Add to `%APPDATA%/Ayen-Ode/.env` via Settings:
```
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your-auth-token
```
