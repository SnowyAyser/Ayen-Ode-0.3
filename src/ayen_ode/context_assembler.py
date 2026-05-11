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

        packet = {
            "game_time": {
                "seconds": time_row["game_time_seconds"] if time_row else 0,
                "label": time_row["game_time_label"] if time_row else "",
            },
            "scene": scene,
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
        """Serialize the packet to compact JSON for system prompt injection."""
        return json.dumps(packet, indent=2, ensure_ascii=False)

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
