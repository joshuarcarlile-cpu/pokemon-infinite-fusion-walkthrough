"""
Lean Deterministic Fusion Math & Movepool Engine for Pokémon Infinite Fusion
Calculates:
- Asymmetric Base Stats:
    Atk, Def, Spe = floor(2/3 * Body + 1/3 * Head)
    HP, SpA, SpD = floor(2/3 * Head + 1/3 * Body)
- Resulting Dual Typing with PIF overrides
- Defensive Weaknesses, Resistances, and Immunities
- Role Classification
"""

import math
import json
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_FILE = os.path.join(BASE_DIR, "data", "mechanics", "base_stats.json")

# Load decoupled data
with open(STATS_FILE, "r", encoding="utf-8") as f:
    SPECIES_DATA = json.load(f)

# PIF type overrides
TYPE_OVERRIDES = {
    "Magnemite": ("Steel", "Electric"), "Magneton": ("Steel", "Electric"), "Magnezone": ("Steel", "Electric"),
    "Spiritomb": ("Dark", "Ghost"), "Phantump": ("Grass", "Ghost"), "Trevenant": ("Grass", "Ghost"),
    "Ferroseed": ("Steel", "Grass"), "Ferrothorn": ("Steel", "Grass"),
    "Sandygast": ("Ground", "Ghost"), "Palossand": ("Ground", "Ghost")
}

TYPE_CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water": {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5},
    "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0, "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison": {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2},
    "Ground": {"Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2, "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2},
    "Flying": {"Electric": 0.5, "Grass": 2, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0, "Steel": 0.5},
    "Bug": {"Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Bug": 2, "Steel": 0.5},
    "Ghost": {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2, "Rock": 2, "Steel": 0.5, "Fairy": 2},
    "Dark": {"Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5, "Fairy": 0.5},
    "Fairy": {"Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2, "Steel": 0.5, "Dark": 2}
}

ALL_TYPES = list(TYPE_CHART.keys())

def get_species_types(species):
    if species in TYPE_OVERRIDES:
        return list(TYPE_OVERRIDES[species])
    return SPECIES_DATA[species]["types"]

def calculate_fusion_types(head, body):
    h_types = get_species_types(head)
    b_types = get_species_types(body)
    
    # Head provides its primary type (Normal/Flying always provides Flying)
    t1 = "Flying" if h_types == ["Normal", "Flying"] else h_types[0]
    
    # Body normally provides its secondary type (Normal/Flying always provides Flying)
    if b_types == ["Normal", "Flying"]:
        t2 = "Flying"
    elif len(b_types) > 1:
        t2 = b_types[1]
    else:
        t2 = b_types[0]
        
    # Canonical Redundancy Fallback:
    # If the head already provides the type the body wants to pass,
    # the body provides its primary type instead (e.g. Grimer + Oddish -> Poison/Grass)
    if t1 == t2 and len(b_types) > 1:
        t2 = b_types[0]
        
    if t1 == t2:
        return [t1]
    return [t1, t2]

def calculate_fusion_stats(head, body):
    h = SPECIES_DATA[head]
    b = SPECIES_DATA[body]
    
    hp = math.floor((2 * h["hp"] + b["hp"]) / 3)
    atk = math.floor((2 * b["atk"] + h["atk"]) / 3)
    defn = math.floor((2 * b["def"] + h["def"]) / 3)
    spa = math.floor((2 * h["spa"] + b["spa"]) / 3)
    spd = math.floor((2 * h["spd"] + b["spd"]) / 3)
    spe = math.floor((2 * b["spe"] + h["spe"]) / 3)
    
    return {
        "hp": hp, "atk": atk, "def": defn,
        "spa": spa, "spd": spd, "spe": spe,
        "bst": hp + atk + defn + spa + spd + spe
    }

def calculate_defensive_profile(types):
    profile = {}
    for atk_type in ALL_TYPES:
        mult = 1.0
        for def_type in types:
            if def_type in TYPE_CHART[atk_type]:
                mult *= TYPE_CHART[atk_type][def_type]
        if mult != 1.0:
            profile[atk_type] = mult
    return profile

def classify_role(stats):
    atk = stats["atk"]
    spa = stats["spa"]
    spe = stats["spe"]
    hp = stats["hp"]
    defn = stats["def"]
    spd = stats["spd"]
    
    if spe >= 85 and atk >= 95:
        return "Fast Physical Sweeper"
    elif spe >= 85 and spa >= 95:
        return "Fast Special Sweeper"
    elif atk >= 110:
        return "Physical Wallbreaker"
    elif spa >= 110:
        return "Special Wallbreaker"
    elif hp + defn >= 170:
        return "Physical Tank"
    elif hp + spd >= 170:
        return "Special Tank"
    return "Bulky Balanced"

def fuse(head, body):
    if head not in SPECIES_DATA or body not in SPECIES_DATA:
        raise ValueError(f"Unknown species: {head} or {body}")
        
    f_types = calculate_fusion_types(head, body)
    stats = calculate_fusion_stats(head, body)
    role = classify_role(stats)
    defensive = calculate_defensive_profile(f_types)
    
    h_data = SPECIES_DATA[head]
    b_data = SPECIES_DATA[body]
    
    h_abs = h_data.get("abilities", [])
    b_abs = b_data.get("abilities", [])
    h_habs = h_data.get("hidden_abilities", [])
    b_habs = b_data.get("hidden_abilities", [])
    
    head_primary = h_abs[0] if h_abs else None
    body_secondary = b_abs[1] if len(b_abs) > 1 else (b_abs[0] if b_abs else None)
    hidden_options = list(set(h_habs + b_habs))
    
    abilities = []
    if head_primary:
        abilities.append(head_primary)
    if body_secondary and body_secondary not in abilities:
        abilities.append(body_secondary)
    for hab in hidden_options:
        if hab not in abilities:
            abilities.append(hab)
    
    return {
        "head": head,
        "body": body,
        "name": f"{head}/{body}",
        "types": f_types,
        "stats": stats,
        "role": role,
        "abilities_choice": abilities,
        "ability_slots": {
            "head_primary": head_primary,
            "body_secondary": body_secondary,
            "hidden": hidden_options
        },
        "defensive_profile": defensive
    }

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        h = sys.argv[1]
        b = sys.argv[2]
        res = fuse(h, b)
        
        # Check if --cap is passed
        if "--cap" in sys.argv:
            try:
                cap_idx = sys.argv.index("--cap") + 1
                cap = int(sys.argv[cap_idx])
                from learnset_lookup import get_reachable_moves
                head_moves = get_reachable_moves(h, cap)
                body_moves = get_reachable_moves(b, cap)
                combined = sorted(list(set(head_moves + body_moves)))
                res["legal_moves_at_cap"] = {
                    "cap": cap,
                    f"{h}_moves": head_moves,
                    f"{b}_moves": body_moves,
                    "combined_pool": combined
                }
            except Exception as e:
                res["cap_error"] = str(e)
                
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python fusion_calc.py <Head_Species> <Body_Species> [--cap <Level>]")
