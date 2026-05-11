# Worlds

One subfolder per world. Name subfolders as `<world-slug>/`.

Each world folder should contain:

| File | Purpose |
|------|---------|
| `campaign-state.md` | Current arc, scene, and active threads |
| `character-ledger.md` | Quick-reference list of important characters in this world |
| `story-pressure.md` | Active tensions, hidden objectives, and dramatic pressure |
| `last-system-handoff.md` | The most recent system-side summary — restored when re-entering this world |

---

## Convention

When a world is first created:
1. Create a folder here: `worlds/<world-slug>/`
2. Create the four files above using the templates below
3. Register the world in `world-registry.md`
4. Create the world via `create_world` on the server

The server is the authoritative state store. These files are the human-readable narrative surface.

---

## campaign-state.md template

```markdown
# Campaign State — <World Name>

## Current Arc
_(name and brief description)_

## Active Scene
_(where we are right now)_

## Open Threads
- _(thread 1)_
- _(thread 2)_
```

---

## character-ledger.md template

```markdown
# Character Ledger — <World Name>

| Name | Role | Status | Notes |
|------|------|--------|-------|
```

---

## story-pressure.md template

```markdown
# Story Pressure — <World Name>

## Hidden Objectives
1. _(objective)_
2. _(objective)_

## Active Tensions
- _(tension)_

## Dramatic Pressure Direction
- [ ] Intensifying
- [ ] Holding
- [ ] Releasing
```

---

## last-system-handoff.md template

```markdown
# Last System Handoff — <World Name>

**Saved:** _(date)_

_(The system-side summary that picks up where the story left off. Replayed when re-entering this world.)_
```
