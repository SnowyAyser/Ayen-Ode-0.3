# World Registry

Human-readable registry of all worlds. The authoritative state lives in the server's SQLite database — this file is a readable reference and backup surface.

Use `/worlds` or the `list_worlds` endpoint to get the live list.

---

## Active World

_(none)_

---

## World List

| Slug | Name | Status | Premise Summary | Last Handoff |
|------|------|--------|----------------|--------------|
| — | — | — | No worlds created yet | — |

---

## World Status Key

| Status | Meaning |
|--------|---------|
| `active` | The one current world. Only one may be active at a time. |
| `paused` | A world that exists but is not currently active. |
| `archived` | A world that has been closed. Not selectable without restore. |
| `draft` | A world stub that hasn't been activated yet. |

---

## Notes

- Switching worlds saves the current handoff and restores the target world's last handoff automatically.
- Entities and stats are world-scoped — they do not bleed across worlds.
- Cross-world comparison is not supported in v1.
