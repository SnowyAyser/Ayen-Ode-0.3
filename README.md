# Ayen-Ode

A narrative RPG engine. Manages deterministic game state — worlds, entities,
hidden stats, a containment tree, and investigation jobs — so the AI
storyteller can focus on narrative while the server enforces rules and
consistency. Narration is driven by the Anthropic Claude API.

Python 3.11+ (Starlette + SQLite); the static HTML/JS frontend is served from
the same process. Production deploys to Render (`render.yaml`).

---

## Quickstart — Windows

```powershell
git clone <repo-url> C:\dev\Ayen-Ode
cd C:\dev\Ayen-Ode
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

Open <http://localhost:8000>. The script will prompt for your
`ANTHROPIC_API_KEY` on first run and start the server when done.

## Quickstart — macOS / Linux / WSL

```bash
git clone <repo-url> ~/dev/Ayen-Ode
cd ~/dev/Ayen-Ode
./scripts/setup.sh
```

---

## What you'll need

- **Python 3.11+** — install via `winget install Python.Python.3.12` (Windows)
  or your OS package manager. The setup script will tell you if Python is
  missing.
- An **Anthropic API key** — get one at <https://console.anthropic.com/>.

---

## Subsequent runs

Re-run the same script. It's idempotent — it skips finished steps (`.venv`,
deps, `.env`) and just starts the server.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

You can also launch the server directly once installed:

```powershell
.venv\Scripts\python.exe -m ayen_ode
# or, after `pip install -e .` puts it on PATH:
ayen-ode
```

VS Code users: hit **F5** (config defined in `.vscode/launch.json`).

---

## Configuration

All settings live in `.env` (created from `.env.example` on first run). The
only required value is `ANTHROPIC_API_KEY`. Optional knobs:

| Variable | Default | Purpose |
|---|---|---|
| `APP_USERNAME` / `APP_PASSWORD` | empty | Web UI login credentials |
| `ALLOWED_IPS` | empty | Comma-separated client IP allowlist (plus `127.0.0.1`/`::1`) |
| `AYEN_ODE_DB_PATH` | `data/ayen_ode.db` | SQLite path |
| `AYEN_ODE_HOST` | `0.0.0.0` | Bind host |
| `AYEN_ODE_PORT` | `8000` | Bind port |
| `AYEN_ODE_RELOAD` | `1` | Set `0` to disable uvicorn auto-reload |

---

## Tests

```powershell
.venv\Scripts\python.exe -m pytest tests/
```

---

## Troubleshooting

- **"Python was not found; run without arguments to install from the Microsoft
  Store"** — that's the Microsoft Store stub, not real Python. Install with
  `winget install Python.Python.3.12`, then **open a new shell** and re-run
  the setup script.
- **"Running scripts is disabled on this system"** — run via
  `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1` (or set the
  policy once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`).
- **Don't put the project inside OneDrive / iCloud / Dropbox / Google Drive**
  — sync locks `.venv` files mid-write, can corrupt the SQLite DB, and uploads
  your `.env` (with API key) to the cloud. The setup script refuses to run
  inside these folders. Use `C:\dev\` or similar.
- **Server won't reload on code changes** — only files inside
  `src/ayen_ode/` trigger reloads (deliberate; prevents reload cascades
  from `.venv` writes and DB updates). To disable reload entirely, set
  `AYEN_ODE_RELOAD=0` in `.env`.

---

## Project layout

See [CLAUDE.md](CLAUDE.md) for the full directory map, services-layer breakdown,
and architecture notes.

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) and `render.yaml`. Render runs
`pip install -e .` then launches uvicorn directly (no auto-reload).
