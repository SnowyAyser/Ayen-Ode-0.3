# Local Tool Flow

A simple flow you can hit against the running server (e.g. via `curl` or the dashboard).

1. `create_world`

```json
{
  "name": "Ash Vale",
  "premise": "A haunted frontier where bargains echo for generations.",
  "theme_tone": "Gothic frontier mystery",
  "player_role": "A reluctant oathkeeper",
  "activate_now": true
}
```

2. `save_world_handoff`

```json
{
  "handoff_text": "Ash Vale waits at dusk. The oathkeeper has just learned the bell tower remembers names.",
  "current_state_summary": "The first mystery centers on the bell tower and a missing witness.",
  "active_tensions": ["The witness is missing", "The bell tower reacts to spoken names"]
}
```

3. `create_entity`

```json
{
  "name": "Mira Voss",
  "entity_type": "character",
  "summary": "A wary guide who knows the old road.",
  "tags": ["guide", "local"],
  "metadata": {
    "public_identity": "Road guide",
    "hidden_truths": ["She has heard the bell tower speak."]
  },
  "stats": {
    "will": 62,
    "perception": 70,
    "volatility": 25
  }
}
```

4. `create_world`

```json
{
  "name": "Glass Harbor",
  "premise": "A coastal city where masks are legal contracts.",
  "activate_now": true
}
```

5. `switch_world`

```json
{
  "world": "ash-vale"
}
```

Expected result: the restored handoff is the Ash Vale handoff, and Glass Harbor entities are not listed.
