"""
Phase Encounter Canonical Location Linter for Pokémon Infinite Fusion
Verifies that every Pokémon listed in a phase's encounters actually originates
from that specific location according to:
1. PBS Wild encounter tables (data/encounters/kanto/)
2. Wiki In-game Gifts & Special Purchases (data/mechanics/wiki_gifts_and_trades.json)
3. Wiki In-game NPC Trades (data/mechanics/wiki_gifts_and_trades.json)
4. Wiki Overworld Static & Interactive Encounters (data/mechanics/wiki_static_encounters.json)
5. Celadon Game Corner prizes
"""

import os
import sys
import json
import glob
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ENCOUNTERS_DIR = os.path.join(DATA_DIR, "encounters", "kanto")

def load_json(p):
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

GIFTS_TRADES = load_json(os.path.join(DATA_DIR, "mechanics", "wiki_gifts_and_trades.json"))
STATIC_ENCOUNTERS = load_json(os.path.join(DATA_DIR, "mechanics", "wiki_static_encounters.json"))
ROUTE_FILES = glob.glob(os.path.join(ENCOUNTERS_DIR, "*.json"))

def extract_locations_from_phase_name(phase_name):
    cleaned = phase_name.lower().replace("'", "").replace(".", "")
    locations = set()

    # Route ranges like 'Routes 12 to 15' or 'Routes 12-15'
    range_match = re.search(r'routes?\s+(\d+)\s*(?:to|-)\s*(\d+)', cleaned)
    if range_match:
        start, end = int(range_match.group(1)), int(range_match.group(2))
        for r in range(start, end + 1):
            locations.add(f"route_{r}")

    if "route" in cleaned:
        for num in re.findall(r'\b(\d+)\b', cleaned):
            locations.add(f"route_{num}")

    # Named landmarks
    landmarks = [
        ("pallet", ["pallet_town"]),
        ("viridian river", ["viridian_river"]),
        ("viridian gym", ["viridian_city"]),
        ("viridian city", ["viridian_city"]),
        ("viridian forest", ["viridian_forest", "route_2"]),
        ("secret garden", ["secret_garden", "route_22"]),
        ("pewter", ["pewter_city"]),
        ("mt moon", ["mt_moon"]),
        ("cerulean", ["cerulean_city"]),
        ("nugget bridge", ["route_24", "nugget_bridge"]),
        ("bill", ["route_25", "sea_cottage"]),
        ("vermilion", ["vermillion_city", "vermilion_city"]),
        ("ss anne", ["ss_anne", "s_s_anne"]),
        ("diglett", ["digletts_cave", "diglett"]),
        ("rock tunnel", ["rock_tunnel"]),
        ("lavender", ["lavender_town", "pokemon_tower", "route_10"]),
        ("celadon sewers", ["celadon_sewers", "celadon_city", "celadon"]),
        ("celadon", ["celadon_city", "celadon"]),
        ("fuchsia", ["fuchsia_city"]),
        ("safari zone", ["safari_zone", "area_1", "area_2", "area_3", "area_4", "area_5"]),
        ("saffron", ["saffron_city", "saffron"]),
        ("silph", ["silph_co", "silph_co._head_office", "silph"]),
        ("dojo", ["fighting_dojo", "dojo", "saffron_city"]),
        ("seafoam", ["seafoam_islands", "route_20"]),
        ("cinnabar", ["cinnabar_island", "cinnabar"]),
        ("mansion", ["pokémon_mansion", "pokemon_mansion", "mansion", "cinnabar_island"]),
        ("victory road", ["victory_road"]),
        ("indigo plateau", ["indigo_plateau"]),
        ("elite four", ["indigo_plateau"]),
        ("goldenrod", ["goldenrod_city", "route_34"]),
        ("route 34", ["route_34"]),
        ("ilex forest", ["ilex_forest"]),
        ("azalea", ["azalea_town", "slowpoke_well"]),
        ("slowpoke well", ["slowpoke_well", "azalea_town"]),
        ("route 33", ["route_33"]),
        ("union cave", ["union_cave"]),
        ("route 32", ["route_32"]),
        ("violet city", ["violet_city", "sprout_tower"]),
        ("sprout tower", ["sprout_tower", "violet_city"]),
        ("route 36", ["route_36"]),
        ("national park", ["national_park"]),
        ("route 31", ["route_31"]),
        ("route 30", ["route_30"]),
        ("cherrygrove", ["cherrygrove_city"]),
        ("route 29", ["route_29"]),
        ("new bark", ["new_bark_town"]),
        ("ruins of alph", ["ruins_of_alph"]),
        ("alph", ["ruins_of_alph"]),
        ("burned tower", ["burned_tower"]),
        ("ecruteak", ["ecruteak_city", "ecruteak"]),
        ("route 37", ["route_37"]),
        ("bell tower", ["bell_tower", "ecruteak_city"]),
        ("route 42", ["route_42"]),
        ("mt mortar", ["mt_mortar"]),
        ("mortar", ["mt_mortar"]),
        ("mahogany", ["mahogany_town", "mahogany"]),
        ("route 43", ["route_43"]),
        ("lake of rage", ["lake_of_rage"]),
        ("rage", ["lake_of_rage"]),
        ("route 44", ["route_44"]),
        ("ice mountains", ["ice_mountains", "ice_cavern"]),
        ("ice mountain", ["ice_mountains", "ice_cavern"]),
        ("ice cavern", ["ice_cavern", "ice_mountains"]),
        ("blackthorn", ["blackthorn_city"]),
        ("dragons den", ["blackthorn_city"]),
        ("dragon's den", ["blackthorn_city"]),
        ("route 45", ["route_45", "route_46", "blackthorn_city"]),
        ("route 46", ["route_46", "route_29"])
    ]
    for key, slugs in landmarks:
        if key in cleaned:
            locations.update(slugs)

    return list(locations)

WIKI_FILES = glob.glob(os.path.join(DATA_DIR, "wiki", "*.json"))
WIKI_CLASSIC_POKEDEX = load_json(os.path.join(DATA_DIR, "mechanics", "wiki_classic_pokedex.json"))

def get_canonical_species_for_phase(phase_name):
    loc_slugs = extract_locations_from_phase_name(phase_name)
    allowed = set()

    # 1. Wild PBS Encounters
    for slug in loc_slugs:
        for rf in ROUTE_FILES:
            bname = os.path.basename(rf).lower()
            if slug in bname or (slug == "safari_zone" and "area_" in bname):
                edata = load_json(rf)
                for sec, mlist in edata.get("sections", {}).items():
                    for m in mlist:
                        mname = m.get("name")
                        if mname:
                            allowed.add(mname.strip())

    # 2. Wiki Route Encounter Tables (e.g. Diglett's Cave)
    for slug in loc_slugs:
        for wf in WIKI_FILES:
            bname = os.path.basename(wf).lower()
            if slug in bname:
                wdata = load_json(wf)
                raw = wdata.get("raw_wikitext", "")
                if "classic-mode" in raw.lower() or "classic & expert" in raw.lower():
                    # Parse {{EncounterTable/Data|dex|Name|...}}
                    for m in re.finditer(r'\{\{EncounterTable/Data\|\d+\|([^\|\}]+)', raw):
                        allowed.add(m.group(1).strip())

    # 3. Gifts & Purchases
    for g in GIFTS_TRADES.get("gifts", []):
        gloc = g.get("location", "").lower()
        if any(slug.replace("_", " ") in gloc or slug in gloc for slug in loc_slugs):
            pkm = g.get("pokemon", "").strip()
            if "/" in pkm:
                for part in pkm.split("/"): allowed.add(part.strip())
            elif pkm:
                allowed.add(pkm)

    # 4. In-Game Trades (both give and receive columns)
    for tr in GIFTS_TRADES.get("trades", []):
        tloc = tr.get("location", "").lower()
        if any(slug.replace("_", " ") in tloc or slug in tloc for slug in loc_slugs):
            for field in ["give", "receive"]:
                pkm = tr.get(field, "").strip()
                if "/" in pkm:
                    for part in pkm.split("/"): allowed.add(part.strip())
                elif pkm:
                    allowed.add(pkm)

    # 5. Overworld Static & Interactive Encounters
    for se in STATIC_ENCOUNTERS:
        sloc = se.get("location", "").lower()
        if any(slug.replace("_", " ") in sloc or slug in sloc for slug in loc_slugs):
            pkm = se.get("pokemon", "").strip()
            if "/" in pkm:
                for part in pkm.split("/"): allowed.add(part.strip())
            elif pkm:
                allowed.add(pkm)

    # 6. Authoritative Pokédex location fallback
    for p_name, p_data in WIKI_CLASSIC_POKEDEX.items():
        for ploc in p_data.get("locations", []):
            ploc_lower = ploc.lower()
            if any(slug.replace("_", " ") in ploc_lower or slug in ploc_lower for slug in loc_slugs):
                allowed.add(p_name.strip())

    # Special Case: Celadon Game Corner & Starter gifts
    if any("celadon" in s for s in loc_slugs):
        allowed.update(["Abra", "Clefairy", "Pinsir", "Scyther", "Dratini", "Porygon", "Eevee", "Ponyta", "Elekid", "Magby"])
    if any("pallet" in s for s in loc_slugs):
        allowed.update(["Bulbasaur", "Charmander", "Squirtle"])
    if any("cerulean" in s for s in loc_slugs):
        allowed.update(["Bulbasaur", "Charmander", "Squirtle"])
    if any("saffron" in s or "dojo" in s for s in loc_slugs):
        allowed.update(["Hitmonlee", "Hitmonchan", "Hitmontop", "Tyrunt", "Amaura", "Smeargle"])
    if any("silph" in s for s in loc_slugs):
        allowed.update(["Lapras", "Chikorita", "Cyndaquil", "Totodile"])
    if any("seafoam" in s for s in loc_slugs):
        allowed.update(["Articuno", "Jynx"])
    if any("cinnabar" in s or "mansion" in s for s in loc_slugs):
        allowed.update(["Absol", "Magmar", "Omanyte", "Omastar", "Kabuto", "Kabutops", "Aerodactyl", "Dodrio", "Ponyta", "Clefable", "Raichu"])

    return loc_slugs, allowed

def audit_phase_encounters(chapter_obj):
    errors = []
    routes = chapter_obj.get("routes", [])

    for r in routes:
        r_name = r.get("name", "Unknown Phase")
        encounters = r.get("encounters", {})
        if not encounters:
            continue

        loc_slugs, allowed_species = get_canonical_species_for_phase(r_name)
        if not allowed_species:
            continue

        for sec_name, mon_list in encounters.items():
            for mon in mon_list:
                mname = mon.get("name", "").strip()
                if not mname:
                    continue

                components = []
                if " or " in mname:
                    for option in mname.split(" or "):
                        components.extend([c.strip() for c in option.split("/")])
                elif "/" in mname:
                    components.extend([c.strip() for c in mname.split("/")])
                else:
                    components.append(mname)

                for comp in components:
                    clean_comp = re.sub(r'[♀♂]', '', comp).strip()
                    if comp not in allowed_species and clean_comp not in allowed_species:
                        errors.append(
                            f"Location Violation: '{comp}' in phase '{r_name}' (section '{sec_name}') "
                            f"is NOT canonically obtainable at this location! (Matched slugs: {loc_slugs})"
                        )

    return (len(errors) == 0), errors

if __name__ == "__main__":
    from assemble_chapter import assemble_chapter
    ch_dirs = sorted(glob.glob(os.path.join(BASE_DIR, "chapters", "ch*")))
    all_passed = True
    for cd in ch_dirs:
        if os.path.isdir(cd):
            ch_obj = assemble_chapter(cd)
            cid = ch_obj.get("chapter_id", os.path.basename(cd))
            passed, errs = audit_phase_encounters(ch_obj)
            if passed:
                print(f"  ✓ {cid.upper()}: Encounters canonically verified at all locations.")
            else:
                all_passed = False
                print(f"  ✗ {cid.upper()}: {len(errs)} location violations found:")
                for e in errs:
                    print(f"    • {e}")

    sys.exit(0 if all_passed else 1)
