# Codex Kickoff Prompt

Use the project spec in `docs/CODEX_MCP_PROJECT_SPEC.md` as the primary source of truth.

You are helping build the first MCP server for a GPT-based narrative roleplay system called Ayen-Ode.

## Goal
Build a clean, non-overengineered custom MCP server that gives the agent deterministic support for:
- multiple named worlds
- exactly one active world at a time
- world switching without continuity bleed
- saving and restoring the last system-side handoff per world
- structured entity storage
- hidden stat storage and comparison
- simple stat reconciliation across linked entities

## Context
This project already exists as a GPT agent system with:
- narrative instructions
- attached skills for world onboarding, world state management, canon sync, and stat reconciliation
- local canon files and indexes
- Memory for long-running continuity
- Notion intended as the primary structured world database

The MCP should become the code-first backend for the strict state logic, while the GPT agent continues to handle storytelling, onboarding conversation, director commands, and scene writing.

## Requirements
Read and follow:
- `docs/CODEX_MCP_PROJECT_SPEC.md`

Then scaffold a first working version of the MCP server.

## Build priorities
Implement in this order:
1. world registry and active-world enforcement
2. save/restore world handoff
3. entity CRUD by world
4. hidden stat storage
5. basic stat comparison
6. simple stat reconciliation hooks

## Version 1 actions to build
Create actions or tool endpoints for:
- `list_worlds`
- `create_world`
- `get_active_world`
- `switch_world`
- `get_world_status`
- `archive_world`
- `save_world_handoff`
- `get_world_handoff`
- `list_entities`
- `get_entity`
- `create_entity`
- `update_entity`
- `link_entities`
- `get_entity_stats`
- `compare_entities`
- `apply_stat_change`
- `reconcile_linked_stats`
- `sync_canon_record`
- `sync_world_summary`

## Technical preferences
- Prefer a beginner-friendly stack.
- Keep the implementation readable and modular.
- Use a simple storage approach first, ideally SQLite or another lightweight structured store.
- Design so Notion sync can be added cleanly later even if version 1 does not fully automate Notion schema creation.
- Include clear local run instructions.
- Include example seed data or example requests where useful.

## Repo file suggestions
Please create a practical initial repo structure, such as:
- `README.md`
- `docs/CODEX_MCP_PROJECT_SPEC.md` (already exists conceptually; preserve it)
- `docs/MCP_ACTIONS.md`
- `docs/DATA_MODEL.md`
- `src/` or equivalent server folder
- simple config and storage setup
- example requests or fixtures

## Important constraints
- Only one world can be active at a time.
- World switching must save and restore the last handoff.
- Entities and stats must remain world-scoped.
- No dice-roll mechanics.
- No cross-world continuity merging unless explicitly added later.
- Keep narrative generation out of the MCP server itself.

## Definition of done for first pass
The first pass is successful if a local developer can:
- run the server
- create two worlds
- switch between them
- store a different handoff for each world
- restore the correct handoff when switching back
- create entities in each world
- store and retrieve hidden stats
- compare entities in the same world
- avoid continuity bleed across worlds

## Output style
Work step by step.
First propose the repo structure and implementation plan.
Then generate the initial files.
Then explain how to run and test the server locally.
