# Reference Map

Tracks significant relationships between entities. Updated when alliances form, betrayals land, allegiances shift, or links between characters, factions, locations, and objects become narratively meaningful.

Authoritative links live in the server (`entity_links` table). This file is a human-readable relationship surface.

---

## Active Relationships

| Entity A | Entity B | Relation Type | Status | World | Notes |
|----------|----------|---------------|--------|-------|-------|
| — | — | — | — | — | No relationships yet |

---

## Relation Type Guide

Common relation types to use consistently:

| Type | Meaning |
|------|---------|
| `ally` | Active mutual support |
| `rival` | Active opposition or competition |
| `enemy` | Hostile — willing to harm |
| `controlled_by` | Entity A is under B's authority or influence |
| `owns` | Entity A possesses entity B |
| `located_in` | Entity A is physically based in entity B (a location) |
| `member_of` | Entity A is part of faction entity B |
| `knows_secret` | Entity A holds hidden information about entity B |
| `bonded` | A significant personal or magical bond |
| `betrayed` | A broken trust, still active as a narrative pressure |

Add custom types as needed. Keep them descriptive and consistent.

---

## Status Key

| Status | Meaning |
|--------|---------|
| `active` | Relationship is current and operational |
| `strained` | Under pressure — may break |
| `broken` | Was a relationship, now severed |
| `hidden` | Neither party knows the full picture |
| `one-sided` | Only one entity is aware of or invested in the link |
