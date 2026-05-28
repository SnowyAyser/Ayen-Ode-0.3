"""Tests for the Semantic Debts and Containment Type Constraint validations."""

from pathlib import Path
import unittest
import uuid

from ayen_ode.service import AyenOdeService


class ArchTests(unittest.TestCase):
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

    def _entity(self, name: str, etype: str) -> dict:
        return self.svc.create_entity(name=name, entity_type=etype, world=self.wid)["entity"]

    # ------------------------------------------------------------------
    # Debts (Quadruplets) Tests
    # ------------------------------------------------------------------

    def test_record_and_satisfy_debt(self) -> None:
        debtor = self._entity("Debtor Character", "character")
        creditor = self._entity("Creditor Character", "character")

        # Record a quadruplet debt: Debtor owes Creditor 3 cows
        debt = self.svc.record_debt(
            debtor_id=debtor["entity_id"],
            creditor_id=creditor["entity_id"],
            resource_type="cows",
            quantity="3",
            detail="borrowed for breeding",
            evidence="He promised to repay 3 cows",
            world=self.wid,
        )

        self.assertEqual(debt["debtor_id"], debtor["entity_id"])
        self.assertEqual(debt["creditor_id"], creditor["entity_id"])
        self.assertEqual(debt["resource_type"], "cows")
        self.assertEqual(debt["quantity"], "3")
        self.assertEqual(debt["status"], "active")

        # List active debts
        active_debts = self.svc.list_active_debts(world=self.wid)["debts"]
        self.assertEqual(len(active_debts), 1)
        self.assertEqual(active_debts[0]["debt_id"], debt["debt_id"])

        # Satisfy the debt
        resolved = self.svc.update_debt_status(
            debt_id=debt["debt_id"],
            status="satisfied",
            detail="repaid all 3 cows",
            world=self.wid,
        )
        self.assertEqual(resolved["status"], "satisfied")
        self.assertEqual(resolved["detail"], "repaid all 3 cows")

        # Check list active is empty
        active_debts_after = self.svc.list_active_debts(world=self.wid)["debts"]
        self.assertEqual(len(active_debts_after), 0)

        # Check list history has the satisfied debt
        history_debts = self.svc.list_debt_history(world=self.wid)["debts"]
        self.assertEqual(len(history_debts), 1)
        self.assertEqual(history_debts[0]["debt_id"], debt["debt_id"])

    def test_invalid_debt_entities_raise_error(self) -> None:
        char = self._entity("Valid Character", "character")
        with self.assertRaises(ValueError):
            # Invalid creditor_id
            self.svc.record_debt(
                debtor_id=char["entity_id"],
                creditor_id="invalid_id",
                resource_type="gold",
                quantity="50",
                detail="test",
                world=self.wid,
            )

    # ------------------------------------------------------------------
    # Containment Type Constraints Tests
    # ------------------------------------------------------------------

    def test_valid_containment_placements(self) -> None:
        room = self._entity("Garrison Room", "location")
        chest = self._entity("Lockbox", "object")
        sword = self._entity("Iron Sword", "object")
        char = self._entity("Guard Vane", "character")

        # Locations can contain Locations, Characters, and Objects
        sub_room = self._entity("Closet", "location")
        self.svc.move(sub_room["entity_id"], room["entity_id"], world=self.wid)
        self.svc.move(char["entity_id"], room["entity_id"], world=self.wid)
        self.svc.move(chest["entity_id"], room["entity_id"], world=self.wid)

        # Characters can contain Objects (inventory)
        self.svc.move(sword["entity_id"], char["entity_id"], world=self.wid)

        # Objects can contain Objects
        map_scroll = self._entity("Map Scroll", "object")
        self.svc.move(map_scroll["entity_id"], chest["entity_id"], world=self.wid)

        # Verify placement succeeded
        self.assertEqual(self.svc.get_entity(sub_room["entity_id"], world=self.wid)["entity"]["container_id"], room["entity_id"])
        self.assertEqual(self.svc.get_entity(char["entity_id"], world=self.wid)["entity"]["container_id"], room["entity_id"])
        self.assertEqual(self.svc.get_entity(chest["entity_id"], world=self.wid)["entity"]["container_id"], room["entity_id"])
        self.assertEqual(self.svc.get_entity(sword["entity_id"], world=self.wid)["entity"]["container_id"], char["entity_id"])
        self.assertEqual(self.svc.get_entity(map_scroll["entity_id"], world=self.wid)["entity"]["container_id"], chest["entity_id"])

    def test_invalid_containment_placements_rejected(self) -> None:
        room = self._entity("Garrison Room", "location")
        chest = self._entity("Lockbox", "object")
        char = self._entity("Guard Vane", "character")
        thief = self._entity("Guard Bram", "character")

        # Character cannot contain another Character
        with self.assertRaises(ValueError):
            self.svc.move(thief["entity_id"], char["entity_id"], world=self.wid)

        # Character cannot contain a Location
        with self.assertRaises(ValueError):
            self.svc.move(room["entity_id"], char["entity_id"], world=self.wid)

        # Object cannot contain a Character
        with self.assertRaises(ValueError):
            self.svc.move(char["entity_id"], chest["entity_id"], world=self.wid)

        # Object cannot contain a Location
        with self.assertRaises(ValueError):
            self.svc.move(room["entity_id"], chest["entity_id"], world=self.wid)
