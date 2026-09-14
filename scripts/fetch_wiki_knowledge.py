"""
Authoritative Pokémon Infinite Fusion Wiki Knowledge Fetcher & Local Cache Engine
Queries the official MediaWiki API at infinitefusion.fandom.com.
Caches structured JSON into data/wiki/{page}.json to serve as an immutable ground truth
for all agents, subagents, and automated linting scripts.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(BASE_DIR, "data", "wiki")
API_URL = "https://infinitefusion.fandom.com/api.php"

os.makedirs(WIKI_DIR, exist_ok=True)

def fetch_wiki_page(page_title, force_refresh=False):
    clean_title = page_title.strip().replace(" ", "_")
    file_safe_title = clean_title.replace("/", "__")
    cache_file = os.path.join(WIKI_DIR, f"{file_safe_title}.json")
    
    if os.path.exists(cache_file) and not force_refresh:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    print(f"Fetching '{clean_title}' from Pokémon Infinite Fusion Wiki API...")
    params = {
        "action": "parse",
        "page": clean_title,
        "prop": "wikitext|sections",
        "format": "json"
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "AntigravityPIFBot/1.0"})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_data = json.loads(resp.read().decode("utf-8"))
            
        parse_data = raw_data.get("parse", {})
        if not parse_data:
            err = raw_data.get("error", {}).get("info", "Unknown error")
            print(f"Error fetching {clean_title}: {err}")
            return None
            
        wikitext = parse_data.get("wikitext", {}).get("*", "")
        
        # Check for #REDIRECT
        redir_match = re.match(r'#REDIRECT\s*\[\[(.*?)\]\]', wikitext, re.IGNORECASE)
        if redir_match:
            redir_target = redir_match.group(1).strip()
            print(f"Following redirect from '{clean_title}' to '{redir_target}'...")
            target_data = fetch_wiki_page(redir_target, force_refresh=force_refresh)
            if target_data:
                alias_path = os.path.join(WIKI_DIR, f"{clean_title}.json")
                with open(alias_path, "w", encoding="utf-8") as f:
                    json.dump(target_data, f, indent=2, ensure_ascii=False)
            return target_data
            
        sections = parse_data.get("sections", [])
        
        # Parse wikitext into structured components
        # 1. Lead text (before first == Section ==)
        first_section_idx = wikitext.find("==")
        lead_raw = wikitext[:first_section_idx] if first_section_idx != -1 else wikitext
        
        # Clean wikitext markup for readability
        lead_clean = re.sub(r'\{\{.*?\}\}', '', lead_raw, flags=re.DOTALL)
        lead_clean = re.sub(r'<gallery>.*?</gallery>', '', lead_clean, flags=re.DOTALL)
        lead_clean = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', lead_clean)
        lead_clean = re.sub(r"'''?", '', lead_clean)
        lead_clean = re.sub(r'\n+', '\n', lead_clean).strip()
        
        # 2. Extract Items from {{ItemTable/Data|...}}
        items = []
        item_matches = re.findall(r'\{\{ItemTable/Data\|([^}]+)\}\}', wikitext)
        for im in item_matches:
            parts = [p.strip() for p in im.split("|")]
            if len(parts) >= 3:
                items.append({
                    "internal_id": parts[0],
                    "quantity": parts[1] if len(parts) > 1 else "1",
                    "name": parts[2] if len(parts) > 2 else parts[0],
                    "location_details": parts[3] if len(parts) > 3 else ""
                })
                
        # 3. Detect Critical Warnings (Missable, Karma, Glitches)
        missable_warnings = []
        if "permanently miss" in wikitext.lower():
            missable_warnings.append("WARNING: Contains permanently missable triggers!")
        if "karma" in wikitext.lower():
            missable_warnings.append("NOTE: Contains actions that alter player Karma.")
            
        parsed_result = {
            "title": clean_title,
            "url": f"https://infinitefusion.fandom.com/wiki/{clean_title}",
            "lead_summary": lead_clean,
            "missable_warnings": missable_warnings,
            "items": items,
            "sections": [s.get("line") for s in sections],
            "raw_wikitext": wikitext
        }
        
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(parsed_result, f, indent=2, ensure_ascii=False)
            
        print(f"SUCCESS: Cached '{clean_title}' ({len(items)} items, {len(sections)} sections) to {cache_file}")
        return parsed_result
        
    except Exception as e:
        print(f"Exception fetching {clean_title}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        target = sys.argv[1]
        fetch_wiki_page(target, force_refresh=True)
    else:
        print("Usage: python fetch_wiki_knowledge.py <Page_Name>")
