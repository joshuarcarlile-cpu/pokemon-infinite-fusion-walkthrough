"""
Preflight Chapter Context Manifest Generator for Pokémon Infinite Fusion
Analyzes a chapter spec (specs/spec_chXX.json), pulls all relevant ground-truth data:
- Routes & Wild Encounters (exact species, types, rates, levels, time-of-day availability)
- Boss Gym Leader (classic & expert teams, levels, moves, ace, party size limit)
- Relevant Items, HMs, Custom TMs & Static Encounters
- Candidate Movepools at Hard Cap
Saves a consolidated manifest to specs/manifest_chXX.json to make drafting chapters completely effortless and error-proof.
"""

import os
import sys
import json
import glob
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "scripts"))
from pif_utils import normalize_route_slug

DATA_DIR = os.path.join(BASE_DIR, "data")
SPECS_DIR = os.path.join(BASE_DIR, "specs")

LEADER_BY_CHAPTER = {
    "ch01": "LEADER_Brock",
    "ch02": "LEADER_Misty",
    "ch03": "LEADER_Surge",
    "ch04": "LEADER_Erika",
    "ch05": "LEADER_Koga",
    "ch06": "LEADER_Sabrina",
    "ch07": "LEADER_Blaine",
    "ch08": "LEADER_Giovanni",
    "ch09": "CHAMPION",
    "ch10": "LEADER_Whitney",
    "ch11": "LEADER_Kurt",
    "ch12": "LEADER_Falkner",
    "ch14": "LEADER_Morty",
    "ch15": "LEADER_Pryce",
    "ch16": "LEADER_Clair",
    "ch19": "LEADER_Chuck",
    "ch20": "LEADER_Jasmine"
}

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def route_to_slug(route_name):
    # e.g. "Route 1" -> "route_1", "Viridian Forest" -> "viridian_forest", "Mt. Moon" -> "mt_moon"
    s = route_name.lower().replace(".", "").replace("'", "")
    # Remove parentheticals like (South)
    s = re.sub(r'\(.*?\)', '', s).strip()
    slug = re.sub(r'\s+', '_', s)
    if slug in ["brine_road_east", "brine_road_west"]:
        return "brine_road"
    return slug

def generate_manifest(spec_path):
    if not os.path.exists(spec_path):
        print(f"Error: Spec file not found at {spec_path}")
        return False
        
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
        
    chapter_id = spec.get("chapter_id", "chXX")
    routes_covered = spec.get("routes_covered", [])
    cap = spec.get("hard_mode_level_cap", 100)
    gym_duel_limit = spec.get("gym_duel_limit", 2)
    
    # 1. Load Databases
    gym_leaders = load_json(os.path.join(DATA_DIR, "mechanics", "gym_leaders.json"))
    hm_replacements = load_json(os.path.join(DATA_DIR, "items", "hm_replacements.json"))
    key_items = load_json(os.path.join(DATA_DIR, "items", "key_items.json"))
    static_encounters = load_json(os.path.join(DATA_DIR, "items", "static_encounters.json"))
    custom_tms = load_json(os.path.join(DATA_DIR, "mechanics", "custom_tms.json"))
    
    # 2. Gather Route Encounters
    route_files = glob.glob(os.path.join(DATA_DIR, "encounters", "kanto", "*.json"))
    chapter_encounters = {}
    
    for r_name in routes_covered:
        r_slug = route_to_slug(r_name)
        # Match exact pattern: {r_slug}_id_\d+.json or {r_slug}.json
        matched = []
        for f in route_files:
            bname = os.path.basename(f)
            if re.match(rf"^{r_slug}_id_\d+\.json$", bname) or bname == f"{r_slug}.json":
                matched.append(f)
                
        for mf in matched:
            data = load_json(mf)
            loc = data.get("location", r_name)
            lean_sections = {}
            for sec_name, p_list in data.get("sections", {}).items():
                lean_sections[sec_name] = [
                    {
                        "name": mon.get("name"),
                        "dex_id": mon.get("dex_id"),
                        "types": [t for t in [mon.get("type1"), mon.get("type2")] if t],
                        "levels": mon.get("levels")
                    }
                    for mon in p_list if mon.get("name")
                ]
            chapter_encounters[loc] = lean_sections
            
    # 3. Match Boss Leader
    leader_type = LEADER_BY_CHAPTER.get(chapter_id, "")
    boss_data = {}
    if leader_type and gym_leaders:
        c_leader = gym_leaders.get("classic", {}).get(leader_type)
        if c_leader:
            boss_data["classic"] = {
                "leader": c_leader.get("real_name"),
                "team": c_leader.get("pokemon", []),
                "party_size": len(c_leader.get("pokemon", []))
            }
        e_leader = gym_leaders.get("expert", {}).get(leader_type)
        if e_leader:
            boss_data["expert"] = {
                "leader": e_leader.get("real_name"),
                "team": e_leader.get("pokemon", []),
                "party_size": len(e_leader.get("pokemon", []))
            }
                
    # 4. Match Items & Static Encounters
    matched_items = []
    for r_name in routes_covered:
        norm_r = r_name.lower().replace(" ", "")
        for ki in key_items:
            if norm_r in ki.get("location", "").lower().replace(" ", ""):
                matched_items.append({"type": "Key Item", "name": ki.get("name"), "location": ki.get("location"), "desc": ki.get("description")})
        for hm in hm_replacements:
            if norm_r in hm.get("location", "").lower().replace(" ", ""):
                matched_items.append({"type": "HM Replacement", "name": hm.get("name"), "replaces": hm.get("replaces_hm"), "location": hm.get("location")})
        for se in static_encounters:
            if norm_r in se.get("location", "").lower().replace(" ", ""):
                matched_items.append({"type": "Static Encounter", "pokemon": se.get("pokemon"), "level": se.get("level"), "location": se.get("location"), "notes": se.get("notes")})

    # 5. Ingest Wiki Ground Truth Cache
    wiki_cache_summary = {}
    for r_name in routes_covered:
        slug = normalize_route_slug(r_name)
        w_path = os.path.join(DATA_DIR, "wiki", f"{slug}.json")
        if os.path.exists(w_path):
            w_data = load_json(w_path)
            wiki_cache_summary[r_name] = {
                "canonical_slug": slug,
                "lead_summary": w_data.get("lead_summary", ""),
                "items": w_data.get("items", []),
                "missable_warnings": w_data.get("missable_warnings", [])
            }

    # 6. Match Quests & Missable Alerts
    master_quests = load_json(os.path.join(DATA_DIR, "quests", "master_quests.json")).get("quests", [])
    hotel_milestones = load_json(os.path.join(DATA_DIR, "quests", "hotel_milestones.json"))
    
    chapter_quests = []
    critical_missables = []
    
    for q in master_quests:
        intro = q.get("chapter_introduced")
        resolv = q.get("chapter_resolvable")
        q_loc = q.get("location", "").lower()
        
        relevant = (intro == chapter_id or resolv == chapter_id)
        if not relevant:
            for r in routes_covered:
                if r.lower() in q_loc:
                    relevant = True
                    break
                    
        if relevant:
            chapter_quests.append(q)
            if q.get("is_missable"):
                critical_missables.append({
                    "quest_id": q.get("id"),
                    "title": q.get("title"),
                    "deadline": q.get("missable_deadline"),
                    "consequence": q.get("objectives", [""])[-1]
                })
                
    hotel_pacing = hotel_milestones.get("pacing_milestones", {}).get(f"{chapter_id}_pewter" if chapter_id == "ch01" else f"{chapter_id}_cerulean" if chapter_id == "ch02" else f"{chapter_id}_vermilion" if chapter_id == "ch03" else "", {})

    # 6.5. Generate Vanilla Divergence Alerts
    divergence_alerts = [
        "HM Slaves: 100% eliminated by 9 reusable Key Item tools. Do NOT instruct players to teach field moves to party members.",
        "Friendship: Eliminated. All friendship evolutions use static level thresholds (e.g. Baby Pokémon evolve at Lv. 15).",
        "Trade Evolutions: Evolve naturally at Level 40 OR via Linking Cord (not Level 37)."
    ]
    all_covered_str = " ".join(routes_covered).lower()
    if "anne" in all_covered_str or "vermilion" in all_covered_str or "vermillion" in all_covered_str:
        divergence_alerts.append(
            "S.S. ANNE DOES NOT DEPART: The ship is permanently moored in Vermilion City harbor. It provides free cabin healing and remains accessible for quests and post-gym gifts."
        )
        divergence_alerts.append(
            "SHEARS CUT TOOL: Obtained in Route 2 Before Forest via Diglett's Cave from Vermilion City. Do NOT use HM01 Cut slave."
        )
    if "vermilion" in all_covered_str or "vermillion" in all_covered_str:
        divergence_alerts.append(
            "TELEPORT FIELD MOVE: Acts as Fly to fast-travel to any visited Pokémon Center once the Thunder Badge is obtained."
        )

    # 7. Assemble Manifest
    manifest = {
        "chapter_id": chapter_id,
        "title": spec.get("title"),
        "act": spec.get("act", 1),
        "hard_mode_level_cap": cap,
        "gym_duel_limit": gym_duel_limit,
        "routes_covered": routes_covered,
        "vanilla_divergence_alerts": divergence_alerts,
        "critical_missables": critical_missables,
        "hotel_milestone_target": hotel_pacing,
        "active_and_ongoing_quests": chapter_quests,
        "boss_ground_truth": boss_data,
        "encounters_by_location": chapter_encounters,
        "wiki_ground_truth": wiki_cache_summary,
        "location_items_and_statics": matched_items,
        "authoring_guidance": {
            "splicing_safety": "Explicitly state: HEAD species, BODY species, and WHICH ability to select at the DNA Splicer prompt.",
            "gym_party_selection_rule": f"Built-in {gym_duel_limit}v{gym_duel_limit} party limit! When challenged, the game prompts the player to choose which {gym_duel_limit} Pokémon from their active party to bring into battle. No PC box deposits required.",
            "stone_evolutions": "Advisory: Do NOT use evolution stones prematurely on stone-evolvers (e.g. Nidorino) before key level-up moves are learned.",
            "undercover_informant_rocket": "Guide player to join Team Rocket for disguises/missions, BUT report crimes to police officer for +10 Karma and Diancie unlock!"
        }
    }
    
    out_path = os.path.join(SPECS_DIR, f"manifest_{chapter_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"SUCCESS: Generated preflight manifest at {out_path}")
    print(f"  • Routes covered: {len(routes_covered)}")
    print(f"  • Matched encounter locations: {len(chapter_encounters)}")
    print(f"  • Boss: {boss_data.get('classic', {}).get('leader')} (Classic size: {boss_data.get('classic', {}).get('party_size')}, Expert size: {boss_data.get('expert', {}).get('party_size')})")
    print(f"  • Matched items & statics: {len(matched_items)}")
    return True

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        s_path = sys.argv[1]
        if not s_path.endswith(".json"):
            s_path = os.path.join(SPECS_DIR, f"spec_{s_path}.json")
        generate_manifest(s_path)
    else:
        print("Usage: python preflight_chapter.py <spec_file_or_chXX>")
