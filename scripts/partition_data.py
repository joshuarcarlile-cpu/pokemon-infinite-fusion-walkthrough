import json
import re
import os
import csv

BASE_DIR = r"C:\Users\joshu\OneDrive\Desktop\Pokemon IF Walkthrough"
STEPS_DIR = r"C:\Users\joshu\.gemini\antigravity\brain\3706262b-0b55-4add-ba24-7738fad27825\.system_generated\steps"

def parse_custom_tms():
    src = os.path.join(STEPS_DIR, "159", "content.md")
    if not os.path.exists(src):
        print(f"File not found: {src}")
        return
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Find CSV data start (after ---)
    csv_lines = []
    started = False
    for line in lines:
        if line.strip() == "---":
            started = True
            continue
        if started and line.strip():
            csv_lines.append(line)
    
    reader = csv.reader(csv_lines)
    header = next(reader)
    tms = {h.strip(): [] for h in header if h.strip()}
    
    for row in reader:
        for idx, val in enumerate(row):
            if idx < len(header):
                tm_name = header[idx].strip()
                val_clean = val.strip()
                if tm_name in tms and val_clean:
                    tms[tm_name].append(val_clean)
    
    out_path = os.path.join(BASE_DIR, "data", "mechanics", "custom_tms.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(tms, f, indent=2)
    print(f"Saved custom TMs: {len(tms)} moves to {out_path}")

def parse_custom_tutors():
    src = os.path.join(STEPS_DIR, "163", "content.md")
    if not os.path.exists(src):
        print(f"File not found: {src}")
        return
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    csv_lines = []
    started = False
    for line in lines:
        if line.strip() == "---":
            started = True
            continue
        if started and line.strip():
            csv_lines.append(line)
    
    reader = csv.reader(csv_lines)
    header = next(reader)
    tutors = {h.strip(): [] for h in header if h.strip() and "New Tutors" not in h}
    
    for row in reader:
        for idx, val in enumerate(row):
            if idx < len(header):
                move_name = header[idx].strip()
                val_clean = val.strip()
                if move_name in tutors and val_clean:
                    tutors[move_name].append(val_clean)
    
    out_path = os.path.join(BASE_DIR, "data", "mechanics", "custom_tutors.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(tutors, f, indent=2)
    print(f"Saved custom Tutors: {len(tutors)} moves to {out_path}")

def parse_wild_encounters():
    src = os.path.join(STEPS_DIR, "57", "content.md")
    if not os.path.exists(src):
        print(f"File not found: {src}")
        return
    with open(src, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Locate JSON start on line after ---
    json_start = content.find('{"parse":')
    if json_start == -1:
        print("Could not find JSON in content.md")
        return
    
    raw_json = json.loads(content[json_start:])
    wikitext = raw_json["parse"]["wikitext"]["*"]
    
    # Split by location headings: '''Location Name (ID X)'''
    pattern = r"'''([^'\n]+(?:\(ID\s*\d+\))?)'''"
    splits = re.split(pattern, wikitext)
    
    # splits[0] is preamble. Then (location_title, body_text) pairs
    encounters_by_loc = {}
    kanto_dir = os.path.join(BASE_DIR, "data", "encounters", "kanto")
    os.makedirs(kanto_dir, exist_ok=True)
    
    for i in range(1, len(splits), 2):
        loc_title = splits[i].strip()
        body = splits[i+1].strip() if i+1 < len(splits) else ""
        
        # Parse sections within body: {{EncounterTable/Section|Grass}}
        section_pattern = r"\{\{EncounterTable/Section\|([^}]+)\}\}"
        section_splits = re.split(section_pattern, body)
        
        sections = {}
        for s in range(1, len(section_splits), 2):
            sec_name = section_splits[s].strip()
            sec_body = section_splits[s+1] if s+1 < len(section_splits) else ""
            
            # Parse rows: {{EncounterTable/Data|ID|Name|Type1|Type2|Levels|CatchRate|Rates...}}
            row_pattern = r"\{\{EncounterTable/Data\|([^}]+)\}\}"
            rows = re.findall(row_pattern, sec_body)
            parsed_rows = []
            for r in rows:
                cols = [c.strip() for c in r.split("|")]
                if len(cols) >= 6:
                    dex_id = cols[0]
                    name = cols[1]
                    t1 = cols[2] if len(cols) > 2 else ""
                    t2 = cols[3] if len(cols) > 3 else ""
                    levels = cols[4] if len(cols) > 4 else ""
                    catch_rate = cols[5] if len(cols) > 5 else ""
                    # Remaining cols are encounter rates (Morning / Day / Night or single rate)
                    rates = cols[6:] if len(cols) > 6 else []
                    parsed_rows.append({
                        "dex_id": dex_id,
                        "name": name,
                        "type1": t1,
                        "type2": t2,
                        "levels": levels,
                        "catch_rate": catch_rate,
                        "rates": rates
                    })
            sections[sec_name] = parsed_rows
        
        # Sanitize filename
        safe_name = re.sub(r"[^\w\s-]", "", loc_title).strip().lower().replace(" ", "_")
        if not safe_name:
            continue
        
        loc_data = {
            "location": loc_title,
            "sections": sections
        }
        
        file_path = os.path.join(kanto_dir, f"{safe_name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(loc_data, f, indent=2)
        encounters_by_loc[safe_name] = loc_title
    
    print(f"Parsed {len(encounters_by_loc)} route locations into {kanto_dir}")

def parse_static_encounters():
    src = os.path.join(STEPS_DIR, "59", "content.md")
    if not os.path.exists(src):
        return
    with open(src, "r", encoding="utf-8") as f:
        content = f.read()
    
    json_start = content.find('{"parse":')
    if json_start == -1:
        return
    raw_json = json.loads(content[json_start:])
    wikitext = raw_json["parse"]["wikitext"]["*"]
    
    # Parse rows: | Pokémon || Location || Level || Notes
    rows = []
    lines = wikitext.split("\n")
    current_mon = None
    
    for line in lines:
        if line.startswith("|") and "||" in line:
            parts = [p.strip() for p in line.lstrip("|").split("||")]
            if len(parts) >= 3:
                pokemon = re.sub(r"\[\[|\]\]", "", parts[0]).strip()
                location = re.sub(r"\[\[|\]\]", "", parts[1]).strip()
                level = parts[2].strip()
                notes = parts[3].strip() if len(parts) > 3 else ""
                # Clean html tags from notes
                notes = re.sub(r"<[^>]+>", "", notes).strip()
                rows.append({
                    "pokemon": pokemon,
                    "location": location,
                    "level": level,
                    "notes": notes
                })
    
    out_path = os.path.join(BASE_DIR, "data", "items", "static_encounters.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"Saved static encounters: {len(rows)} encounters to {out_path}")

if __name__ == "__main__":
    parse_custom_tms()
    parse_custom_tutors()
    parse_wild_encounters()
    parse_static_encounters()
