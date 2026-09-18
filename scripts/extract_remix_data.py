"""
Pokémon Infinite Fusion Remix Data Extractor
Extracts canonical wild encounters and trainer rosters for Remix Mode
directly from binary game files (encounters_remix.dat, trainers_remix.dat).
Outputs:
- data/trainers_remix.json
- data/mechanics/gym_leaders.json (keyed with "remix")
- data/encounters/remix/*.json
"""

import os
import sys
import json
import re
import math
from pathlib import Path
import rubymarshal.reader
import rubymarshal.classes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DATA_DIR = os.path.join(BASE_DIR, "IF GAME", "InfiniteFusion", "Data")
OUTPUT_DATA_DIR = os.path.join(BASE_DIR, "data")
MECHANICS_DIR = os.path.join(OUTPUT_DATA_DIR, "mechanics")
ENCOUNTERS_REMIX_DIR = os.path.join(OUTPUT_DATA_DIR, "encounters", "remix")

XOR_KEY = [0x4A, 0x8F, 0x2C, 0xE1, 0x73, 0xB5, 0x96, 0x0D,
           0x5E, 0xA2, 0x3F, 0xC7, 0x81, 0x14, 0x6B, 0xD9]

def decrypt_xor(raw_bytes):
    return bytes([b ^ XOR_KEY[i % len(XOR_KEY)] for i, b in enumerate(raw_bytes)])

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

def load_species_map():
    """Build mapping from species symbol/ID to canonical display name."""
    bs_path = os.path.join(MECHANICS_DIR, "base_stats.json")
    dex_to_name = {}
    sym_to_name = {}
    if os.path.exists(bs_path):
        with open(bs_path, "r", encoding="utf-8") as f:
            base_stats = json.load(f)
        for name, data in base_stats.items():
            did = data.get("dex_id")
            if did:
                dex_to_name[did] = name
            sym_to_name[name.upper().replace(" ", "").replace("-", "").replace(".", "")] = name
            
    # Also load from species.dat directly for any unmapped symbols
    sp_path = os.path.join(GAME_DATA_DIR, "species.dat")
    if os.path.exists(sp_path):
        with open(sp_path, "rb") as f:
            raw = f.read()
        dec = decrypt_xor(raw)
        sp_data = rubymarshal.reader.loads(dec)
        for k, sp in sp_data.items():
            sym_id = sp.attributes.get("@id")
            real_name = sp.attributes.get("@real_name")
            num_id = sp.attributes.get("@id_number")
            if sym_id and real_name:
                s_str = str(sym_id.name) if hasattr(sym_id, "name") else str(sym_id)
                n_str = real_name.decode("utf-8", errors="replace").strip()
                sym_to_name[s_str.upper()] = n_str
                if num_id:
                    dex_to_name[num_id] = n_str
                    
    return dex_to_name, sym_to_name

def resolve_species_name(species_sym_or_str, dex_to_name, sym_to_name):
    """Resolves single species or fusion symbols like B54H390 into canonical names."""
    if isinstance(species_sym_or_str, rubymarshal.classes.Symbol):
        s_val = str(species_sym_or_str.name)
    else:
        s_val = str(species_sym_or_str)
        
    s_clean = s_val.strip().lstrip(":")
    
    # Check for fusion pattern: B<body_id>H<head_id>
    m_fusion = re.match(r"^B(\d+)H(\d+)$", s_clean)
    if m_fusion:
        body_id = int(m_fusion.group(1))
        head_id = int(m_fusion.group(2))
        head_name = dex_to_name.get(head_id, f"Species_{head_id}")
        body_name = dex_to_name.get(body_id, f"Species_{body_id}")
        return f"{head_name}/{body_name}"
        
    # Check single species symbol
    clean_key = s_clean.upper().replace(" ", "").replace("-", "").replace(".", "")
    if clean_key in sym_to_name:
        return sym_to_name[clean_key]
        
    return s_clean.title()

def extract_trainers_remix():
    print("--- Extracting Remix Trainers & Bosses ---")
    moves_map = load_moves_map()
    dex_to_name, sym_to_name = load_species_map()
    
    tr_path = os.path.join(GAME_DATA_DIR, "trainers_remix.dat")
    if not os.path.exists(tr_path):
        print(f"Error: {tr_path} not found")
        return
        
    with open(tr_path, "rb") as f:
        raw = f.read()
    data = rubymarshal.reader.loads(decrypt_xor(raw))
    
    trainers_dict = {}
    remix_leaders = {}
    
    for k, tr in data.items():
        if not isinstance(k, int):
            continue
            
        t_type = tr.attributes.get("@trainer_type")
        t_name = tr.attributes.get("@real_name") or tr.attributes.get("@name")
        version = tr.attributes.get("@version", 0)
        items = tr.attributes.get("@items", [])
        raw_pokemon = tr.attributes.get("@pokemon", [])
        
        type_str = str(t_type.name) if hasattr(t_type, "name") else str(t_type)
        name_str = t_name.decode("utf-8", errors="replace").strip() if isinstance(t_name, bytes) else (str(t_name).strip() if t_name else None)
        
        clean_items = []
        for it in items:
            it_s = str(it.name) if hasattr(it, "name") else str(it)
            clean_items.append(it_s.upper())
            
        clean_pokemon = []
        for p in raw_pokemon:
            sp_raw = p.get(rubymarshal.classes.Symbol("species"))
            base_lvl = p.get(rubymarshal.classes.Symbol("level"), 1)
            hard_lvl = math.ceil(base_lvl * 1.1)
            if hard_lvl > 100:
                hard_lvl = 100
                
            sp_resolved = resolve_species_name(sp_raw, dex_to_name, sym_to_name)
            
            p_moves = p.get(rubymarshal.classes.Symbol("moves"), [])
            clean_moves = []
            for mv in p_moves:
                mv_s = str(mv.name) if hasattr(mv, "name") else str(mv)
                clean_moves.append(moves_map.get(mv_s.upper(), mv_s.title()))
                
            p_item = p.get(rubymarshal.classes.Symbol("item"))
            item_clean = str(p_item.name) if hasattr(p_item, "name") else (str(p_item) if p_item else None)
            
            p_obj = {
                "species": sp_resolved,
                "raw_species": str(sp_raw),
                "level": base_lvl,
                "hard_level": hard_lvl,
                "moves": clean_moves,
            }
            if item_clean:
                p_obj["item"] = item_clean
            ability_idx = p.get(rubymarshal.classes.Symbol("ability_index"))
            if ability_idx is not None:
                p_obj["ability_index"] = ability_idx
                
            clean_pokemon.append(p_obj)
            
        trainer_entry = {
            "id_number": k,
            "trainer_type": type_str,
            "name": name_str,
            "version": version,
            "items": clean_items,
            "pokemon": clean_pokemon
        }
        trainers_dict[str(k)] = trainer_entry
        
        # Track gym leaders and key bosses for gym_leaders.json
        if any(pfx in type_str for pfx in ["LEADER", "ELITEFOUR", "CHAMPION"]):
            if type_str not in remix_leaders or version == 0:
                remix_leaders[type_str] = {
                    "id_number": k,
                    "trainer_type": type_str,
                    "real_name": name_str or type_str.replace("LEADER_", "").replace("ELITEFOUR_", ""),
                    "items": clean_items,
                    "pokemon": [
                        {
                            "species": p["species"],
                            "raw_species": p["raw_species"],
                            "level": p["hard_level"], # gym_leaders.json stores the Hard cap level
                            "base_level": p["level"],
                            "moves": p["moves"],
                            "item": p.get("item"),
                            "ability_index": p.get("ability_index")
                        }
                        for p in clean_pokemon
                    ]
                }

    # Save data/trainers_remix.json
    out_tr = os.path.join(OUTPUT_DATA_DIR, "trainers_remix.json")
    with open(out_tr, "w", encoding="utf-8") as f:
        json.dump(trainers_dict, f, indent=2)
    print(f"Saved {len(trainers_dict)} Remix trainers to {out_tr}")
    
    # Ingest "remix" key into data/mechanics/gym_leaders.json
    gl_path = os.path.join(MECHANICS_DIR, "gym_leaders.json")
    gl_data = {}
    if os.path.exists(gl_path):
        with open(gl_path, "r", encoding="utf-8") as f:
            gl_data = json.load(f)
            
    gl_data["remix"] = remix_leaders
    with open(gl_path, "w", encoding="utf-8") as f:
        json.dump(gl_data, f, indent=2)
    print(f"Updated {gl_path} with {len(remix_leaders)} Remix boss rosters.")

def extract_encounters_remix():
    print("--- Extracting Remix Wild Encounters ---")
    dex_to_name, sym_to_name = load_species_map()
    
    enc_path = os.path.join(GAME_DATA_DIR, "encounters_remix.dat")
    map_infos_path = os.path.join(GAME_DATA_DIR, "MapInfos.rxdata")
    
    if not os.path.exists(enc_path) or not os.path.exists(map_infos_path):
        print("Missing encounters_remix.dat or MapInfos.rxdata")
        return
        
    with open(enc_path, "rb") as f:
        enc_data = rubymarshal.reader.loads(f.read())
        
    with open(map_infos_path, "rb") as f:
        map_infos = rubymarshal.reader.loads(f.read())
        
    os.makedirs(ENCOUNTERS_REMIX_DIR, exist_ok=True)
    
    # Map Essentials section symbols to standard section names
    section_map = {
        "Land": "Grass",
        "LandMorning": "Grass",
        "LandDay": "Grass",
        "LandNight": "Grass",
        "Cave": "Cave",
        "Water": "Surf",
        "OldRod": "Old Rod",
        "GoodRod": "Good Rod",
        "SuperRod": "Super Rod",
        "RockSmash": "Rock Smash",
        "HeadbuttLow": "Headbutt",
        "HeadbuttHigh": "Headbutt",
        "BugContest": "Bug Contest"
    }
    
    # Find existing kanto filename slugs for map IDs to maintain exact naming alignment
    kanto_dir = os.path.join(OUTPUT_DATA_DIR, "encounters", "kanto")
    kanto_slug_by_id = {}
    if os.path.exists(kanto_dir):
        for f in os.listdir(kanto_dir):
            m = re.match(r"^(.*)_id_(\d+)\.json$", f)
            if m:
                kanto_slug_by_id[int(m.group(2))] = m.group(1)

    count = 0
    for k, v in enc_data.items():
        map_id = v.attributes.get("@map")
        raw_types = v.attributes.get("@types", {})
        
        info = map_infos.get(map_id)
        if info and hasattr(info, "attributes"):
            raw_name = info.attributes.get("@name")
            map_name = str(raw_name) if raw_name else f"Map {map_id}"
        else:
            map_name = f"Map {map_id}"
            
        # Determine slug
        if map_id in kanto_slug_by_id:
            slug = kanto_slug_by_id[map_id]
        else:
            slug = re.sub(r"[^a-z0-9]+", "_", map_name.lower()).strip("_")
            
        filename = f"{slug}_id_{map_id}.json"
        out_file = os.path.join(ENCOUNTERS_REMIX_DIR, filename)
        
        sections = {}
        for sym, table in raw_types.items():
            sym_name = str(sym.name) if hasattr(sym, "name") else str(sym)
            sec_display = section_map.get(sym_name, sym_name)
            
            if sec_display not in sections:
                sections[sec_display] = []
                
            for entry in table:
                # format: [chance, species_symbol, min_lvl, max_lvl]
                if len(entry) < 4:
                    continue
                chance = entry[0]
                sp_sym = entry[1]
                min_l = entry[2]
                max_l = entry[3]
                
                sp_name = resolve_species_name(sp_sym, dex_to_name, sym_to_name)
                levels_str = f"{min_l}-{max_l}" if min_l != max_l else str(min_l)
                
                # Check for existing entry to aggregate rates if times of day
                existing = next((x for x in sections[sec_display] if x["name"] == sp_name and x["levels"] == levels_str), None)
                if existing:
                    existing["rates"].append(f"{chance}% ({sym_name})")
                else:
                    sections[sec_display].append({
                        "name": sp_name,
                        "levels": levels_str,
                        "rates": [f"{chance}%"]
                    })
                    
        payload = {
            "location": f"{map_name} (ID {map_id})",
            "map_id": map_id,
            "sections": sections
        }
        
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        count += 1

    print(f"Saved {count} Remix encounter map files to {ENCOUNTERS_REMIX_DIR}")

if __name__ == "__main__":
    extract_trainers_remix()
    extract_encounters_remix()
    print("SUCCESS: All Remix game data extracted.")
