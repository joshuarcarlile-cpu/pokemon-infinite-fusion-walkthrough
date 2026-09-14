---
name: pif-ground-truth
description: >-
  Authoritative ground-truth reference and fact-checking workflow for Pokémon Infinite Fusion.
  Use whenever auditing game mechanics, route access, missable events, evolution methods,
  tool requirements, or NPC behaviors before making definitive statements.
---

# Pokémon Infinite Fusion: Ground Truth & Fact-Checking Workflow

This skill provides agents with standard operating procedures to verify facts against local authoritative databases, preventing vanilla Pokémon (Gen 1 / FRLG) assumptions from contaminating the walkthrough.

---

## 1. The 3 Authoritative Local Ground Truth Tiers

When verifying any mechanic, quest, or encounter, search the local repository in this priority order:

1. **Local Wiki Cache (`data/wiki/<Page>.json`)**:
   - MediaWiki API dump of canonical wiki pages for every route, city, and mechanic.
   - Contains item coordinates, full trainer rosters, exact encounter percentages, and points of interest.
   - *Example*: `data/wiki/S.S._Anne.json` contains: `"The S. S. Anne does not depart when the player disembarks, and players may board and disembark as much as they want."`
2. **Master Quests Registry (`data/quests/master_quests.json`)**:
   - Complete registry of all 98+ quests across Kanto and Johto.
   - Authoritative for `is_missable`, `missable_deadline`, `karma_delta`, and `rewards`.
   - *Rule*: If an event is NOT listed with `"is_missable": true`, it is NOT permanently missable!
3. **Unpacked Game Engine Scripts (`IF GAME/InfiniteFusion/Data/Scripts/`)**:
   - The literal Ruby source code of Pokémon Infinite Fusion.
   - Inspect `Gameplay/Quests/Quests.rb` for quest triggers, `Gameplay/Items/` for tool mechanics, and `Data/dex.json` for base stats and pokedex entries.

---

## 2. Instant Fact-Checking with `query_ground_truth.py`

Agents should run the CLI oracle tool to immediately pull verified facts before writing:

```bash
# Query all data for a specific route or city
python scripts/query_ground_truth.py --route "Vermilion City"

# Query S.S. Anne mechanics, quests, and departure status
python scripts/query_ground_truth.py --route "S.S. Anne"

# List all verified permanently missable events in the game
python scripts/query_ground_truth.py --missables

# Audit a statement against known vanilla hallucination patterns
python scripts/query_ground_truth.py --check "The S.S. Anne leaves port after talking to the Captain"
```

---

## 3. Mandatory Fact-Checking Checklist Before Authoring

Before saving any phase, boss card, or team fixture:
- [ ] **Missables**: Is every claimed missable registered in `master_quests.json` with `is_missable: true`?
- [ ] **HM Tools**: Are players routed to the Key Item tool (e.g. Shears on Route 2 Before Forest) rather than instructed to use an HM move?
- [ ] **Evolutions**: Are trade evolutions set to Level 40 or Linking Cord (NOT 37)?
- [ ] **Level Cap**: Are all party levels and moves legal at or below the Hard Mode Gym Cap?
- [ ] **Area Accessibility**: Does the local wiki confirm the area remains accessible or locks out?
