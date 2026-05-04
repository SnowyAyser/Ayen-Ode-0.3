# Codex-Ready MCP Project Spec

## Purpose
This document # Codex Kickoff Prompt

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
 the first coded backend for the narrative roleplay system used by this agent. The goal is to move strict state management, world switching, handoff restore, and structured continuity logic into code, while leaving narrative judgment and storytelling in the agent.

 ## System role split

 ### The agent should continue to own
 - onboarding and worldbuilding conversation
 - narrative scene writing
 - director-command interpretation
 - user-facing summaries and recaps
 - flexible responses to vague or creative user input

 ### The MCP server should own
 - world creation and switching
 - enforcement that only one world is active at a time
 - world registry storage
 - per-world continuity state retrieval
 - saving and restoring the last system-side handoff per world
 - structured entity storage and lookup
 - stat reconciliation logic
 - canon sync orchestration
 - Notion sync orchestration and validation

 ## Core product behavior
 The overall system is a multi-world narrative roleplay engine.

 Requirements:
 - support multiple named worlds
 - only one world may be active at a time
 - each world has separate continuity, entities, stats, records, and handoffs
 - when the user switches back into a world, the last saved system-side handoff for that world must be restored and repeated
 - Notion is the primary structured world database
 - local canon files remain the schema and backup continuity layer
 - Memory remains the long-running continuity layer across runs

 ## World model
 Each world should have:
 - `world_id`: stable unique identifier
 - `slug`: short machine-safe identifier
 - `name`: user-facing world name
 - `status`: `active | paused | archived | draft`
 - `premise`: short summary of the world
 - `theme_tone`: world tone and thematic direction
 - `player_role`: the playerâ€™s role in this world
 - `current_state_summary`: current continuity summary
 - `active_tensions`: list of unresolved pressures
 - `last_system_handoff`: the last system-side handoff to replay on return
 - `created_at`
 - `updated_at`

 ## Active-world rules
 - exactly one world can be active at a time
 - switching worlds must deactivate the old one before activating the new one
 - world switching must not leak continuity between worlds
 - comparisons across worlds are allowed only when explicitly requested
 - cross-world merging is not allowed unless explicitly requested later as a separate feature

 ## Entity model
 All important entities belong to one world.

 Shared fields for all entity records:
 - `entity_id`
 - `world_id`
 - `entity_type`: `character | faction | location | object | event`
 - `name`
 - `summary`
 - `status`
 - `tags`
 - `linked_entity_ids`
 - `timeline_notes`
 - `open_questions`
 - `created_at`
 - `updated_at`

 ### Character fields
 - public_identity
 - hidden_truths
 - motives
 - fears
 - limits
 - current_condition

 ### Faction fields
 - public_identity
 - hidden_agenda
 - leadership
 - territory_influence
 - goals
 - methods
 - allies_enemies

 ### Location fields
 - region_position
 - description
 - atmosphere
 - access_boundaries
 - controllers
 - risks
 - secrets
 - current_state

 ### Object fields
 - current_owner
 - current_location
 - properties_powers
 - limitations
 - condition
 - significance

 ### Event fields
 - time_marker
 - trigger
 - outcome
 - consequences
 - open_fallout

 ## Hidden stat model
 Use a shared `0-100` scale across all important entities.

 ### Character stats
 - force
 - influence
 - will
 - perception
 - resilience
 - volatility

 ### Faction stats
 - power
 - cohesion
 - reach
 - resources
 - secrecy
 - instability

 ### Location stats
 - security
 - prosperity
 - corruption
 - danger
 - stability
 - mystique

 ### Object stats
 - potency
 - rarity
 - durability
 - risk
 - control
 - significance

 ### Event stats
 - scale
 - urgency
 - fallout
 - visibility
 - disruption
 - momentum

 ## Stat rules
 - stats are mostly hidden from the end user during normal play
 - the system should expose light summaries by default
 - exact values are shown only when explicitly requested
 - stat changes should usually be small and justified
 - large changes require a clear event or turning point
 - linked entities may need cascading changes when one entity changes significantly

 ## Handoff restore behavior
 When the active world changes away from the current world:
 - save the current worldâ€™s latest system-side handoff
 - the saved handoff should be a concise continuity bridge for re-entry

 When switching back into a world:
 - restore that worldâ€™s continuity state
 - return the saved last system-side handoff
 - the agent should repeat that handoff before continuing play

 ## Notion integration
 Notion is the primary structured world database.

 The MCP should support a Notion-backed structure for:
 - worlds
 - characters
 - factions
 - locations
 - objects
 - events

 The MCP should eventually ensure:
 - all major records belong to a specific world
 - record schemas are consistent
 - linked references remain valid
 - updates in code can be synced to Notion reliably

 First version does not need full automatic Notion schema generation if that slows delivery, but it should be designed so Notion sync can be added cleanly.

 ## Local canon alignment
 The local canon files in the agent remain the schema and backup layer.
 The MCP should be designed to align with these folders and concepts:
 - `worlds/`
 - `characters/`
 - `factions/`
 - `locations/`
 - `objects/`
 - `events/`
 - `indexes/`

 Important local indexes:
 - `indexes/world-registry.md`
 - `indexes/stat-framework.md`
 - `indexes/stat-ledger.md`
 - `indexes/reference-map.md`
 - `indexes/canon-index.md`
 - `indexes/open-threads.md`

 ## First MCP version: minimum viable actions
 Build the first version around these actions:

 ### World actions
 - `list_worlds`
 - `create_world`
 - `get_active_world`
 - `switch_world`
 - `get_world_status`
 - `archive_world`

 ### Handoff actions
 - `save_world_handoff`
 - `get_world_handoff`

 ### Entity actions
 - `list_entities`
 - `get_entity`
 - `create_entity`
 - `update_entity`
 - `link_entities`

 ### Stat actions
 - `get_entity_stats`
 - `compare_entities`
 - `apply_stat_change`
 - `reconcile_linked_stats`

 ### Sync actions
 - `sync_canon_record`
 - `sync_world_summary`

 ## Suggested action behavior

 ### `create_world`
 Input:
 - name
 - premise
 - optional theme_tone
 - optional player_role
 - optional activate_now

 Output:
 - created world record
 - world slug
 - whether it is active

 ### `switch_world`
 Input:
 - world id or slug

 Output:
 - previous world
 - new active world
 - restored handoff
 - current world summary

 ### `save_world_handoff`
 Input:
 - world id or slug
 - handoff text

 Output:
 - saved status
 - timestamp

 ### `get_world_handoff`
 Input:
 - world id or slug

 Output:
 - saved handoff text
 - timestamp

 ### `apply_stat_change`
 Input:
 - world id
 - entity id
 - changed stats
 - reason
 - optional source event id

 Output:
 - updated stat block
 - affected linked entities if any

 ## Recommended storage design
 Use a simple structured database first.
 Good beginner options:
 - SQLite
 - Postgres
 - Supabase-backed Postgres

 Recommended tables:
 - worlds
 - world_handoffs
 - entities
 - entity_links
 - entity_stats
 - world_events
 - sync_log

 ## Suggested implementation path
 For a non-expert-friendly first build:
 1. build world registry and switching first
 2. add handoff save/restore
 3. add entity CRUD
 4. add stat storage and comparison
 5. add stat reconciliation rules
 6. add Notion sync later

 ## Hosting guidance
 This project does not require a normal website.
 It requires a reachable service endpoint for the MCP server.
 Good beginner hosting targets later:
 - Replit
 - Render
 - Railway
 - Fly.io

 ## Success criteria for version 1
 Version 1 is successful if it can:
 - create multiple worlds
 - keep only one world active at a time
 - switch worlds cleanly
 - restore and return the last saved handoff for a world
 - store and fetch world-specific entities
 - store and compare hidden stats
 - avoid continuity bleed across worlds

 ## What should remain out of scope for version 1
 - dice rolling mechanics
 - full combat engine
 - cross-world merging
 - automatic narrative generation inside the MCP
 - full Notion schema automation if it blocks delivery
 - complex permission systems

 ## Codex build prompt seed
 Use this project spec to scaffold a custom MCP server for a GPT-based narrative roleplay system. Build the first version with world registry, active-world switching, handoff save/restore, entity CRUD, hidden stat storage, and simple stat reconciliation. Prefer a clean, readable implementation suitable for a non-expert owner. Include a simple local run path, a basic storage layer, and clear action definitions that can later be connected as MCP tools.