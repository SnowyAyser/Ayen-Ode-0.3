#!/usr/bin/env python3
"""
Seed the knowledge graph and consequence records for Cyber-Rim.

Phase 1 — Knowledge: learn() for direct knowledge, spread() for propagated.
Phase 2 — Consequences: record_chain() for causal history.

Run from project root: python seed_knowledge_consequences.py
Requires seed_cyber_rim.py to have already been run.
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ayen_ode.config import load_settings
from ayen_ode.service import AyenOdeService

settings = load_settings()
svc = AyenOdeService(settings.db_path)
WORLD = "cyber-rim"

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Load entity IDs from DB
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("Loading entity IDs from DB...")
raw = svc.list_entities(world=WORLD, include_archived=True)["entities"]

chars = {e["name"]: e["entity_id"] for e in raw if e["entity_type"] == "character"}
facs  = {e["name"]: e["entity_id"] for e in raw if e["entity_type"] == "faction"}
locs  = {e["name"]: e["entity_id"] for e in raw if e["entity_type"] == "location"}
objs  = {e["name"]: e["entity_id"] for e in raw if e["entity_type"] == "object"}
evts  = {e["name"]: e["entity_id"] for e in raw if e["entity_type"] == "event"}

print(f"  {len(chars)} chars, {len(facs)} facs, {len(locs)} locs, {len(objs)} objs, {len(evts)} evts")


def L(entity_id: str, target_id: str, degree: str, source_id: str | None = None) -> None:
    """Shorthand for learn()."""
    svc.learn(entity_id=entity_id, target_id=target_id, degree=degree,
              source_id=source_id, world=WORLD)


def S(target_id: str, from_id: str, to_id: str, decay: int = 1) -> None:
    """Shorthand for spread()."""
    svc.spread(knowledge_target_id=target_id, from_entity=from_id,
               to_entity=to_id, degree_decay=decay, world=WORLD)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PHASE 1: KNOWLEDGE GRAPH
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Phase 1: Knowledge â”€â”€")

# â”€â”€ A. The Vellmore Assassination — who knows and at what degree â”€â”€
print("  A. Vellmore Assassination knowledge...")
asgn = evts["The Vellmore Assassination"]

# Direct knowledge (learn)
L(chars["Marcus Thell"],                asgn, "deeply_knows")
L(chars["Zero"],                        asgn, "deeply_knows")
L(chars["The Archivist"],               asgn, "deeply_knows")
L(chars["Ossian Vrek"],                 asgn, "witnessed")
L(chars["Detective Roen Kasra"],        asgn, "witnessed")
L(chars["Tomas Vellmore"],              asgn, "witnessed")
L(chars["Senator Brenni Vorst"],        asgn, "secondhand")
L(chars["Commander Helise Orvani"],     asgn, "secondhand")
L(chars["Inspector Caye Norn"],         asgn, "secondhand")
L(chars["Lena Moro"],                   asgn, "secondhand")
L(chars["Dr. Yara Blinn"],              asgn, "secondhand")
L(chars["Father Azeth Nura"],           asgn, "heard_rumor")
L(chars["Emery Vixt"],                  asgn, "heard_rumor")
L(chars["Constable Pren Dalik"],        asgn, "heard_rumor")
L(facs["Department of Information Control"], asgn, "fabricated")  # official cover story

# Spread chains (require source to already know)
# Marcus Thell → Veronika Strand (deeply_knows decay 2 → secondhand)
S(asgn, chars["Marcus Thell"], chars["Veronika Strand"], decay=2)
# Ossian Vrek → Gavrel Mout (witnessed decay 1 → secondhand)
S(asgn, chars["Ossian Vrek"], chars["Gavrel Mout"], decay=1)
# Tomas Vellmore → Kaia Thell (witnessed decay 1 → secondhand)
S(asgn, chars["Tomas Vellmore"], chars["Kaia Thell"], decay=1)
# Splice learns about assassination via breach data, then tells Kasra
L(chars["Splice"], asgn, "secondhand")
# DoIC fabricated narrative → City Security Division
S(asgn, facs["Department of Information Control"], facs["City Security Division"], decay=0)
# Lena Moro → public-facing faction (Vellmore Political Alliance) — secondhand from secondhand
S(asgn, chars["Lena Moro"], facs["Vellmore Political Alliance"], decay=1)

# â”€â”€ B. Ascendancy Override Chip â”€â”€
print("  B. Override Chip knowledge...")
chip = objs["Ascendancy Override Chip"]
L(chars["Marcus Thell"],            chip, "deeply_knows")
L(chars["Zero"],                    chip, "witnessed")
L(chars["The Archivist"],           chip, "secondhand")
L(chars["Inspector Caye Norn"],     chip, "secondhand")
L(chars["Commander Helise Orvani"], chip, "heard_rumor")

# â”€â”€ C. BioNex Prototype Canister â”€â”€
print("  C. BioNex Canister knowledge...")
canister = objs["BioNex Prototype Canister"]
L(chars["Dr. Yara Blinn"],      canister, "deeply_knows")
L(chars["Zero"],                canister, "witnessed")
L(chars["Ossian Vrek"],         canister, "secondhand")
L(chars["Marcus Thell"],        canister, "secondhand")
L(chars["Veronika Strand"],     canister, "heard_rumor")
L(chars["The Archivist"],       canister, "secondhand")

# â”€â”€ D. Chrome Hand Identification Coin â”€â”€
print("  D. Chrome Hand Coin knowledge...")
coin = objs["Chrome Hand Identification Coin"]
L(chars["Ossian Vrek"],             coin, "deeply_knows")
L(chars["Marcus Thell"],            coin, "deeply_knows")
L(chars["Commander Helise Orvani"], coin, "witnessed")
L(chars["Inspector Caye Norn"],     coin, "secondhand")
L(chars["Gavrel Mout"],             coin, "heard_rumor")
L(chars["Detective Roen Kasra"],    coin, "heard_rumor")

# â”€â”€ E. Vellmore's Decrypted Comm Logs â”€â”€
print("  E. Decrypted Comm Logs knowledge...")
logs = objs["Vellmore's Decrypted Comm Logs"]
L(chars["Splice"],               logs, "deeply_knows")
L(chars["The Archivist"],        logs, "deeply_knows")
L(chars["Lena Moro"],            logs, "witnessed")
S(logs, chars["Splice"], chars["Detective Roen Kasra"], decay=1)

# â”€â”€ F. Orbital Relay Bypass Module â”€â”€
print("  F. Bypass Module knowledge...")
bypass = objs["Orbital Relay Bypass Module"]
L(chars["Zero"],                bypass, "deeply_knows")
L(chars["The Archivist"],       bypass, "secondhand")
L(facs["Harbor Consortium"],    bypass, "secondhand")
L(chars["Inspector Caye Norn"], bypass, "heard_rumor")
L(facs["Iron Augment Cartel"],  bypass, "secondhand")

# â”€â”€ G. Magrail Seal Log (key technical evidence) â”€â”€
print("  G. Magrail Seal Log knowledge...")
seallog = objs["Magrail Seal Log"]
L(chars["Marcus Thell"],            seallog, "deeply_knows")
L(chars["Zero"],                    seallog, "witnessed")
L(chars["Detective Roen Kasra"],    seallog, "witnessed")
L(chars["Inspector Caye Norn"],     seallog, "secondhand")
L(chars["Commander Helise Orvani"], seallog, "secondhand")
L(chars["The Archivist"],           seallog, "secondhand")
L(chars["Splice"],                  seallog, "heard_rumor")

# â”€â”€ H. Encrypted Message â”€â”€
print("  H. Encrypted Message knowledge...")
msg = objs["Encrypted Message"]
L(chars["Tomas Vellmore"],                    msg, "witnessed")
L(chars["The Archivist"],                     msg, "secondhand")
L(chars["Splice"],                            msg, "witnessed")
L(facs["Department of Information Control"],  msg, "heard_rumor")

# â”€â”€ I. Sublevel Syndicate Ledger â”€â”€
print("  I. Syndicate Ledger knowledge...")
ledger = objs["Sublevel Syndicate Ledger"]
L(chars["Gavrel Mout"],          ledger, "deeply_knows")
L(chars["The Archivist"],        ledger, "secondhand")
L(chars["Emery Vixt"],           ledger, "heard_rumor")
L(chars["Inspector Caye Norn"],  ledger, "heard_rumor")
L(chars["Detective Roen Kasra"], ledger, "heard_rumor")

# â”€â”€ J. Neural Suppressor Device â”€â”€
print("  J. Neural Suppressor knowledge...")
suppressor = objs["Neural Suppressor Device"]
L(chars["Zero"],                suppressor, "deeply_knows")
L(facs["Iron Augment Cartel"],  suppressor, "deeply_knows")
L(chars["Marcus Thell"],        suppressor, "secondhand")
L(chars["Ossian Vrek"],         suppressor, "secondhand")
L(facs["The Null Collective"],  suppressor, "secondhand")
L(chars["Inspector Caye Norn"], suppressor, "heard_rumor")
L(chars["Dr. Yara Blinn"],      suppressor, "secondhand")

# â”€â”€ K. Ghost Net Access Cipher â”€â”€
print("  K. Ghost Net Cipher knowledge...")
cipher = objs["Ghost Net Access Cipher"]
L(chars["Splice"],               cipher, "deeply_knows")
L(facs["The Ghost Net"],         cipher, "deeply_knows")
L(chars["Detective Roen Kasra"], cipher, "witnessed")

# â”€â”€ L. BioNex Gene-Lock Vial â”€â”€
print("  L. Gene-Lock Vial knowledge...")
vial = objs["BioNex Gene-Lock Vial"]
L(chars["Dr. Yara Blinn"],      vial, "deeply_knows")
L(chars["Zero"],                vial, "witnessed")
L(chars["Marcus Thell"],        vial, "secondhand")
L(chars["The Archivist"],       vial, "secondhand")
L(chars["Inspector Caye Norn"], vial, "heard_rumor")
L(facs["BioNex Industries"],    vial, "deeply_knows")

# â”€â”€ M. Zero's Sniper Rig â”€â”€
print("  M. Sniper Rig knowledge...")
rig = objs["Zero's Sniper Rig"]
L(chars["Zero"],                rig, "deeply_knows")
L(chars["Ossian Vrek"],         rig, "witnessed")
L(chars["Marcus Thell"],        rig, "secondhand")
L(chars["Detective Roen Kasra"], rig, "heard_rumor")
L(chars["Inspector Caye Norn"], rig, "heard_rumor")
L(facs["Harbor Consortium"],    rig, "heard_rumor")

# â”€â”€ N. Vellmore Amendment Draft â”€â”€
print("  N. Vellmore Amendment knowledge...")
amend = objs["Vellmore Amendment Draft"]
L(chars["Senator Ilias Vellmore"], amend, "deeply_knows")
L(chars["Marcus Thell"],           amend, "deeply_knows")
L(chars["Veronika Strand"],        amend, "deeply_knows")
L(chars["Senator Brenni Vorst"],   amend, "deeply_knows")
L(chars["Lena Moro"],              amend, "witnessed")
L(chars["Tomas Vellmore"],         amend, "secondhand")
L(chars["The Archivist"],          amend, "deeply_knows")
L(facs["Vellmore Reform Movement"], amend, "witnessed")
L(facs["Ascendancy Council"],      amend, "deeply_knows")
L(facs["Helix Corporation"],       amend, "deeply_knows")

# â”€â”€ O. Ghost Net Helix Corp Data Breach (event) â”€â”€
print("  O. Data Breach event knowledge...")
breach = evts["Ghost Net Helix Corp Data Breach"]
L(chars["Splice"],                      breach, "deeply_knows")
L(facs["The Ghost Net"],                breach, "deeply_knows")
L(chars["Veronika Strand"],             breach, "witnessed")
L(facs["Helix Corporation"],            breach, "witnessed")
L(chars["Lena Moro"],                   breach, "secondhand")
L(chars["The Archivist"],               breach, "secondhand")
L(chars["Detective Roen Kasra"],        breach, "heard_rumor")
L(facs["Department of Information Control"], breach, "secondhand")
# Splice spread the breach knowledge to Roen Kasra
S(breach, chars["Splice"], chars["Detective Roen Kasra"], decay=1)

# â”€â”€ P. Chrome Hand Contract (event) â”€â”€
print("  P. Chrome Hand Contract knowledge...")
contract = evts["Chrome Hand Contract Posted"]
L(chars["Ossian Vrek"],          contract, "deeply_knows")
L(chars["Marcus Thell"],         contract, "deeply_knows")
L(facs["The Chrome Hand"],       contract, "deeply_knows")
L(chars["Gavrel Mout"],          contract, "secondhand")
L(chars["Emery Vixt"],           contract, "heard_rumor")
L(chars["Kaia Thell"],           contract, "secondhand")
L(chars["The Archivist"],        contract, "secondhand")
L(chars["Tomas Vellmore"],       contract, "heard_rumor")
# Ossian Vrek tells Gavrel Mout about the contract
S(contract, chars["Ossian Vrek"], chars["Gavrel Mout"], decay=2)

# â”€â”€ Q. Tomas Vellmore's hiding location â”€â”€
print("  Q. Tomas hiding location knowledge...")
hiding = locs["Lower Tier Slums"]
L(chars["Kaia Thell"],          hiding, "deeply_knows")
L(chars["Tomas Vellmore"],      hiding, "deeply_knows")
L(facs["Reclaimer Underground"], hiding, "secondhand")
L(chars["The Archivist"],       hiding, "secondhand")
L(chars["Emery Vixt"],          hiding, "heard_rumor")
L(chars["Zero"],                hiding, "heard_rumor")

# â”€â”€ R. Ghost Node Alpha location â”€â”€
print("  R. Ghost Node Alpha knowledge...")
node = locs["Ghost Node Alpha"]
L(chars["Splice"],                            node, "deeply_knows")
L(facs["The Ghost Net"],                      node, "deeply_knows")
L(chars["The Archivist"],                     node, "heard_rumor")
L(facs["Department of Information Control"],  node, "heard_rumor")

# â”€â”€ S. Iron Augment Clinic â”€â”€
print("  S. Iron Augment Clinic knowledge...")
clinic = locs["Iron Augment Clinic"]
L(chars["Zero"],                clinic, "deeply_knows")
L(facs["Iron Augment Cartel"],  clinic, "deeply_knows")
L(facs["The Null Collective"],  clinic, "witnessed")
L(chars["Inspector Caye Norn"], clinic, "heard_rumor")
L(chars["Emery Vixt"],          clinic, "heard_rumor")
L(chars["Gavrel Mout"],         clinic, "secondhand")

# â”€â”€ T. Zero's identity â”€â”€
print("  T. Zero's identity knowledge...")
zero = chars["Zero"]
L(chars["Marcus Thell"],        zero, "deeply_knows")
L(chars["Ossian Vrek"],         zero, "deeply_knows")
L(chars["The Archivist"],       zero, "secondhand")
L(facs["Iron Augment Cartel"],  zero, "secondhand")
L(chars["Inspector Caye Norn"], zero, "heard_rumor")
L(facs["Harbor Consortium"],    zero, "heard_rumor")

# â”€â”€ U. Kaia Thell's defection â”€â”€
print("  U. Kaia's defection knowledge...")
kaia = chars["Kaia Thell"]
L(chars["Marcus Thell"],         kaia, "deeply_knows")
L(chars["Kaia Thell"],           kaia, "deeply_knows")
L(facs["Reclaimer Underground"], kaia, "witnessed")
L(chars["Tomas Vellmore"],       kaia, "witnessed")
L(chars["Director Syl Quen"],    kaia, "secondhand")
L(chars["Inspector Caye Norn"],  kaia, "heard_rumor")
L(facs["Ascendancy Council"],    kaia, "secondhand")

# â”€â”€ V. Roen Kasra's cold case â”€â”€
print("  V. Cold case pattern knowledge...")
cold = evts["Roen Kasra's Cold Case"]
L(chars["Detective Roen Kasra"], cold, "deeply_knows")
L(chars["The Archivist"],        cold, "secondhand")
L(chars["Inspector Caye Norn"],  cold, "heard_rumor")
L(chars["Commander Helise Orvani"], cold, "heard_rumor")

# â”€â”€ W. Dr. Blinn's situation â”€â”€
print("  W. Dr. Blinn situation knowledge...")
blinn = chars["Dr. Yara Blinn"]
L(chars["Marcus Thell"],         blinn, "secondhand")
L(chars["Veronika Strand"],      blinn, "secondhand")
L(facs["BioNex Industries"],     blinn, "witnessed")
L(chars["Lena Moro"],            blinn, "secondhand")
L(chars["Inspector Caye Norn"],  blinn, "heard_rumor")
L(chars["Detective Roen Kasra"], blinn, "heard_rumor")
L(chars["The Archivist"],        blinn, "secondhand")

# â”€â”€ X. Key event knowledge (Vault Breach, Lab Fire, Emergency Session) â”€â”€
print("  X. Supporting event knowledge...")
vault_breach = evts["Precinct 17 Evidence Vault Breach"]
L(chars["Commander Helise Orvani"], vault_breach, "deeply_knows")
L(chars["Marcus Thell"],            vault_breach, "deeply_knows")
L(chars["Ossian Vrek"],             vault_breach, "witnessed")
L(chars["Inspector Caye Norn"],     vault_breach, "secondhand")
L(chars["Detective Roen Kasra"],    vault_breach, "secondhand")
L(chars["The Archivist"],           vault_breach, "secondhand")
L(chars["Father Azeth Nura"],       vault_breach, "heard_rumor")

lab_fire = evts["BioNex Wing-7 Lab Fire"]
L(chars["Dr. Yara Blinn"],       lab_fire, "witnessed")
L(chars["Marcus Thell"],         lab_fire, "deeply_knows")
L(facs["BioNex Industries"],     lab_fire, "witnessed")
L(chars["Veronika Strand"],      lab_fire, "secondhand")
L(chars["Lena Moro"],            lab_fire, "secondhand")
L(chars["Inspector Caye Norn"],  lab_fire, "heard_rumor")
L(chars["The Archivist"],        lab_fire, "secondhand")

emrg = evts["Ascendancy Emergency Session"]
L(chars["Marcus Thell"],         emrg, "deeply_knows")
L(facs["Ascendancy Council"],    emrg, "witnessed")
L(chars["Senator Brenni Vorst"], emrg, "witnessed")
L(chars["Director Syl Quen"],    emrg, "witnessed")
L(chars["Inspector Caye Norn"],  emrg, "secondhand")
L(chars["The Archivist"],        emrg, "secondhand")
L(chars["Kaia Thell"],           emrg, "heard_rumor")

# â”€â”€ Y. Reclaimer Contact List â”€â”€
print("  Y. Reclaimer Contact List knowledge...")
rlist = objs["Reclaimer Contact List"]
L(chars["Kaia Thell"],           rlist, "deeply_knows")
L(facs["Reclaimer Underground"], rlist, "deeply_knows")
L(chars["The Archivist"],        rlist, "secondhand")
L(chars["Director Syl Quen"],    rlist, "heard_rumor")
L(chars["Inspector Caye Norn"],  rlist, "heard_rumor")

# â”€â”€ Z. Magrail System Override Hack (event) â”€â”€
print("  Z. Override Hack event knowledge...")
hack = evts["Magrail System Override Hack"]
L(chars["Marcus Thell"],            hack, "deeply_knows")
L(chars["Zero"],                    hack, "witnessed")
L(chars["Detective Roen Kasra"],    hack, "witnessed")
L(chars["The Archivist"],           hack, "secondhand")
L(chars["Inspector Caye Norn"],     hack, "secondhand")
L(chars["Splice"],                  hack, "secondhand")
L(chars["Commander Helise Orvani"], hack, "heard_rumor")
L(facs["Ascendancy Council"],       hack, "secondhand")

print("  Knowledge phase complete.")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PHASE 2: CONSEQUENCE RECORDS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Phase 2: Consequences â”€â”€")


def chain(cause_id: str, effects: list[tuple[str, str, str]]) -> None:
    """Record a consequence chain. effects = [(effect_type, target_id, detail)]"""
    svc.record_chain(
        cause_id=cause_id,
        effects=[
            {"effect_type": et, "target_id": tid, "detail": det}
            for et, tid, det in effects
        ],
        world=WORLD,
    )


def record(cause_id: str, effect_type: str, target_id: str, detail: str) -> None:
    svc.record_consequence(cause_id=cause_id, effect_type=effect_type,
                           target_id=target_id, detail=detail, world=WORLD)


# Chain 1 — Magrail System Override Hack → enables assassination
# (record this first so it appears before Chain 2 in the causal tree)
print("  Chain 1: Magrail Override Hack...")
chain(evts["Magrail System Override Hack"], [
    ("triggered_event", evts["The Vellmore Assassination"],
     "trigger: magrail seal disengaged → assassination window opened"),
    ("state_changed", locs["Magrail Car Omega-7"],
     "security: sealed → breached for 11 seconds"),
])

# Chain 2 — Precinct 17 Evidence Vault Breach
print("  Chain 2: Evidence Vault Breach...")
chain(evts["Precinct 17 Evidence Vault Breach"], [
    ("moved",                 objs["Chrome Hand Identification Coin"],
     "location: contractor-hold → evidence-vault"),
    ("state_changed",         locs["Precinct 17 Evidence Vault"],
     "integrity: secure → compromised"),
    ("relationship_changed",  chars["Commander Helise Orvani"],
     "trust-status: commander → under-suspicion"),
])

# Chain 3 — BioNex Wing-7 Lab Fire
print("  Chain 3: BioNex Lab Fire...")
chain(evts["BioNex Wing-7 Lab Fire"], [
    ("destroyed",        locs["BioNex Research Campus"],
     "wing-7-records: intact → destroyed"),
    ("triggered_event",  evts["Dr. Blinn Requests Protective Custody"],
     "trigger: records-destroyed → whistleblower-panicked"),
    ("state_changed",    chars["Dr. Yara Blinn"],
     "status: at-work → in-hiding"),
    ("state_changed",    facs["BioNex Industries"],
     "data-integrity: maintained → compromised"),
])

# Chain 4 — The Vellmore Assassination (central cause — largest chain)
print("  Chain 4: The Vellmore Assassination...")
chain(evts["The Vellmore Assassination"], [
    ("state_changed",        chars["Senator Ilias Vellmore"],
     "status: alive → archived"),
    ("triggered_event",      evts["Ascendancy Emergency Session"],
     "trigger: assassination → emergency session convened"),
    ("triggered_event",      evts["Helix Corp Stock Crash"],
     "trigger: assassination → market panic"),
    ("triggered_event",      evts["Tomas Vellmore Goes Missing"],
     "trigger: father's death → heir fled"),
    ("triggered_event",      evts["Sublevel Market Riots"],
     "trigger: political shock → riots ignited"),
    ("triggered_event",      evts["Internal Affairs Investigation Opened"],
     "trigger: suspicious death → IA file opened"),
    ("triggered_event",      evts["Chrome Hand Contract Posted"],
     "trigger: assassination aftermath → survivors targeted"),
    ("triggered_event",      evts["Encrypted Message Interception Attempt"],
     "trigger: assassination → surveillance escalated"),
    ("relationship_changed", facs["Vellmore Political Alliance"],
     "cohesion: strong → fragile"),
    ("relationship_changed", facs["Vellmore Reform Movement"],
     "leadership: active → leaderless"),
])

# Chain 5 — Ghost Net Helix Corp Data Breach
print("  Chain 5: Ghost Net Data Breach...")
chain(evts["Ghost Net Helix Corp Data Breach"], [
    ("triggered_event",      evts["Lena Moro's First Article"],
     "trigger: data-breach → publication"),
    ("state_changed",        facs["Helix Corporation"],
     "exposure: concealed → public"),
    ("relationship_changed", chars["Veronika Strand"],
     "public-status: untouchable → under-scrutiny"),
    ("state_changed",        facs["The Ghost Net"],
     "profile: invisible → noticed"),
])

# Chain 6 — Null Zone Crackdown (earlier event)
print("  Chain 6: Null Zone Crackdown...")
chain(evts["Null Zone Crackdown"], [
    ("state_changed",        locs["The Null Zone"],
     "population-status: diverse → displaced"),
    ("state_changed",        facs["The Null Collective"],
     "position: border → deep-null-zone"),
    ("relationship_changed", facs["Reclaimer Underground"],
     "recruitment-rate: stable → accelerated"),
    ("relationship_changed", facs["City Security Division"],
     "public-trust: moderate → eroded"),
])

# Chain 7 — Roen Kasra's Cold Case (pattern recognition)
print("  Chain 7: Cold Case pattern...")
chain(evts["Roen Kasra's Cold Case"], [
    ("state_changed",        chars["Detective Roen Kasra"],
     "pattern-awareness: none → active"),
    ("relationship_changed", evts["The Vellmore Assassination"],
     "case-status: isolated → connected-to-prior-death"),
])

# Chain 8 — Sublevel Market Riots
print("  Chain 8: Sublevel Market Riots...")
chain(evts["Sublevel Market Riots"], [
    ("state_changed",   chars["Emery Vixt"],
     "status: active → injured"),
    ("state_changed",   locs["Sublevel Markets"],
     "stability: tense → riot-damaged"),
    ("state_changed",   facs["Sublevel Syndicate"],
     "strategy: passive → exploiting-chaos"),
    ("state_changed",   facs["City Security Division"],
     "deployment: standard → crisis-response"),
])

# Chain 9 — Ascendancy Emergency Session
print("  Chain 9: Ascendancy Emergency Session...")
chain(evts["Ascendancy Emergency Session"], [
    ("state_changed",        facs["Ascendancy Council"],
     "response-mode: reactive → coordinated"),
    ("relationship_changed", facs["Vellmore Political Alliance"],
     "institutional-support: partial → withdrawn"),
    ("state_changed",        facs["Department of Information Control"],
     "mandate: standard → crisis-expanded"),
    ("state_changed",        chars["Marcus Thell"],
     "control: secure → consolidating"),
])

# Chain 10 — Encrypted Message Interception Attempt
print("  Chain 10: Encrypted Message Interception...")
chain(evts["Encrypted Message Interception Attempt"], [
    ("state_changed",        objs["Encrypted Message"],
     "delivery-security: intact → retroactively-targeted"),
    ("state_changed",        facs["Department of Information Control"],
     "surveillance-scope: targeted → aggressive"),
    ("relationship_changed", chars["Director Syl Quen"],
     "operational-posture: managing → aggressive"),
])

# Chain 11 — Zero Sighting at Harbor Docks
print("  Chain 11: Zero sighting and escape...")
chain(evts["Zero Sighting at Harbor Docks"], [
    ("moved",          chars["Zero"],
     "location: Cyber-Rim → orbital-transit"),
    ("state_changed",  locs["Orbital Relay Station"],
     "departure-log: accurate → falsified"),
    ("state_changed",  objs["Zero's Sniper Rig"],
     "status: with-operator → abandoned-at-docks"),
    ("state_changed",  objs["Orbital Relay Bypass Module"],
     "status: unused → expended"),
])

# Chain 12 — Dr. Blinn Requests Protective Custody
print("  Chain 12: Dr. Blinn custody request...")
chain(evts["Dr. Blinn Requests Protective Custody"], [
    ("state_changed",        chars["Dr. Yara Blinn"],
     "contact-status: reachable → unreachable"),
    ("relationship_changed", facs["BioNex Industries"],
     "internal-safety: compliant → liability-risk"),
    ("state_changed",        objs["BioNex Prototype Canister"],
     "investigation-link: dormant → active"),
])

# Chain 13 — Chrome Hand Contract Posted
print("  Chain 13: Chrome Hand Contract...")
chain(evts["Chrome Hand Contract Posted"], [
    ("state_changed",   chars["Tomas Vellmore"],
     "threat-level: low → actively-hunted"),
    ("state_changed",   chars["Kaia Thell"],
     "exposure-risk: managed → elevated"),
    ("state_changed",   facs["Vellmore Political Alliance"],
     "member-safety: at-risk → threatened"),
])

# Chain 14 — Reclaimer Protest at Ascendancy Spires
print("  Chain 14: Reclaimer Protest...")
chain(evts["Reclaimer Protest at Ascendancy Spires"], [
    ("state_changed",        facs["Reclaimer Underground"],
     "operational-visibility: covert → exposed"),
    ("state_changed",        chars["Kaia Thell"],
     "exposure-risk: elevated → compromised"),
    ("relationship_changed", facs["Ascendancy Council"],
     "tolerance-of-dissent: managing → zero"),
    ("state_changed",        locs["Deprogramming Center"],
     "intake: normal → emergency-intake"),
])

# â”€â”€ Bonus: Individual record_consequence calls for cross-system links â”€â”€
print("  Bonus: Cross-system consequence records...")

# Vellmore's Final Speech → triggered Ascendancy awareness of reform threat
record(evts["Vellmore's Final Public Speech"],
       "triggered_event", evts["Magrail System Override Hack"],
       "trigger: reform speech → assassination decision made")

record(evts["Vellmore's Final Public Speech"],
       "relationship_changed", facs["Ascendancy Council"],
       "threat-assessment: manageable → must-eliminate")

# Helix Corp Stock Crash → consequences for Strand
record(evts["Helix Corp Stock Crash"],
       "state_changed", chars["Veronika Strand"],
       "regulatory-exposure: low → under-investigation")

record(evts["Helix Corp Stock Crash"],
       "state_changed", facs["Academic Institute of Augmentation"],
       "helix-funding: secure → jeopardized")

# Tomas Vellmore going missing → Kaia takes custody
record(evts["Tomas Vellmore Goes Missing"],
       "relationship_changed", chars["Kaia Thell"],
       "role: rebel-financier → protector")

record(evts["Tomas Vellmore Goes Missing"],
       "moved", chars["Tomas Vellmore"],
       "location: registered-address → lower-tier-slums")

# Order Mass Gathering creates alibi complexity for Nura
record(evts["Order of the Neural Seal Mass Gathering"],
       "state_changed", chars["Father Azeth Nura"],
       "alibi-status: partial → documented-witnesses")

record(evts["Order of the Neural Seal Mass Gathering"],
       "relationship_changed", objs["Order Neural Circuit Relic"],
       "significance: ceremonial → evidence-adjacent")

# Lena Moro's Article triggers consequences
record(evts["Lena Moro's First Article"],
       "state_changed", chars["Lena Moro"],
       "threat-level: watched → actively-targeted")

record(evts["Lena Moro's First Article"],
       "relationship_changed", facs["Department of Information Control"],
       "press-suppression: ongoing → emergency-priority")

print("  Consequence phase complete.")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# SUMMARY
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Verification spot-checks â”€â”€")

# Count knowledge records
with svc.connect() as conn:
    k_count = conn.execute(
        "SELECT COUNT(*) FROM entity_knowledge ek "
        "JOIN entities e ON ek.world_id = e.world_id "
        "WHERE ek.world_id = (SELECT world_id FROM worlds WHERE slug = ?)",
        (WORLD,)
    ).fetchone()[0]
    c_count = conn.execute(
        "SELECT COUNT(*) FROM consequence_records cr "
        "WHERE cr.world_id = (SELECT world_id FROM worlds WHERE slug = ?)",
        (WORLD,)
    ).fetchone()[0]

print(f"  Knowledge links in DB:   {k_count}")
print(f"  Consequence records:     {c_count}")
print(f"\n  Cyber-Rim knowledge + consequence graphs seeded.")
