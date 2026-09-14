"""
Pokémon Infinite Fusion Game Data Extractor
Decrypts and deserializes internal game binary files (.dat) using the 16-byte XOR key
and RubyMarshal. Populates authoritative, ground-truth JSON files for trainers,
species base stats, and level-up learnsets with exact official move names.
"""

import os
import json
import rubymarshal.reader
import rubymarshal.classes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DATA_DIR = os.path.join(BASE_DIR, "IF GAME", "InfiniteFusion", "Data")
OUTPUT_DATA_DIR = os.path.join(BASE_DIR, "data")
MECHANICS_DIR = os.path.join(OUTPUT_DATA_DIR, "mechanics")

XOR_KEY = [0x4A, 0x8F, 0x2C, 0xE1, 0x73, 0xB5, 0x96, 0x0D,
           0x5E, 0xA2, 0x3F, 0xC7, 0x81, 0x14, 0x6B, 0xD9]

def decrypt_xor(raw_bytes):
    return bytes([b ^ XOR_KEY[i % len(XOR_KEY)] for i, b in enumerate(raw_bytes)])

def to_dict(obj):
    if isinstance(obj, rubymarshal.classes.RubyObject):
        d = {"_class": obj.ruby_class_name}
        for k, v in obj.attributes.items():
            k_clean = str(k).lstrip("@")
            d[k_clean] = to_dict(v)
        return d
    elif isinstance(obj, rubymarshal.classes.Symbol):
        return str(obj.name)
    elif isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    elif isinstance(obj, list):
        return [to_dict(x) for x in obj]
    elif isinstance(obj, tuple):
        return [to_dict(x) for x in obj]
    elif isinstance(obj, dict):
        return {str(to_dict(k)): to_dict(v) for k, v in obj.items()}
    return obj

def load_moves_map():
    moves_path = os.path.join(GAME_DATA_DIR, "moves.dat")
    if not os.path.exists(moves_path):
        return {}
    with open(moves_path, "rb") as f:
        raw = f.read()
    dec = decrypt_xor(raw)
    data = rubymarshal.reader.loads(dec)
    m_map = {}
    for k, mv in data.items():
        sym_id = mv.attributes.get("@id")
        real_name = mv.attributes.get("@real_name")
        if sym_id and real_name:
            s_name = str(sym_id.name) if hasattr(sym_id, "name") else str(sym_id)
            n_str = real_name.decode("utf-8", errors="replace").strip()
            m_map[s_name.upper()] = n_str
    return m_map

def extract_trainers():
    classic_path = os.path.join(GAME_DATA_DIR, "trainers.dat")
    expert_path = os.path.join(GAME_DATA_DIR, "trainers_expert.dat")
    
    if os.path.exists(classic_path):
        with open(classic_path, "rb") as f:
            raw = f.read()
        dec = decrypt_xor(raw)
        data = rubymarshal.reader.loads(dec)
        serializable = {}
        for k, tr in data.items():
            if isinstance(k, int):
                serializable[str(k)] = to_dict(tr)
        out = os.path.join(OUTPUT_DATA_DIR, "trainers_classic.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)
        print(f"Extracted {len(serializable)} Classic trainers to {out}")

    if os.path.exists(expert_path):
        with open(expert_path, "rb") as f:
            raw = f.read()
        try:
            data = rubymarshal.reader.loads(raw)
        except Exception:
            data = rubymarshal.reader.loads(decrypt_xor(raw))
        serializable = {}
        for k, tr in data.items():
            if isinstance(k, int):
                serializable[str(k)] = to_dict(tr)
        out = os.path.join(OUTPUT_DATA_DIR, "trainers_expert.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)
        print(f"Extracted {len(serializable)} Expert trainers to {out}")

def load_abilities_map():
    abilities_path = os.path.join(GAME_DATA_DIR, "abilities.dat")
    if not os.path.exists(abilities_path):
        return {}
    with open(abilities_path, "rb") as f:
        raw = f.read()
    dec = decrypt_xor(raw)
    data = rubymarshal.reader.loads(dec)
    a_map = {}
    for k, ab in data.items():
        sym_id = ab.attributes.get("@id")
        real_name = ab.attributes.get("@real_name")
        if sym_id and real_name:
            s_name = str(sym_id.name) if hasattr(sym_id, "name") else str(sym_id)
            n_str = real_name.decode("utf-8", errors="replace").strip()
            a_map[s_name.upper()] = n_str
    return a_map

def extract_species_and_learnsets():
    moves_map = load_moves_map()
    abilities_map = load_abilities_map()
    species_path = os.path.join(GAME_DATA_DIR, "species.dat")
    if not os.path.exists(species_path):
        print("species.dat not found!")
        return
        
    with open(species_path, "rb") as f:
        raw = f.read()
    dec = decrypt_xor(raw)
    data = rubymarshal.reader.loads(dec)
    
    learnsets = {}
    base_stats = {}
    sym_to_name = {}
    direct_prev = {}
    
    # First pass: map symbols to real names
    for k, sp in data.items():
        name_raw = sp.attributes.get("@real_name")
        sym_id = sp.attributes.get("@id")
        if name_raw and sym_id:
            species_name = name_raw.decode("utf-8", errors="replace").strip()
            s_str = str(sym_id.name) if hasattr(sym_id, "name") else str(sym_id)
            sym_to_name[s_str.upper()] = species_name

    for k, sp in data.items():
        name_raw = sp.attributes.get("@real_name")
        if not name_raw:
            continue
        species_name = name_raw.decode("utf-8", errors="replace").strip()
        
        # Moves
        moves_list = sp.attributes.get("@moves", [])
        formatted_moves = []
        for mv in moves_list:
            lvl = mv[0]
            move_sym = str(mv[1].name) if hasattr(mv[1], "name") else str(mv[1])
            move_clean = moves_map.get(move_sym.upper(), move_sym.title())
            formatted_moves.append({
                "level": lvl,
                "move": move_clean
            })
        learnsets[species_name] = formatted_moves
        
        # Base Stats & Typing
        stats = sp.attributes.get("@base_stats", {})
        t1 = sp.attributes.get("@type1")
        t2 = sp.attributes.get("@type2")
        type1 = str(t1.name).capitalize() if hasattr(t1, "name") else (str(t1).capitalize() if t1 else "Normal")
        type2 = str(t2.name).capitalize() if hasattr(t2, "name") else (str(t2).capitalize() if t2 else None)
        
        types = [type1]
        if type2 and type2 != type1:
            types.append(type2)
            
        # Abilities
        raw_abilities = sp.attributes.get("@abilities", [])
        raw_hidden = sp.attributes.get("@hidden_abilities", [])
        
        clean_abilities = []
        for a in raw_abilities:
            a_sym = str(a.name) if hasattr(a, "name") else str(a)
            clean_name = abilities_map.get(a_sym.upper(), a_sym.title())
            if clean_name and clean_name not in clean_abilities:
                clean_abilities.append(clean_name)
                
        clean_hidden = []
        for a in raw_hidden:
            a_sym = str(a.name) if hasattr(a, "name") else str(a)
            clean_name = abilities_map.get(a_sym.upper(), a_sym.title())
            if clean_name and clean_name not in clean_hidden:
                clean_hidden.append(clean_name)
            
        dex_num = sp.attributes.get("@id_number", 0)
        
        base_stats[species_name] = {
            "dex_id": dex_num,
            "hp": stats.get(rubymarshal.classes.Symbol("HP"), 0) if isinstance(stats, dict) else 0,
            "atk": stats.get(rubymarshal.classes.Symbol("ATTACK"), 0) if isinstance(stats, dict) else 0,
            "def": stats.get(rubymarshal.classes.Symbol("DEFENSE"), 0) if isinstance(stats, dict) else 0,
            "spa": stats.get(rubymarshal.classes.Symbol("SPECIAL_ATTACK"), 0) if isinstance(stats, dict) else 0,
            "spd": stats.get(rubymarshal.classes.Symbol("SPECIAL_DEFENSE"), 0) if isinstance(stats, dict) else 0,
            "spe": stats.get(rubymarshal.classes.Symbol("SPEED"), 0) if isinstance(stats, dict) else 0,
            "types": types,
            "abilities": clean_abilities,
            "hidden_abilities": clean_hidden
        }
        
        # Track pre-evolutions (is_prev == True)
        evos = sp.attributes.get("@evolutions", [])
        for evo in evos:
            if len(evo) >= 4 and evo[3] is True:
                prev_s = str(evo[0].name) if hasattr(evo[0], "name") else str(evo[0])
                direct_prev[species_name] = sym_to_name.get(prev_s.upper(), prev_s.title())

    # Build full recursive pre-evolution chains
    all_prev = {}
    for sp in sym_to_name.values():
        chain = []
        cur = sp
        while cur in direct_prev and direct_prev[cur] not in chain:
            chain.append(direct_prev[cur])
            cur = direct_prev[cur]
        if chain:
            all_prev[sp] = chain
        
    os.makedirs(MECHANICS_DIR, exist_ok=True)
    learnsets_out = os.path.join(MECHANICS_DIR, "learnsets.json")
    with open(learnsets_out, "w", encoding="utf-8") as f:
        json.dump(learnsets, f, indent=2)
    print(f"Extracted {len(learnsets)} species learnsets to {learnsets_out}")
    
    stats_out = os.path.join(MECHANICS_DIR, "base_stats.json")
    with open(stats_out, "w", encoding="utf-8") as f:
        json.dump(base_stats, f, indent=2)
    print(f"Extracted {len(base_stats)} species base stats with abilities to {stats_out}")

    prev_out = os.path.join(MECHANICS_DIR, "pre_evolutions.json")
    with open(prev_out, "w", encoding="utf-8") as f:
        json.dump(all_prev, f, indent=2)
    print(f"Extracted {len(all_prev)} pre-evolution chains to {prev_out}")

if __name__ == "__main__":
    extract_trainers()
    extract_species_and_learnsets()
