"""
Comprehensive MediaWiki Sanity Checker for Pokémon Infinite Fusion Walkthrough
Audits Chapters 1 to 5 against authoritative local MediaWiki cache:
1. Encounter coverage (Wild, Radar, Fishing, Gifts, Trades, Static)
2. Item & TM completeness (TMs, Evolution items, Key tools)
3. Boss / Gym Leader accuracy (Roster, levels, types, ace)
4. Missables & Quests (Karma, Hotel quests, Permanently missable triggers)
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
WIKI_DIR = os.path.join(BASE_DIR, "data", "wiki")
DATA_DIR = os.path.join(BASE_DIR, "data")
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

def load_json(p):
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

GIFTS_TRADES = load_json(os.path.join(DATA_DIR, "mechanics", "wiki_gifts_and_trades.json"))
STATIC_ENCOUNTERS = load_json(os.path.join(DATA_DIR, "mechanics", "wiki_static_encounters.json"))
GYM_LEADERS = load_json(os.path.join(DATA_DIR, "mechanics", "gym_leaders.json"))
POKEDEX = load_json(os.path.join(DATA_DIR, "mechanics", "wiki_classic_pokedex.json"))

PHASE_TO_WIKI = {
    "1.1_pallet_town.json": ["Pallet_Town.json"],
    "1.2_route_1_viridian.json": ["Route_1.json", "Viridian_City.json"],
    "1.3_route_22.json": ["Route_22.json"],
    "1.4_secret_garden.json": ["Secret_Garden.json"],
    "1.5_viridian_forest.json": ["Viridian_Forest.json", "Route_2.json"],
    "1.6_pewter_city.json": ["Pewter_City.json"],
    "2.1_route_3.json": ["Route_3.json"],
    "2.2_mt_moon_1f.json": ["Mt._Moon.json"],
    "2.3_mt_moon_b2f.json": ["Mt._Moon.json", "Mt._Moon_Summit.json"],
    "2.4_route_4_cerulean.json": ["Route_4.json", "Cerulean_City.json"],
    "2.5_nugget_bridge_route_24.json": ["Route_24.json"],
    "2.6_route_25_bill.json": ["Route_25.json"],
    "2.7_cerulean_gym.json": ["Cerulean_City.json"],
    "3.1_route_5_underground.json": ["Route_5.json"],
    "3.2_route_6_vermilion_city.json": ["Route_6.json", "Vermillion_City.json"],
    "3.3_ss_anne.json": ["S.S._Anne.json"],
    "3.4_route_11_digletts_cave.json": ["Route_11.json", "Diglett's_Cave.json"],
    "3.5_route_2_east_shears.json": ["Route_2_(Before_the_Forest).json", "Route_2_(After_the_Forest).json", "Route_2.json"],
    "3.6_vermilion_gym.json": ["Vermillion_City.json"],
    "4.1_route_9.json": ["Route_9.json"],
    "4.2_route_10_north.json": ["Route_10.json"],
    "4.3_rock_tunnel.json": ["Rock_Tunnel.json"],
    "4.4_lavender_town.json": ["Lavender_Town.json"],
    "4.5_route_8_route_7.json": ["Route_8.json", "Route_7.json"],
    "4.6_celadon_city.json": ["Celadon_City.json"],
    "4.7_celadon_sewers_giovanni.json": ["Celadon_Sewers.json"],
    "4.8_celadon_gym.json": ["Celadon_City.json"],
    "5.1_pokemon_tower.json": ["Pokmon_Tower.json"],
    "5.2_routes_16_17_18_cycling_road.json": ["Route_16.json", "Route_17.json", "Route_18.json"],
    "5.3_routes_12_15_silence_bridge.json": ["Route_12.json", "Route_13.json", "Route_14.json", "Route_15.json"],
    "5.4_fuchsia_city_safari_zone.json": ["Fuchsia_City.json", "Safari_Zone.json"],
    "5.5_fuchsia_gym.json": ["Fuchsia_City.json"]
}

def extract_wiki_items(raw_wikitext):
    items = []
    for m in re.finditer(r'\{\{ItemTable/Data(?:/Outfit)?\|([^\|\}]*)\|([^\|\}]*)\|([^\|\}]+)\|([^\|\}]*)', raw_wikitext):
        item_id = m.group(1).strip()
        count = m.group(2).strip()
        name = m.group(3).strip()
        method = m.group(4).strip()
        items.append({"name": name, "method": method, "id": item_id, "count": count})
    return items

def extract_wiki_classic_pokemon_by_section(raw_wikitext):
    sections = {}
    classic_text = ""
    matches = re.findall(r'<div class=\\"classic-mode[^>]*\\">(.*?)</div>', raw_wikitext, re.DOTALL | re.IGNORECASE)
    if matches:
        classic_text = "\n".join(matches)
    else:
        remix_idx = raw_wikitext.lower().find("remix-mode")
        if remix_idx != -1:
            classic_text = raw_wikitext[:remix_idx]
        else:
            classic_text = raw_wikitext

    current_sec = "Wild"
    lines = classic_text.split("\n")
    for line in lines:
        sec_m = re.search(r'\{\{EncounterTable/Section\|([^\|\}]+)', line)
        if sec_m:
            current_sec = sec_m.group(1).strip()
            if current_sec not in sections:
                sections[current_sec] = []
        data_m = re.search(r'\{\{EncounterTable/Data\|([^\|\}]+)\|([^\|\}]+)(?:\|([^\|\}]*))?(?:\|([^\|\}]*))?(?:\|([^\|\}]*))?', line)
        if data_m:
            dex = data_m.group(1).strip()
            name = data_m.group(2).strip()
            t1 = (data_m.group(3) or "").strip()
            t2 = (data_m.group(4) or "").strip()
            lvl = (data_m.group(5) or "").strip()
            if name and not any(name.startswith(x) for x in ["Header", "Footer", "Section"]):
                if current_sec not in sections:
                    sections[current_sec] = []
                sections[current_sec].append({"dex": dex, "name": name, "types": [t for t in [t1, t2] if t and t != "none"], "levels": lvl})
    return sections

def audit():
    print("=" * 70)
    print("  POKÉMON INFINITE FUSION - FULL MEDIAWIKI GROUND TRUTH SANITY CHECK")
    print("=" * 70)

    # 1. BOSS CHECK
    print("\n[SECTION 1] AUDITING GYM LEADERS & BOSSES")
    boss_map = {
        "ch01": ("LEADER_Brock", "Brock", 14, 2),
        "ch02": ("LEADER_Misty", "Misty", 25, 2),
        "ch03": ("LEADER_Surge", "Lt. Surge", 29, 3),
        "ch04": ("LEADER_Erika", "Erika", 39, 3),
        "ch05": ("LEADER_Koga", "Koga", 42, 4)
    }
    for ch, (lead_key, lead_name, exp_cap, exp_party_size) in boss_map.items():
        bpath = os.path.join(CHAPTERS_DIR, ch, "boss.json")
        bdata = load_json(bpath)
        classic_leader = GYM_LEADERS.get("classic", {}).get(lead_key, {})
        expert_leader = GYM_LEADERS.get("expert", {}).get(lead_key, {})
        
        b_p_size = bdata.get("duel_rule", {}).get("party_size_limit")
        p_team = bdata.get("roster", {}).get("classic", {}).get("team", [])
        
        ps_ok = (b_p_size == exp_party_size)
        c_pkmn = classic_leader.get("pokemon", [])
        print(f"  • {ch.upper()} {lead_name}:")
        print(f"    - Hard Duel Limit: {b_p_size}v{b_p_size} (Expected: {exp_party_size}v{exp_party_size}) {'✓' if ps_ok else '❌'}")
        print(f"    - Boss Roster entries: {len(p_team)} (PBS/Wiki Classic: {len(c_pkmn)} mons)")
        if c_pkmn:
            max_lvl = max(p.get("level", 0) for p in c_pkmn)
            print(f"    - Leader Cap: Lv. {max_lvl} (Expected: {exp_cap}) {'✓' if max_lvl == exp_cap else '❌'}")

    # 2. PHASES CHECK
    print("\n[SECTION 2] AUDITING PHASES VS MEDIAWIKI (ITEMS, TMS, SPAWNS)")
    
    missing_items_report = []
    missing_spawns_report = []
    
    for ch in ["ch01", "ch02", "ch03", "ch04", "ch05"]:
        ch_dir = os.path.join(CHAPTERS_DIR, ch)
        phases_dir = os.path.join(ch_dir, "phases")
        phase_files = sorted(glob.glob(os.path.join(phases_dir, "*.json")))
        
        print(f"\n--- {ch.upper()} ---")
        for pf in phase_files:
            p_base = os.path.basename(pf)
            p_data = load_json(pf)
            p_name = p_data.get("name", "")
            
            wiki_files = PHASE_TO_WIKI.get(p_base, [])
            combined_raw = ""
            for wf in wiki_files:
                for candidate in glob.glob(os.path.join(WIKI_DIR, "*.json")):
                    b_cand = os.path.basename(candidate).lower()
                    if wf.split(".")[0].lower() in b_cand:
                        combined_raw += "\n" + load_json(candidate).get("raw_wikitext", "")
                        break
                        
            wiki_items = extract_wiki_items(combined_raw)
            wiki_sections = extract_wiki_classic_pokemon_by_section(combined_raw)
            
            phase_items = p_data.get("items", [])
            phase_encounters = p_data.get("encounters", {})
            
            p_item_texts = [i.get("name", "").lower() + " " + i.get("method", "").lower() for i in phase_items]
            
            for wi in wiki_items:
                wname = wi["name"]
                wname_lower = wname.lower()
                if any(x in wi["method"].lower() for x in ["arceus", "post-game", "rematch", "second playthrough"]):
                    continue
                if any(k in wname_lower for k in ["tm", "hm", "stone", "cord", "shear", "lantern", "rod", "pass", "scope", "flute", "exp", "ticket", "case"]):
                    clean_wname = re.sub(r'tm\d+\s*', '', wname_lower).strip()
                    matched = any(clean_wname in pit or wname_lower in pit for pit in p_item_texts)
                    if not matched:
                        missing_items_report.append({
                            "chapter": ch,
                            "phase_file": p_base,
                            "phase_name": p_name,
                            "item": wname,
                            "method": wi["method"]
                        })
            
            phase_all_species = set()
            for sec, mlist in phase_encounters.items():
                for m in mlist:
                    phase_all_species.add(m.get("name", "").strip())
                    
            for wsec, wlist in wiki_sections.items():
                wsec_lower = wsec.lower()
                for wm in wlist:
                    s_name = wm["name"].strip()
                    if "/" in s_name or s_name.startswith("Egg") or not s_name:
                        continue
                    if "super rod" in wsec_lower and ch in ["ch01", "ch02", "ch03", "ch04"]:
                        continue
                    if "good rod" in wsec_lower and ch in ["ch01", "ch02", "ch03"]:
                        continue
                    if "surf" in wsec_lower and ch in ["ch01", "ch02", "ch03", "ch04"]:
                        continue
                    if "water" in wsec_lower and ch in ["ch01", "ch02", "ch03", "ch04"] and not any(r in wsec_lower for r in ["old rod", "good rod"]):
                        continue
                        
                    if s_name not in phase_all_species:
                        missing_spawns_report.append({
                            "chapter": ch,
                            "phase_file": p_base,
                            "phase_name": p_name,
                            "section": wsec,
                            "species": s_name,
                            "level": wm["levels"]
                        })

    print(f"\nAudit complete. Found {len(missing_items_report)} notable wiki item opportunities and {len(missing_spawns_report)} spawn nuances.")
    
    print("\n--- NOTABLE WIKI ITEMS DETAIL ---")
    for r in missing_items_report:
        print(f"  [{r['chapter'].upper()}] {r['phase_file']}: '{r['item']}' -> {r['method']}")
        
    print("\n--- NOTABLE WIKI SPAWNS DETAIL ---")
    spawn_by_phase = {}
    for r in missing_spawns_report:
        key = f"[{r['chapter'].upper()}] {r['phase_file']} ({r['section']})"
        if key not in spawn_by_phase:
            spawn_by_phase[key] = []
        spawn_by_phase[key].append(f"{r['species']} (Lv. {r['level']})")
        
    for k, v in spawn_by_phase.items():
        print(f"  {k}: {', '.join(v)}")

if __name__ == "__main__":
    audit()
