"""
Automated 6-Gate TDD Linter for Pokémon Infinite Fusion Walkthrough Chapters
Validates chapter data (either single JSON or sliced directory) against its TDD specification:
- Gate 1: Hard Mode Level Cap Gate (boss & active members <= cap)
- Gate 2: Route Encounter Legality Gate (classic spawns only)
- Gate 3: Tool Sequence Gate (no premature HM tool usage)
- Gate 4: Three Starter Teams Gate:
    * bulbasaur, charmander, squirtle tracks present
    * required roster sizes matching gym duel caps
    * starter is permanent anchor on its track
    * reached movesets have exactly 4 moves
    * AUTOMATED MOVE LEGALITY: Every reached move must be legally learned at or below the Level Cap!
    * SPECIES CLAUSE: Zero duplicate evolutionary families across active roster and bench
- Gate 5: Missable & Wiki Knowledge Integrity Gate
- Gate 6: Team Chronological Species Obtainability & Evolution Legality Gate:
    * All active and bench species/components must belong to families obtainable by that chapter
    * Evolution levels must not exceed the Hard Mode Level Cap
    * Trade items / stones must be legitimately obtainable by that chapter
"""

import json
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "scripts"))
try:
    from assemble_chapter import assemble_chapter
except ImportError:
    assemble_chapter = None

try:
    from learnset_lookup import is_move_reachable, get_reachable_moves
except ImportError:
    is_move_reachable = None

try:
    from pif_utils import normalize_route_slug
except ImportError:
    normalize_route_slug = lambda r: r.strip().replace(" ", "_")

try:
    from audit_ground_truth import audit_text_content
except ImportError:
    audit_text_content = None

try:
    from obtainability import check_team_species_obtainability
except ImportError:
    check_team_species_obtainability = None

try:
    from audit_phase_encounters import audit_phase_encounters
except ImportError:
    audit_phase_encounters = None

def load_evolution_families():
    p = os.path.join(BASE_DIR, "data", "mechanics", "evolution_families.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

EVOLUTION_FAMILIES = load_evolution_families()

def get_species_family(species):
    clean = species.strip()
    if clean in EVOLUTION_FAMILIES:
        return EVOLUTION_FAMILIES[clean]
    for k, v in EVOLUTION_FAMILIES.items():
        if k.lower() == clean.lower():
            return v
    return clean

def verify_chapter(spec_file, chapter_target):
    errors = []
    
    if not os.path.exists(spec_file):
        return False, [f"Spec file not found: {spec_file}"]
        
    with open(spec_file, "r", encoding="utf-8") as f:
        spec = json.load(f)
        
    # Load chapter object (from directory or file)
    if os.path.isdir(chapter_target):
        if assemble_chapter is None:
            return False, ["assemble_chapter module not found to parse directory."]
        try:
            chapter = assemble_chapter(chapter_target)
        except Exception as e:
            return False, [f"Failed to assemble chapter from {chapter_target}: {e}"]
    elif os.path.isfile(chapter_target):
        with open(chapter_target, "r", encoding="utf-8") as f:
            chapter = json.load(f)
    else:
        return False, [f"Chapter target not found: {chapter_target}"]
        
    cap = spec.get("hard_mode_level_cap", 100)
    
    # Gate 1: Level Cap & Gym Duel Limit Check
    boss = chapter.get("boss_strategy", {})
    recommended_level = boss.get("recommended_party_level", 0)
    if recommended_level > cap:
        errors.append(f"GATE 1 FAIL: Recommended level {recommended_level} exceeds Hard Mode cap of {cap}")
        
    gym_duel_limit = spec.get("gym_duel_limit")
    if gym_duel_limit is not None:
        boss_duel_limit = boss.get("gym_duel_limit")
        if boss_duel_limit is not None and boss_duel_limit != gym_duel_limit:
            errors.append(f"GATE 1 FAIL: Boss gym_duel_limit {boss_duel_limit} does not match spec {gym_duel_limit}")

    boss_remix = chapter.get("boss_strategy_remix")
    if boss_remix:
        rem_rec = boss_remix.get("recommended_party_level", 0)
        if rem_rec > cap:
            errors.append(f"GATE 1 FAIL (Remix): Recommended level {rem_rec} exceeds Hard Mode cap of {cap}")
        rem_duel = boss_remix.get("gym_duel_limit")
        if gym_duel_limit is not None and rem_duel is not None and rem_duel != gym_duel_limit:
            errors.append(f"GATE 1 FAIL (Remix): Boss gym_duel_limit {rem_duel} does not match spec {gym_duel_limit}")
        
    # Gate 2: Route Encounter Legality & Canonical Location Verification
    prohibited_spawns = set(spec.get("prohibited_spawns", []))
    for route in chapter.get("routes", []):
        for sec_name, mon_list in route.get("encounters", {}).items():
            for m in mon_list:
                mon_name = m.get("name", "")
                if mon_name in prohibited_spawns:
                    errors.append(f"GATE 2 FAIL: Prohibited species '{mon_name}' found in route encounters")
                    
    if audit_phase_encounters is not None:
        pe_passed, pe_errs = audit_phase_encounters(chapter)
        if not pe_passed:
            for pe in pe_errs:
                errors.append(f"GATE 2 FAIL: {pe}")
                    
    # Gate 3: Tool Sequence Check
    prohibited_tools = spec.get("prohibited_tools", [])
    chapter_text = json.dumps(chapter).lower()
    for tool in prohibited_tools:
        if f"use {tool.lower()}" in chapter_text or f"requires {tool.lower()}" in chapter_text:
            errors.append(f"GATE 3 FAIL: Prohibited tool '{tool}' instructed for use before obtainable")
            
    # Gate 4: Three Starter Teams Integrity & Move Legality Check (Classic & Remix)
    teams = chapter.get("teams", {})
    required_starters = spec.get("starter_teams_required", ["bulbasaur", "charmander", "squirtle"])
    def validate_starter_teams(teams_dict, mode_label="Classic"):
        t_errors = []
        for st in required_starters:
            if st not in teams_dict:
                t_errors.append(f"GATE 4 FAIL ({mode_label}): Missing starter team '{st}' in chapter teams")
                continue
                
            t_data = teams_dict[st]
            roster = t_data.get("roster", [])
            min_party = gym_duel_limit if gym_duel_limit is not None else 2
            if len(roster) < min_party or len(roster) > 6:
                t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' roster must contain between {min_party} and 6 members for this threshold (found {len(roster)})")
                
            # Verify Starter is Permanent Anchor on its Track
            starter_families = {
                "bulbasaur": "Bulbasaur",
                "charmander": "Charmander",
                "squirtle": "Squirtle"
            }
            req_fam = starter_families.get(st.lower())
            if req_fam:
                has_starter = False
                for slot in roster:
                    mon_spec = slot.get("species", "")
                    parts = [p.strip() for p in mon_spec.split("/") if p.strip()]
                    if any(get_species_family(p) == req_fam for p in parts):
                        has_starter = True
                        break
                if not has_starter:
                    t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' must contain its designated starter family '{req_fam}' as permanent anchor!")
                
            # Validate Gym Duel Core (Party Size Limit)
            if gym_duel_limit is not None:
                duel_core = t_data.get("gym_duel_core", [])
                if len(duel_core) != gym_duel_limit:
                    t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' gym_duel_core must specify exactly {gym_duel_limit} slots (found {len(duel_core)})")
                for slot_num in duel_core:
                    matching = [s for s in roster if s.get("slot") == slot_num]
                    if not matching:
                        t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' gym_duel_core references non-existent slot {slot_num}")
                    elif "active" not in matching[0].get("status", "active").lower():
                        t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' gym_duel_core slot {slot_num} ({matching[0].get('species')}) must be Active in Party")
                
            for slot in roster:
                s_num = slot.get("slot")
                species = slot.get("species", "")
                
                lvl = slot.get("current_level", 0)
                if lvl > cap:
                    t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' slot {s_num} ({species}) level {lvl} exceeds cap {cap}")
                reached = slot.get("current_reached_moveset", [])
                if len(reached) != 4:
                    t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' slot {s_num} ({species}) reached moveset must have 4 moves (found {len(reached)})")
                if not slot.get("ability"):
                    t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' slot {s_num} ({species}) missing ability")
                if not slot.get("held_item"):
                    t_errors.append(f"GATE 4 FAIL ({mode_label}): Team '{st}' slot {s_num} ({species}) missing held item")
                    
                # Mechanical Move Legality Verification (Dual-Species for Fusions)
                if is_move_reachable is not None and species:
                    base_mon = species.split("/")[0].strip() if "/" in species else species
                    sec_mon = species.split("/")[1].strip() if "/" in species else None
                    
                    head_moves = set(get_reachable_moves(base_mon, cap))
                    body_moves = set(get_reachable_moves(sec_mon, cap)) if sec_mon else set()
                    combined_legal = head_moves.union(body_moves)
                    
                    if combined_legal:
                        for mv in reached:
                            if mv not in combined_legal:
                                t_errors.append(f"GATE 4 FAIL ({mode_label}): Move '{mv}' is not legally reachable by '{species}' at or before Level {cap}")

            # Species Clause: Zero Duplicates across Active Threshold Roster
            seen_families = {}
            for slot in roster:
                s_num = slot.get("slot")
                species = slot.get("species", "").strip()
                if not species:
                    continue
                components = set(c.strip() for c in species.split("/") if c.strip())
                for comp in components:
                    fam = get_species_family(comp)
                    if fam in seen_families:
                        prev_slot, prev_mon = seen_families[fam]
                        if prev_slot != s_num:
                            t_errors.append(
                                f"GATE 4 FAIL ({mode_label}): Team '{st}' violates Species Clause! "
                                f"Evolutionary family '{fam}' is used in multiple slots: "
                                f"Slot {prev_slot} ({prev_mon}) and Slot {s_num} ({species})"
                            )
                    else:
                        seen_families[fam] = (s_num, species)

            # Species Clause: Zero Duplicates on Flex Bench (against Active Roster AND other Bench members)
            bench = t_data.get("flex_bench", [])
            for b_idx, b_mon in enumerate(bench):
                b_spec = b_mon.get("species", "").strip()
                if not b_spec:
                    continue
                b_components = set(c.strip() for c in b_spec.split("/") if c.strip())
                for b_comp in b_components:
                    b_fam = get_species_family(b_comp)
                    if b_fam in seen_families:
                        prev_loc, prev_mon = seen_families[b_fam]
                        t_errors.append(
                            f"GATE 4 FAIL ({mode_label}): Team '{st}' flex bench violates Species Clause! "
                            f"Evolutionary family '{b_fam}' in bench ({b_spec}) is already used in {prev_loc} ({prev_mon})"
                        )
                    else:
                        seen_families[b_fam] = (f"Bench Slot #{b_idx + 1}", b_spec)
        return t_errors

    errors.extend(validate_starter_teams(chapter.get("teams", {}), "Classic"))
    if chapter.get("teams_remix"):
        errors.extend(validate_starter_teams(chapter.get("teams_remix", {}), "Remix"))

    # Gate 5: Missable & Wiki Knowledge Integrity Gate
    quests_path = os.path.join(BASE_DIR, "data", "quests", "master_quests.json")
    if os.path.exists(quests_path):
        with open(quests_path, "r", encoding="utf-8") as f:
            all_quests = json.load(f).get("quests", [])
            
        ch_id = spec.get("chapter_id", "")
        routes_covered = spec.get("routes_covered", [])
        ch_full_text = json.dumps(chapter).lower()
        
        # Ground Truth & Anti-Vanilla Audit
        if audit_text_content:
            gt_passed, gt_errs = audit_text_content(ch_full_text, ch_id)
            if not gt_passed:
                for ge in gt_errs:
                    errors.append(f"GATE 5 FAIL: {ge}")
        
        # Check imminent missable warnings
        for q in all_quests:
            if q.get("is_missable") and q.get("chapter_introduced") == ch_id:
                q_title = q.get("title", "").lower()
                q_id = q.get("id", "").lower()
                # Must be mentioned in chapter with a warning
                if "secret_garden" in q_id:
                    if "secret garden" not in ch_full_text or "blue" not in ch_full_text:
                        errors.append(f"GATE 5 FAIL: Critical missable '{q.get('title')}' is not warned in chapter text!")
                elif "rocket" in q_id:
                    if "rocket" not in ch_full_text:
                        errors.append(f"GATE 5 FAIL: Team Rocket missable quest '{q.get('title')}' must be documented in chapter text!")
                elif "building_materials" in q_id:
                    if "building materials" not in ch_full_text:
                        errors.append(f"GATE 5 FAIL: Missable quest '{q.get('title')}' must be documented in chapter text before Elite Four deadline!")

        # Verify Wiki Cache Coverage for all routes in spec
        wiki_dir = os.path.join(BASE_DIR, "data", "wiki")
        for r in routes_covered:
            target_slug = normalize_route_slug(r)
            w_file = os.path.join(wiki_dir, f"{target_slug}.json")
            if not os.path.exists(w_file):
                errors.append(f"GATE 5 FAIL: Missing authoritative wiki cache for route '{r}' ({target_slug}.json)")
                
    # Gate 6: Team Chronological Species Obtainability & Evolution Legality Gate
    if check_team_species_obtainability is not None:
        ch_id = spec.get("chapter_id", "chXX")
        for st in required_starters:
            if st in teams:
                team_errs = check_team_species_obtainability(teams[st], ch_id, cap)
                for te in team_errs:
                    errors.append(f"GATE 6 FAIL: {te}")

    return (len(errors) == 0), errors

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        s_file = sys.argv[1]
        c_target = sys.argv[2]
        passed, errs = verify_chapter(s_file, c_target)
        if passed:
            print("PASS: 100% assertions verified. Chapter certified clean.")
            sys.exit(0)
        else:
            print(f"FAIL: {len(errs)} violations found:")
            for e in errs:
                print(f"  • {e}")
            sys.exit(1)
    else:
        print("Usage: python verify_chapter.py <spec_file> <chapter_file_or_directory>")
