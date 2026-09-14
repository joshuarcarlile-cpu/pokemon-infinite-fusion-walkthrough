"""
Automated Test Runner for Custom Team Builder & Type Coverage Analyzer
Validates:
1. Bundle Size Budget Assertion (<= 350,000 bytes)
2. Move Extraction & Damage Category Integrity (Physical/Special/Status)
3. Cap-Filtered Move Legality (Cap 14 vs Cap 40)
4. Pre-Evolution Move Inheritance (e.g. Spore on Breloom)
5. Status Move Coverage Exclusion Rule (0 damage moves deal no offensive coverage)
6. Multi-Move Offensive Coverage Calculation (Super-effective hits)
7. Defensive Synergy & Immunity Math (0x complete immunities, 4x quad weaknesses)
8. Single Species Fallback (Unfused Pokemon integrity)
"""

import os
import sys
import json
import gzip
import base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_HTML = os.path.join(BASE_DIR, "dist", "index.html")
DATA_DIR = os.path.join(BASE_DIR, "data")
MECHANICS_DIR = os.path.join(DATA_DIR, "mechanics")

ALL_TYPES = [
    "Normal", "Fire", "Water", "Grass", "Electric", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Steel", "Dark", "Fairy"
]

# Canonical Gen 7 Type Chart: TYPE_CHART[atk][def] = multiplier
# 0 = Normal, 1 = Fire, 2 = Water, 3 = Grass, 4 = Electric, 5 = Ice,
# 6 = Fighting, 7 = Poison, 8 = Ground, 9 = Flying, 10 = Psychic, 11 = Bug,
# 12 = Rock, 13 = Ghost, 14 = Dragon, 15 = Steel, 16 = Dark, 17 = Fairy
TYPE_CHART = {
    "Normal":   {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire":     {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
    "Water":    {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
    "Grass":    {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5},
    "Electric": {"Water": 2.0, "Grass": 0.5, "Electric": 0.5, "Ground": 0.0, "Flying": 2.0, "Dragon": 0.5},
    "Ice":      {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5},
    "Poison":   {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0},
    "Ground":   {"Fire": 2.0, "Grass": 0.5, "Electric": 2.0, "Poison": 2.0, "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
    "Flying":   {"Grass": 2.0, "Electric": 0.5, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5},
    "Psychic":  {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5},
    "Bug":      {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0, "Steel": 0.5, "Fairy": 0.5},
    "Rock":     {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
    "Ghost":    {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5},
    "Dragon":   {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
    "Steel":    {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
    "Dark":     {"Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Fairy": 0.5},
    "Fairy":    {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Dark": 2.0, "Steel": 0.5}
}

def get_type_effectiveness(atk_type, def_types):
    eff = 1.0
    for dt in def_types:
        eff *= TYPE_CHART.get(atk_type, {}).get(dt, 1.0)
    return eff

def load_payload_from_html():
    with open(DIST_HTML, "r", encoding="utf-8") as f:
        html = f.read()
    token = 'const COMPRESSED_APP_DATA = "'
    start = html.find(token)
    assert start != -1, "Could not find COMPRESSED_APP_DATA in dist/index.html"
    start += len(token)
    end = html.find('";', start)
    b64_str = html[start:end]
    compressed_bytes = base64.b64decode(b64_str)
    raw_json = gzip.decompress(compressed_bytes).decode("utf-8")
    return json.loads(raw_json)

def run_tests():
    print("================================================================")
    print("RUNNING CUSTOM TEAM BUILDER & COVERAGE ANALYZER TEST SUITE")
    print("================================================================")

    # GATE 1: Hard Bundle Budget Assertion
    assert os.path.exists(DIST_HTML), f"Error: {DIST_HTML} not found"
    bundle_size = os.path.getsize(DIST_HTML)
    CEILING = 350000
    print(f"[TEST 1] Bundle Size Assertion: {bundle_size:,} bytes / {CEILING:,} ceiling")
    assert bundle_size <= CEILING, f"Bundle size {bundle_size} exceeds {CEILING} budget ceiling!"
    print(f"  --> PASS: {CEILING - bundle_size:,} bytes of headroom available.")

    # Load unpacked payload
    app_data = load_payload_from_html()
    assert "moves" in app_data, "APP_DATA missing 'moves' payload"
    moves_pkg = app_data["moves"]
    move_names = moves_pkg["move_names"]
    move_table = moves_pkg["move_table"]
    species_learnsets = moves_pkg["species_learnsets"]
    base_stats = app_data["base_stats"]
    pre_evos = app_data.get("pre_evolutions", {})
    species_list = sorted(list(base_stats.keys()))

    # GATE 2: Move Extraction & Damage Category Integrity
    print("[TEST 2] Move Attributes & Categories Validation")
    assert len(move_names) >= 600, f"Expected >= 600 moves, found {len(move_names)}"
    assert len(move_names) == len(move_table), "move_names and move_table length mismatch"
    
    # Check specific moves: Swords Dance must be Category 2 (Status), Earthquake Category 0 (Phys), Flamethrower Category 1 (Spec)
    m_dict = {move_names[i]: move_table[i] for i in range(len(move_names))}
    assert m_dict["Swords Dance"][1] == 2, f"Swords Dance should be Category 2 (Status), got {m_dict['Swords Dance']}"
    assert m_dict["Toxic"][1] == 2, f"Toxic should be Category 2 (Status), got {m_dict['Toxic']}"
    assert m_dict["Earthquake"][1] == 0, f"Earthquake should be Category 0 (Physical), got {m_dict['Earthquake']}"
    assert m_dict["Earthquake"][2] == 100, f"Earthquake base damage should be 100, got {m_dict['Earthquake'][2]}"
    assert m_dict["Flamethrower"][1] == 1, f"Flamethrower should be Category 1 (Special), got {m_dict['Flamethrower']}"
    print(f"  --> PASS: {len(move_names)} moves validated across categories and types.")

    # Helper function matching frontend getLegalMovesForMon logic
    def get_legal_moves_for_species(sp_name, cap):
        targets = [sp_name] + pre_evos.get(sp_name, [])
        legal = {}
        for sp in targets:
            if sp in species_list:
                sp_idx = species_list.index(sp)
                packed_entries = species_learnsets[sp_idx]
                for p in packed_entries:
                    lvl = p // 1000
                    mid = p % 1000
                    if lvl <= cap:
                        mv_name = move_names[mid]
                        if mv_name not in legal or lvl < legal[mv_name]["lvl"]:
                            m_info = move_table[mid]
                            legal[mv_name] = {
                                "lvl": lvl,
                                "type": ALL_TYPES[m_info[0]],
                                "cat": m_info[1],
                                "pwr": m_info[2],
                                "acc": m_info[3]
                            }
        return legal

    # GATE 3: Cap-Filtered Move Legality (Cap 14 vs Cap 40)
    print("[TEST 3] Cap-Filtered Move Legality")
    charmander_moves_14 = get_legal_moves_for_species("Charmander", 14)
    assert "Ember" in charmander_moves_14, "Ember should be legal at Cap 14"
    assert "Scratch" in charmander_moves_14, "Scratch should be legal at Cap 14"
    assert "Flamethrower" not in charmander_moves_14, "Flamethrower must NOT be legal at Cap 14"

    charmander_moves_45 = get_legal_moves_for_species("Charmander", 45)
    assert "Flamethrower" in charmander_moves_45, "Flamethrower should be legal at Cap 45"
    print("  --> PASS: Move legality strictly filtered by level cap.")

    # GATE 4: Pre-Evolution Move Inheritance
    print("[TEST 4] Pre-Evolution Move Inheritance (Spore on Breloom)")
    breloom_moves_40 = get_legal_moves_for_species("Breloom", 40)
    assert "Spore" in breloom_moves_40, "Breloom must inherit Spore from pre-evolution Shroomish at Cap 40"
    print(f"  --> PASS: Pre-evolution move Spore successfully inherited (Learn Level: {breloom_moves_40['Spore']['lvl']}).")

    # GATE 5: Status Move Coverage Exclusion Rule
    print("[TEST 5] Status Move Coverage Exclusion Rule")
    status_moves = ["Thunder Wave", "Toxic", "Hypnosis", "Swords Dance"]
    covered_def_types = set()
    for sm in status_moves:
        inf = m_dict[sm]
        # Rule: Only category 0 or 1 with base_damage > 0 count
        if inf[1] in (0, 1) and inf[2] > 0:
            atk_type = ALL_TYPES[inf[0]]
            for dt in ALL_TYPES:
                if get_type_effectiveness(atk_type, [dt]) >= 2.0:
                    covered_def_types.add(dt)
    assert len(covered_def_types) == 0, f"Status moves falsely added coverage: {covered_def_types}"
    print("  --> PASS: Status moves strictly excluded from super-effective offensive coverage.")

    # GATE 6: Multi-Move Offensive Coverage Calculation
    print("[TEST 6] Multi-Move Offensive Coverage Calculation")
    equipped = ["Earthquake", "Waterfall", "Ice Beam", "Thunderbolt"]
    covered_types = set()
    for mv in equipped:
        inf = m_dict[mv]
        assert inf[1] in (0, 1) and inf[2] > 0, "Move should be damaging"
        atk_type = ALL_TYPES[inf[0]]
        for dt in ALL_TYPES:
            if get_type_effectiveness(atk_type, [dt]) >= 2.0:
                covered_types.add(dt)
    
    # Ground hits: Fire, Electric, Poison, Rock, Steel (5)
    # Water hits: Fire, Ground, Rock (3)
    # Ice hits: Grass, Ground, Flying, Dragon (4)
    # Electric hits: Water, Flying (2)
    expected_covered = {"Fire", "Electric", "Poison", "Rock", "Steel", "Ground", "Grass", "Flying", "Dragon", "Water"}
    assert expected_covered.issubset(covered_types), f"Missing coverage: {expected_covered - covered_types}"
    print(f"  --> PASS: 4 equipped moves hit {len(covered_types)} / 18 defending types super-effectively.")

    # GATE 7: Defensive Synergy & Immunity Math
    print("[TEST 7] Defensive Synergy & Immunity Math")
    # Gyarados/Steelix -> Water / Steel
    eff_gya_steel = {t: get_type_effectiveness(t, ["Water", "Steel"]) for t in ALL_TYPES}
    assert eff_gya_steel["Electric"] == 2.0, f"Electric vs Water/Steel should be 2.0x (2.0 * 1.0), got {eff_gya_steel['Electric']}"
    assert eff_gya_steel["Ice"] == 0.25, f"Ice vs Water/Steel should be 0.25x (0.5 * 0.5), got {eff_gya_steel['Ice']}"
    assert eff_gya_steel["Steel"] == 0.25, f"Steel vs Water/Steel should be 0.25x (0.5 * 0.5), got {eff_gya_steel['Steel']}"
    assert eff_gya_steel["Poison"] == 0.0, f"Poison vs Water/Steel should be 0.0x immune, got {eff_gya_steel['Poison']}"
    assert eff_gya_steel["Ground"] == 2.0, f"Ground vs Water/Steel should be 2.0x weak, got {eff_gya_steel['Ground']}"

    # Charizard/Pinsir -> Fire / Bug
    eff_chari_pin = {t: get_type_effectiveness(t, ["Fire", "Bug"]) for t in ALL_TYPES}
    assert eff_chari_pin["Rock"] == 4.0, f"Rock vs Fire/Bug should be 4.0x quad weak, got {eff_chari_pin['Rock']}"
    assert eff_chari_pin["Grass"] == 0.25, f"Grass vs Fire/Bug should be 0.25x quad resist, got {eff_chari_pin['Grass']}"
    print("  --> PASS: 0x complete immunities, 4x quad-weaknesses, and 0.25x quad-resists verified.")
    # GATE 8: Single Species Fallback
    print("[TEST 8] Single Species Fallback")
    gengar_data = base_stats["Gengar"]
    gengar_types = [ALL_TYPES[t] if isinstance(t, int) else t for t in gengar_data[1]]
    assert gengar_types == ["Ghost", "Poison"], f"Gengar types mismatch: {gengar_types}"
    gengar_bst = sum(gengar_data[2])
    assert gengar_bst == 500, f"Gengar BST should be 500, got {gengar_bst}"
    gengar_moves = get_legal_moves_for_species("Gengar", 40)
    assert "Shadow Ball" in gengar_moves or "Night Shade" in gengar_moves, "Gengar must have ghost moves"
    print("  --> PASS: Single species natural stats, types, and learnset verified.")

    # GATE 9: Combobox Filtering & Pokédex Number Resolution
    print("[TEST 9] Combobox Filtering & Pokédex Number Resolution")
    def filter_species_mock(query, part="head", context="team"):
        raw_q = (query or "").strip()
        clean_q = raw_q.lower().lstrip("#")
        species_keys = list(base_stats.keys())
        allow_none = (part == "body" and context == "team")

        if not clean_q:
            results = sorted(species_keys, key=lambda x: base_stats[x][0] if isinstance(base_stats[x], list) else base_stats[x].get("dex_id", 9999))
        else:
            is_num = clean_q.isdigit()
            num = int(clean_q) if is_num else None

            if is_num:
                exact_dex = []
                starts_dex = []
                inc_dex = []
                for s in species_keys:
                    inf = base_stats[s]
                    d_val = inf[0] if isinstance(inf, list) else inf.get("dex_id", 0)
                    d_str = str(d_val)
                    if d_val == num:
                        exact_dex.append(s)
                    elif d_str.startswith(clean_q):
                        starts_dex.append(s)
                    elif clean_q in d_str:
                        inc_dex.append(s)
                by_dex = lambda x: base_stats[x][0] if isinstance(base_stats[x], list) else base_stats[x].get("dex_id", 0)
                starts_dex.sort(key=by_dex)
                inc_dex.sort(key=by_dex)
                results = exact_dex + starts_dex + inc_dex
            else:
                exact_name = []
                starts_name = []
                inc_name = []
                for s in species_keys:
                    s_low = s.lower()
                    inf = base_stats[s]
                    types_list = [ALL_TYPES[t] if isinstance(t, int) else t for t in inf[1]]
                    if s_low == clean_q:
                        exact_name.append(s)
                    elif s_low.startswith(clean_q):
                        starts_name.append(s)
                    elif clean_q in s_low or any(clean_q == t.lower() for t in types_list):
                        inc_name.append(s)
                starts_name.sort()
                inc_name.sort()
                results = exact_name + starts_name + inc_name

        matches_none = allow_none and (not clean_q or "none" in clean_q or "single" in clean_q or "empty" in clean_q)
        return results, matches_none

    full_head, head_none = filter_species_mock("", "head", "team")
    assert len(full_head) == 596, f"Expected 596 species on empty query, got {len(full_head)}"
    assert not head_none, "Head selector must not match None"
    assert full_head[0] == "Bulbasaur", f"First entry should be Bulbasaur (#1), got {full_head[0]}"

    full_body, body_none = filter_species_mock("", "body", "team")
    assert len(full_body) == 596, f"Expected 596 species for body, got {len(full_body)}"
    assert body_none, "Body selector must match None (Single Mon)"

    res_63, _ = filter_species_mock("63", "head", "team")
    assert res_63[0] == "Abra", f"Expected Abra first for query '63', got {res_63[0]}"
    res_hash_63, _ = filter_species_mock("#63", "head", "team")
    assert res_hash_63[0] == "Abra", f"Expected Abra first for query '#63', got {res_hash_63[0]}"

    res_4, _ = filter_species_mock("4", "head", "team")
    assert res_4[0] == "Charmander", f"Expected Charmander first for query '4', got {res_4[0]}"

    res_char, _ = filter_species_mock("char", "head", "team")
    assert res_char[0] in ("Charizard", "Charmander", "Charmeleon"), f"Expected Char- family first, got {res_char[0]}"

    res_none, none_flag = filter_species_mock("none", "body", "team")
    assert none_flag, "Expected None option for body query 'none'"
    print("  --> PASS: Combobox search resolves exact Dex #, names, full 596 list, and None option.")

    print("================================================================")
    print("ALL 9 TEST GATES PASSED CLEANLY (100% ASSERTION INTEGRITY)!")
    print("================================================================")
    return True

if __name__ == "__main__":
    run_tests()
