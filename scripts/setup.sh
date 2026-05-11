#!/usr/bin/env bash
# Ayen-Ode setup + run script (macOS / Linux / WSL)
#
# Idempotent: first run installs everything; subsequent runs skip finished
# steps and just start the server.
#
# Usage:
#   ./scripts/setup.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo ">> Ayen-Ode setup ($ROOT)"

# Refuse to run inside a syncing folder
case "$ROOT" in
  */OneDrive/*|*/Dropbox/*|*/iCloudDrive/*|*/Google\ Drive/*|*/Library/Mobile\ Documents/*)
    echo "ERROR: project is inside a cloud-sync folder ($ROOT)." >&2
    echo "Sync corrupts .venv and SQLite. Move to e.g. ~/dev/Ayen-Ode and re-run." >&2
    exit 1
    ;;
esac

# --- Step 1: find a real Python interpreter ---
PYTHON=""
for cand in python3.12 python3.11 python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then
        ver="$("$cand" --version 2>&1 || true)"
        if [[ "$ver" =~ ^Python\ 3\.(11|12|13|14) ]]; then
            PYTHON="$cand"
            echo ">> Python: $cand ($ver)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: no Python 3.11+ found." >&2
    echo "Install Python 3.12 from https://www.python.org/downloads/ or your package manager." >&2
    exit 1
fi

# --- Step 2: virtualenv ---
VENV_PY="$ROOT/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    echo ">> Creating .venv ..."
    "$PYTHON" -m venv "$ROOT/.venv"
fi

# --- Step 3: install deps if anthropic isn't present ---
if ! "$VENV_PY" -c "import anthropic" 2>/dev/null; then
    echo ">> Installing dependencies ..."
    "$VENV_PY" -m pip install --upgrade pip
    "$VENV_PY" -m pip install -e .
fi

# --- Step 4: .env ---
ENV_PATH="$ROOT/.env"
NEEDS_KEY=0
if [ ! -f "$ENV_PATH" ]; then
    echo ">> Creating .env from .env.example ..."
    cp "$ROOT/.env.example" "$ENV_PATH"
    NEEDS_KEY=1
elif grep -qE '^ANTHROPIC_API_KEY=(sk-ant-\.\.\.)?[[:space:]]*$' "$ENV_PATH"; then
    NEEDS_KEY=1
fi

if [ "$NEEDS_KEY" = "1" ]; then
    echo ">> Opening settings window for first-run setup ..."
    echo "   (enter your Anthropic API key in the window, then Save)"
    "$VENV_PY" -m ayen_ode.settings_window || \
        echo "   (settings window unavailable — edit $ENV_PATH manually before continuing)"
fi

# --- Step 5: data dir ---
mkdir -p "$ROOT/data"

# --- Step 6: launch server ---
echo
echo ">> Starting server on http://localhost:8000  (Ctrl-C to stop)"
echo
exec "$VENV_PY" -m ayen_ode
