"""Tests for the knowledge system."""

from pathlib import Path
import unittest
import uuid

from ayen_ode.service import AyenOdeService


class KnowledgeTests(unittest.TestCase):
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

    def _entity(self, name: str, etype: str = "character") -> dict:
        return self.svc.create_entity(name=name, entity_type=etype, world=self.wid)["entity"]

    # ------------------------------------------------------------------
    # learn / get_knowledge
    # ------------------------------------------------------------------

    def test_learn_creates_link(self) -> None:
        anya = self._entity("Anya")
        secret = self._entity("The King's Secret", "event")
        self.svc.learn(anya["entity_id"], secret["entity_id"], "witnessed", world=self.wid)
        result = self.svc.get_knowledge(anya["entity_id"], world=self.wid)
        ids = [k["knows_about_id"] for k in result["knowledge"]]
        self.assertIn(secret["entity_id"], ids)

    def test_learn_upserts_existing(self) -> None:
        anya = self._entity("Anya")
        target = self._entity("Dragon's Lair", "location")
        self.svc.learn(anya["entity_id"], target["entity_id"], "heard_rumor", world=self.wid)
        self.svc.learn(anya["entity_id"], target["entity_id"], "witnessed", world=self.wid)
        result = self.svc.get_knowledge(anya["entity_id"], world=self.wid)
        self.assertEqual(len(result["knowledge"]), 1)
        self.assertEqual(result["knowledge"][0]["degree"], "witnessed")

    def test_get_knowledge_returns_entity_snapshot(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        self.svc.learn(anya["entity_id"], bram["entity_id"], "secondhand", world=self.wid)
        result = self.svc.get_knowledge(anya["entity_id"], world=self.wid)
        entry = result["knowledge"][0]
        self.assertEqual(entry["entity"]["name"], "Bram")
        self.assertEqual(entry["degree"], "secondhand")

    # ------------------------------------------------------------------
    # get_known_by
    # ------------------------------------------------------------------

    def test_get_known_by(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        secret = self._entity("Vault Location", "location")
        self.svc.learn(anya["entity_id"], secret["entity_id"], "deeply_knows", world=self.wid)
        self.svc.learn(bram["entity_id"], secret["entity_id"], "heard_rumor", world=self.wid)
        result = self.svc.get_known_by(secret["entity_id"], world=self.wid)
        knower_ids = [k["entity"]["entity_id"] for k in result["known_by"]]
        self.assertIn(anya["entity_id"], knower_ids)
        self.assertIn(bram["entity_id"], knower_ids)

    # ------------------------------------------------------------------
    # get_shared_knowledge
    # ------------------------------------------------------------------

    def test_get_shared_knowledge(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        shared_target = self._entity("The Conspiracy", "event")
        private_target = self._entity("Anya's Secret", "event")
        self.svc.learn(anya["entity_id"], shared_target["entity_id"], "witnessed", world=self.wid)
        self.svc.learn(bram["entity_id"], shared_target["entity_id"], "heard_rumor", world=self.wid)
        self.svc.learn(anya["entity_id"], private_target["entity_id"], "deeply_knows", world=self.wid)
        result = self.svc.get_shared_knowledge(anya["entity_id"], bram["entity_id"], world=self.wid)
        shared_ids = [s["knows_about_id"] for s in result["shared"]]
        self.assertIn(shared_target["entity_id"], shared_ids)
        self.assertNotIn(private_target["entity_id"], shared_ids)
        entry = next(s for s in result["shared"] if s["knows_about_id"] == shared_target["entity_id"])
        self.assertEqual(entry["degree_a"], "witnessed")
        self.assertEqual(entry["degree_b"], "heard_rumor")

    # ------------------------------------------------------------------
    # get_knowledge_by_degree
    # ------------------------------------------------------------------

    def test_get_knowledge_by_degree(self) -> None:
        anya = self._entity("Anya")
        e1 = self._entity("Tomb A", "location")
        e2 = self._entity("Tomb B", "location")
        e3 = self._entity("Tomb C", "location")
        self.svc.learn(anya["entity_id"], e1["entity_id"], "witnessed", world=self.wid)
        self.svc.learn(anya["entity_id"], e2["entity_id"], "heard_rumor", world=self.wid)
        self.svc.learn(anya["entity_id"], e3["entity_id"], "witnessed", world=self.wid)
        result = self.svc.get_knowledge_by_degree(anya["entity_id"], "witnessed", world=self.wid)
        ids = [k["knows_about_id"] for k in result["knowledge"]]
        self.assertIn(e1["entity_id"], ids)
        self.assertIn(e3["entity_id"], ids)
        self.assertNotIn(e2["entity_id"], ids)

    def test_invalid_degree_rejected(self) -> None:
        anya = self._entity("Anya")
        target = self._entity("Mystery", "event")
        with self.assertRaises(ValueError):
            self.svc.learn(anya["entity_id"], target["entity_id"], "totally_made_up", world=self.wid)

    # ------------------------------------------------------------------
    # get_knowledge_chain
    # ------------------------------------------------------------------

    def test_get_knowledge_chain(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        event = self._entity("Council Meeting", "event")
        secret = self._entity("The Prophecy", "event")
        # Bram witnessed the secret at the event
        self.svc.learn(bram["entity_id"], secret["entity_id"], "witnessed", source_id=event["entity_id"], world=self.wid)
        # Anya heard it secondhand from Bram
        self.svc.learn(anya["entity_id"], secret["entity_id"], "secondhand", source_id=bram["entity_id"], world=self.wid)
        result = self.svc.get_knowledge_chain(anya["entity_id"], secret["entity_id"], world=self.wid)
        chain = result["chain"]
        self.assertEqual(chain[0]["entity_id"], anya["entity_id"])
        self.assertEqual(chain[1]["entity_id"], bram["entity_id"])
        self.assertEqual(len(chain), 2)

    def test_knowledge_chain_no_source_is_one_hop(self) -> None:
        anya = self._entity("Anya")
        target = self._entity("Dungeon Map", "object")
        self.svc.learn(anya["entity_id"], target["entity_id"], "deeply_knows", world=self.wid)
        result = self.svc.get_knowledge_chain(anya["entity_id"], target["entity_id"], world=self.wid)
        self.assertEqual(len(result["chain"]), 1)
        self.assertIsNone(result["chain"][0]["source_id"])

    # ------------------------------------------------------------------
    # spread
    # ------------------------------------------------------------------

    def test_spread_with_decay(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        secret = self._entity("Secret Passage", "location")
        self.svc.learn(anya["entity_id"], secret["entity_id"], "witnessed", world=self.wid)
        self.svc.spread(secret["entity_id"], anya["entity_id"], bram["entity_id"], degree_decay=1, world=self.wid)
        result = self.svc.get_knowledge(bram["entity_id"], world=self.wid)
        entry = next(k for k in result["knowledge"] if k["knows_about_id"] == secret["entity_id"])
        self.assertEqual(entry["degree"], "secondhand")
        self.assertEqual(entry["source_id"], anya["entity_id"])

    def test_spread_fabricated_stays_fabricated(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        target = self._entity("Rebel Leader", "character")
        self.svc.learn(anya["entity_id"], target["entity_id"], "fabricated", world=self.wid)
        self.svc.spread(target["entity_id"], anya["entity_id"], bram["entity_id"], degree_decay=2, world=self.wid)
        result = self.svc.get_knowledge(bram["entity_id"], world=self.wid)
        entry = next(k for k in result["knowledge"] if k["knows_about_id"] == target["entity_id"])
        self.assertEqual(entry["degree"], "fabricated")

    def test_spread_floor_at_unaware(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        target = self._entity("Old Rumor", "event")
        self.svc.learn(anya["entity_id"], target["entity_id"], "heard_rumor", world=self.wid)
        self.svc.spread(target["entity_id"], anya["entity_id"], bram["entity_id"], degree_decay=99, world=self.wid)
        result = self.svc.get_knowledge(bram["entity_id"], world=self.wid)
        entry = next(k for k in result["knowledge"] if k["knows_about_id"] == target["entity_id"])
        self.assertEqual(entry["degree"], "unaware")

    def test_spread_requires_source_knowledge(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        target = self._entity("Unknown Thing", "object")
        with self.assertRaises(ValueError):
            self.svc.spread(target["entity_id"], anya["entity_id"], bram["entity_id"], world=self.wid)

    # ------------------------------------------------------------------
    # forget / update_degree
    # ------------------------------------------------------------------

    def test_forget_removes_link(self) -> None:
        anya = self._entity("Anya")
        target = self._entity("Old Secret", "event")
        self.svc.learn(anya["entity_id"], target["entity_id"], "witnessed", world=self.wid)
        self.svc.forget(anya["entity_id"], target["entity_id"], world=self.wid)
        result = self.svc.get_knowledge(anya["entity_id"], world=self.wid)
        ids = [k["knows_about_id"] for k in result["knowledge"]]
        self.assertNotIn(target["entity_id"], ids)

    def test_update_degree(self) -> None:
        anya = self._entity("Anya")
        target = self._entity("The Heir", "character")
        self.svc.learn(anya["entity_id"], target["entity_id"], "heard_rumor", world=self.wid)
        result = self.svc.update_degree(anya["entity_id"], target["entity_id"], "witnessed", world=self.wid)
        self.assertEqual(result["old_degree"], "heard_rumor")
        self.assertEqual(result["new_degree"], "witnessed")
        knowledge = self.svc.get_knowledge(anya["entity_id"], world=self.wid)
        entry = next(k for k in knowledge["knowledge"] if k["knows_about_id"] == target["entity_id"])
        self.assertEqual(entry["degree"], "witnessed")

    def test_update_degree_requires_existing_link(self) -> None:
        anya = self._entity("Anya")
        target = self._entity("Stranger", "character")
        with self.assertRaises(ValueError):
            self.svc.update_degree(anya["entity_id"], target["entity_id"], "witnessed", world=self.wid)

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def test_learn_fires_hook(self) -> None:
        anya = self._entity("Anya")
        secret = self._entity("Crown Conspiracy", "event")
        self.svc.register_knowledge_hook(
            trigger_event_type="learn",
            action_type="log_note",
            action_params={"note": "Anya learned something dangerous"},
            trigger_entity_id=anya["entity_id"],
            world=self.wid,
        )
        result = self.svc.learn(anya["entity_id"], secret["entity_id"], "witnessed", world=self.wid)
        self.assertEqual(len(result["triggered_hooks"]), 1)
        self.assertEqual(result["triggered_hooks"][0]["action_type"], "log_note")

    def test_spread_fires_hook(self) -> None:
        anya = self._entity("Anya")
        bram = self._entity("Bram")
        secret = self._entity("Safe House", "location")
        self.svc.learn(anya["entity_id"], secret["entity_id"], "witnessed", world=self.wid)
        self.svc.register_knowledge_hook(
            trigger_event_type="learn",
            action_type="log_note",
            action_params={"note": "Bram learned about the safe house"},
            trigger_entity_id=bram["entity_id"],
            world=self.wid,
        )
        result = self.svc.spread(secret["entity_id"], anya["entity_id"], bram["entity_id"], world=self.wid)
        self.assertEqual(len(result["triggered_hooks"]), 1)

    def test_hook_fires_only_for_matching_target(self) -> None:
        anya = self._entity("Anya")
        secret_a = self._entity("Secret A", "event")
        secret_b = self._entity("Secret B", "event")
        self.svc.register_knowledge_hook(
            trigger_event_type="learn",
            action_type="log_note",
            action_params={"note": "secret A was learned"},
            trigger_target_id=secret_a["entity_id"],
            world=self.wid,
        )
        result_a = self.svc.learn(anya["entity_id"], secret_a["entity_id"], "heard_rumor", world=self.wid)
        result_b = self.svc.learn(anya["entity_id"], secret_b["entity_id"], "heard_rumor", world=self.wid)
        self.assertEqual(len(result_a["triggered_hooks"]), 1)
        self.assertEqual(len(result_b["triggered_hooks"]), 0)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def test_learn_logs_event(self) -> None:
        anya = self._entity("Anya")
        target = self._entity("Ancient Tome", "object")
        self.svc.learn(anya["entity_id"], target["entity_id"], "deeply_knows", world=self.wid)
        events = self.svc.get_knowledge_events(world=self.wid, entity_id=anya["entity_id"])
        self.assertEqual(len(events["events"]), 1)
        self.assertEqual(events["events"][0]["event_type"], "learn")
        self.assertEqual(events["events"][0]["degree"], "deeply_knows")

    def test_forget_logs_event(self) -> None:
        anya = self._entity("Anya")
        target = self._entity("Lost Memory", "event")
        self.svc.learn(anya["entity_id"], target["entity_id"], "secondhand", world=self.wid)
        self.svc.forget(anya["entity_id"], target["entity_id"], world=self.wid)
        events = self.svc.get_knowledge_events(world=self.wid, entity_id=anya["entity_id"])
        event_types = [e["event_type"] for e in events["events"]]
        self.assertIn("forget", event_types)
