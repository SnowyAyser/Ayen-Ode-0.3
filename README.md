# Ayen-Ode MCP v0.1

A beginner-friendly first MCP server for Ayen-Ode world state management.

## What this server does
- Manages multiple named worlds
- Enforces exactly one active world at a time
- Saves/restores per-world handoffs
- Stores world-scoped entities
- Stores hidden stats and compares entities
- Applies simple linked-entity stat reconciliation

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ayen_ode_mcp.server
```

Server defaults:
- transport: stdio
- SQLite DB: `data/ayen_ode.db`

## Example local smoke flow
1. `create_world` twice (`activate_now=true` for first)
2. `switch_world` to second world
3. `save_world_handoff` in each world
4. `switch_world` back and confirm `restored_handoff`
5. Create entities in each world and confirm isolation with `list_entities`
6. Add stats and compare with `compare_entities`

## Project layout
- `docs/CODEX_MCP_PROJECT_SPEC.md` source spec
- `docs/MCP_ACTIONS.md` tool contract reference
- `docs/DATA_MODEL.md` SQLite schema and behaviors
- `src/ayen_ode_mcp/` implementation
