# Ayen-Ode

A narrative RPG engine. Manages deterministic game state — worlds, entities,
hidden stats, a containment tree, and investigation jobs — so the AI
storyteller can focus on narrative while the server enforces rules and
consistency. Narration is driven by the Anthropic Claude API.

Python 3.11+ (Starlette + SQLite); the static HTML/JS frontend is served from
the same process. Production deploys to Render (`render.yaml`).

There are **two ways to run it**:

1. **Desktop app (recommended for end users)** — a Windows installer or
   portable EXE that bundles Python, all dependencies, the server, and the UI
   into one app. No prerequisites, no terminal, opens in a native window. See
   [Desktop app](#desktop-app) below.
2. **Source / web mode (for developers)** — the original Python + browser
   setup. The server binds a local port and you visit it in your browser.

---

## Desktop app

The desktop build wraps the same server + UI inside a native window (Edge
WebView2 on Windows 10/11). It binds to `127.0.0.1` on a random free port —
nothing is exposed to the network. Your worlds and `.env` live in
`%APPDATA%\Ayen-Ode\` so they survive reinstalls.

### Running it

Either:

- Run **`Ayen-Ode-Setup-<version>.exe`** to install (per-user, no admin) and
  launch from the Start Menu, **or**
- Unzip the portable `Ayen-Ode\` folder anywhere and double-click
  `Ayen-Ode.exe`.

On first launch the app seeds `%APPDATA%\Ayen-Ode\.env` from the bundled
template and opens a dashboard. Click **Settings** to enter your
`ANTHROPIC_API_KEY`, then **Restart**. The window will close — re-open it
from the Start Menu (a one-click in-app reload is on the v2 list).

### Building it from source

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1            # portable EXE
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1 -Installer # + .exe installer
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1 -Clean     # wipe build/dist first
```

The script creates a dedicated build venv at `.venv-build\`, installs
PyInstaller + pywebview, and runs `pyinstaller ayen-ode.spec`. Output:

- **Portable:** `dist\Ayen-Ode\Ayen-Ode.exe` (the whole `dist\Ayen-Ode\`
  folder is the portable bundle — copy it anywhere).
- **Installer:** `dist\Ayen-Ode-Setup-<version>.exe`. Requires
  [Inno Setup 6](https://jrsoftware.org/isinfo.php). Install via
  `winget install JRSoftware.InnoSetup`.

The installer is unsigned, so Windows SmartScreen will show
"Windows protected your PC" on first run. Click **More info → Run anyway**.

### Files the desktop app creates

- `%APPDATA%\Ayen-Ode\.env` — config, edit via in-app Settings or directly.
- `%APPDATA%\Ayen-Ode\data\ayen_ode.db` — SQLite state.
- `%APPDATA%\Ayen-Ode\runtime.json` — chosen port + base URL (rewritten on
  each launch). Handy if you want to talk to the API from another tool.
- `%APPDATA%\Ayen-Ode\app.log` — captured stdout/stderr of the current run
  (`.log.1` is the previous run). Look here if the window won't open.

Uninstalling never touches `%APPDATA%\Ayen-Ode\` — your worlds are preserved.

### How it works

`desktop_launcher.py` is the PyInstaller entry point. It picks a free port,
seeds `%APPDATA%\Ayen-Ode\`, starts uvicorn in a thread, waits for `/health`,
then opens a pywebview window pointed at `/desktop-bootstrap` — a one-shot
HTML page that drops a fresh session token into `localStorage` and redirects
to the dashboard, so the user never sees the login screen. The auth flow,
SessionStore, and routes are unchanged; the desktop launcher just
short-circuits the login form.

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
| `AYEN_ODE_USER_DATA` | (empty) | Override the per-user data dir (`.env` + `data/` location). Frozen builds default to `%APPDATA%\Ayen-Ode`. |
| `AYEN_ODE_DESKTOP` | (empty) | Set to `1` to enable the `/desktop-bootstrap` route. The desktop launcher sets this automatically — don't set it manually for web mode. |

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
