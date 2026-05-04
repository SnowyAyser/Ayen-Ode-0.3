# MCP Actions (v1)

## World
- `list_worlds()`
- `create_world(name, premise, theme_tone?, player_role?, activate_now?)`
- `get_active_world()`
- `switch_world(world_ref)`
- `get_world_status(world_ref)`
- `archive_world(world_ref)`

## Handoff
- `save_world_handoff(world_ref, handoff)`
- `get_world_handoff(world_ref)`

## Entity
- `list_entities(world_ref, entity_type?)`
- `get_entity(world_ref, entity_ref)`
- `create_entity(world_ref, entity_type, name, summary?, status?, tags?)`
- `update_entity(world_ref, entity_ref, patch)`
- `link_entities(world_ref, entity_a_ref, entity_b_ref, relation?)`

## Stats
- `get_entity_stats(world_ref, entity_ref, reveal_exact=false)`
- `compare_entities(world_ref, left_entity_ref, right_entity_ref)`
- `apply_stat_change(world_ref, entity_ref, changes, reason, source_event_id?)`
- `reconcile_linked_stats(world_ref, entity_ref, reason="linked reconciliation")`

## Sync stubs
- `sync_canon_record(world_ref, entity_ref?)`
- `sync_world_summary(world_ref)`
