#!/usr/bin/env python3
"""
Seed Cyber-Rim with ~20 of each entity type.

All entities are cross-referenced so the world feels built through gameplay.
Run from the project root: python seed_cyber_rim.py
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

locs: dict[str, str] = {}
facs: dict[str, str] = {}
chars: dict[str, str] = {}
objs: dict[str, str] = {}
evts: dict[str, str] = {}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# LOCATIONS  (security, prosperity, corruption, danger, stability, mystique)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Locations â”€â”€")
_locs = [
    (
        "Precinct 17",
        "Rain-soaked detective bureau perched on a rusted catwalk above Neon Canyon. "
        "Commander Orvani runs it with an iron fist and a selective memory. "
        "The player's home base; the evidence vault downstairs was breached the night before Vellmore died.",
        ["law-enforcement", "tier-upper", "player-base"],
        dict(security=72, prosperity=45, corruption=38, danger=40, stability=68, mystique=20),
    ),
    (
        "Sublevel Markets",
        "A labyrinthine black-market district six levels below street tier. "
        "Every faction has a stall here. Emery Vixt knows the floor plan by feel in the dark. "
        "The encrypted message the player received traced back to a terminal here.",
        ["underground", "black-market", "tier-lower"],
        dict(security=15, prosperity=55, corruption=85, danger=70, stability=30, mystique=60),
    ),
    (
        "Ascendancy Spires",
        "The gleaming needle-towers where the Council governs from altitude. "
        "Civilian access is forbidden above Level 3. "
        "The Reclaimer Underground staged a protest here that ended badly.",
        ["government", "tier-upper", "restricted"],
        dict(security=95, prosperity=80, corruption=55, danger=20, stability=82, mystique=40),
    ),
    (
        "Magrail Car Omega-7",
        "The sealed magtrain car where Senator Vellmore was found dead. "
        "Now locked in forensic hold at Station Theta-9. "
        "The bullet entry point defies ballistic physics — there was no shooter's angle.",
        ["crime-scene", "evidence", "transport"],
        dict(security=90, prosperity=10, corruption=30, danger=35, stability=50, mystique=88),
    ),
    (
        "Neon Canyon District",
        "The central commercial canyon where holographic propaganda waterfalls endlessly. "
        "Magrails run at eye-level between buildings. "
        "Ground level is always wet; upper catwalks belong to corporate couriers.",
        ["downtown", "tier-mid", "public"],
        dict(security=55, prosperity=62, corruption=48, danger=45, stability=58, mystique=52),
    ),
    (
        "BioNex Research Campus",
        "Sterile complex on the upper east rim. After the Wing-7 fire, half the campus is under lockdown. "
        "Dr. Blinn's old office is now a crime scene. "
        "The gene-lock vial was manufactured in Lab 4.",
        ["corporate", "research", "restricted"],
        dict(security=78, prosperity=70, corruption=42, danger=55, stability=60, mystique=65),
    ),
    (
        "Harbor Docks Zone 9",
        "Contraband passes through here every night. "
        "Zero was sighted loading onto an orbital shuttle pod three days after the assassination. "
        "The dockmaster owes no one loyalty — not anymore.",
        ["port", "smuggling", "tier-lower"],
        dict(security=28, prosperity=40, corruption=72, danger=65, stability=35, mystique=30),
    ),
    (
        "Vellmore Penthouse Suite",
        "Sealed by Precinct 17 after the murder. Someone entered before the forensics team arrived. "
        "The Ascendancy Override Chip was found hidden behind a false wall panel. "
        "The security footage shows a 90-second gap.",
        ["crime-scene", "residential", "upper-tier"],
        dict(security=88, prosperity=90, corruption=20, danger=25, stability=55, mystique=72),
    ),
    (
        "Lower Tier Slums",
        "Pitch-dark warrens beneath the city plate. "
        "The Reclaimer Underground recruits here; the Chrome Hand culls here. "
        "Kaia Thell hides somewhere in Sublevel 4, watched by people she trusts.",
        ["residential", "tier-lower", "dangerous"],
        dict(security=8, prosperity=12, corruption=65, danger=88, stability=22, mystique=40),
    ),
    (
        "The Obsidian Court",
        "Cyber-Rim's judicial complex — polished black walls and automated verdicts. "
        "Chief Justice Maren has not ruled against the Ascendancy Council in eleven years. "
        "Internal Affairs opened its Vellmore file here in secret.",
        ["government", "justice", "public"],
        dict(security=82, prosperity=68, corruption=60, danger=15, stability=75, mystique=35),
    ),
    (
        "Ghost Node Alpha",
        "A hidden hacker den tucked inside a decommissioned power relay. "
        "Splice runs operations here. The address changes every 72 hours. "
        "The Ghost Net's leaked Helix Corp files originated from this terminal.",
        ["underground", "tech", "faction-hq"],
        dict(security=20, prosperity=30, corruption=40, danger=50, stability=25, mystique=88),
    ),
    (
        "Synthwave Club Neonkiss",
        "A pulse-loud nightclub in Neon Canyon's mid-tier. "
        "The Synthwave Cartel runs deals through the back bar. "
        "Gavrel Mout holds client meetings here every Thursday — the music masks everything.",
        ["entertainment", "criminal", "tier-mid"],
        dict(security=30, prosperity=65, corruption=78, danger=55, stability=42, mystique=70),
    ),
    (
        "Deprogramming Center",
        "The Department of Information Control's re-education facility. "
        "Citizens who question Ascendancy narratives are 'voluntarily' processed here. "
        "Director Quen co-founded it and still visits on Fridays.",
        ["government", "propaganda", "restricted"],
        dict(security=85, prosperity=25, corruption=88, danger=40, stability=80, mystique=55),
    ),
    (
        "Helix Corp Executive Tower",
        "The tallest private structure in Cyber-Rim. Veronika Strand's office crowns the summit. "
        "The lower floors are a labyrinth of corporate security and shell companies. "
        "Helix stock cratered 34 points the morning after the assassination.",
        ["corporate", "tier-upper", "faction-hq"],
        dict(security=88, prosperity=92, corruption=55, danger=22, stability=78, mystique=48),
    ),
    (
        "Iron Augment Clinic",
        "An unlicensed body-modification clinic in Sublevel 2. "
        "Neural suppressors are installed here quietly, no registration required. "
        "A fresh installation was performed 48 hours before the assassination.",
        ["underground", "medical", "criminal"],
        dict(security=22, prosperity=35, corruption=80, danger=45, stability=38, mystique=55),
    ),
    (
        "Precinct 17 Evidence Vault",
        "The locked subfloor beneath Precinct 17. "
        "It was breached the night before Vellmore's murder. "
        "Three items were accessed and one was replaced — the swap was sloppy.",
        ["law-enforcement", "evidence", "restricted"],
        dict(security=85, prosperity=10, corruption=30, danger=20, stability=70, mystique=75),
    ),
    (
        "The Null Zone",
        "A district-wide no-technology pocket where augmentation blockers run constantly. "
        "The Null Collective retreated here after the Ascendancy crackdown. "
        "No surveillance reaches inside; some people live here because of that.",
        ["residential", "anti-tech", "sanctuary"],
        dict(security=42, prosperity=20, corruption=15, danger=35, stability=55, mystique=90),
    ),
    (
        "Orbital Relay Station",
        "A docking and comms hub in low orbit. The Orbital Authority runs it; the Ascendancy co-opts it. "
        "Zero used a bypass module to disappear from here after the murder. "
        "Transit logs show a departure that officially never happened.",
        ["orbital", "transport", "strategic"],
        dict(security=75, prosperity=60, corruption=35, danger=30, stability=72, mystique=60),
    ),
    (
        "Underground Connector Tunnels",
        "A decommissioned maintenance network threading every sublevel. "
        "The Reclaimer Underground uses them as escape routes. "
        "Holographic maps can be purchased in Sublevel Markets — if you know who to ask.",
        ["underground", "transit", "smuggling"],
        dict(security=10, prosperity=5, corruption=50, danger=75, stability=20, mystique=65),
    ),
    (
        "Ascendancy Council Chamber",
        "The inner sanctum where the seven Council members vote on the fate of Cyber-Rim. "
        "The session following Vellmore's death was not officially recorded. "
        "Marcus Thell exited alone. The other six remain unaccounted for that hour.",
        ["government", "political", "restricted"],
        dict(security=98, prosperity=75, corruption=65, danger=15, stability=88, mystique=78),
    ),
]

for name, summary, tags, stats in _locs:
    r = svc.create_entity(name=name, entity_type="location", summary=summary,
                          world=WORLD, tags=tags, stats=stats)
    locs[name] = r["entity"]["entity_id"]
    print(f"  + {name}")
print(f"  → {len(locs)} locations created.")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# FACTIONS  (power, cohesion, reach, resources, secrecy, instability)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Factions â”€â”€")
_facs = [
    (
        "Ascendancy Council",
        "The seven-member ruling body of Cyber-Rim. Absolute legislative and executive authority. "
        "Chair Marcus Thell controls three votes outright. "
        "Vellmore's reform agenda was a direct threat to their monopoly on augmentation licensing.",
        ["government", "ruling-party", "antagonist"],
        dict(power=92, cohesion=65, reach=95, resources=98, secrecy=72, instability=30),
    ),
    (
        "Precinct Detective Bureau",
        "The detective division operating out of Precinct 17 and its sister precincts. "
        "Nominally independent; in practice, answers to Commander Orvani who answers to the Council. "
        "The player's institutional home — compromised but not entirely corrupt.",
        ["law-enforcement", "player-faction", "government"],
        dict(power=45, cohesion=58, reach=55, resources=48, secrecy=35, instability=42),
    ),
    (
        "Helix Corporation",
        "Cyber-Rim's dominant mega-corporation: augmentation tech, pharmaceuticals, data brokerage. "
        "CEO Veronika Strand personally lobbied against the Vellmore Amendment. "
        "Their stock crash post-assassination looks like foreknowledge, not shock.",
        ["corporate", "mega-corp", "antagonist"],
        dict(power=85, cohesion=72, reach=90, resources=95, secrecy=60, instability=35),
    ),
    (
        "Sublevel Syndicate",
        "The dominant organized crime network in the lower tiers. "
        "Gavrel Mout runs it from Synthwave Club Neonkiss. "
        "They provided logistical support for something big the week before the assassination — for a price.",
        ["criminal", "underworld", "tier-lower"],
        dict(power=62, cohesion=55, reach=70, resources=65, secrecy=80, instability=45),
    ),
    (
        "BioNex Industries",
        "Biotech rival to Helix Corp, specializing in gene modification and neuro-chemistry. "
        "The Wing-7 fire destroyed records that the Vellmore investigation needs. "
        "Dr. Blinn was their lead researcher before she asked to leave.",
        ["corporate", "biotech", "research"],
        dict(power=58, cohesion=60, reach=65, resources=72, secrecy=55, instability=48),
    ),
    (
        "The Chrome Hand",
        "Elite mercenary outfit with a reputation for clean, deniable work. "
        "Leader Ossian Vrek takes contracts only from clients who can afford silence. "
        "A Chrome Hand identification coin was found in the Precinct 17 evidence vault — not catalogued.",
        ["mercenary", "criminal", "elite"],
        dict(power=70, cohesion=78, reach=60, resources=68, secrecy=88, instability=25),
    ),
    (
        "Vellmore Reform Movement",
        "The political coalition Senator Vellmore built over six years. "
        "Tomas Vellmore and Lena Moro are trying to keep it alive. "
        "The Ascendancy is systematically dismantling it through the Deprogramming Center and legal pressure.",
        ["political", "reformist", "under-pressure"],
        dict(power=28, cohesion=42, reach=50, resources=22, secrecy=30, instability=70),
    ),
    (
        "The Null Collective",
        "Anti-augmentation activists who retreated to the Null Zone after the crackdown. "
        "They believe neural modification is a form of Ascendancy control. "
        "They know things about the Iron Augment Clinic that no one else does.",
        ["activist", "anti-tech", "fringe"],
        dict(power=20, cohesion=62, reach=25, resources=15, secrecy=70, instability=38),
    ),
    (
        "The Ghost Net",
        "Decentralized hacker collective operating out of rotating nodes. "
        "Splice is their most active field operator. "
        "Their Helix Corp data breach is the most explosive document leak in Cyber-Rim's history — if authentic.",
        ["hacker", "underground", "information"],
        dict(power=35, cohesion=38, reach=72, resources=30, secrecy=90, instability=50),
    ),
    (
        "Order of the Neural Seal",
        "A techno-cult venerating the moment of first augmentation as a spiritual awakening. "
        "Father Azeth Nura leads gatherings at the Null Zone's edge. "
        "They have members in the Precinct Detective Bureau and possibly the Council.",
        ["cult", "religious", "infiltration"],
        dict(power=30, cohesion=85, reach=40, resources=35, secrecy=75, instability=22),
    ),
    (
        "Harbor Consortium",
        "The smugglers' guild running Zone 9. They move anything — cargo, people, information. "
        "They provided Zero's escape route to the Orbital Relay Station. "
        "They do not ask what they are moving or for whom.",
        ["criminal", "smuggling", "port"],
        dict(power=48, cohesion=52, reach=58, resources=55, secrecy=78, instability=35),
    ),
    (
        "City Security Division",
        "The uniformed police authority — technically above Precinct 17 in the chain of command. "
        "Currently being used by the Ascendancy to contain the Sublevel riots. "
        "Their Null Zone crackdown three months ago displaced 2,000 residents.",
        ["law-enforcement", "government", "authoritarian"],
        dict(power=68, cohesion=62, reach=75, resources=70, secrecy=35, instability=40),
    ),
    (
        "Ascendancy Internal Affairs",
        "The watchdog unit that investigates misconduct within Ascendancy institutions. "
        "Inspector Caye Norn leads the quiet Vellmore file that nobody asked for. "
        "Internal Affairs reports directly to the Council — which is the problem.",
        ["law-enforcement", "government", "investigation"],
        dict(power=55, cohesion=50, reach=50, resources=52, secrecy=65, instability=38),
    ),
    (
        "The Synthwave Cartel",
        "Vice and narcotics operation embedded inside Synthwave Club Neonkiss. "
        "They distribute neural-high compounds that bypass standard augment filters. "
        "Gavrel Mout uses them as a parallel revenue stream to fund Syndicate operations.",
        ["criminal", "narcotics", "tier-mid"],
        dict(power=45, cohesion=48, reach=55, resources=58, secrecy=70, instability=52),
    ),
    (
        "Iron Augment Cartel",
        "Black-market body modification network operating through the Iron Augment Clinic. "
        "Specializes in off-registry neural suppressors and identity-masking hardware. "
        "Zero's modifications were done here — no record, no liability.",
        ["criminal", "body-mod", "underground"],
        dict(power=40, cohesion=55, reach=45, resources=48, secrecy=88, instability=30),
    ),
    (
        "Reclaimer Underground",
        "Anti-Ascendancy rebel network operating from the Lower Tier Slums. "
        "Kaia Thell defected from the Council to fund their operations. "
        "They are two weeks from something large — the Chrome Hand contract may be theirs.",
        ["rebel", "underground", "anti-government"],
        dict(power=32, cohesion=60, reach=35, resources=28, secrecy=82, instability=60),
    ),
    (
        "Department of Information Control",
        "The Ascendancy's censorship and narrative-management bureau. "
        "Director Syl Quen is personally overseeing suppression of the Vellmore investigation in the press. "
        "Lena Moro's articles are their primary current target.",
        ["government", "propaganda", "censorship"],
        dict(power=72, cohesion=70, reach=80, resources=75, secrecy=68, instability=22),
    ),
    (
        "Orbital Authority",
        "The oversight body governing Cyber-Rim's orbital infrastructure. "
        "Nominally independent; in practice, the Ascendancy controls appointment of its Director. "
        "The falsified departure log from the assassination night was generated here.",
        ["government", "orbital", "transportation"],
        dict(power=50, cohesion=58, reach=55, resources=62, secrecy=48, instability=28),
    ),
    (
        "Vellmore Political Alliance",
        "The surviving bloc of senators and council delegates who backed the Vellmore Amendment. "
        "Down to four members after two withdrew following anonymous threats. "
        "Senator Brenni Vorst conspicuously did not join — then offered a memorial speech.",
        ["political", "reformist", "fragile"],
        dict(power=22, cohesion=35, reach=38, resources=25, secrecy=40, instability=78),
    ),
    (
        "Academic Institute of Augmentation",
        "The official research body that certifies augmentation technology. "
        "Helix Corp funds 60% of its operating budget. "
        "The Institute's safety report on the BioNex prototype was classified the day after the lab fire.",
        ["academic", "research", "compromised"],
        dict(power=35, cohesion=65, reach=42, resources=45, secrecy=50, instability=28),
    ),
]

for name, summary, tags, stats in _facs:
    r = svc.create_entity(name=name, entity_type="faction", summary=summary,
                          world=WORLD, tags=tags, stats=stats)
    facs[name] = r["entity"]["entity_id"]
    print(f"  + {name}")
print(f"  → {len(facs)} factions created.")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CHARACTERS  (force, influence, will, perception, resilience, volatility)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Characters â”€â”€")
_chars = [
    (
        "Senator Ilias Vellmore",
        "Reformist senator, recently assassinated inside Magrail Car Omega-7. "
        "His Vellmore Amendment would have broken Helix Corp's augmentation monopoly. "
        "Dead for 26 hours before the player caught the case. "
        "Three different factions had reason to want him gone.",
        "archived",
        ["politician", "victim", "reformist"],
        dict(force=30, influence=88, will=82, perception=70, resilience=45, volatility=25),
    ),
    (
        "Detective Roen Kasra",
        "The player's partner of eight years. Quiet in a way that says everything. "
        "Smokes violet-burning cigarettes. Knows something about the Vellmore cold case "
        "that predates the current murder by three years. Has not volunteered the connection.",
        "active",
        ["detective", "ally", "partner"],
        dict(force=62, influence=45, will=75, perception=85, resilience=70, volatility=28),
    ),
    (
        "Commander Helise Orvani",
        "Precinct 17 commander. Efficient, unreadable, and under pressure from above. "
        "She signed the order to restrict access to the Vellmore case. "
        "Her access card was used at the Evidence Vault two hours before the break-in.",
        "active",
        ["commander", "authority", "suspect"],
        dict(force=55, influence=72, will=78, perception=60, resilience=65, volatility=40),
    ),
    (
        "Marcus Thell",
        "Chair of the Ascendancy Council. Three votes in his pocket, two more within reach. "
        "His daughter Kaia defected to the Reclaimer Underground. "
        "He has not publicly acknowledged her in four months. "
        "The Council session after the assassination — he exited alone.",
        "active",
        ["politician", "antagonist", "council"],
        dict(force=40, influence=95, will=88, perception=72, resilience=75, volatility=35),
    ),
    (
        "Dr. Yara Blinn",
        "Former lead researcher at BioNex Industries. "
        "She submitted a formal safety concern about the prototype canister the week before the Wing-7 fire. "
        "The report was classified. She requested protective custody from Precinct 17 — then withdrew the request.",
        "active",
        ["scientist", "witness", "at-risk"],
        dict(force=20, influence=38, will=65, perception=88, resilience=42, volatility=55),
    ),
    (
        "Splice",
        "The Ghost Net's most active field operator — real name unknown. "
        "Runs operations from Ghost Node Alpha. "
        "The Helix Corp data breach is their work; authentication is their gift to the investigation. "
        "They want something in return.",
        "active",
        ["hacker", "ally", "information"],
        dict(force=25, influence=50, will=70, perception=92, resilience=38, volatility=60),
    ),
    (
        "Veronika Strand",
        "CEO of Helix Corporation. Polished, strategic, and present in the city the night Vellmore died. "
        "She publicly opposed the Vellmore Amendment through legal channels. "
        "Her private comms to the Ascendancy Council are in the Ghost Net breach.",
        "active",
        ["corporate", "antagonist", "ceo"],
        dict(force=35, influence=90, will=85, perception=68, resilience=72, volatility=28),
    ),
    (
        "Gavrel Mout",
        "Boss of the Sublevel Syndicate. Operates from Synthwave Club Neonkiss on Thursdays. "
        "The Syndicate provided logistical support for the Vellmore operation — "
        "he claims he didn't know what it was for. That may even be true.",
        "active",
        ["crime-boss", "information", "underworld"],
        dict(force=72, influence=68, will=62, perception=60, resilience=65, volatility=55),
    ),
    (
        "Inspector Caye Norn",
        "Internal Affairs investigator assigned to a file nobody asked for. "
        "Quiet, methodical, and reporting directly to the Ascendancy Council — "
        "which means they know everything she discovers before the player does.",
        "active",
        ["investigator", "rival", "internal-affairs"],
        dict(force=45, influence=55, will=80, perception=82, resilience=58, volatility=32),
    ),
    (
        "Tomas Vellmore",
        "The senator's son — 24 years old, distraught, and hiding. "
        "He received the same encrypted message the player did, twelve hours earlier. "
        "He has not been seen in public since his father's death. "
        "The Reclaimer Underground is sheltering him.",
        "active",
        ["civilian", "witness", "at-risk"],
        dict(force=28, influence=40, will=45, perception=55, resilience=32, volatility=75),
    ),
    (
        "Constable Pren Dalik",
        "Beat cop assigned to Neon Canyon District. He saw the black sedan. "
        "He wrote it down in his patrol log and then found the entry had been deleted. "
        "He is afraid. He will talk if the player comes alone.",
        "active",
        ["police", "witness", "low-rank"],
        dict(force=50, influence=20, will=38, perception=70, resilience=45, volatility=62),
    ),
    (
        "The Archivist",
        "An information broker whose identity is unknown even to regular clients. "
        "They operate through dead drops in the Sublevel Markets. "
        "They have a complete record of every Ascendancy Council vote, including the ones that never happened.",
        "active",
        ["broker", "unknown", "information"],
        dict(force=15, influence=65, will=78, perception=95, resilience=50, volatility=20),
    ),
    (
        "Lena Moro",
        "Investigative journalist, currently publishing stories that Director Quen is trying to kill. "
        "She has a source inside the Ascendancy Council. "
        "She was at Vellmore's final speech and recorded something the official feeds did not.",
        "active",
        ["journalist", "ally", "at-risk"],
        dict(force=22, influence=58, will=80, perception=85, resilience=48, volatility=50),
    ),
    (
        "Director Syl Quen",
        "Head of the Department of Information Control. "
        "Co-founder of the Deprogramming Center. "
        "Personally managing the suppression of the Vellmore case in the press. "
        "His background before the Ascendancy is sealed — by the Ascendancy.",
        "active",
        ["government", "antagonist", "propaganda"],
        dict(force=38, influence=82, will=88, perception=65, resilience=72, volatility=30),
    ),
    (
        "Father Azeth Nura",
        "Leader of the Order of the Neural Seal. "
        "Preaches that augmentation is spiritual elevation. "
        "Has members inside the Precinct Detective Bureau and possibly higher. "
        "He knew Vellmore personally — and is not grieving.",
        "active",
        ["cult-leader", "suspect", "information"],
        dict(force=30, influence=60, will=90, perception=75, resilience=68, volatility=28),
    ),
    (
        "Ossian Vrek",
        "Commander of the Chrome Hand mercenary outfit. "
        "He knows who issued the contract that led to the night of the assassination. "
        "He will not say. He has one rule: the Chrome Hand does not burn clients. "
        "He might bend it, at a price the player has not yet offered.",
        "active",
        ["mercenary", "suspect", "chrome-hand"],
        dict(force=88, influence=55, will=82, perception=70, resilience=80, volatility=38),
    ),
    (
        "Kaia Thell",
        "Daughter of Ascendancy Council Chair Marcus Thell. "
        "Defected to the Reclaimer Underground six months ago with access codes she should not have had. "
        "She is sheltering Tomas Vellmore in the Lower Tier Slums. "
        "She does not trust police. She may trust someone who proves the system is broken.",
        "active",
        ["defector", "ally", "reclaimer"],
        dict(force=45, influence=55, will=85, perception=72, resilience=60, volatility=50),
    ),
    (
        "Senator Brenni Vorst",
        "Vellmore's political rival. Did not join the Vellmore Political Alliance. "
        "Offered a polished memorial speech 18 hours after the death — written before the body was found. "
        "His access badge shows a trip to the Ascendancy Council Chamber two days before the murder.",
        "active",
        ["politician", "suspect", "council-adjacent"],
        dict(force=32, influence=78, will=72, perception=62, resilience=60, volatility=38),
    ),
    (
        "Zero",
        "The assassin. No identity on record, no biological trace at the scene. "
        "Modifications from the Iron Augment Clinic rendered them undetectable on standard forensics. "
        "They used the orbital bypass module to disappear. One question remains: "
        "were they hired by the same people who authorized the Chrome Hand contract?",
        "active",
        ["assassin", "antagonist", "unknown"],
        dict(force=90, influence=20, will=88, perception=95, resilience=82, volatility=30),
    ),
    (
        "Emery Vixt",
        "The player's street-level informant in the Sublevel Markets. "
        "Reliable, cautious, and currently very scared. "
        "They saw the person who paid for the logistical support the Syndicate provided. "
        "They have not told the player yet. They are deciding if the player can keep them alive.",
        "active",
        ["informant", "ally", "at-risk"],
        dict(force=30, influence=25, will=48, perception=78, resilience=35, volatility=68),
    ),
]

for name, summary, status, tags, stats in _chars:
    r = svc.create_entity(name=name, entity_type="character", summary=summary,
                          world=WORLD, status=status, tags=tags, stats=stats)
    chars[name] = r["entity"]["entity_id"]
    print(f"  + {name}")
print(f"  → {len(chars)} characters created.")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# OBJECTS  (potency, rarity, durability, risk, control, significance)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Objects â”€â”€")
_objs = [
    (
        "Neural Badge (Vellmore)",
        "The senator's standard-issue neural identification badge, recovered from the crime scene. "
        "It logged a secondary authentication pulse 4 seconds before the bullet struck — "
        "as if someone cloned it momentarily. The timestamp is impossible by standard means.",
        ["evidence", "crime-scene", "tech"],
        dict(potency=40, rarity=80, durability=70, risk=75, control=55, significance=92),
    ),
    (
        "Encrypted Message",
        "The single-line transmission that arrived on the player's wrist terminal in the opening scene. "
        "'They are watching.' Source traced to a terminal in the Sublevel Markets. "
        "Tomas Vellmore received an identical message 12 hours earlier.",
        ["evidence", "communication", "mystery"],
        dict(potency=35, rarity=65, durability=90, risk=60, control=30, significance=85),
    ),
    (
        "Magrail Seal Log",
        "The technical override log from Magrail Car Omega-7. "
        "It shows the car's external seal was disengaged for exactly 11 seconds during transit — "
        "impossible without a Council-level override code. The entry is unsigned.",
        ["evidence", "crime-scene", "technical"],
        dict(potency=70, rarity=72, durability=95, risk=65, control=40, significance=90),
    ),
    (
        "BioNex Prototype Canister",
        "A sealed neuro-chemical delivery canister found in the magrail car's ventilation shaft. "
        "Matches a batch number from BioNex Lab 4 — the lab destroyed in the Wing-7 fire. "
        "Dr. Blinn's initials are on the base.",
        ["evidence", "biotech", "weapon"],
        dict(potency=85, rarity=90, durability=60, risk=88, control=35, significance=92),
    ),
    (
        "Ghost Net Access Cipher",
        "A single-use cryptographic key provided by Splice. "
        "It allows one authenticated read session on the Ghost Net's Helix Corp breach archive. "
        "Using it will tell Splice exactly what the player is looking for.",
        ["tech", "information", "ally-gift"],
        dict(potency=60, rarity=88, durability=10, risk=50, control=45, significance=75),
    ),
    (
        "Ascendancy Override Chip",
        "Found hidden behind a false wall panel in the Vellmore Penthouse Suite. "
        "Council-level hardware — it can disengage any city-system lock including magrail seals. "
        "The ownership log was wiped, but the manufacturing serial points to one of seven people.",
        ["evidence", "government", "weapon"],
        dict(potency=92, rarity=95, durability=80, risk=90, control=60, significance=95),
    ),
    (
        "Vellmore's Private Comm Tablet",
        "The senator's personal encrypted communicator, found in his jacket. "
        "The last message sent was to an unregistered recipient 90 minutes before death. "
        "The content is encrypted with a key the player does not yet have.",
        ["evidence", "communication", "encrypted"],
        dict(potency=55, rarity=70, durability=85, risk=60, control=35, significance=88),
    ),
    (
        "Zero's Sniper Rig",
        "Disassembled precision weapon recovered at Harbor Docks Zone 9. "
        "Standard ballistics don't explain the wound — this rig fires a projectile that "
        "does not appear on standard forensic scans. Someone modified it beyond legal spec.",
        ["evidence", "weapon", "assassin"],
        dict(potency=90, rarity=85, durability=65, risk=82, control=50, significance=88),
    ),
    (
        "Forged Helix Corp Security Pass",
        "A near-perfect forgery of a Helix Corp Level-7 access pass. "
        "Found in a jacket discarded in the Underground Connector Tunnels. "
        "The biometric layer was overwritten with data that matches no registered individual.",
        ["evidence", "forgery", "corporate"],
        dict(potency=50, rarity=72, durability=75, risk=55, control=42, significance=70),
    ),
    (
        "Underground Holographic Map",
        "A complete holographic rendering of the Underground Connector Tunnels — "
        "including sections officially decommissioned and sealed. "
        "Sold in the Sublevel Markets. The Reclaimer Underground uses a variant of this map.",
        ["map", "information", "underground"],
        dict(potency=35, rarity=55, durability=30, risk=45, control=60, significance=65),
    ),
    (
        "Sublevel Syndicate Ledger",
        "A physical data-ledger seized during a Sublevel Market sweep. "
        "Contains coded entries for payments made the week before the assassination. "
        "One entry matches the Chrome Hand identification coin in the Evidence Vault.",
        ["evidence", "criminal", "financial"],
        dict(potency=65, rarity=60, durability=80, risk=70, control=50, significance=82),
    ),
    (
        "Neural Suppressor Device",
        "An illegal piece of hardware that blocks neural augmentation recording within a 5-meter radius. "
        "One was active in Magrail Car Omega-7 based on the dead zone in the car's sensor log. "
        "Manufactured and installed at the Iron Augment Clinic.",
        ["evidence", "weapon", "illegal-tech"],
        dict(potency=78, rarity=80, durability=55, risk=85, control=40, significance=85),
    ),
    (
        "Anti-Forensics Aerosol",
        "A compound that degrades biological and electronic trace evidence on contact. "
        "Used in the magrail car and at the Vellmore Penthouse before forensics arrived. "
        "The formulation matches a BioNex research compound from a project that was classified.",
        ["evidence", "weapon", "cover-up"],
        dict(potency=72, rarity=78, durability=20, risk=68, control=35, significance=80),
    ),
    (
        "Vellmore's Decrypted Comm Logs",
        "The senator's complete communication record from his final 72 hours. "
        "Decrypted by Splice using a Ghost Net tool. "
        "They reveal three meetings that were never on the public schedule — "
        "one of them with someone inside the Ascendancy Council.",
        ["evidence", "information", "decrypted"],
        dict(potency=75, rarity=70, durability=90, risk=72, control=45, significance=92),
    ),
    (
        "BioNex Gene-Lock Vial",
        "A small vial containing a genetically targeted delivery compound. "
        "Recovered from Zero's discard bag near the Orbital Relay Station. "
        "If analyzed, it can be matched to a specific biological profile — "
        "whoever commissioned it had access to the target's medical records.",
        ["evidence", "biotech", "weapon"],
        dict(potency=88, rarity=92, durability=50, risk=90, control=38, significance=90),
    ),
    (
        "Chrome Hand Identification Coin",
        "Found in the Precinct 17 Evidence Vault, not catalogued in any incident file. "
        "The Chrome Hand issues these to mark completed contracts. "
        "Someone placed it there after the vault breach — a message, or a mistake.",
        ["evidence", "criminal", "mercenary"],
        dict(potency=30, rarity=75, durability=95, risk=65, control=55, significance=80),
    ),
    (
        "Vellmore Amendment Draft",
        "A leaked copy of the legislation that would have broken Helix Corp's augmentation monopoly. "
        "Annotated by hand — the handwriting matches two different people. "
        "One set of notes is supportive. The other contains a single word: 'unacceptable.'",
        ["document", "political", "evidence"],
        dict(potency=45, rarity=65, durability=85, risk=55, control=60, significance=88),
    ),
    (
        "Order Neural Circuit Relic",
        "A ceremonial neural circuit worn by senior members of the Order of the Neural Seal. "
        "One was found near the Precinct 17 Evidence Vault breach site. "
        "Father Nura claims the Order does not engage in criminal activity.",
        ["evidence", "cult", "religious"],
        dict(potency=25, rarity=70, durability=90, risk=45, control=65, significance=68),
    ),
    (
        "Orbital Relay Bypass Module",
        "Custom hardware that creates a ghost entry in the Orbital Relay Station's departure manifest. "
        "Used by Zero to exit Cyber-Rim without a logged identity. "
        "The manufacture signature is from the Iron Augment Cartel.",
        ["evidence", "tech", "escape"],
        dict(potency=70, rarity=88, durability=60, risk=78, control=40, significance=82),
    ),
    (
        "Reclaimer Contact List",
        "A partial list of Reclaimer Underground contacts in the upper and mid tiers. "
        "Recovered from a dead drop in the Sublevel Markets. "
        "Several names are Precinct Detective Bureau staff. "
        "One name is in the Ascendancy Council Chamber.",
        ["document", "rebel", "information"],
        dict(potency=55, rarity=68, durability=70, risk=80, control=35, significance=78),
    ),
]

for name, summary, tags, stats in _objs:
    r = svc.create_entity(name=name, entity_type="object", summary=summary,
                          world=WORLD, tags=tags, stats=stats)
    objs[name] = r["entity"]["entity_id"]
    print(f"  + {name}")
print(f"  → {len(objs)} objects created.")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# EVENTS  (scale, urgency, fallout, visibility, disruption, momentum)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Events â”€â”€")
_evts = [
    (
        "The Vellmore Assassination",
        "Senator Ilias Vellmore shot dead inside a sealed, moving magrail car. "
        "No physical shooter's angle exists. Neural forensics blocked by a suppressor. "
        "The brass wants it closed quietly. The player's gut says otherwise.",
        "active",
        ["murder", "central", "political"],
        dict(scale=95, urgency=95, fallout=90, visibility=85, disruption=88, momentum=80),
    ),
    (
        "Precinct 17 Evidence Vault Breach",
        "The vault beneath Precinct 17 was accessed the night before the assassination. "
        "Three items reviewed, one replaced. Commander Orvani's card was used. "
        "The replacement item is the Chrome Hand identification coin — never catalogued.",
        "active",
        ["crime", "evidence", "precinct"],
        dict(scale=55, urgency=80, fallout=72, visibility=30, disruption=65, momentum=70),
    ),
    (
        "Vellmore's Final Public Speech",
        "The senator's last address, given at the Ascendancy Council Chamber three days before his death. "
        "He named no names but the room understood. "
        "Lena Moro recorded something in the crowd's reaction that the official feeds cut.",
        "active",
        ["political", "public", "prelude"],
        dict(scale=70, urgency=45, fallout=60, visibility=88, disruption=55, momentum=65),
    ),
    (
        "Ascendancy Emergency Session",
        "An unscheduled Council session convened within 4 hours of the assassination. "
        "Not officially recorded. Marcus Thell exited alone. "
        "Six other Council members' locations during the following hour remain unconfirmed.",
        "active",
        ["government", "cover-up", "council"],
        dict(scale=80, urgency=85, fallout=78, visibility=25, disruption=72, momentum=75),
    ),
    (
        "BioNex Wing-7 Lab Fire",
        "A fire destroyed Wing-7 of the BioNex Research Campus 48 hours before the assassination. "
        "The Wing held records for the prototype canister project. "
        "The campus fire suppression system was deactivated for a 7-minute window.",
        "active",
        ["fire", "cover-up", "biotech"],
        dict(scale=62, urgency=70, fallout=80, visibility=55, disruption=70, momentum=60),
    ),
    (
        "Ghost Net Helix Corp Data Breach",
        "The Ghost Net released internal Helix Corp communications to a dark-net archive. "
        "Splice authenticated the data. The files show private Council lobbying "
        "and a payment to an unnamed contractor three weeks before the assassination.",
        "active",
        ["hacker", "information", "explosive"],
        dict(scale=75, urgency=65, fallout=85, visibility=60, disruption=78, momentum=72),
    ),
    (
        "Sublevel Market Riots",
        "Three days of unrest following Vellmore's death. The Sublevel Syndicate let it run; "
        "the City Security Division moved in on the fourth day. "
        "Emery Vixt got hurt in the sweep. Something was moved during the chaos.",
        "active",
        ["unrest", "political", "tier-lower"],
        dict(scale=68, urgency=55, fallout=62, visibility=72, disruption=75, momentum=45),
    ),
    (
        "Zero Sighting at Harbor Docks",
        "A Harbor Consortium dockworker reported seeing someone matching Zero's profile "
        "loading onto a shuttle pod three days after the assassination. "
        "By the time Precinct 17 received the tip, the departure log had been altered.",
        "active",
        ["fugitive", "assassin", "port"],
        dict(scale=50, urgency=75, fallout=55, visibility=30, disruption=45, momentum=65),
    ),
    (
        "Lena Moro's First Article",
        "Moro published a piece naming the Vellmore Amendment's opponents in corporate and government circles. "
        "Director Quen moved to suppress it within the hour. "
        "Three media outlets ran it anyway. Two have since retracted under unspecified pressure.",
        "active",
        ["journalism", "political", "information"],
        dict(scale=65, urgency=60, fallout=72, visibility=80, disruption=58, momentum=68),
    ),
    (
        "Null Zone Crackdown",
        "City Security Division cleared 2,000 residents from the Null Zone three months ago. "
        "The Null Collective retreated inward rather than fight. "
        "The stated reason was public safety. The actual reason has not been established.",
        "active",
        ["government", "oppression", "null-zone"],
        dict(scale=72, urgency=30, fallout=65, visibility=58, disruption=68, momentum=40),
    ),
    (
        "Tomas Vellmore Goes Missing",
        "The senator's son vanished from his registered address 6 hours after his father's death. "
        "He is alive — the Reclaimer Underground and Kaia Thell are sheltering him in the Lower Tier Slums. "
        "The player doesn't know this yet.",
        "active",
        ["missing-person", "civilian", "hidden"],
        dict(scale=48, urgency=72, fallout=50, visibility=45, disruption=38, momentum=60),
    ),
    (
        "Helix Corp Stock Crash",
        "Helix Corp's stock dropped 34 points beginning at 6:00 AM on the morning of the assassination — "
        "two hours before the body was officially discovered. "
        "Veronika Strand has not commented. The Ascendancy financial regulator opened a review.",
        "active",
        ["financial", "corporate", "suspicious"],
        dict(scale=62, urgency=55, fallout=70, visibility=75, disruption=60, momentum=55),
    ),
    (
        "Magrail System Override Hack",
        "Analysis of the Magrail Seal Log revealed a Council-level override command "
        "injected remotely into the Omega-7 car's lock system 11 seconds before death. "
        "The command origin was routed through three relay nodes — two are in Ascendancy Spires.",
        "active",
        ["technical", "evidence", "conspiracy"],
        dict(scale=70, urgency=80, fallout=75, visibility=30, disruption=65, momentum=72),
    ),
    (
        "Internal Affairs Investigation Opened",
        "Inspector Caye Norn quietly opened a Vellmore file inside Internal Affairs — "
        "nobody asked for it. The investigation is legitimate on paper "
        "and directly reported to the Ascendancy Council, who approved it.",
        "active",
        ["investigation", "internal", "political"],
        dict(scale=55, urgency=58, fallout=62, visibility=25, disruption=45, momentum=60),
    ),
    (
        "Order of the Neural Seal Mass Gathering",
        "Father Azeth Nura convened a large gathering at the Null Zone's edge "
        "the night of the assassination. Attendance was 600+. "
        "A neural circuit relic was found near the Evidence Vault breach site. "
        "Nura says he was at the gathering all night. Witnesses confirm it. Most of them.",
        "active",
        ["cult", "gathering", "alibi"],
        dict(scale=45, urgency=35, fallout=48, visibility=52, disruption=38, momentum=40),
    ),
    (
        "Encrypted Message Interception Attempt",
        "Someone tried to intercept the encrypted message sent to the player's wrist terminal. "
        "The attempt was made from a Department of Information Control relay. "
        "It failed — barely. The message was routed through Ghost Net infrastructure.",
        "active",
        ["communication", "surveillance", "government"],
        dict(scale=38, urgency=65, fallout=48, visibility=20, disruption=35, momentum=58),
    ),
    (
        "Roen Kasra's Cold Case",
        "Three years ago, Detective Kasra worked a case involving a sealed vehicle death. "
        "No bullet. No shooter's angle. Case closed as accidental. "
        "The victim was a minor Vellmore political ally. Kasra has said nothing.",
        "active",
        ["cold-case", "pattern", "partner"],
        dict(scale=50, urgency=40, fallout=60, visibility=15, disruption=42, momentum=55),
    ),
    (
        "Chrome Hand Contract Posted",
        "An open-scope contract was posted to Chrome Hand channels within 48 hours of the assassination. "
        "The target profile matches Tomas Vellmore and two members of the Vellmore Political Alliance. "
        "Ossian Vrek has not confirmed or denied accepting it.",
        "active",
        ["contract", "mercenary", "threat"],
        dict(scale=55, urgency=80, fallout=65, visibility=20, disruption=55, momentum=72),
    ),
    (
        "Dr. Blinn Requests Protective Custody",
        "Dr. Yara Blinn filed a formal protection request with Precinct 17 24 hours after the lab fire. "
        "She withdrew the request 6 hours later without explanation. "
        "She has not been seen at BioNex since. Her personal comms have gone dark.",
        "active",
        ["witness", "at-risk", "disappearance"],
        dict(scale=42, urgency=75, fallout=55, visibility=20, disruption=40, momentum=65),
    ),
    (
        "Reclaimer Protest at Ascendancy Spires",
        "The Reclaimer Underground staged an unannounced protest at the base of the Ascendancy Spires. "
        "It was broken up within minutes. Kaia Thell was not present — she organized it remotely. "
        "Three protestors were taken to the Deprogramming Center.",
        "active",
        ["protest", "rebel", "suppression"],
        dict(scale=52, urgency=40, fallout=58, visibility=65, disruption=60, momentum=45),
    ),
]

for name, summary, status, tags, stats in _evts:
    r = svc.create_entity(name=name, entity_type="event", summary=summary,
                          world=WORLD, status=status, tags=tags, stats=stats)
    evts[name] = r["entity"]["entity_id"]
    print(f"  + {name}")
print(f"  → {len(evts)} events created.")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# LINKS — wire the world together
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Links â”€â”€")

def link(a_id: str, b_id: str, relation: str) -> None:
    svc.link_entities(entity_id_a=a_id, entity_id_b=b_id, world=WORLD, relation=relation)


# Characters â†” Factions
link(chars["Senator Ilias Vellmore"],   facs["Vellmore Reform Movement"],         "founded")
link(chars["Senator Ilias Vellmore"],   facs["Vellmore Political Alliance"],       "led")
link(chars["Detective Roen Kasra"],     facs["Precinct Detective Bureau"],         "member-of")
link(chars["Commander Helise Orvani"], facs["Precinct Detective Bureau"],          "commands")
link(chars["Marcus Thell"],             facs["Ascendancy Council"],                "chairs")
link(chars["Dr. Yara Blinn"],           facs["BioNex Industries"],                 "former-researcher")
link(chars["Splice"],                   facs["The Ghost Net"],                     "operates")
link(chars["Veronika Strand"],          facs["Helix Corporation"],                 "ceo-of")
link(chars["Gavrel Mout"],              facs["Sublevel Syndicate"],                "boss-of")
link(chars["Gavrel Mout"],              facs["The Synthwave Cartel"],              "controls")
link(chars["Inspector Caye Norn"],      facs["Ascendancy Internal Affairs"],       "leads")
link(chars["Tomas Vellmore"],           facs["Vellmore Reform Movement"],          "heir-to")
link(chars["Tomas Vellmore"],           facs["Reclaimer Underground"],             "sheltered-by")
link(chars["Director Syl Quen"],        facs["Department of Information Control"], "directs")
link(chars["Father Azeth Nura"],        facs["Order of the Neural Seal"],          "leads")
link(chars["Ossian Vrek"],              facs["The Chrome Hand"],                   "commands")
link(chars["Kaia Thell"],               facs["Reclaimer Underground"],             "finances")
link(chars["Kaia Thell"],               facs["Ascendancy Council"],                "defected-from")
link(chars["Senator Brenni Vorst"],     facs["Ascendancy Council"],                "aligned-with")
link(chars["Emery Vixt"],               facs["Sublevel Syndicate"],                "informant-inside")
link(chars["Zero"],                     facs["Iron Augment Cartel"],               "modified-by")
link(chars["Zero"],                     facs["The Chrome Hand"],                   "suspected-contractor")
link(chars["Lena Moro"],                facs["Vellmore Reform Movement"],          "supports")
link(chars["Constable Pren Dalik"],     facs["Precinct Detective Bureau"],         "member-of")

# Characters â†” Locations (base / last-seen / key-connection)
link(chars["Detective Roen Kasra"],     locs["Precinct 17"],                       "based-at")
link(chars["Commander Helise Orvani"], locs["Precinct 17"],                        "commands")
link(chars["Commander Helise Orvani"], locs["Precinct 17 Evidence Vault"],         "accessed-before-breach")
link(chars["Senator Ilias Vellmore"],  locs["Magrail Car Omega-7"],               "died-in")
link(chars["Senator Ilias Vellmore"],  locs["Vellmore Penthouse Suite"],           "residence")
link(chars["Marcus Thell"],             locs["Ascendancy Council Chamber"],        "operates-from")
link(chars["Marcus Thell"],             locs["Ascendancy Spires"],                 "based-at")
link(chars["Dr. Yara Blinn"],           locs["BioNex Research Campus"],            "former-workplace")
link(chars["Splice"],                   locs["Ghost Node Alpha"],                  "operates-from")
link(chars["Veronika Strand"],          locs["Helix Corp Executive Tower"],        "based-at")
link(chars["Gavrel Mout"],              locs["Sublevel Markets"],                  "controls")
link(chars["Gavrel Mout"],              locs["Synthwave Club Neonkiss"],           "meets-clients-here")
link(chars["Inspector Caye Norn"],      locs["The Obsidian Court"],                "operates-from")
link(chars["Tomas Vellmore"],           locs["Lower Tier Slums"],                  "hiding-here")
link(chars["Constable Pren Dalik"],     locs["Neon Canyon District"],              "beat-assignment")
link(chars["The Archivist"],            locs["Sublevel Markets"],                  "uses-dead-drops")
link(chars["Lena Moro"],                locs["Neon Canyon District"],              "operates-from")
link(chars["Director Syl Quen"],        locs["Deprogramming Center"],              "founded")
link(chars["Father Azeth Nura"],        locs["The Null Zone"],                     "gathers-here")
link(chars["Ossian Vrek"],              locs["Harbor Docks Zone 9"],               "uses-for-operations")
link(chars["Kaia Thell"],               locs["Lower Tier Slums"],                  "hides-here")
link(chars["Zero"],                     locs["Iron Augment Clinic"],               "modified-here")
link(chars["Zero"],                     locs["Orbital Relay Station"],             "fled-from")
link(chars["Zero"],                     locs["Harbor Docks Zone 9"],               "last-sighted-here")
link(chars["Emery Vixt"],               locs["Sublevel Markets"],                  "operates-from")

# Characters â†” Events
link(chars["Senator Ilias Vellmore"],  evts["The Vellmore Assassination"],         "victim")
link(chars["Senator Ilias Vellmore"],  evts["Vellmore's Final Public Speech"],     "speaker")
link(chars["Detective Roen Kasra"],     evts["Roen Kasra's Cold Case"],            "lead-investigator")
link(chars["Commander Helise Orvani"], evts["Precinct 17 Evidence Vault Breach"],  "access-card-used")
link(chars["Marcus Thell"],             evts["Ascendancy Emergency Session"],      "presided-over")
link(chars["Dr. Yara Blinn"],           evts["BioNex Wing-7 Lab Fire"],            "witness")
link(chars["Dr. Yara Blinn"],           evts["Dr. Blinn Requests Protective Custody"], "subject")
link(chars["Splice"],                   evts["Ghost Net Helix Corp Data Breach"],  "executed")
link(chars["Veronika Strand"],          evts["Helix Corp Stock Crash"],            "implicated-by")
link(chars["Gavrel Mout"],              evts["Sublevel Market Riots"],             "allowed-to-run")
link(chars["Inspector Caye Norn"],      evts["Internal Affairs Investigation Opened"], "opened-file")
link(chars["Tomas Vellmore"],           evts["Tomas Vellmore Goes Missing"],       "subject")
link(chars["Lena Moro"],                evts["Lena Moro's First Article"],         "author")
link(chars["Lena Moro"],                evts["Vellmore's Final Public Speech"],    "recorded-footage")
link(chars["Director Syl Quen"],        evts["Encrypted Message Interception Attempt"], "ordered")
link(chars["Director Syl Quen"],        evts["Null Zone Crackdown"],               "co-authorized")
link(chars["Father Azeth Nura"],        evts["Order of the Neural Seal Mass Gathering"], "led")
link(chars["Ossian Vrek"],              evts["Chrome Hand Contract Posted"],       "contractor")
link(chars["Kaia Thell"],               evts["Reclaimer Protest at Ascendancy Spires"], "organized")
link(chars["Zero"],                     evts["The Vellmore Assassination"],        "perpetrator")
link(chars["Zero"],                     evts["Zero Sighting at Harbor Docks"],     "sighted")
link(chars["Senator Brenni Vorst"],     evts["Vellmore's Final Public Speech"],    "attended")
link(chars["Emery Vixt"],               evts["Sublevel Market Riots"],             "injured-in")

# Characters â†” Objects
link(chars["Senator Ilias Vellmore"],  objs["Neural Badge (Vellmore)"],            "owned")
link(chars["Senator Ilias Vellmore"],  objs["Vellmore's Private Comm Tablet"],     "owned")
link(chars["Senator Ilias Vellmore"],  objs["Vellmore Amendment Draft"],           "authored")
link(chars["Senator Ilias Vellmore"],  objs["Vellmore's Decrypted Comm Logs"],     "source")
link(chars["Splice"],                   objs["Ghost Net Access Cipher"],           "provided")
link(chars["Splice"],                   objs["Vellmore's Decrypted Comm Logs"],    "decrypted")
link(chars["Dr. Yara Blinn"],           objs["BioNex Prototype Canister"],         "created")
link(chars["Zero"],                     objs["Zero's Sniper Rig"],                 "used")
link(chars["Zero"],                     objs["BioNex Gene-Lock Vial"],             "carried")
link(chars["Zero"],                     objs["Orbital Relay Bypass Module"],       "used-to-escape")
link(chars["Zero"],                     objs["Neural Suppressor Device"],          "deployed")
link(chars["Zero"],                     objs["Anti-Forensics Aerosol"],            "deployed")
link(chars["Commander Helise Orvani"], objs["Chrome Hand Identification Coin"],    "placed-in-vault")
link(chars["The Archivist"],            objs["Reclaimer Contact List"],            "compiled")
link(chars["Tomas Vellmore"],           objs["Encrypted Message"],                 "received-prior-copy")

# Factions â†” Locations (controls / operates-from)
link(facs["Ascendancy Council"],        locs["Ascendancy Spires"],                 "governs-from")
link(facs["Ascendancy Council"],        locs["Ascendancy Council Chamber"],        "meets-in")
link(facs["Precinct Detective Bureau"], locs["Precinct 17"],                       "operates-from")
link(facs["Precinct Detective Bureau"], locs["Precinct 17 Evidence Vault"],        "controls")
link(facs["Helix Corporation"],         locs["Helix Corp Executive Tower"],        "headquartered")
link(facs["Sublevel Syndicate"],        locs["Sublevel Markets"],                  "controls")
link(facs["Sublevel Syndicate"],        locs["Synthwave Club Neonkiss"],           "operates")
link(facs["BioNex Industries"],         locs["BioNex Research Campus"],            "owns")
link(facs["The Chrome Hand"],           locs["Harbor Docks Zone 9"],               "uses-for-exfil")
link(facs["The Ghost Net"],             locs["Ghost Node Alpha"],                  "operates-from")
link(facs["Order of the Neural Seal"],  locs["The Null Zone"],                     "gathers-at")
link(facs["Harbor Consortium"],         locs["Harbor Docks Zone 9"],               "controls")
link(facs["City Security Division"],    locs["Neon Canyon District"],              "patrols")
link(facs["Ascendancy Internal Affairs"], locs["The Obsidian Court"],              "uses")
link(facs["Department of Information Control"], locs["Deprogramming Center"],      "runs")
link(facs["Iron Augment Cartel"],       locs["Iron Augment Clinic"],               "operates")
link(facs["Reclaimer Underground"],     locs["Underground Connector Tunnels"],     "uses-as-routes")
link(facs["Reclaimer Underground"],     locs["Lower Tier Slums"],                  "recruits-from")
link(facs["The Null Collective"],       locs["The Null Zone"],                     "based-in")
link(facs["Orbital Authority"],         locs["Orbital Relay Station"],             "administers")

# Events â†” Locations (happened-at)
link(evts["The Vellmore Assassination"],              locs["Magrail Car Omega-7"],        "occurred-in")
link(evts["Precinct 17 Evidence Vault Breach"],       locs["Precinct 17 Evidence Vault"],  "occurred-in")
link(evts["Vellmore's Final Public Speech"],          locs["Ascendancy Council Chamber"],  "occurred-in")
link(evts["Ascendancy Emergency Session"],            locs["Ascendancy Council Chamber"],  "occurred-in")
link(evts["BioNex Wing-7 Lab Fire"],                  locs["BioNex Research Campus"],      "occurred-at")
link(evts["Ghost Net Helix Corp Data Breach"],        locs["Ghost Node Alpha"],            "originated-from")
link(evts["Sublevel Market Riots"],                   locs["Sublevel Markets"],            "occurred-in")
link(evts["Zero Sighting at Harbor Docks"],           locs["Harbor Docks Zone 9"],         "sighting-location")
link(evts["Null Zone Crackdown"],                     locs["The Null Zone"],               "occurred-in")
link(evts["Tomas Vellmore Goes Missing"],             locs["Lower Tier Slums"],            "destination")
link(evts["Helix Corp Stock Crash"],                  locs["Helix Corp Executive Tower"],  "corporate-location")
link(evts["Magrail System Override Hack"],            locs["Magrail Car Omega-7"],         "target")
link(evts["Magrail System Override Hack"],            locs["Ascendancy Spires"],           "origin-nodes")
link(evts["Order of the Neural Seal Mass Gathering"], locs["The Null Zone"],               "occurred-at")
link(evts["Reclaimer Protest at Ascendancy Spires"],  locs["Ascendancy Spires"],           "occurred-at")
link(evts["Zero Sighting at Harbor Docks"],           locs["Orbital Relay Station"],       "fled-to")

# Events â†” Objects (evidence / artifacts)
link(evts["The Vellmore Assassination"],        objs["Neural Badge (Vellmore)"],           "evidence")
link(evts["The Vellmore Assassination"],        objs["BioNex Prototype Canister"],         "evidence")
link(evts["The Vellmore Assassination"],        objs["Neural Suppressor Device"],          "used-in")
link(evts["The Vellmore Assassination"],        objs["Anti-Forensics Aerosol"],            "used-in")
link(evts["The Vellmore Assassination"],        objs["Zero's Sniper Rig"],                 "weapon-used")
link(evts["Precinct 17 Evidence Vault Breach"], objs["Chrome Hand Identification Coin"],   "left-behind")
link(evts["Precinct 17 Evidence Vault Breach"], objs["Order Neural Circuit Relic"],        "found-near-scene")
link(evts["Magrail System Override Hack"],      objs["Magrail Seal Log"],                  "documented-in")
link(evts["Magrail System Override Hack"],      objs["Ascendancy Override Chip"],          "used-for")
link(evts["Ghost Net Helix Corp Data Breach"],  objs["Ghost Net Access Cipher"],           "access-point")
link(evts["Ghost Net Helix Corp Data Breach"],  objs["Vellmore's Decrypted Comm Logs"],    "recovered-from")
link(evts["BioNex Wing-7 Lab Fire"],            objs["BioNex Prototype Canister"],         "records-destroyed-for")
link(evts["BioNex Wing-7 Lab Fire"],            objs["BioNex Gene-Lock Vial"],             "manufacture-site-destroyed")
link(evts["Zero Sighting at Harbor Docks"],     objs["Orbital Relay Bypass Module"],       "used-here")
link(evts["Vellmore's Final Public Speech"],    objs["Vellmore Amendment Draft"],          "referenced")
link(evts["Chrome Hand Contract Posted"],       objs["Sublevel Syndicate Ledger"],         "payment-logged-in")
link(evts["Encrypted Message Interception Attempt"], objs["Encrypted Message"],            "target")

# Events â†” Factions
link(evts["The Vellmore Assassination"],        facs["Ascendancy Council"],                "politically-motivated")
link(evts["The Vellmore Assassination"],        facs["The Chrome Hand"],                   "suspected-executor")
link(evts["Ghost Net Helix Corp Data Breach"],  facs["The Ghost Net"],                     "perpetrated-by")
link(evts["Ghost Net Helix Corp Data Breach"],  facs["Helix Corporation"],                 "target")
link(evts["Sublevel Market Riots"],             facs["City Security Division"],            "suppressed-by")
link(evts["Sublevel Market Riots"],             facs["Sublevel Syndicate"],                "allowed-by")
link(evts["Null Zone Crackdown"],               facs["City Security Division"],            "executed-by")
link(evts["Null Zone Crackdown"],               facs["The Null Collective"],               "target")
link(evts["Internal Affairs Investigation Opened"], facs["Ascendancy Internal Affairs"],  "opened-by")
link(evts["Chrome Hand Contract Posted"],       facs["The Chrome Hand"],                   "issued-to")
link(evts["Chrome Hand Contract Posted"],       facs["Reclaimer Underground"],             "possible-client")
link(evts["Reclaimer Protest at Ascendancy Spires"], facs["Reclaimer Underground"],        "organized-by")
link(evts["BioNex Wing-7 Lab Fire"],            facs["BioNex Industries"],                 "affected")
link(evts["Helix Corp Stock Crash"],            facs["Helix Corporation"],                 "affected")
link(evts["Ascendancy Emergency Session"],      facs["Ascendancy Council"],                "held-by")
link(evts["Encrypted Message Interception Attempt"], facs["Department of Information Control"], "executed-by")

print(f"  Links created.")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CONTAINMENT — place key objects and characters in their locations
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print("\nâ”€â”€ Containment placements â”€â”€")

def move(entity_name: str, entity_dict: dict, container_name: str) -> None:
    eid = entity_dict[entity_name]
    cid = locs[container_name]
    svc.move(entity_id=eid, new_container_id=cid, world=WORLD,
             reason=f"Initial world seeding: {entity_name} placed in {container_name}")
    print(f"  {entity_name} → {container_name}")


# Objects in locations
move("Neural Badge (Vellmore)",      objs, "Magrail Car Omega-7")
move("Magrail Seal Log",             objs, "Magrail Car Omega-7")
move("BioNex Prototype Canister",    objs, "Magrail Car Omega-7")
move("Ascendancy Override Chip",     objs, "Vellmore Penthouse Suite")
move("Vellmore's Private Comm Tablet", objs, "Vellmore Penthouse Suite")
move("Vellmore Amendment Draft",     objs, "Vellmore Penthouse Suite")
move("Chrome Hand Identification Coin", objs, "Precinct 17 Evidence Vault")
move("Order Neural Circuit Relic",   objs, "Precinct 17 Evidence Vault")
move("Zero's Sniper Rig",            objs, "Harbor Docks Zone 9")
move("Forged Helix Corp Security Pass", objs, "Underground Connector Tunnels")
move("Underground Holographic Map",  objs, "Sublevel Markets")
move("Sublevel Syndicate Ledger",    objs, "Sublevel Markets")
move("Reclaimer Contact List",       objs, "Sublevel Markets")
move("Neural Suppressor Device",     objs, "Iron Augment Clinic")
move("Orbital Relay Bypass Module",  objs, "Orbital Relay Station")
move("BioNex Gene-Lock Vial",        objs, "Harbor Docks Zone 9")
move("Ghost Net Access Cipher",      objs, "Ghost Node Alpha")
move("Vellmore's Decrypted Comm Logs", objs, "Ghost Node Alpha")

# Characters in locations (current position)
move("Detective Roen Kasra",         chars, "Precinct 17")
move("Commander Helise Orvani",      chars, "Precinct 17")
move("Constable Pren Dalik",         chars, "Neon Canyon District")
move("Emery Vixt",                   chars, "Sublevel Markets")
move("Gavrel Mout",                  chars, "Synthwave Club Neonkiss")
move("Splice",                       chars, "Ghost Node Alpha")
move("Veronika Strand",              chars, "Helix Corp Executive Tower")
move("Marcus Thell",                 chars, "Ascendancy Spires")
move("Director Syl Quen",            chars, "Deprogramming Center")
move("Father Azeth Nura",            chars, "The Null Zone")
move("Ossian Vrek",                  chars, "Harbor Docks Zone 9")
move("Kaia Thell",                   chars, "Lower Tier Slums")
move("Tomas Vellmore",               chars, "Lower Tier Slums")
move("Inspector Caye Norn",          chars, "The Obsidian Court")
move("Lena Moro",                    chars, "Neon Canyon District")
move("Senator Brenni Vorst",         chars, "Ascendancy Council Chamber")
move("The Archivist",                chars, "Sublevel Markets")

print("\nâ”€â”€ Seed complete â”€â”€")
print(f"  {len(locs)} locations")
print(f"  {len(facs)} factions")
print(f"  {len(chars)} characters")
print(f"  {len(objs)} objects")
print(f"  {len(evts)} events")
print("  Links + containment placements applied.")
print("  Cyber-Rim is live.")
