# world/

Human-readable game world content: entity reference files, lore frameworks, and maps.

**The SQLite database is the authoritative source of live game state.** Files here are reference
documents and manual backups — they do not drive the server.

## Contents

| Path | What it is |
|------|-----------|
| `characters/` | Character reference files |
| `factions/` | Faction reference files |
| `locations/` | Location reference files |
| `objects/` | Object reference files |
| `events/` | Event reference files |
| `stat-framework.md` | Stat model definitions (six stats per entity type, 0–100 range) |
| `stat-ledger.md` | Human-readable snapshot of stat changes |
| `reference-map.md` | Entity relationship reference map |
| `story-framework.md` | Active campaign control sheet |

## worlds/ vs world/

- **`world/`** (this folder) — general lore and reference content, not tied to a specific game run
- **`worlds/`** (sibling folder at repo root) — per-world operational files, one subfolder per world slug
