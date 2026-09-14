"""
scripts/obtainability.py - Authoritative Chronological Obtainability Checker
Enforces game ground truth on when Pokémon species, evolutionary families,
and evolution methods become legally obtainable in Pokémon Infinite Fusion (Classic Mode).
"""

import os
import sys
import json
import glob
import re
from typing import Dict, List, Set, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SPECS_DIR = os.path.join(BASE_DIR, "specs")

CHAPTER_SEQUENCE = ["ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08"]

def load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

EVOLUTION_FAMILIES = load_json(os.path.join(DATA_DIR, "mechanics", "evolution_families.json"))
EVOLUTION_REQS = load_json(os.path.join(DATA_DIR, "mechanics", "evolution_requirements.json"))
STATIC_ENCOUNTERS = load_json(os.path.join(DATA_DIR, "mechanics", "wiki_static_encounters.json"))
if not STATIC_ENCOUNTERS:
    STATIC_ENCOUNTERS = load_json(os.path.join(DATA_DIR, "items", "static_encounters.json"))
GIFTS_AND_TRADES = load_json(os.path.join(DATA_DIR, "mechanics", "wiki_gifts_and_trades.json"))

def route_to_slug(route_name: str) -> str:
    s = route_name.lower().replace('.', '').replace("'", "")
    s = re.sub(r'\(.*?\)', '', s).strip()
    return re.sub(r'\s+', '_', s)

ROUTE_FILES = glob.glob(os.path.join(DATA_DIR, "encounters", "kanto", "*.json"))

def get_species_family(species: str) -> str:
    clean = species.strip()
    if clean in EVOLUTION_FAMILIES:
        return EVOLUTION_FAMILIES[clean]
    for k, v in EVOLUTION_FAMILIES.items():
        if k.lower() == clean.lower():
            return v
    return clean

def get_obtainable_families_up_to(chapter_id: str) -> Set[str]:
    """
    Returns the set of all base evolutionary families obtainable up to and including chapter_id.
    Aggregates:
    - Guaranteed Starters (Bulbasaur, Charmander, Squirtle)
    - All expected_classic_spawns from specs <= chapter_id
    - All wild spawns from encounter files for routes_covered in specs <= chapter_id
    - Static encounters and gift Pokémon from locations accessible <= chapter_id
    """
    if chapter_id not in CHAPTER_SEQUENCE:
        return set(EVOLUTION_FAMILIES.values())
        
    target_idx = CHAPTER_SEQUENCE.index(chapter_id)
    active_chapters = CHAPTER_SEQUENCE[:target_idx + 1]
    
    cumulative_routes = []
    cumulative_spawns = set(["Bulbasaur", "Charmander", "Squirtle"])
    
    for ch in active_chapters:
        spec_file = os.path.join(SPECS_DIR, f"spec_{ch}.json")
        if not os.path.exists(spec_file):
            continue
        spec = load_json(spec_file)
        for r in spec.get("routes_covered", []):
            if r not in cumulative_routes:
                cumulative_routes.append(r)
        for sp in spec.get("expected_classic_spawns", []):
            cumulative_spawns.add(sp)
            
    # Pull wild encounters for cumulative routes
    for r_name in cumulative_routes:
        r_slug = route_to_slug(r_name)
        for rf in ROUTE_FILES:
            bname = os.path.basename(rf)
            if re.match(rf"^{r_slug}_id_\d+\.json$", bname) or bname == f"{r_slug}.json" or bname.startswith(f"{r_slug}_"):
                edata = load_json(rf)
                for sec, mlist in edata.get("sections", {}).items():
                    for m in mlist:
                        mname = m.get("name")
                        if mname:
                            cumulative_spawns.add(mname)
                            
    # Pull static encounters for cumulative routes
    if isinstance(STATIC_ENCOUNTERS, list):
        for se in STATIC_ENCOUNTERS:
            loc = se.get("location", "")
            pkm = se.get("pokemon", "")
            if any(r.lower() in loc.lower() for r in cumulative_routes):
                if "/" in pkm:
                    for part in pkm.split("/"):
                        cumulative_spawns.add(part.strip())
                elif pkm:
                    cumulative_spawns.add(pkm.strip())

    # Pull gifts and trades for cumulative routes
    if isinstance(GIFTS_AND_TRADES, dict):
        for g in GIFTS_AND_TRADES.get("gifts", []):
            loc = g.get("location", "")
            pkm = g.get("pokemon", "")
            if any(r.lower() in loc.lower() for r in cumulative_routes):
                if "/" in pkm:
                    for part in pkm.split("/"):
                        cumulative_spawns.add(part.strip())
                elif pkm:
                    cumulative_spawns.add(pkm.strip())
        for tr in GIFTS_AND_TRADES.get("trades", []):
            loc = tr.get("location", "")
            rec = tr.get("receive", "")
            if any(r.lower() in loc.lower() for r in cumulative_routes):
                if rec:
                    cumulative_spawns.add(rec.strip())

    obtainable_families: Set[str] = set()
    for sp in cumulative_spawns:
        fam = get_species_family(sp)
        obtainable_families.add(fam)
            
    return obtainable_families

def check_species_legality(species: str, chapter_id: str, level_cap: int) -> Tuple[bool, Optional[str]]:
    """
    Checks if a single species (or component) is legally obtainable and evolved
    by the specified chapter and level cap.
    """
    clean_sp = species.strip()
    if not clean_sp:
        return True, None
        
    # 1. Family Obtainability Check
    allowed_families = get_obtainable_families_up_to(chapter_id)
    fam = get_species_family(clean_sp)
    if fam not in allowed_families:
        return False, f"Evolutionary family '{fam}' of species '{clean_sp}' is NOT obtainable by {chapter_id}!"
        
    # 2. Evolution Level & Method Check
    reqs = EVOLUTION_REQS.get(clean_sp, [])
    if reqs:
        # The species is an evolved form. Check if at least ONE evolution path is legal.
        is_legal = False
        reasons = []
        
        ch_idx = CHAPTER_SEQUENCE.index(chapter_id) if chapter_id in CHAPTER_SEQUENCE else 99
        
        for r in reqs:
            method = r.get("method")
            param = r.get("parameter")
            
            if method == "Level":
                min_lvl = int(param)
                if min_lvl <= level_cap:
                    is_legal = True
                    break
                else:
                    reasons.append(f"requires Level {min_lvl} (Cap is {level_cap})")
                    
            elif method == "Item":
                item_name = str(param).upper()
                if item_name == "LINKINGCORD":
                    # Linking Cord is obtainable in Chapter 4+ (15 hotel quests / Celadon Dept Store)
                    if ch_idx >= CHAPTER_SEQUENCE.index("ch04"):
                        is_legal = True
                        break
                    else:
                        reasons.append("requires Linking Cord (unlocked in Chapter 4)")
                elif item_name in ("FIRESTONE", "WATERSTONE", "THUNDERSTONE", "LEAFSTONE"):
                    # Elemental stones obtainable in Celadon Dept Store (Chapter 4+)
                    if ch_idx >= CHAPTER_SEQUENCE.index("ch04"):
                        is_legal = True
                        break
                    else:
                        reasons.append(f"requires {item_name} from Celadon Dept Store (Chapter 4)")
                elif item_name == "MOONSTONE":
                    # Moon Stone obtainable in Mt. Moon (Chapter 2+)
                    if ch_idx >= CHAPTER_SEQUENCE.index("ch02"):
                        is_legal = True
                        break
                    else:
                        reasons.append("requires Moon Stone from Mt. Moon (Chapter 2)")
                elif item_name in ("SUNSTONE", "SHINYSTONE", "DUSKSTONE", "DAWNSTONE"):
                    if ch_idx >= CHAPTER_SEQUENCE.index("ch04"):
                        is_legal = True
                        break
                    else:
                        reasons.append(f"requires {item_name} (unlocked in Chapter 4+)")
                else:
                    # Other items (Metal Coat, Dragon Scale, etc. - late game)
                    if ch_idx >= CHAPTER_SEQUENCE.index("ch05"):
                        is_legal = True
                        break
                    else:
                        reasons.append(f"requires {item_name} (unlocked mid-late game)")
            else:
                # Other evolution conditions (e.g. Happiness replaced by level in PIF)
                is_legal = True
                break
                
        if not is_legal:
            err_details = "; ".join(reasons) if reasons else "no legal evolution path"
            return False, f"Species '{clean_sp}' cannot legally evolve by {chapter_id} (Cap {level_cap}): {err_details}"
            
    return True, None

def check_team_species_obtainability(team_data: dict, chapter_id: str, level_cap: int) -> List[str]:
    """
    Audits an entire team JSON (roster and flex bench) for chronological obtainability.
    Returns a list of error strings.
    """
    errors = []
    starter = team_data.get("starter", "Unknown")
    
    all_members = []
    for m in team_data.get("roster", []):
        all_members.append(("Roster", m.get("slot"), m.get("species", "")))
    for b in team_data.get("flex_bench", []):
        all_members.append(("Flex Bench", b.get("slot"), b.get("species", "")))
        
    for section, slot, full_spec in all_members:
        if not full_spec:
            continue
        comps = [c.strip() for c in full_spec.split("/") if c.strip()]
        for comp in comps:
            legal, err_msg = check_species_legality(comp, chapter_id, level_cap)
            if not legal:
                errors.append(
                    f"Team '{starter}' {section} Slot {slot} ({full_spec}): {err_msg}"
                )
                
    return errors

if __name__ == "__main__":
    ch = sys.argv[1] if len(sys.argv) > 1 else "ch02"
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    fams = get_obtainable_families_up_to(ch)
    print(f"Obtainable families up to {ch} ({len(fams)}):")
    print(", ".join(sorted(fams)))
    
    # Test Pinsir
    ok, reason = check_species_legality("Pinsir", ch, cap)
    print(f"\nPinsir check for {ch} (Cap {cap}): legal={ok}, reason={reason}")
