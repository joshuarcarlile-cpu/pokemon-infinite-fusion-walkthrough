"""
Move Data & Learnset Extraction Pipeline for Pokémon Infinite Fusion
Decrypts IF GAME/InfiniteFusion/Data/moves.dat using the 16-byte XOR key.
Extracts name, type, damage category (0=Physical, 1=Special, 2=Status), base damage, and accuracy.
Deduplicates species level-up learnsets from data/mechanics/learnsets.json.
Generates data/mechanics/moves_compact.json for the dashboard compilation pipeline.
"""

import os
import json
import rubymarshal.reader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DATA_DIR = os.path.join(BASE_DIR, "IF GAME", "InfiniteFusion", "Data")
MOVES_DAT_FILE = os.path.join(GAME_DATA_DIR, "moves.dat")
LEARNSETS_FILE = os.path.join(BASE_DIR, "data", "mechanics", "learnsets.json")
BASE_STATS_FILE = os.path.join(BASE_DIR, "data", "mechanics", "base_stats.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "mechanics", "moves_compact.json")

XOR_KEY = [0x4A, 0x8F, 0x2C, 0xE1, 0x73, 0xB5, 0x96, 0x0D,
           0x5E, 0xA2, 0x3F, 0xC7, 0x81, 0x14, 0x6B, 0xD9]

ALL_TYPES = [
    "Normal", "Fire", "Water", "Grass", "Electric", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Steel", "Dark", "Fairy"
]
TYPE_TO_ID = {t: i for i, t in enumerate(ALL_TYPES)}

def decrypt_xor(raw_bytes):
    return bytes([b ^ XOR_KEY[i % len(XOR_KEY)] for i, b in enumerate(raw_bytes)])

def extract_moves_data():
    print(f"Reading moves binary from {MOVES_DAT_FILE}...")
    with open(MOVES_DAT_FILE, "rb") as f:
        raw = f.read()
    dec = decrypt_xor(raw)
    moves_data = rubymarshal.reader.loads(dec)

    move_info = {}
    for k, v in moves_data.items():
        name = v.attributes.get("@real_name")
        if not name:
            continue
        name_str = name.decode("utf-8", errors="replace").strip()
        t = v.attributes.get("@type")
        t_str = str(getattr(t, "name", t)).capitalize()
        cat = int(v.attributes.get("@category", 0))  # 0: Phys, 1: Spec, 2: Status
        pwr = int(v.attributes.get("@base_damage", 0))
        acc = int(v.attributes.get("@accuracy", 100))
        
        move_info[name_str] = [t_str, cat, pwr, acc]

    print(f"Extracted {len(move_info)} moves from binary data.")

    # Load species base stats, excluding internal dummy/triple-fusion entries (dex_id >= 1000000)
    with open(BASE_STATS_FILE, "r", encoding="utf-8") as f:
        base_stats = json.load(f)
    species_list = sorted([name for name, d in base_stats.items() if d.get("dex_id", 0) < 1000000])

    PRE_EVOLUTIONS_FILE = os.path.join(BASE_DIR, "data", "mechanics", "pre_evolutions.json")
    pre_evos = {}
    if os.path.exists(PRE_EVOLUTIONS_FILE):
        with open(PRE_EVOLUTIONS_FILE, "r", encoding="utf-8") as f:
            pre_evos = json.load(f)

    # Load and deduplicate learnsets, baking pre-evolution moves directly into each species
    with open(LEARNSETS_FILE, "r", encoding="utf-8") as f:
        raw_learnsets = json.load(f)

    dedup = {}
    for sp in species_list:
        seen = {}
        targets = [sp] + pre_evos.get(sp, [])
        for tgt in targets:
            for m in raw_learnsets.get(tgt, []):
                lvl = int(m.get("level", 0))
                mv = m.get("move", "")
                if mv and (mv not in seen or lvl < seen[mv]):
                    seen[mv] = lvl
        dedup[sp] = sorted([[lvl, mv] for mv, lvl in seen.items()], key=lambda x: x[0])

    all_move_names = sorted(list(move_info.keys()))
    move_name_to_id = {m: i for i, m in enumerate(all_move_names)}

    # Move table: [type_id, category, base_damage, accuracy]
    move_table = []
    for m in all_move_names:
        inf = move_info[m]
        t_id = TYPE_TO_ID.get(inf[0], 0)
        move_table.append([t_id, inf[1], inf[2], inf[3]])

    # Pack learnsets as dictionary keyed by species name: { [speciesName]: [packedInt, ...] }
    learnsets_dict = {}
    for sp in species_list:
        entries = dedup.get(sp, [])
        packed = []
        for lvl, mv in entries:
            if mv in move_name_to_id:
                packed.append(min(100, lvl) * 1000 + move_name_to_id[mv])
        if packed:
            learnsets_dict[sp] = packed

    output_payload = {
        "move_names": all_move_names,
        "move_table": move_table,
        "learnsets": learnsets_dict
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, separators=(",", ":"))

    print(f"Successfully generated {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes).")
    return output_payload

if __name__ == "__main__":
    extract_moves_data()
