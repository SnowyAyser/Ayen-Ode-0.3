#!/usr/bin/env python3
"""Apply containment placements only — run after seed_cyber_rim.py."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ayen_ode.config import load_settings
from ayen_ode.service import AyenOdeService

settings = load_settings()
svc = AyenOdeService(settings.db_path)
WORLD = "cyber-rim"

# Pull all entities from the world and build name→id dicts
raw = svc.list_entities(world=WORLD, include_archived=True)["entities"]

locs  = {e["name"]: e["entity_id"] for e in raw if e["entity_type"] == "location"}
chars = {e["name"]: e["entity_id"] for e in raw if e["entity_type"] == "character"}
objs  = {e["name"]: e["entity_id"] for e in raw if e["entity_type"] == "object"}

print(f"Loaded {len(locs)} locations, {len(chars)} characters, {len(objs)} objects.")

def move(entity_name: str, entity_dict: dict, container_name: str) -> None:
    eid = entity_dict[entity_name]
    cid = locs[container_name]
    svc.move(entity_id=eid, new_container_id=cid, world=WORLD)
    print(f"  {entity_name} → {container_name}")


print("\nâ”€â”€ Containment placements â”€â”€")

# Objects in locations
move("Neural Badge (Vellmore)",         objs, "Magrail Car Omega-7")
move("Magrail Seal Log",                objs, "Magrail Car Omega-7")
move("BioNex Prototype Canister",       objs, "Magrail Car Omega-7")
move("Ascendancy Override Chip",        objs, "Vellmore Penthouse Suite")
move("Vellmore's Private Comm Tablet",  objs, "Vellmore Penthouse Suite")
move("Vellmore Amendment Draft",        objs, "Vellmore Penthouse Suite")
move("Chrome Hand Identification Coin", objs, "Precinct 17 Evidence Vault")
move("Order Neural Circuit Relic",      objs, "Precinct 17 Evidence Vault")
move("Zero's Sniper Rig",               objs, "Harbor Docks Zone 9")
move("Forged Helix Corp Security Pass", objs, "Underground Connector Tunnels")
move("Underground Holographic Map",     objs, "Sublevel Markets")
move("Sublevel Syndicate Ledger",       objs, "Sublevel Markets")
move("Reclaimer Contact List",          objs, "Sublevel Markets")
move("Neural Suppressor Device",        objs, "Iron Augment Clinic")
move("Orbital Relay Bypass Module",     objs, "Orbital Relay Station")
move("BioNex Gene-Lock Vial",           objs, "Harbor Docks Zone 9")
move("Ghost Net Access Cipher",         objs, "Ghost Node Alpha")
move("Vellmore's Decrypted Comm Logs",  objs, "Ghost Node Alpha")

# Characters in locations (current position)
move("Detective Roen Kasra",    chars, "Precinct 17")
move("Commander Helise Orvani", chars, "Precinct 17")
move("Constable Pren Dalik",    chars, "Neon Canyon District")
move("Emery Vixt",              chars, "Sublevel Markets")
move("Gavrel Mout",             chars, "Synthwave Club Neonkiss")
move("Splice",                  chars, "Ghost Node Alpha")
move("Veronika Strand",         chars, "Helix Corp Executive Tower")
move("Marcus Thell",            chars, "Ascendancy Spires")
move("Director Syl Quen",       chars, "Deprogramming Center")
move("Father Azeth Nura",       chars, "The Null Zone")
move("Ossian Vrek",             chars, "Harbor Docks Zone 9")
move("Kaia Thell",              chars, "Lower Tier Slums")
move("Tomas Vellmore",          chars, "Lower Tier Slums")
move("Inspector Caye Norn",     chars, "The Obsidian Court")
move("Lena Moro",               chars, "Neon Canyon District")
move("Senator Brenni Vorst",    chars, "Ascendancy Council Chamber")
move("The Archivist",           chars, "Sublevel Markets")

print("\nâ”€â”€ Done. â”€â”€")
