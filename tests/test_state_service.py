from pathlib import Path
import unittest
import uuid

from ayen_ode.service import AyenOdeService


class AyenOdeServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db_root = Path.cwd() / "data" / "test-dbs"
        self.db_root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_root / f"{uuid.uuid4().hex}.db"
        self.service = AyenOdeService(self.db_path)

    def tearDown(self) -> None:
        for path in self.db_root.glob(f"{self.db_path.name}*"):
            path.unlink(missing_ok=True)

    def test_world_switching_restores_isolated_handoffs_and_entities(self) -> None:
        world_a = self.service.create_world("Ash Vale", "A haunted frontier.")["world"]
        self.service.save_world_handoff("Ash Vale handoff.", world=world_a["slug"])
        entity_a = self.service.create_entity(
            name="Mira",
            entity_type="character",
            summary="A wary guide.",
            stats={"will": 60},
        )["entity"]

        world_b = self.service.create_world("Glass Harbor", "A city of masks.")["world"]
        self.service.save_world_handoff("Glass Harbor handoff.", world=world_b["slug"])
        entity_b = self.service.create_entity(
            name="The Blue Choir",
            entity_type="faction",
            summary="A hidden faction.",
            stats={"secrecy": 70},
        )["entity"]

        restored = self.service.switch_world(world_a["slug"])
        self.assertEqual(restored["restored_handoff"], "Ash Vale handoff.")

        active_entities = self.service.list_entities()["entities"]
        self.assertEqual([entity["entity_id"] for entity in active_entities], [entity_a["entity_id"]])
        with self.assertRaises(ValueError):
            self.service.get_entity(entity_b["entity_id"])

    def test_only_one_world_is_active(self) -> None:
        world_a = self.service.create_world("First World", "One.")["world"]
        world_b = self.service.create_world("Second World", "Two.")["world"]

        worlds = self.service.list_worlds()["worlds"]
        active = [world for world in worlds if world["status"] == "active"]
        paused = [world for world in worlds if world["status"] == "paused"]

        self.assertEqual([world["world_id"] for world in active], [world_b["world_id"]])
        self.assertEqual([world["world_id"] for world in paused], [world_a["world_id"]])

    def test_compare_rejects_cross_world_entity_lookup(self) -> None:
        world_a = self.service.create_world("A", "First.")["world"]
        entity_a = self.service.create_entity(
            name="Asha",
            entity_type="character",
            stats={"force": 45},
        )["entity"]
        world_b = self.service.create_world("B", "Second.")["world"]
        entity_b = self.service.create_entity(
            name="Boros",
            entity_type="character",
            stats={"force": 55},
        )["entity"]

        with self.assertRaises(ValueError):
            self.service.compare_entities(entity_a["entity_id"], entity_b["entity_id"], world=world_a["slug"])

        comparison = self.service.compare_entities(entity_b["entity_id"], entity_b["entity_id"], world=world_b["slug"])
        self.assertEqual(comparison["differences"][0]["relation"], "equal")

    def test_stat_change_and_reconciliation_suggestions(self) -> None:
        self.service.create_world("Linked World", "Linked stats.")
        source = self.service.create_entity(
            name="Source",
            entity_type="character",
            stats={"will": 50, "force": 40},
        )["entity"]
        linked = self.service.create_entity(
            name="Linked",
            entity_type="character",
            stats={"will": 40, "force": 40},
        )["entity"]
        self.service.link_entities(source["entity_id"], linked["entity_id"], relation="rivals")

        result = self.service.apply_stat_change(
            source["entity_id"],
            changes={"will": 12},
            reason="A decisive victory.",
        )

        self.assertEqual(result["after"]["will"], 62)
        self.assertEqual(result["reconciliation_suggestions"][0]["suggested_deltas"], {"will": 6})

        applied = self.service.reconcile_linked_stats(
            source["entity_id"],
            changes={"will": 12},
            reason="Cascade test.",
            apply=True,
        )
        self.assertEqual(applied["applied"][0]["after"]["will"], 46)


if __name__ == "__main__":
    unittest.main()
