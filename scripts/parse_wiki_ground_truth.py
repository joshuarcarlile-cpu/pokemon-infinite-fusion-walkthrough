"""
scripts/parse_wiki_ground_truth.py - Parse official wiki pages into structured JSON ground truth.
Parses:
1. Pokédex/Kanto/Classic -> data/mechanics/wiki_classic_pokedex.json
2. List of Gift Pokémon and Trades -> data/mechanics/wiki_gifts_and_trades.json
3. List of Static Encounters -> data/mechanics/wiki_static_encounters.json
"""

import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(BASE_DIR, "data", "wiki")
OUT_DIR = os.path.join(BASE_DIR, "data", "mechanics")
os.makedirs(OUT_DIR, exist_ok=True)

def clean_wiki_text(s: str) -> str:
    """Strip wiki links, tags, and formatting."""
    if not s:
        return ""
    # Remove HTML tags
    s = re.sub(r'<.*?>', ' ', s)
    # Remove templates {{...}}
    s = re.sub(r'\{\{.*?\}\}', '', s)
    # Clean [[Link|Text]] -> Text and [[Link]] -> Link
    s = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', s)
    # Remove bold/italic quotes
    s = re.sub(r"'''+|''+", '', s)
    # Clean excess whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def parse_classic_pokedex():
    src = os.path.join(WIKI_DIR, "Pokédex__Kanto__Classic.json")
    if not os.path.exists(src):
        print(f"Skipping Pokedex: {src} not found")
        return {}
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    wikitext = data.get("raw_wikitext", "")
    pokedex = {}
    matches = re.findall(r'\{\{PokedexTable/Data\|([^}]+)\}\}', wikitext)
    
    for m in matches:
        parts = [p.strip() for p in m.split("|")]
        if len(parts) < 3:
            continue
        id_num = parts[0]
        dex_num = parts[1]
        name = parts[2]
        
        # PokedexTable/Data format: |id|dex|Name||Type1|Type2|Locations/Evo||
        type1 = parts[4] if len(parts) > 4 else ""
        type2 = parts[5] if len(parts) > 5 else ""
        types = [t for t in [type1, type2] if t and not t.startswith("Category:")]
        
        loc_text = parts[6] if len(parts) > 6 else ""
        
        is_evolution = bool(re.search(r'\bEvolve\b', loc_text, re.IGNORECASE))
        evolution_info = ""
        if is_evolution:
            evo_match = re.search(r'Evolve\s+([^(]+)(?:\(([^)]+)\))?', loc_text)
            if evo_match:
                evolution_info = evo_match.group(0).strip()

        # Extract wiki links as distinct locations
        raw_locs = re.findall(r'\[\[(.*?)\]\]', loc_text)
        locations = []
        for l in raw_locs:
            parts_l = l.split("|")
            loc_name = parts_l[0].strip()
            # filter out non-location links
            if not any(skip in loc_name for skip in ["List of", "Category:", "File:"]):
                locations.append(loc_name)

        clean_loc_summary = clean_wiki_text(loc_text)

        pokedex[name] = {
            "id": id_num,
            "dex_num": dex_num,
            "name": name,
            "types": types,
            "is_evolution": is_evolution,
            "evolution_info": evolution_info,
            "locations": list(dict.fromkeys(locations)),
            "summary": clean_loc_summary
        }

    out_file = os.path.join(OUT_DIR, "wiki_classic_pokedex.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(pokedex, f, indent=2, ensure_ascii=False)
    print(f"SUCCESS: Saved {len(pokedex)} Classic Pokédex entries to {out_file}")
    return pokedex

def parse_gifts_and_trades():
    src = os.path.join(WIKI_DIR, "List_of_Gift_Pokémon_and_Trades.json")
    if not os.path.exists(src):
        print(f"Skipping Gifts: {src} not found")
        return {}
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    wikitext = data.get("raw_wikitext", "")
    
    # Table 1: Gift Pokémon
    # Table 2: NPC Trades
    tables = wikitext.split("{|")
    gifts = []
    trades = []
    
    # Process Gifts (Table 1)
    if len(tables) > 1:
        gift_table = tables[1]
        rows = [r.strip() for r in gift_table.split("|-") if r.strip()]
        last_loc = ""
        last_lvl = ""
        last_notes = ""
        
        for r in rows:
            if r.startswith("!"):
                continue
            cells = [c.strip() for c in r.split("||")]
            if not cells or not cells[0].startswith("|"):
                continue
            # Strip initial '|'
            first = cells[0].lstrip("|").strip()
            # Clean rowspan
            first_clean = re.sub(r'rowspan="?\d+"?\s*\|', '', first).strip()
            mon_name = clean_wiki_text(first_clean)
            if not mon_name or mon_name.lower().startswith("pokemon"):
                continue
                
            loc = last_loc
            lvl = last_lvl
            notes = last_notes
            
            if len(cells) >= 4:
                loc = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[1]))
                lvl = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[2]))
                notes = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[3]))
                last_loc, last_lvl, last_notes = loc, lvl, notes
            elif len(cells) == 3:
                loc = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[1]))
                lvl = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[2]))
                last_loc, last_lvl = loc, lvl
            elif len(cells) == 2:
                loc = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[1]))
                last_loc = loc
                
            gifts.append({
                "pokemon": mon_name,
                "location": loc,
                "level": lvl,
                "notes": notes
            })

    # Process Trades (Table 2)
    if len(tables) > 2:
        trade_table = tables[2]
        rows = [r.strip() for r in trade_table.split("|-") if r.strip()]
        for r in rows:
            if r.startswith("!"):
                continue
            cells = [c.strip() for c in r.split("||")]
            if len(cells) >= 3:
                give_mon = clean_wiki_text(cells[0].lstrip("|"))
                receive_mon = clean_wiki_text(cells[1])
                loc = clean_wiki_text(cells[2])
                notes = clean_wiki_text(cells[3]) if len(cells) > 3 else ""
                if give_mon and receive_mon and not give_mon.lower().startswith("pokemon"):
                    trades.append({
                        "give": give_mon,
                        "receive": receive_mon,
                        "location": loc,
                        "notes": notes
                    })

    result = {"gifts": gifts, "trades": trades}
    out_file = os.path.join(OUT_DIR, "wiki_gifts_and_trades.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"SUCCESS: Saved {len(gifts)} gifts & {len(trades)} trades to {out_file}")
    return result

def parse_static_encounters():
    src = os.path.join(WIKI_DIR, "List_of_Static_Encounters.json")
    if not os.path.exists(src):
        print(f"Skipping Static: {src} not found")
        return []
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    wikitext = data.get("raw_wikitext", "")
    tables = wikitext.split("{|")
    statics = []
    
    if len(tables) > 1:
        table = tables[1]
        rows = [r.strip() for r in table.split("|-") if r.strip()]
        last_mon = ""
        last_lvl = ""
        
        for r in rows:
            if r.startswith("!"):
                continue
            cells = [c.strip() for c in r.split("||")]
            if not cells or not cells[0].startswith("|"):
                continue
            
            first = cells[0].lstrip("|").strip()
            first_clean = re.sub(r'rowspan="?\d+"?\s*\|', '', first).strip()
            first_text = clean_wiki_text(first_clean)
            
            mon_name = first_text if first_text else last_mon
            last_mon = mon_name
            
            if len(cells) >= 4:
                loc = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[1]))
                lvl = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[2]))
                notes = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[3]))
                last_loc, last_lvl, last_notes = loc, lvl, notes
            elif len(cells) == 3:
                loc = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[1]))
                lvl = last_lvl
                notes = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[2]))
                last_loc = loc
            elif len(cells) == 2:
                loc = clean_wiki_text(re.sub(r'rowspan="?\d+"?\s*\|', '', cells[1]))
                lvl = last_lvl
                notes = ""
                last_loc = loc
            elif len(cells) == 1:
                loc = last_loc
                lvl = last_lvl
                notes = last_notes
            else:
                continue
                
            if mon_name and not mon_name.lower().startswith("pokemon"):
                statics.append({
                    "pokemon": mon_name,
                    "location": loc,
                    "level": lvl,
                    "notes": notes
                })

    out_file = os.path.join(OUT_DIR, "wiki_static_encounters.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(statics, f, indent=2, ensure_ascii=False)
    print(f"SUCCESS: Saved {len(statics)} static encounters to {out_file}")
    return statics

if __name__ == "__main__":
    print("Parsing Wiki Ground Truth...")
    parse_classic_pokedex()
    parse_gifts_and_trades()
    parse_static_encounters()
