# Action Reference

All actions default to the active world when a `world` argument is omitted. A `world` argument may be a `world_id` or `slug`.

## World Tools

### `list_worlds(include_archived=false)`

Returns all non-archived worlds by default.

### `create_world(name, premise, theme_tone="", player_role="", activate_now=true)`

Creates a world. If `activate_now` is true, the new world becomes active and the previous active world becomes paused. If this is the first world, it becomes active even if `activate_now` is false.

### `get_active_world()`

Returns the active world, or `null` if no world exists yet.

### `switch_world(world)`

Activates the selected world, pauses the previous active world, and returns:

- previous world
- new active world
- restored handoff
- current state summary

Archived worlds cannot be activated.

### `get_world_status(world=null)`

Returns world details and entity counts by entity type.

### `archive_world(world)`

Archives a world. If the archived world was active, the most recently updated non-archived world becomes active when one exists.

## Handoff Tools

### `save_world_handoff(handoff_text, world=null, current_state_summary=null, active_tensions=null)`

Saves the latest system-side handoff for a world and stores a history row.

### `get_world_handoff(world=null)`

Returns the latest saved handoff for a world.

## Entity Tools

### `list_entities(world=null, entity_type=null, include_archived=false)`

Lists world-scoped entities. Supported entity types are:

- `character`
- `faction`
- `location`
- `object`
- `event`

### `get_entity(entity_id, world=null)`

Gets one entity from the selected world.

### `create_entity(...)`

Creates an entity with optional hidden stats.

Important arguments:

- `name`
- `entity_type`
- `summary`
- `status`
- `tags`
- `timeline_notes`
- `open_questions`
- `metadata`
- `stats`

### `update_entity(...)`

Updates entity fields. If `stats` is provided, it replaces the entity's hidden stat block.

### `link_entities(entity_id_a, entity_id_b, world=null, relation="")`

Links two entities inside the same world.

## Stat Tools

### `get_entity_stats(entity_id, world=null)`

Returns exact hidden stat values. This tool should only be used when exact values are needed.

### `compare_entities(entity_id_a, entity_id_b, world=null)`

Compares two entities in the same world. Cross-world comparison is rejected in v1.

### `apply_stat_change(entity_id, changes, reason, world=null, source_event_id=null, include_reconciliation_suggestions=true)`

Applies signed stat deltas and logs the reason.

Example:

```json
{
  "entity_id": "entity_abc",
  "changes": { "will": 5, "volatility": -2 },
  "reason": "The character survived a major trial."
}
```

### `reconcile_linked_stats(entity_id, changes, reason="", world=null, apply=false)`

Suggests or applies related changes to linked entities. V1 applies half-strength deltas only when linked entities share the same stat key. Otherwise it returns a director-review suggestion.

## Sync Placeholders

### `sync_canon_record(sync_type, payload, world=null, entity_id=null)`

Logs a planned canon/Notion sync action. It does not write to Notion in v1.

### `sync_world_summary(summary, world=null, active_tensions=null, source="client")`

Updates the world summary and logs a sync placeholder.
