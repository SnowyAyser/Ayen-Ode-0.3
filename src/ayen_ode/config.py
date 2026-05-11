"""Runtime configuration for the Ayen-Ode server.

Model strings are defined here as module-level constants so a model upgrade
is a single-line change. Import from here rather than hardcoding strings in
narrative.py, intake.py, or quests.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv
from anthropic import Anthropic

from . import paths

# Seed %APPDATA%/Ayen-Ode/.env from the bundled .env.example on first run (frozen
# builds), then point dotenv at the user-writable .env regardless of cwd.
paths.ensure_user_dir()
load_dotenv(paths.env_path(), override=False)
# Fall back to dotenv's cwd-based search too, so devs running `python -m ayen_ode`
# from anywhere still pick up a project-root .env.
load_dotenv(override=False)

# ---------------------------------------------------------------------------
# Model constants
# ---------------------------------------------------------------------------

#: Primary narrator/world-builder model -- used for all narrative calls.
SONNET_MODEL = "claude-sonnet-4-6"

#: Fast secondary model -- used for intake, quest scanning, and world init.
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# config.py lives at src/ayen_ode/config.py -- three parents up is the project root
# (kept for source-mode parity; frozen builds resolve paths via paths.py instead).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Settings:
    db_path: Path
    host: str
    port: int
    anthropic_api_key: str
    anthropic_client: Anthropic
    app_username: str
    app_password: str
    allowed_ips: frozenset


def load_settings() -> Settings:
    """Load settings from environment variables with local-friendly defaults."""

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    # Treat the .env.example placeholder as unset.
    if api_key == "sk-ant-...":
        api_key = ""
    # The server boots without a key so the dashboard can render and the
    # native settings window can be launched. Narrative calls will fail with
    # an Anthropic auth error until a real key is saved + server restarted.

    # In frozen (desktop) builds the DB lives in %APPDATA%/Ayen-Ode/data/.
    # In source mode it stays at <repo>/data/ — same as before.
    db_path = paths.db_path_default()

    host = os.getenv("AYEN_ODE_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("AYEN_ODE_PORT", "8000")))

    # Anthropic() rejects empty strings, so use a placeholder when unset.
    # Real auth failure surfaces on the first API request.
    client = Anthropic(api_key=api_key or "missing-api-key")

    app_username = os.getenv("APP_USERNAME", "")
    app_password = os.getenv("APP_PASSWORD", "")
    allowed_ips_raw = os.getenv("ALLOWED_IPS", "")
    raw_ips = {ip.strip() for ip in allowed_ips_raw.split(",") if ip.strip()}
    # Include IPv4-mapped IPv6 variants and localhost
    expanded: set[str] = set(raw_ips)
    for ip in raw_ips:
        if "." in ip and not ip.startswith("::"):
            expanded.add("::ffff:" + ip)
    expanded |= {"127.0.0.1", "::1"}

    return Settings(
        db_path=db_path,
        host=host,
        port=port,
        anthropic_api_key=api_key,
        anthropic_client=client,
        app_username=app_username,
        app_password=app_password,
        allowed_ips=frozenset(expanded),
    )
