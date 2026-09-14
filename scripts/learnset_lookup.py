"""
Deterministic Move Legality Lookup Engine for Pokémon Infinite Fusion
Queries canonical Gen 7 learnsets from data/mechanics/learnsets.json.
Returns all moves legally reachable by a species at or below a given Level Cap.
"""

import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEARNSETS_FILE = os.path.join(BASE_DIR, "data", "mechanics", "learnsets.json")
PRE_EVOS_FILE = os.path.join(BASE_DIR, "data", "mechanics", "pre_evolutions.json")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

LEARNSETS = load_json(LEARNSETS_FILE)
PRE_EVOLUTIONS = load_json(PRE_EVOS_FILE)

def get_reachable_moves(species, level_cap):
    all_targets = [species] + PRE_EVOLUTIONS.get(species, [])
    moves = set()
    
    for sp in all_targets:
        if sp in LEARNSETS:
            for e in LEARNSETS[sp]:
                if e.get("level", 0) <= level_cap:
                    moves.add(e.get("move"))
                    
    return sorted(list(moves))

def is_move_reachable(species, move_name, level_cap):
    moves = get_reachable_moves(species, level_cap)
    return move_name in moves

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        spec = sys.argv[1]
        cap = int(sys.argv[2])
        res = get_reachable_moves(spec, cap)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python learnset_lookup.py <Species> <Level_Cap>")
