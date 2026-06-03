"""Deterministic world-state packet assembler for the narrative system prompt.

Runs before every AI narrative call. Opens one SQLite connection, executes all 9
queries within that transaction, deduplicates, and returns a JSON-serializable dict.

Critical constraint: all queries share the single conn from assemble().
Never call service methods that open their own connect() inside _query_* methods.
"""

from __future__ import annotations

import json
from typing import Any

from .context_player_queries import PlayerQueryMixin


class ContextAssembler(PlayerQueryMixin):
    """Orchestrates world-state packet assembly for the narrative system prompt.

    Usage:
        assembler = ContextAssembler(service)
        packet = assembler.assemble(world_id, player_entity_id)
        text = assembler.to_prompt_text(packet)

    When player_entity_id is None, player sub-sections are empty and all
    player-anchored queries are skipped gracefully.
    """

    def __init__(self, service: Any) -> None:
        self._service = service

    def assemble(
        self,
        world_id: str,
        player_entity_id: str | None,
        history_depth: int = 10,
        tension_limit: int = 3,
    ) -> dict[str, Any]:
        """Run all 9 queries in one DB transaction and return the context packet."""
        with self._service.connect() as conn:
            wid = self._service._resolve_world(conn, world_id)["world_id"]

            time_row = conn.execute(
                "SELECT game_time_seconds, game_time_label FROM worlds WHERE world_id = ?",
                (wid,),
            ).fetchone()

            scene = self._query_scene(conn, wid, player_entity_id)
            scene_ids = self._collect_scene_entity_ids(scene)

            actor_awareness = self._query_actor_awareness(conn, wid, scene, scene_ids)
            recent_history = self._query_recent_history(conn, wid, scene_ids, history_depth)
            open_threads = self._query_open_threads(conn, wid, tension_limit)
            player = self._query_player_state(conn, wid, player_entity_id)
            entity_histories = self._query_entity_histories(conn, wid, scene_ids, history_depth)
            player_journey = self._query_player_journey(conn, wid, player_entity_id, scene_ids)
            relationship_histories = self._query_relationship_histories(conn, wid, scene, player_entity_id)
            world_bleed = self._query_world_bleed(conn, wid, scene_ids)

            debt_rows = conn.execute(
                """
                SELECT wd.*, e1.name AS debtor_name, e2.name AS creditor_name
                FROM world_debts wd
                JOIN entities e1 ON e1.entity_id = wd.debtor_id
                JOIN entities e2 ON e2.entity_id = wd.creditor_id
                WHERE wd.world_id = ? AND wd.status = 'active'
                ORDER BY wd.created_at DESC
                """,
                (wid,),
            ).fetchall()
            active_debts = [
                {
                    "debt_id": r["debt_id"],
                    "debtor_id": r["debtor_id"],
                    "debtor_name": r["debtor_name"],
                    "creditor_id": r["creditor_id"],
                    "creditor_name": r["creditor_name"],
                    "resource_type": r["resource_type"],
                    "quantity": r["quantity"],
                    "detail": r["detail"],
                    "evidence": r["evidence"],
                }
                for r in debt_rows
            ]

        packet = {
            "game_time": {
                "seconds": time_row["game_time_seconds"] if time_row else 0,
                "label": time_row["game_time_label"] if time_row else "",
            },
            "scene": scene,
            "active_debts": active_debts,
            "actor_awareness": actor_awareness,
            "recent_history": recent_history,
            "open_threads": open_threads,
            "player": player,
            "entity_histories": entity_histories,
            "player_journey": player_journey,
            "relationship_histories": relationship_histories,
            "world_bleed": world_bleed,
        }
        self._deduplicate_consequence_records(packet)
        return packet

    def to_prompt_text(self, packet: dict[str, Any]) -> str:
        """Serialize the context packet into clean, compact, human-readable Markdown prose.
        Completely strips out empty values and structural JSON noise for maximum local AI accuracy.
        """
        lines = []

        # 1. Game Time
        game_time = packet.get("game_time") or {}
        time_label = game_time.get("label", "")
        time_secs = game_time.get("seconds", 0)
        if time_label:
            lines.append(f"- **Current Game Time**: {time_label} ({time_secs} seconds elapsed)")

        # 2. Scene
        scene = packet.get("scene") or {}
        curr_container = scene.get("current_container")
        if curr_container:
            lines.append("\n### CURRENT SCENE & SURROUNDINGS:")
            lines.append(f"- **Location**: {curr_container.get('name')} ({curr_container.get('entity_type', 'location')})")
            
            contents = scene.get("contents") or []
            if contents:
                lines.append("- **Nearby Elements & Entities**:")
                for item in contents:
                    if item:
                        lines.append(f"  - {item.get('name')} ({item.get('entity_type', 'object')})")
            
            adj_containers = scene.get("adjacent_containers") or []
            if adj_containers:
                lines.append("- **Adjacent Areas**:")
                for adj in adj_containers:
                    c = adj.get("container")
                    if c:
                        c_name = c.get("name")
                        c_type = c.get("entity_type", "location")
                        lines.append(f"  - {c_name} ({c_type})")
            
            chain = scene.get("container_chain") or []
            if chain:
                path = " is located within ".join(item.get("name", "") for item in reversed(chain) if item)
                if path:
                    lines.append(f"- **Wider Context**: {curr_container.get('name')} is located within {path}.")

        # 3. Player State
        player = packet.get("player") or {}
        if player and player.get("name"):
            lines.append("\n### YOUR STATE & ATTRIBUTES:")
            lines.append(f"- **Character**: {player.get('name')} ({player.get('entity_type', 'character')})")
            
            stats = player.get("stats") or {}
            if stats:
                stat_str = ", ".join(f"{k.capitalize()}: {v}" for k, v in stats.items())
                lines.append(f"- **Stats**: {stat_str}")
            
            inventory = player.get("inventory") or []
            if inventory:
                inv_items = ", ".join(f"{item.get('name')} ({item.get('entity_type', 'object')})" for item in inventory if item)
                lines.append(f"- **Held Inventory**: {inv_items}")
            else:
                lines.append("- **Held Inventory**: None")

        # 4. Active Debts
        debts = packet.get("active_debts") or []
        if debts:
            lines.append("\n### ACTIVE DEBTS & OBLIGATIONS:")
            for d in debts:
                lines.append(f"- {d.get('debtor_name')} owes {d.get('creditor_name')} {d.get('quantity')} {d.get('resource_type')} for: {d.get('detail')}")

        # 5. Actor Awareness
        awareness = packet.get("actor_awareness") or {}
        active_awareness = {k: v for k, v in awareness.items() if v}
        if active_awareness:
            lines.append("\n### CHARACTER AWARENESS & STATES:")
            for actor_id, state in active_awareness.items():
                if state:
                    state_str = ", ".join(f"{k.replace('_', ' ')} is {v}" for k, v in state.items())
                    lines.append(f"- {actor_id}: {state_str}")

        # 6. Recent History (Consequences)
        history = packet.get("recent_history") or []
        if history:
            lines.append("\n### RECENT NARRATIVE EVENTS:")
            for h in history:
                summary = h.get("narrative_summary") or h.get("summary")
                if summary:
                    lines.append(f"- {summary}")

        # 7. Open Threads
        threads = packet.get("open_threads") or []
        if threads:
            lines.append("\n### ACTIVE QUESTS & GOALS:")
            for t in threads:
                summary = t.get("narrative_summary") or t.get("summary")
                if summary:
                    lines.append(f"- {summary}")

        # 8. Entity Histories
        entity_hist = packet.get("entity_histories") or {}
        active_entity_hist = {k: v for k, v in entity_hist.items() if v and (v.get("full") or v.get("compressed"))}
        if active_entity_hist:
            lines.append("\n### KNOWN LORE & HISTORY OF NEARBY ELEMENTS:")
            for ent_id, hist in active_entity_hist.items():
                recs = hist.get("compressed") or hist.get("full") or []
                for r in recs:
                    summary = r.get("narrative_summary") or r.get("summary")
                    if summary:
                        lines.append(f"- {summary}")

        # 9. Player Journey
        journey = packet.get("player_journey") or []
        if journey:
            lines.append("\n### YOUR RECENT MOVEMENTS:")
            for j in journey:
                summary = j.get("narrative_summary") or j.get("summary")
                if summary:
                    lines.append(f"- {summary}")

        # 10. Relationship Histories
        rel_hist = packet.get("relationship_histories") or {}
        active_rel_hist = {k: v for k, v in rel_hist.items() if v}
        if active_rel_hist:
            lines.append("\n### RELATIONSHIPS & TENSIONS:")
            for key, val in active_rel_hist.items():
                if isinstance(val, dict):
                    rel_str = ", ".join(f"{k}: {v}" for k, v in val.items())
                    lines.append(f"- {key}: {rel_str}")
                elif isinstance(val, list):
                    for item in val:
                        summary = item.get("narrative_summary") or item.get("summary")
                        if summary:
                            lines.append(f"- {summary}")

        # 11. World Bleed
        bleed = packet.get("world_bleed") or []
        if bleed:
            lines.append("\n### HISTORICAL LORE & WORLD BACKGROUND:")
            for b in bleed:
                summary = b.get("narrative_summary") or b.get("summary")
                if summary:
                    lines.append(f"- {summary}")

        return "\n".join(lines).strip()

    def _collect_scene_entity_ids(self, scene: dict[str, Any]) -> set[str]:
        """Collect every entity_id visible in the scene dict."""
        ids: set[str] = set()
        container = scene.get("current_container")
        if container:
            ids.add(container["entity_id"])
        for e in scene.get("contents", []):
            if e:
                ids.add(e["entity_id"])
        for adj in scene.get("adjacent_containers", []):
            c = adj.get("container")
            if c:
                ids.add(c["entity_id"])
            for e in adj.get("contents", []):
                if e:
                    ids.add(e["entity_id"])
        for e in scene.get("container_chain", []):
            if e:
                ids.add(e["entity_id"])
        return ids

    def _deduplicate_consequence_records(self, packet: dict[str, Any]) -> None:
        """Remove duplicate consequence records within each individual section."""

        def _dedup_list(records: list) -> list:
            seen: set[str] = set()
            out = []
            for r in records:
                cid = r.get("consequence_id")
                if cid and cid in seen:
                    continue
                if cid:
                    seen.add(cid)
                out.append(r)
            return out

        packet["recent_history"] = _dedup_list(packet.get("recent_history") or [])
        packet["open_threads"] = _dedup_list(packet.get("open_threads") or [])

        player = packet.get("player") or {}
        player["caused"] = _dedup_list(player.get("caused") or [])

        for eid, hist in (packet.get("entity_histories") or {}).items():
            hist["full"] = _dedup_list(hist.get("full") or [])
            hist["compressed"] = _dedup_list(hist.get("compressed") or [])

        packet["player_journey"] = _dedup_list(packet.get("player_journey") or [])
        packet["world_bleed"] = _dedup_list(packet.get("world_bleed") or [])
