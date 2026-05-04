import json
import re
from typing import Any
from mcp.server.fastmcp import FastMCP
from .db import connect, init_db, tx

mcp = FastMCP("Ayen-Ode-MCP")
conn = connect()
init_db(conn)

ALLOWED_ENTITY_TYPES = {"character", "faction", "location", "object", "event"}
STAT_KEYS = {
    "character": {"force", "influence", "will", "perception", "resilience", "volatility"},
    "faction": {"power", "cohesion", "reach", "resources", "secrecy", "instability"},
    "location": {"security", "prosperity", "corruption", "danger", "stability", "mystique"},
    "object": {"potency", "rarity", "durability", "risk", "control", "significance"},
    "event": {"scale", "urgency", "fallout", "visibility", "disruption", "momentum"},
}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def resolve_world(world_ref: str | int):
    if isinstance(world_ref, int) or str(world_ref).isdigit():
        row = conn.execute("SELECT * FROM worlds WHERE world_id=?", (int(world_ref),)).fetchone()
    else:
        row = conn.execute("SELECT * FROM worlds WHERE slug=?", (str(world_ref),)).fetchone()
    if not row:
        raise ValueError("World not found")
    return row


def resolve_entity(world_id: int, entity_ref: str | int):
    if isinstance(entity_ref, int) or str(entity_ref).isdigit():
        row = conn.execute("SELECT * FROM entities WHERE world_id=? AND entity_id=?", (world_id, int(entity_ref))).fetchone()
    else:
        row = conn.execute("SELECT * FROM entities WHERE world_id=? AND name=?", (world_id, str(entity_ref))).fetchone()
    if not row:
        raise ValueError("Entity not found")
    return row


def ensure_active_world_exists():
    row = conn.execute("SELECT world_id FROM worlds WHERE status='active' LIMIT 1").fetchone()
    if not row:
        fallback = conn.execute("SELECT world_id FROM worlds WHERE status IN ('draft','paused') ORDER BY updated_at DESC LIMIT 1").fetchone()
        if fallback:
            conn.execute("UPDATE worlds SET status='active' WHERE world_id=?", (fallback["world_id"],))


@mcp.tool()
def list_worlds():
    return [dict(r) for r in conn.execute("SELECT * FROM worlds ORDER BY created_at DESC")]


@mcp.tool()
def create_world(name: str, premise: str, theme_tone: str = "", player_role: str = "", activate_now: bool = False):
    slug = slugify(name)
    with tx(conn):
        if activate_now or conn.execute("SELECT 1 FROM worlds WHERE status='active' LIMIT 1").fetchone() is None:
            conn.execute("UPDATE worlds SET status='paused' WHERE status='active'")
            status = "active"
        else:
            status = "draft"
        conn.execute(
            "INSERT INTO worlds(slug,name,premise,theme_tone,player_role,status) VALUES(?,?,?,?,?,?)",
            (slug, name, premise, theme_tone, player_role, status),
        )
    return dict(conn.execute("SELECT * FROM worlds WHERE slug=?", (slug,)).fetchone())


@mcp.tool()
def get_active_world():
    row = conn.execute("SELECT * FROM worlds WHERE status='active' LIMIT 1").fetchone()
    return dict(row) if row else None


@mcp.tool()
def switch_world(world_ref: str, handoff_to_save: str = ""):
    new_world = resolve_world(world_ref)
    old_world = conn.execute("SELECT * FROM worlds WHERE status='active' LIMIT 1").fetchone()
    with tx(conn):
        if old_world and handoff_to_save.strip():
            conn.execute(
                "INSERT INTO world_handoffs(world_id,handoff,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(world_id) DO UPDATE SET handoff=excluded.handoff, updated_at=CURRENT_TIMESTAMP",
                (old_world["world_id"], handoff_to_save.strip()),
            )
        conn.execute("UPDATE worlds SET status='paused' WHERE status='active'")
        conn.execute("UPDATE worlds SET status='active' WHERE world_id=?", (new_world["world_id"],))
    handoff = conn.execute("SELECT handoff,updated_at FROM world_handoffs WHERE world_id=?", (new_world["world_id"],)).fetchone()
    return {
        "previous_world": dict(old_world) if old_world else None,
        "new_active_world": dict(resolve_world(new_world["world_id"])),
        "restored_handoff": dict(handoff) if handoff else None,
    }


@mcp.tool()
def get_world_status(world_ref: str):
    return dict(resolve_world(world_ref))


@mcp.tool()
def archive_world(world_ref: str):
    world = resolve_world(world_ref)
    with tx(conn):
        conn.execute("UPDATE worlds SET status='archived' WHERE world_id=?", (world["world_id"],))
        if world["status"] == "active":
            replacement = conn.execute(
                "SELECT world_id FROM worlds WHERE world_id<>? AND status IN ('paused','draft') ORDER BY updated_at DESC LIMIT 1",
                (world["world_id"],),
            ).fetchone()
            if not replacement:
                raise ValueError("Cannot archive the only active world; create another world first")
            conn.execute("UPDATE worlds SET status='active' WHERE world_id=?", (replacement["world_id"],))
    return {"archived": world["world_id"]}


@mcp.tool()
def save_world_handoff(world_ref: str, handoff: str):
    world = resolve_world(world_ref)
    with tx(conn):
        conn.execute("INSERT INTO world_handoffs(world_id,handoff,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(world_id) DO UPDATE SET handoff=excluded.handoff, updated_at=CURRENT_TIMESTAMP", (world["world_id"], handoff))
    return {"saved": True}


@mcp.tool()
def get_world_handoff(world_ref: str):
    world = resolve_world(world_ref)
    row = conn.execute("SELECT handoff,updated_at FROM world_handoffs WHERE world_id=?", (world["world_id"],)).fetchone()
    return dict(row) if row else None


@mcp.tool()
def list_entities(world_ref: str, entity_type: str = ""):
    world = resolve_world(world_ref)
    if entity_type and entity_type not in ALLOWED_ENTITY_TYPES:
        raise ValueError("Invalid entity_type")
    if entity_type:
        rows = conn.execute("SELECT * FROM entities WHERE world_id=? AND entity_type=?", (world["world_id"], entity_type)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM entities WHERE world_id=?", (world["world_id"],)).fetchall()
    return [dict(r) for r in rows]


@mcp.tool()
def get_entity(world_ref: str, entity_ref: str):
    world = resolve_world(world_ref)
    return dict(resolve_entity(world["world_id"], entity_ref))


@mcp.tool()
def create_entity(world_ref: str, entity_type: str, name: str, summary: str = "", status: str = "active", tags: list[str] | None = None):
    world = resolve_world(world_ref)
    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise ValueError("Invalid entity_type")
    tags = tags or []
    with tx(conn):
        conn.execute("INSERT INTO entities(world_id,entity_type,name,summary,status,tags) VALUES(?,?,?,?,?,?)", (world["world_id"], entity_type, name, summary, status, json.dumps(tags)))
    return dict(conn.execute("SELECT * FROM entities WHERE rowid=last_insert_rowid()").fetchone())


@mcp.tool()
def update_entity(world_ref: str, entity_ref: str, patch: dict[str, Any]):
    world = resolve_world(world_ref)
    ent = resolve_entity(world["world_id"], entity_ref)
    allowed = {"name", "summary", "status", "tags", "payload", "timeline_notes", "open_questions"}
    fields = {k: json.dumps(v) if k in {"tags", "payload", "timeline_notes", "open_questions"} else v for k, v in patch.items() if k in allowed}
    if not fields:
        return {"updated": False}
    sets = ", ".join([f"{k}=?" for k in fields])
    with tx(conn):
        conn.execute(f"UPDATE entities SET {sets}, updated_at=CURRENT_TIMESTAMP WHERE entity_id=?", (*fields.values(), ent["entity_id"]))
    return dict(resolve_entity(world["world_id"], ent["entity_id"]))


@mcp.tool()
def link_entities(world_ref: str, entity_a_ref: str, entity_b_ref: str, relation: str = "linked"):
    world = resolve_world(world_ref)
    a = resolve_entity(world["world_id"], entity_a_ref)
    b = resolve_entity(world["world_id"], entity_b_ref)
    low, high = sorted([a["entity_id"], b["entity_id"]])
    with tx(conn):
        conn.execute("INSERT OR IGNORE INTO entity_links(world_id,a_entity_id,b_entity_id,relation) VALUES(?,?,?,?)", (world["world_id"], low, high, relation))
    return {"linked": [low, high], "relation": relation}


def _load_stats(world_id: int, entity_id: int) -> dict[str, int]:
    row = conn.execute("SELECT stats_json FROM entity_stats WHERE world_id=? AND entity_id=?", (world_id, entity_id)).fetchone()
    return json.loads(row[0]) if row else {}


@mcp.tool()
def get_entity_stats(world_ref: str, entity_ref: str, reveal_exact: bool = False):
    world = resolve_world(world_ref)
    ent = resolve_entity(world["world_id"], entity_ref)
    stats = _load_stats(world["world_id"], ent["entity_id"])
    if reveal_exact:
        return stats
    return {k: ("low" if v < 34 else "mid" if v < 67 else "high") for k, v in stats.items()}


@mcp.tool()
def compare_entities(world_ref: str, left_entity_ref: str, right_entity_ref: str):
    world = resolve_world(world_ref)
    left = resolve_entity(world["world_id"], left_entity_ref)
    right = resolve_entity(world["world_id"], right_entity_ref)
    l = _load_stats(world["world_id"], left["entity_id"])
    r = _load_stats(world["world_id"], right["entity_id"])
    keys = sorted(set(l.keys()) | set(r.keys()))
    return {k: {"left": l.get(k, 0), "right": r.get(k, 0), "delta": l.get(k, 0) - r.get(k, 0)} for k in keys}


@mcp.tool()
def apply_stat_change(world_ref: str, entity_ref: str, changes: dict[str, int], reason: str, source_event_id: str = ""):
    world = resolve_world(world_ref)
    ent = resolve_entity(world["world_id"], entity_ref)
    allowed_stats = STAT_KEYS.get(ent["entity_type"], set())
    unknown = set(changes.keys()) - allowed_stats
    if unknown:
        raise ValueError(f"Invalid stats for {ent['entity_type']}: {sorted(unknown)}")
    stats = _load_stats(world["world_id"], ent["entity_id"])
    for k, v in changes.items():
        stats[k] = max(0, min(100, int(stats.get(k, 0) + v)))
    with tx(conn):
        conn.execute("INSERT INTO entity_stats(world_id,entity_id,stats_json,updated_at) VALUES(?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(world_id,entity_id) DO UPDATE SET stats_json=excluded.stats_json, updated_at=CURRENT_TIMESTAMP", (world["world_id"], ent["entity_id"], json.dumps(stats)))
    return {"stats": stats, "reason": reason, "source_event_id": source_event_id}


@mcp.tool()
def reconcile_linked_stats(world_ref: str, entity_ref: str, reason: str = "linked reconciliation"):
    world = resolve_world(world_ref)
    ent = resolve_entity(world["world_id"], entity_ref)
    links = conn.execute("SELECT a_entity_id,b_entity_id FROM entity_links WHERE world_id=? AND (a_entity_id=? OR b_entity_id=?)", (world["world_id"], ent["entity_id"], ent["entity_id"])).fetchall()
    affected = []
    for l in links:
        other_id = l[1] if l[0] == ent["entity_id"] else l[0]
        other = resolve_entity(world["world_id"], other_id)
        preferred = ["stability", "cohesion", "resilience", "durability", "momentum", "security"]
        target = next((k for k in preferred if k in STAT_KEYS.get(other["entity_type"], set())), None)
        if target:
            apply_stat_change(world_ref, str(other_id), {target: -1}, f"{reason}: spillover from {ent['entity_id']}")
            affected.append({"entity_id": other_id, "stat": target, "delta": -1})
    return {"affected_linked_entities": affected}


@mcp.tool()
def sync_canon_record(world_ref: str, entity_ref: str = ""):
    world = resolve_world(world_ref)
    entity_id = None
    if entity_ref:
        entity_id = resolve_entity(world["world_id"], entity_ref)["entity_id"]
    payload = {"status": "stub", "message": "Notion/canon sync hook ready"}
    with tx(conn):
        conn.execute("INSERT INTO sync_log(world_id,entity_id,sync_type,payload) VALUES(?,?,?,?)", (world["world_id"], entity_id, "canon_record", json.dumps(payload)))
    return payload


@mcp.tool()
def sync_world_summary(world_ref: str):
    world = resolve_world(world_ref)
    payload = {"status": "stub", "message": "World summary sync hook ready"}
    with tx(conn):
        conn.execute("INSERT INTO sync_log(world_id,entity_id,sync_type,payload) VALUES(?,?,?,?)", (world["world_id"], None, "world_summary", json.dumps(payload)))
    return payload


if __name__ == "__main__":
    mcp.run()
