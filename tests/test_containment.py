"""Tests for the unified containment system."""

from pathlib import Path
import unittest
import uuid

from ayen_ode.service import AyenOdeService


class ContainmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db_root = Path.cwd() / "data" / "test-dbs"
        self.db_root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_root / f"{uuid.uuid4().hex}.db"
        self.svc = AyenOdeService(self.db_path)
        self.world = self.svc.create_world("Test World", "A test world.")["world"]
        self.wid = self.world["world_id"]

    def tearDown(self) -> None:
        for path in self.db_root.glob(f"{self.db_path.name}*"):
            path.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _entity(self, name: str, etype: str = "location") -> dict:
        return self.svc.create_entity(name=name, entity_type=etype, world=self.wid)["entity"]

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_place_entity_in_container(self) -> None:
        room = self._entity("Tavern", "location")
        char = self._entity("Anya", "character")
        self.svc.move(char["entity_id"], room["entity_id"], world=self.wid)
        result = self.svc.get_contents(room["entity_id"], world=self.wid)
        ids = [e["entity_id"] for e in result["contents"]]
        self.assertIn(char["entity_id"], ids)

    def test_recursive_contents(self) -> None:
        room = self._entity("Room", "location")
        chest = self._entity("Chest", "object")
        sword = self._entity("Sword", "object")
        self.svc.move(chest["entity_id"], room["entity_id"], world=self.wid)
        self.svc.move(sword["entity_id"], chest["entity_id"], world=self.wid)
        result = self.svc.get_contents_recursive(room["entity_id"], world=self.wid)
        ids = {e["entity_id"] for e in result["entities"]}
        self.assertIn(chest["entity_id"], ids)
        self.assertIn(sword["entity_id"], ids)

    def test_recursive_contents_excludes_root(self) -> None:
        room = self._entity("Room", "location")
        child = self._entity("Chair", "object")
        self.svc.move(child["entity_id"], room["entity_id"], world=self.wid)
        result = self.svc.get_contents_recursive(room["entity_id"], world=self.wid)
        ids = {e["entity_id"] for e in result["entities"]}
        self.assertNotIn(room["entity_id"], ids)

    def test_container_chain(self) -> None:
        building = self._entity("Castle", "location")
        room = self._entity("Hall", "location")
        chest = self._entity("Chest", "object")
        sword = self._entity("Sword", "object")
        self.svc.move(room["entity_id"], building["entity_id"], world=self.wid)
        self.svc.move(chest["entity_id"], room["entity_id"], world=self.wid)
        self.svc.move(sword["entity_id"], chest["entity_id"], world=self.wid)
        result = self.svc.get_container_chain(sword["entity_id"], world=self.wid)
        chain_ids = [e["entity_id"] for e in result["chain"]]
        self.assertEqual(chain_ids[0], sword["entity_id"])
        self.assertEqual(chain_ids[-1], building["entity_id"])
        self.assertEqual(len(chain_ids), 4)

    def test_container_chain_root_entity_returns_only_itself(self) -> None:
        region = self._entity("The North", "location")
        result = self.svc.get_container_chain(region["entity_id"], world=self.wid)
        self.assertEqual(len(result["chain"]), 1)
        self.assertEqual(result["chain"][0]["entity_id"], region["entity_id"])

    def test_siblings(self) -> None:
        room = self._entity("Tavern", "location")
        char_a = self._entity("Anya", "character")
        char_b = self._entity("Bram", "character")
        self.svc.move(char_a["entity_id"], room["entity_id"], world=self.wid)
        self.svc.move(char_b["entity_id"], room["entity_id"], world=self.wid)
        result = self.svc.get_siblings(char_a["entity_id"], world=self.wid)
        ids = [e["entity_id"] for e in result["siblings"]]
        self.assertIn(char_b["entity_id"], ids)
        self.assertNotIn(char_a["entity_id"], ids)

    def test_move_fires_hook(self) -> None:
        room = self._entity("Haunted Room", "location")
        char = self._entity("Anya", "character")
        # Register an "enter" hook that reduces Anya's will by 10
        self.svc.register_containment_hook(
            trigger_event_type="enter",
            action_type="stat_change",
            action_params={"entity_id": char["entity_id"], "stat": "will", "delta": -10, "reason": "cursed room"},
            trigger_container_id=room["entity_id"],
            world=self.wid,
        )
        result = self.svc.move(char["entity_id"], room["entity_id"], world=self.wid)
        self.assertEqual(len(result["triggered_hooks"]), 1)
        hook_result = result["triggered_hooks"][0]["result"]
        self.assertEqual(hook_result["stat"], "will")
        self.assertEqual(hook_result["delta"], -10)

    def test_circular_containment_rejected(self) -> None:
        room = self._entity("Room", "location")
        chest = self._entity("Chest", "object")
        self.svc.move(chest["entity_id"], room["entity_id"], world=self.wid)
        with self.assertRaises(ValueError):
            self.svc.move(room["entity_id"], chest["entity_id"], world=self.wid)

    def test_self_reference_rejected(self) -> None:
        entity = self._entity("Bag of Holding", "object")
        with self.assertRaises(ValueError):
            self.svc.move(entity["entity_id"], entity["entity_id"], world=self.wid)

    def test_move_to_null_makes_root(self) -> None:
        room = self._entity("Room", "location")
        char = self._entity("Anya", "character")
        self.svc.move(char["entity_id"], room["entity_id"], world=self.wid)
        self.svc.move(char["entity_id"], None, world=self.wid)
        result = self.svc.get_contents(room["entity_id"], world=self.wid)
        ids = [e["entity_id"] for e in result["contents"]]
        self.assertNotIn(char["entity_id"], ids)

    def test_move_logs_containment_event(self) -> None:
        room = self._entity("Room", "location")
        char = self._entity("Anya", "character")
        self.svc.move(char["entity_id"], room["entity_id"], world=self.wid)
        events = self.svc.get_containment_events(world=self.wid, entity_id=char["entity_id"])
        self.assertEqual(len(events["events"]), 1)
        self.assertEqual(events["events"][0]["to_container_id"], room["entity_id"])

    def test_container_id_returned_in_entity_dict(self) -> None:
        room = self._entity("Room", "location")
        char = self._entity("Anya", "character")
        self.svc.move(char["entity_id"], room["entity_id"], world=self.wid)
        entity = self.svc.get_entity(char["entity_id"], world=self.wid)["entity"]
        self.assertEqual(entity["container_id"], room["entity_id"])

    def test_wildcard_hook_fires_for_any_container(self) -> None:
        room_a = self._entity("Room A", "location")
        room_b = self._entity("Room B", "location")
        char = self._entity("Wanderer", "character")
        # Hook with no trigger_container_id fires for any container entry
        self.svc.register_containment_hook(
            trigger_event_type="enter",
            action_type="log_note",
            action_params={"note": "entered somewhere"},
            world=self.wid,
        )
        result_a = self.svc.move(char["entity_id"], room_a["entity_id"], world=self.wid)
        self.assertEqual(len(result_a["triggered_hooks"]), 1)
        result_b = self.svc.move(char["entity_id"], room_b["entity_id"], world=self.wid)
        # Moving from A to B fires both exit (A) and enter (B) — hook matches enter(B)
        hook_types = {h["action_type"] for h in result_b["triggered_hooks"]}
        self.assertIn("log_note", hook_types)
