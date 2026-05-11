"""Tests for ContextAssembler and get_unresolved_threads."""

import json
from pathlib import Path
import unittest
import uuid

from ayen_ode.service import AyenOdeService
from ayen_ode.context_assembler import ContextAssembler


class ContextAssemblerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db_root = Path.cwd() / "data" / "test-dbs"
        self.db_root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_root / f"{uuid.uuid4().hex}.db"
        self.svc = AyenOdeService(self.db_path)
        self.world = self.svc.create_world("Test World", "A test premise.")["world"]
        self.wid = self.world["world_id"]
        self.assembler = ContextAssembler(self.svc)

    def tearDown(self) -> None:
        for path in self.db_root.glob(f"{self.db_path.name}*"):
            path.unlink(missing_ok=True)

    def _entity(self, name: str, etype: str = "location") -> dict:
        return self.svc.create_entity(name=name, entity_type=etype, world=self.wid)["entity"]

    def _move(self, entity_id: str, container_id: str) -> None:
        self.svc.move(entity_id, container_id, world=self.wid)

    def _consequence(self, cause_id: str, target_id: str, effect_type: str = "state_changed", detail: str = "") -> dict:
        return self.svc.record_consequence(cause_id, effect_type, target_id, detail, world=self.wid)

    # ------------------------------------------------------------------
    # T1: assemble with no player entity returns valid empty player section
    # ------------------------------------------------------------------

    def test_t1_no_player_returns_empty_player(self) -> None:
        packet = self.assembler.assemble(self.wid, None)
        self.assertIsNone(packet["player"]["entity"])
        self.assertEqual(packet["player"]["knowledge_witnessed"], [])
        self.assertEqual(packet["player"]["inventory"], [])
        self.assertIsNone(packet["scene"]["current_container"])
        self.assertEqual(packet["scene"]["contents"], [])

    # ------------------------------------------------------------------
    # T2: player in a container → scene.current_container matches
    # ------------------------------------------------------------------

    def test_t2_player_in_container_scene(self) -> None:
        room = self._entity("Tavern", "location")
        player = self._entity("Aryn", "character")
        self._move(player["entity_id"], room["entity_id"])

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        self.assertIsNotNone(packet["scene"]["current_container"])
        self.assertEqual(packet["scene"]["current_container"]["entity_id"], room["entity_id"])

    # ------------------------------------------------------------------
    # T3: adjacent containers (sibling rooms sharing a parent)
    # ------------------------------------------------------------------

    def test_t3_adjacent_containers(self) -> None:
        building = self._entity("Castle", "location")
        room1 = self._entity("Hall", "location")
        room2 = self._entity("Cellar", "location")
        player = self._entity("Aryn", "character")

        self._move(room1["entity_id"], building["entity_id"])
        self._move(room2["entity_id"], building["entity_id"])
        self._move(player["entity_id"], room1["entity_id"])

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        adj_ids = [adj["container"]["entity_id"] for adj in packet["scene"]["adjacent_containers"]]
        self.assertIn(room2["entity_id"], adj_ids)
        self.assertNotIn(room1["entity_id"], adj_ids)

    # ------------------------------------------------------------------
    # T4: actor awareness filters out off-scene knowledge
    # ------------------------------------------------------------------

    def test_t4_actor_awareness_filters_to_scene(self) -> None:
        room = self._entity("Tavern", "location")
        barkeeper = self._entity("Grom", "character")
        player = self._entity("Aryn", "character")
        offscene = self._entity("Distant Lord", "character")

        self._move(barkeeper["entity_id"], room["entity_id"])
        self._move(player["entity_id"], room["entity_id"])
        # Barkeeper knows about both player (in scene) and offscene (not in scene)
        self.svc.learn(barkeeper["entity_id"], player["entity_id"], "witnessed", world=self.wid)
        self.svc.learn(barkeeper["entity_id"], offscene["entity_id"], "heard_rumor", world=self.wid)

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        awareness = packet["actor_awareness"].get(barkeeper["entity_id"])
        self.assertIsNotNone(awareness)
        known_ids = [k["knows_about_id"] for k in awareness["scene_relevant_knowledge"]]
        self.assertIn(player["entity_id"], known_ids)
        self.assertNotIn(offscene["entity_id"], known_ids)

    # ------------------------------------------------------------------
    # T5: unresolved threads — resolved record excluded, leaf included
    # ------------------------------------------------------------------

    def test_t5_unresolved_threads(self) -> None:
        cause_entity = self._entity("EventA", "event")
        target_entity = self._entity("Target", "character")

        # csqA: cause_entity → target_entity
        csqA = self._consequence(cause_entity["entity_id"], target_entity["entity_id"])
        # csqB: csqA's consequence_id as cause → target_entity (makes csqA resolved)
        csqB = self._consequence(csqA["consequence_id"], target_entity["entity_id"])

        result = self.svc.get_unresolved_threads(world=self.wid, limit=10)
        thread_ids = [t["consequence_id"] for t in result["unresolved_threads"]]

        # csqA produced csqB → resolved
        self.assertNotIn(csqA["consequence_id"], thread_ids)
        # csqB has no downstream → unresolved
        self.assertIn(csqB["consequence_id"], thread_ids)

    # ------------------------------------------------------------------
    # T6: entity history compression — top-3 by downstream count in full
    # ------------------------------------------------------------------

    def test_t6_entity_history_compression(self) -> None:
        room = self._entity("Room", "location")
        player = self._entity("Aryn", "character")
        target = self._entity("NPC", "character")
        self._move(player["entity_id"], room["entity_id"])
        self._move(target["entity_id"], room["entity_id"])

        # Create 5 consequences targeting target
        csqs = []
        for i in range(5):
            c = self._consequence(player["entity_id"], target["entity_id"], detail=f"step: {i} → {i+1}")
            csqs.append(c)

        # Give downstream effects to the first 3 (making them high-score)
        dummy = self._entity("Dummy", "object")
        for csq in csqs[:3]:
            self._consequence(csq["consequence_id"], dummy["entity_id"])

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        tid = target["entity_id"]
        self.assertIn(tid, packet["entity_histories"])
        full = packet["entity_histories"][tid]["full"]
        compressed = packet["entity_histories"][tid]["compressed"]

        self.assertEqual(len(full), 3)
        self.assertEqual(len(compressed), 2)
        # The high-score ones (first 3) should be in full
        full_ids = {r["consequence_id"] for r in full}
        for csq in csqs[:3]:
            self.assertIn(csq["consequence_id"], full_ids)

    # ------------------------------------------------------------------
    # T7: player journey pruning — off-scene fully-resolved records dropped
    # ------------------------------------------------------------------

    def test_t7_player_journey_pruning(self) -> None:
        room = self._entity("Room", "location")
        player = self._entity("Aryn", "character")
        scene_npc = self._entity("SceneNPC", "character")
        offscene_npc = self._entity("OffNPC", "character")
        self._move(player["entity_id"], room["entity_id"])
        self._move(scene_npc["entity_id"], room["entity_id"])

        # Scene-relevant consequence (player → scene_npc)
        csq_scene = self._consequence(player["entity_id"], scene_npc["entity_id"])
        # Off-scene consequence (player → offscene_npc)
        csq_off = self._consequence(player["entity_id"], offscene_npc["entity_id"])
        # Resolve csq_off (give it a downstream effect so it's not unresolved either)
        self._consequence(csq_off["consequence_id"], offscene_npc["entity_id"])

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        journey_ids = [r["consequence_id"] for r in packet["player_journey"]]

        # Scene-relevant → included
        self.assertIn(csq_scene["consequence_id"], journey_ids)
        # Off-scene AND resolved → excluded
        self.assertNotIn(csq_off["consequence_id"], journey_ids)

    # ------------------------------------------------------------------
    # T8: world bleed-in — cross-scene included, same-scene excluded
    # ------------------------------------------------------------------

    def test_t8_world_bleed(self) -> None:
        room = self._entity("Room", "location")
        player = self._entity("Aryn", "character")
        scene_npc = self._entity("SceneNPC", "character")
        offscene_npc = self._entity("OffNPC", "character")
        self._move(player["entity_id"], room["entity_id"])
        self._move(scene_npc["entity_id"], room["entity_id"])

        # Cross-scene: scene_npc caused something to offscene_npc
        csq_cross = self._consequence(scene_npc["entity_id"], offscene_npc["entity_id"])
        # Same-scene: scene_npc caused something to player
        csq_same = self._consequence(scene_npc["entity_id"], player["entity_id"])

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        bleed_ids = [r["consequence_id"] for r in packet["world_bleed"]]

        self.assertIn(csq_cross["consequence_id"], bleed_ids)
        self.assertNotIn(csq_same["consequence_id"], bleed_ids)

    # ------------------------------------------------------------------
    # T9: packet is JSON-serializable
    # ------------------------------------------------------------------

    def test_t9_packet_is_json_serializable(self) -> None:
        room = self._entity("Room", "location")
        player = self._entity("Aryn", "character")
        self._move(player["entity_id"], room["entity_id"])
        packet = self.assembler.assemble(self.wid, player["entity_id"])
        text = self.assembler.to_prompt_text(packet)
        parsed = json.loads(text)
        self.assertIn("scene", parsed)
        self.assertIn("player", parsed)

    # ------------------------------------------------------------------
    # T10: empty world — completes without error
    # ------------------------------------------------------------------

    def test_t10_empty_world_no_error(self) -> None:
        packet = self.assembler.assemble(self.wid, None)
        self.assertIsInstance(packet, dict)
        self.assertIn("scene", packet)
        self.assertIn("open_threads", packet)

    # ------------------------------------------------------------------
    # T11: container chain upward is populated
    # ------------------------------------------------------------------

    def test_t11_container_chain_populated(self) -> None:
        city = self._entity("Ashford", "location")
        district = self._entity("Market Quarter", "location")
        room = self._entity("Bazaar", "location")
        player = self._entity("Aryn", "character")

        self._move(district["entity_id"], city["entity_id"])
        self._move(room["entity_id"], district["entity_id"])
        self._move(player["entity_id"], room["entity_id"])

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        chain_ids = [e["entity_id"] for e in packet["scene"]["container_chain"]]

        self.assertIn(room["entity_id"], chain_ids)
        self.assertIn(district["entity_id"], chain_ids)
        self.assertIn(city["entity_id"], chain_ids)
        # Innermost first
        self.assertEqual(chain_ids[0], room["entity_id"])

    # ------------------------------------------------------------------
    # T12: player inventory populated
    # ------------------------------------------------------------------

    def test_t12_player_inventory(self) -> None:
        room = self._entity("Room", "location")
        player = self._entity("Aryn", "character")
        key = self._entity("Iron Key", "object")
        self._move(player["entity_id"], room["entity_id"])
        self._move(key["entity_id"], player["entity_id"])

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        inv_ids = [e["entity_id"] for e in packet["player"]["inventory"]]
        self.assertIn(key["entity_id"], inv_ids)

    # ------------------------------------------------------------------
    # T13: relationship history direction tagging
    # ------------------------------------------------------------------

    def test_t13_relationship_history_directions(self) -> None:
        room = self._entity("Room", "location")
        npc = self._entity("Grom", "character")
        player = self._entity("Aryn", "character")
        self._move(npc["entity_id"], room["entity_id"])
        self._move(player["entity_id"], room["entity_id"])

        # NPC learns about player
        self.svc.learn(npc["entity_id"], player["entity_id"], "witnessed", world=self.wid)

        packet = self.assembler.assemble(self.wid, player["entity_id"])
        events = packet["relationship_histories"].get(npc["entity_id"], [])
        self.assertTrue(len(events) > 0)
        # The learn event from npc about player should be tagged correctly
        char_about_player = [e for e in events if e["direction"] == "character_about_player"]
        self.assertTrue(len(char_about_player) > 0)
