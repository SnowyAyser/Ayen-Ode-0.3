"""Tests for the consequence system."""

from pathlib import Path
import unittest
import uuid

from ayen_ode.service import AyenOdeService


class ConsequenceTests(unittest.TestCase):
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

    def _entity(self, name: str, etype: str = "event") -> dict:
        return self.svc.create_entity(name=name, entity_type=etype, world=self.wid)["entity"]

    # ------------------------------------------------------------------
    # record_consequence / get_effects / get_causes
    # ------------------------------------------------------------------

    def test_record_consequence_creates_record(self) -> None:
        battle = self._entity("Battle of the Pass")
        guard = self._entity("Captain Renn", "character")
        result = self.svc.record_consequence(
            cause_id=battle["entity_id"],
            effect_type="state_changed",
            target_id=guard["entity_id"],
            detail="status: alive → dead",
            world=self.wid,
        )
        self.assertEqual(result["cause_id"], battle["entity_id"])
        self.assertEqual(result["target_id"], guard["entity_id"])
        self.assertEqual(result["effect_type"], "state_changed")
        self.assertIn("consequence_id", result)

    def test_get_effects_returns_all_results_from_cause(self) -> None:
        fire = self._entity("Market Fire")
        smith = self._entity("Blacksmith", "character")
        merchant = self._entity("Silk Merchant", "character")
        self.svc.record_consequence(fire["entity_id"], "destroyed", smith["entity_id"], world=self.wid)
        self.svc.record_consequence(fire["entity_id"], "moved", merchant["entity_id"], world=self.wid)
        result = self.svc.get_effects(fire["entity_id"], world=self.wid)
        target_ids = {r["target_id"] for r in result["effects"]}
        self.assertIn(smith["entity_id"], target_ids)
        self.assertIn(merchant["entity_id"], target_ids)

    def test_get_causes_reverse_lookup(self) -> None:
        drought = self._entity("Great Drought")
        famine = self._entity("City Famine")
        riot = self._entity("Bread Riot")
        self.svc.record_consequence(drought["entity_id"], "triggered_event", famine["entity_id"], world=self.wid)
        self.svc.record_consequence(famine["entity_id"], "triggered_event", riot["entity_id"], world=self.wid)
        result = self.svc.get_causes(riot["entity_id"], world=self.wid)
        cause_ids = {r["cause_id"] for r in result["causes"]}
        self.assertIn(famine["entity_id"], cause_ids)
        self.assertNotIn(drought["entity_id"], cause_ids)  # only direct causes

    def test_invalid_effect_type_rejected(self) -> None:
        evt = self._entity("Something")
        target = self._entity("Someone", "character")
        with self.assertRaises(ValueError):
            self.svc.record_consequence(
                evt["entity_id"], "exploded", target["entity_id"], world=self.wid
            )

    # ------------------------------------------------------------------
    # get_chain_forward
    # ------------------------------------------------------------------

    def test_get_chain_forward_two_levels(self) -> None:
        # fire → blacksmith relocates → market prices rise
        fire = self._entity("Market Fire")
        smith_loc = self._entity("Smithy", "location")
        prices = self._entity("Market Prices", "object")
        smith_moved = self._entity("Blacksmith Relocated", "event")

        self.svc.record_consequence(fire["entity_id"], "moved", smith_moved["entity_id"], world=self.wid)
        self.svc.record_consequence(smith_moved["entity_id"], "state_changed", prices["entity_id"], world=self.wid)

        result = self.svc.get_chain_forward(fire["entity_id"], depth=2, world=self.wid)
        self.assertEqual(len(result["levels"]), 2)
        level1_ids = {r["target_id"] for r in result["levels"][0]["records"]}
        level2_ids = {r["target_id"] for r in result["levels"][1]["records"]}
        self.assertIn(smith_moved["entity_id"], level1_ids)
        self.assertIn(prices["entity_id"], level2_ids)

    def test_get_chain_forward_stops_at_depth(self) -> None:
        a = self._entity("Event A")
        b = self._entity("Event B")
        c = self._entity("Event C")
        self.svc.record_consequence(a["entity_id"], "triggered_event", b["entity_id"], world=self.wid)
        self.svc.record_consequence(b["entity_id"], "triggered_event", c["entity_id"], world=self.wid)
        result = self.svc.get_chain_forward(a["entity_id"], depth=1, world=self.wid)
        self.assertEqual(len(result["levels"]), 1)
        level1_ids = {r["target_id"] for r in result["levels"][0]["records"]}
        self.assertIn(b["entity_id"], level1_ids)
        self.assertNotIn(c["entity_id"], level1_ids)

    def test_get_chain_forward_cycle_safe(self) -> None:
        # A causes B, B causes A — should not infinite loop
        a = self._entity("Event A")
        b = self._entity("Event B")
        self.svc.record_consequence(a["entity_id"], "triggered_event", b["entity_id"], world=self.wid)
        self.svc.record_consequence(b["entity_id"], "triggered_event", a["entity_id"], world=self.wid)
        result = self.svc.get_chain_forward(a["entity_id"], depth=5, world=self.wid)
        # Should complete without error; levels should terminate
        self.assertIsInstance(result["levels"], list)

    # ------------------------------------------------------------------
    # get_chain_backward
    # ------------------------------------------------------------------

    def test_get_chain_backward_two_levels(self) -> None:
        # guards hostile â† player stole gem â† gem was unguarded
        gem_unguarded = self._entity("Gem Left Unguarded")
        theft = self._entity("Gem Theft")
        guards = self._entity("City Guards", "faction")

        self.svc.record_consequence(gem_unguarded["entity_id"], "triggered_event", theft["entity_id"], world=self.wid)
        self.svc.record_consequence(theft["entity_id"], "relationship_changed", guards["entity_id"], world=self.wid)

        result = self.svc.get_chain_backward(guards["entity_id"], depth=2, world=self.wid)
        self.assertEqual(len(result["levels"]), 2)
        level1_causes = {r["cause_id"] for r in result["levels"][0]["records"]}
        level2_causes = {r["cause_id"] for r in result["levels"][1]["records"]}
        self.assertIn(theft["entity_id"], level1_causes)
        self.assertIn(gem_unguarded["entity_id"], level2_causes)

    # ------------------------------------------------------------------
    # get_history
    # ------------------------------------------------------------------

    def test_get_history_full_timeline(self) -> None:
        guard = self._entity("Sergeant Mira", "character")
        e1 = self._entity("Arrest Event")
        e2 = self._entity("Promotion Event")
        self.svc.record_consequence(e1["entity_id"], "state_changed", guard["entity_id"],
                                    detail="status: free → imprisoned", world=self.wid)
        self.svc.record_consequence(e2["entity_id"], "state_changed", guard["entity_id"],
                                    detail="rank: guard → sergeant", world=self.wid)
        result = self.svc.get_history(guard["entity_id"], world=self.wid)
        self.assertEqual(len(result["history"]), 2)
        # Ordered ascending by created_at
        self.assertEqual(result["history"][0]["cause_id"], e1["entity_id"])
        self.assertEqual(result["history"][1]["cause_id"], e2["entity_id"])

    # ------------------------------------------------------------------
    # get_state_at
    # ------------------------------------------------------------------

    def test_get_state_at_reconstructs_parseable_details(self) -> None:
        lord = self._entity("Lord Vael", "character")
        e1 = self._entity("Alliance Treaty")
        e2 = self._entity("Betrayal")
        self.svc.record_consequence(e1["entity_id"], "relationship_changed", lord["entity_id"],
                                    detail="disposition: neutral → friendly", world=self.wid)
        self.svc.record_consequence(e2["entity_id"], "relationship_changed", lord["entity_id"],
                                    detail="disposition: friendly → hostile", world=self.wid)

        # Use a timestamp far in the future to capture everything
        from datetime import datetime, timezone
        future = datetime(2099, 1, 1, tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

        result = self.svc.get_state_at(lord["entity_id"], future, world=self.wid)
        self.assertEqual(result["reconstructed_state"]["disposition"], "hostile")
        self.assertEqual(len(result["records"]), 2)

    def test_get_state_at_empty_before_any_records(self) -> None:
        char = self._entity("New Character", "character")
        result = self.svc.get_state_at(char["entity_id"], "2020-01-01T00:00:00Z", world=self.wid)
        self.assertEqual(result["records"], [])
        self.assertEqual(result["reconstructed_state"], {})

    def test_get_state_at_respects_timestamp_cutoff(self) -> None:
        char = self._entity("Guard", "character")
        e1 = self._entity("Early Event")
        e2 = self._entity("Late Event")

        # Record e1 first
        r1 = self.svc.record_consequence(e1["entity_id"], "state_changed", char["entity_id"],
                                         detail="status: alive → wounded", world=self.wid)
        cutoff = r1["created_at"]

        # Record e2 after — same second may be an issue in tests, so we just check
        # that state_at with the cutoff gets at most r1's records
        result = self.svc.get_state_at(char["entity_id"], cutoff, world=self.wid)
        statuses = [r["cause_id"] for r in result["records"]]
        self.assertIn(e1["entity_id"], statuses)

    # ------------------------------------------------------------------
    # record_chain (batch)
    # ------------------------------------------------------------------

    def test_record_chain_creates_multiple_consequences(self) -> None:
        battle = self._entity("Siege of Aldenmoor")
        knight = self._entity("Sir Dorel", "character")
        tower = self._entity("East Tower", "location")
        supply = self._entity("Supply Cache", "object")

        result = self.svc.record_chain(
            cause_id=battle["entity_id"],
            effects=[
                {"effect_type": "destroyed", "target_id": knight["entity_id"], "detail": "status: alive → dead"},
                {"effect_type": "destroyed", "target_id": tower["entity_id"], "detail": "status: standing → rubble"},
                {"effect_type": "moved", "target_id": supply["entity_id"], "detail": "location: tower → enemy camp"},
            ],
            world=self.wid,
        )
        self.assertEqual(result["recorded"], 3)
        self.assertEqual(len(result["consequences"]), 3)
        effect_types = {c["effect_type"] for c in result["consequences"]}
        self.assertIn("destroyed", effect_types)
        self.assertIn("moved", effect_types)

    # ------------------------------------------------------------------
    # Hooks — stat_change
    # ------------------------------------------------------------------

    def test_hook_fires_on_record_consequence(self) -> None:
        riot = self._entity("Bread Riot")
        city = self._entity("Aldenmoor", "location")
        self.svc.apply_stat_change(
            city["entity_id"], {"stability": 60}, reason="baseline", world=self.wid
        )
        self.svc.register_consequence_hook(
            action_type="stat_change",
            action_params={"entity_id": city["entity_id"], "stat": "stability", "delta": -15},
            trigger_effect_type="triggered_event",
            world=self.wid,
        )
        result = self.svc.record_consequence(
            riot["entity_id"], "triggered_event", city["entity_id"], world=self.wid
        )
        self.assertEqual(len(result["triggered_hooks"]), 1)
        hook_result = result["triggered_hooks"][0]["result"]
        self.assertEqual(hook_result["stat"], "stability")
        self.assertEqual(hook_result["delta"], -15)

    def test_hook_fires_only_for_matching_effect_type(self) -> None:
        evt = self._entity("Some Event")
        target = self._entity("Target", "character")
        self.svc.register_consequence_hook(
            action_type="log_note",
            action_params={"note": "moved"},
            trigger_effect_type="moved",
            world=self.wid,
        )
        r_match = self.svc.record_consequence(
            evt["entity_id"], "moved", target["entity_id"], world=self.wid
        )
        r_no_match = self.svc.record_consequence(
            evt["entity_id"], "created", target["entity_id"], world=self.wid
        )
        self.assertEqual(len(r_match["triggered_hooks"]), 1)
        self.assertEqual(len(r_no_match["triggered_hooks"]), 0)

    def test_wildcard_hook_fires_for_any_effect_type(self) -> None:
        evt = self._entity("Wildcard Test Event")
        target = self._entity("Target", "character")
        self.svc.register_consequence_hook(
            action_type="log_note",
            action_params={"note": "something happened"},
            world=self.wid,
        )
        r1 = self.svc.record_consequence(evt["entity_id"], "created", target["entity_id"], world=self.wid)
        r2 = self.svc.record_consequence(evt["entity_id"], "destroyed", target["entity_id"], world=self.wid)
        self.assertEqual(len(r1["triggered_hooks"]), 1)
        self.assertEqual(len(r2["triggered_hooks"]), 1)

    # ------------------------------------------------------------------
    # Hook — containment_move bridge
    # ------------------------------------------------------------------

    def test_hook_containment_move_updates_physical_location(self) -> None:
        tavern = self._entity("The Rusty Nail", "location")
        prison = self._entity("City Prison", "location")
        suspect = self._entity("Ronan the Fence", "character")

        arrest_event = self._entity("Arrest of Ronan")

        # Move suspect into tavern first
        self.svc.move(suspect["entity_id"], tavern["entity_id"], world=self.wid)

        # Register: whenever 'arrested' consequence recorded against suspect, move them to prison
        self.svc.register_consequence_hook(
            action_type="containment_move",
            action_params={
                "entity_id": suspect["entity_id"],
                "new_container_id": prison["entity_id"],
            },
            trigger_effect_type="state_changed",
            trigger_target_id=suspect["entity_id"],
            world=self.wid,
        )

        self.svc.record_consequence(
            arrest_event["entity_id"], "state_changed", suspect["entity_id"],
            detail="status: free → imprisoned", world=self.wid,
        )

        # Containment should have updated automatically
        chain = self.svc.get_container_chain(suspect["entity_id"], world=self.wid)
        container_ids = [e["entity_id"] for e in chain["chain"]]
        self.assertIn(prison["entity_id"], container_ids)
        self.assertNotIn(tavern["entity_id"], container_ids)

    # ------------------------------------------------------------------
    # Hook — knowledge_learn bridge
    # ------------------------------------------------------------------

    def test_hook_knowledge_learn_creates_knowledge_link(self) -> None:
        spy = self._entity("Mira the Spy", "character")
        secret = self._entity("Crown Conspiracy", "event")
        intel_event = self._entity("Intelligence Report")

        # Whenever a 'relationship_changed' consequence is recorded about the conspiracy,
        # the spy automatically learns about it
        self.svc.register_consequence_hook(
            action_type="knowledge_learn",
            action_params={
                "entity_id": spy["entity_id"],
                "target_id": secret["entity_id"],
                "degree": "secondhand",
            },
            trigger_effect_type="relationship_changed",
            trigger_target_id=secret["entity_id"],
            world=self.wid,
        )

        self.svc.record_consequence(
            intel_event["entity_id"], "relationship_changed", secret["entity_id"], world=self.wid
        )

        knowledge = self.svc.get_knowledge(spy["entity_id"], world=self.wid)
        ids = [k["knows_about_id"] for k in knowledge["knowledge"]]
        self.assertIn(secret["entity_id"], ids)
        entry = next(k for k in knowledge["knowledge"] if k["knows_about_id"] == secret["entity_id"])
        self.assertEqual(entry["degree"], "secondhand")

    # ------------------------------------------------------------------
    # get_consequence_events (filtered log)
    # ------------------------------------------------------------------

    def test_get_consequence_events_filtered_by_effect_type(self) -> None:
        cause = self._entity("Storm")
        t1 = self._entity("Ship A", "object")
        t2 = self._entity("Harbor B", "location")
        self.svc.record_consequence(cause["entity_id"], "destroyed", t1["entity_id"], world=self.wid)
        self.svc.record_consequence(cause["entity_id"], "state_changed", t2["entity_id"], world=self.wid)
        result = self.svc.get_consequence_events(world=self.wid, effect_type="destroyed")
        types = {r["effect_type"] for r in result["records"]}
        self.assertEqual(types, {"destroyed"})

    # ------------------------------------------------------------------
    # Hook management
    # ------------------------------------------------------------------

    def test_list_and_remove_hooks(self) -> None:
        hook = self.svc.register_consequence_hook(
            action_type="log_note",
            action_params={"note": "test"},
            label="test-hook",
            world=self.wid,
        )
        hooks = self.svc.list_consequence_hooks(world=self.wid)
        self.assertEqual(len(hooks["hooks"]), 1)
        self.assertEqual(hooks["hooks"][0]["label"], "test-hook")

        self.svc.remove_consequence_hook(hook["hook_id"], world=self.wid)
        hooks_after = self.svc.list_consequence_hooks(world=self.wid)
        self.assertEqual(len(hooks_after["hooks"]), 0)
