# Stat Framework

All stats use a shared **0–100 integer scale**, clamped at both ends. Stats operate mostly in the background. They guide outcomes, comparisons, and pressure — they are not visible dice mechanics.

The authoritative stat values live in the server (`entity_stats` table). This document defines the stat model.

---

## Scale Convention

| Range | Meaning |
|-------|---------|
| 0–20 | Critically low — a meaningful weakness or near-collapse |
| 21–40 | Below average — a real liability |
| 41–60 | Average — ordinary for this entity type |
| 61–80 | Strong — a notable advantage |
| 81–100 | Exceptional — rare, dominant, or at its peak |

---

## Entity Types and Stat Categories

### Characters

| Stat | What It Tracks |
|------|---------------|
| `force` | Physical capability, threat, and direct power |
| `influence` | Social reach, persuasion, and pull on others |
| `will` | Drive, resistance to breaking, and determination |
| `perception` | Awareness, insight, and ability to read situations |
| `resilience` | Capacity to absorb damage, loss, or pressure |
| `volatility` | Unpredictability and potential for sudden action |

### Factions

| Stat | What It Tracks |
|------|---------------|
| `power` | Raw organizational strength and capacity to act |
| `cohesion` | Internal unity and loyalty |
| `reach` | Geographic or social presence and access |
| `resources` | Wealth, supply, and material capacity |
| `secrecy` | Operational concealment and information control |
| `instability` | Internal fractures, dissent, or near-breaking pressure |

### Locations

| Stat | What It Tracks |
|------|---------------|
| `security` | How defended or safe the location is |
| `prosperity` | Economic health and resource abundance |
| `corruption` | Moral or institutional decay |
| `danger` | Active threat level to those present |
| `stability` | Political and social steadiness |
| `mystique` | Strangeness, legend, or unknown qualities |

### Objects

| Stat | What It Tracks |
|------|---------------|
| `potency` | How powerful or effective the object is |
| `rarity` | How scarce or irreplaceable it is |
| `durability` | How much use or abuse it can absorb |
| `risk` | Danger in possessing or using it |
| `control` | How reliably it can be directed or wielded |
| `significance` | Narrative or cultural importance |

### Events

| Stat | What It Tracks |
|------|---------------|
| `scale` | How far-reaching or large the event is |
| `urgency` | How immediately it demands response |
| `fallout` | Long-term consequences and damage |
| `visibility` | How visible or public the event is |
| `disruption` | How much it disrupts existing order |
| `momentum` | Whether the event is still building or fading |

---

## Update Rules

- Stats change because of meaningful story events, not arbitrarily.
- Prefer small, explainable movement (±3–10) unless a major turning point justifies a larger shift.
- Log every change via `apply_stat_change` with a reason string.
- Use `reconcile_linked_stats` when one entity's change should ripple to linked entities.

---

## Output Conventions

- During ordinary play: keep stats hidden; use light summary language ("struggling," "at their peak," "fraying").
- On request: provide a compact summary first; give exact values only when the user asks for a full stat sheet.
- `/stats` or an explicit director request for stats unlocks the compact summary or full sheet.
- Use `compare_entities` for explicit entity-vs-entity comparisons within the same world.
