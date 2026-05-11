# Data Model

The v1 server stores data in SQLite.

## Worlds

`worlds` stores the registry and current state bridge.

Fields:

- `world_id`
- `slug`
- `name`
- `status`: `active`, `paused`, `archived`, or `draft`
- `premise`
- `theme_tone`
- `player_role`
- `current_state_summary`
- `active_tensions_json`
- `last_system_handoff`
- `created_at`
- `updated_at`

Rule: after at least one world exists, the server keeps one active world unless the only world is archived.

## Handoffs

`world_handoffs` stores historical saved handoffs.

The current handoff is also copied onto `worlds.last_system_handoff` for fast restore during `switch_world`.

## Entities

`entities` stores all world-scoped records.

Shared fields:

- `entity_id`
- `world_id`
- `entity_type`
- `name`
- `summary`
- `status`
- `tags_json`
- `timeline_notes_json`
- `open_questions_json`
- `metadata_json`
- `created_at`
- `updated_at`

Type-specific fields go into `metadata_json` for v1. This keeps the schema simple while allowing character, faction, location, object, and event fields to evolve.

## Entity Links

`entity_links` stores same-world links between two entities.

Cross-world links are not supported in v1.

## Hidden Stats

`entity_stats` stores a JSON stat block for each entity.

All stats are integers clamped to `0-100`.

Character stats:

- `force`
- `influence`
- `will`
- `perception`
- `resilience`
- `volatility`

Faction stats:

- `power`
- `cohesion`
- `reach`
- `resources`
- `secrecy`
- `instability`

Location stats:

- `security`
- `prosperity`
- `corruption`
- `danger`
- `stability`
- `mystique`

Object stats:

- `potency`
- `rarity`
- `durability`
- `risk`
- `control`
- `significance`

Event stats:

- `scale`
- `urgency`
- `fallout`
- `visibility`
- `disruption`
- `momentum`

## Stat Ledger

`stat_ledger` records every delta applied through `apply_stat_change` or applied reconciliation.

## Sync Log

`sync_log` records placeholder sync activity. It exists so Notion/canon sync can be added later without changing the API contract.
