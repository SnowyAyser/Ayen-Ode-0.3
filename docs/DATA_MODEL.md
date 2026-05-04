# Data model (SQLite)

Tables:
- `worlds`
- `world_handoffs`
- `entities`
- `entity_links`
- `entity_stats`
- `sync_log`

Rules:
- Exactly one active world at a time (transactional switch).
- All entities and stats are world-scoped.
- Handoffs are stored per world and restored on switch.
- Stat values are clamped to 0..100.
