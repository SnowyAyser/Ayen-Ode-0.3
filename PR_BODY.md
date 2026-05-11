## Summary
- Wraps the existing Starlette server + static UI in a native Edge WebView2 window. The bundled EXE binds `uvicorn` to a random `127.0.0.1` port — nothing crosses the network. No Python install required on the target machine.
- New `paths.py` makes the app frozen-aware: static assets stay read-only in the bundle; `.env`, SQLite DB, runtime info, and logs all move to `%APPDATA%\Ayen-Ode\`.
- New `/desktop-bootstrap` route (loopback-only, gated by `AYEN_ODE_DESKTOP=1`) mints a fresh session token and drops it into `localStorage` on the right origin, so the desktop launcher skips the login screen. SessionStore + AuthMiddleware are unchanged.
- One-shot `scripts\build_exe.ps1` produces a portable onedir EXE; `-Installer` also builds the Inno Setup installer.

## What's in the box

| File | Purpose |
| --- | --- |
| `desktop_launcher.py` | PyInstaller entry; `--settings` re-execs the tk settings window |
| `src/ayen_ode/paths.py` | `is_frozen()`, `static_dir()`, `user_data_dir()`, env/DB defaults |
| `src/ayen_ode/desktop.py` | Picks free port, runs uvicorn in a thread, opens pywebview |
| `ayen-ode.spec` | Onedir, UPX off, all dynamic uvicorn submodules + pythonnet/clr + libsql + WinForms backend pulled in explicitly |
| `installer/installer.iss` | Inno Setup, per-user install (no admin), WebView2 runtime probe |
| `scripts/build_exe.ps1` | `-Clean` / `-Installer` flags; creates a dedicated `.venv-build` |

## What stays the same
- All 71 existing tests pass.
- Source mode (`python -m ayen_ode`, the `ayen-ode` console script, Render deploy) is untouched: same `.env` at the repo root, same `data/` dir.
- The UI looks identical to the current website on first run — no redesign.

## Drive-by fixes
The initial commit had two truncations that prevented the server from even starting:
- `src/ayen_ode/routes/auth.py` was cut mid-`restart_handler` with no `Route(...)` list returned from `make_auth_routes`.
- `src/ayen_ode/services/__init__.py` ended with a bare `__a` instead of `__all__ = [...]`.

Both reconstructed here. Worth a quick eyeball before merging in case there are more truncations elsewhere.

## Test plan
- [x] `pytest tests/` — 71 passed in ~12 s.
- [x] `pyinstaller --noconfirm ayen-ode.spec` builds without errors.
- [x] Built `Ayen-Ode.exe` boots in ~3 s, binds 127.0.0.1, responds to `/health`.
- [x] `/desktop-bootstrap` mints a 64-char session token; subsequent `/api/worlds` with that token returns `{"worlds":[]}`; without it returns 401.
- [x] First run creates `%APPDATA%/Ayen-Ode/.env` (from `.env.example`), `data/ayen_ode.db`, `runtime.json`.
- [x] `/api/restart` cleanly exits with code 42 (windowed) / 0 (source).
- [ ] **Reviewer to confirm:** double-clicking the EXE on a fresh Windows box opens a window without prompts.
- [ ] **Reviewer to confirm:** Inno Setup installer (`-Installer` flag) compiles end-to-end on a box with Inno Setup 6 installed.

## Known follow-ups (not blocking)
- After changing the API key in Settings the user must close + reopen the app — in-place reload is a v2 thing (documented in the README).
- Icon stub is in place in the spec/installer (`icon=None`, `SetupIconFile` commented out); drop in `.ico` whenever ready.
- EXE is unsigned, so SmartScreen will warn on first launch. Code signing is a separate decision.

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
