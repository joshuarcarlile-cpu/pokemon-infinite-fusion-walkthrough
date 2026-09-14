"""
Pokémon Infinite Fusion Chapter Assembler
Bundles and validates ultra-sliced sub-files in chapters/chXX/ into a unified chapter object:
- meta.json
- boss.json
- phases/*.json -> routes array
- teams/*.json -> teams dictionary
"""

import os
import sys
import json
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

def assemble_chapter(chapter_input):
    # Resolve directory path
    if os.path.isdir(chapter_input):
        ch_dir = os.path.abspath(chapter_input)
    else:
        ch_dir = os.path.join(CHAPTERS_DIR, chapter_input)
        
    if not os.path.exists(ch_dir) or not os.path.isdir(ch_dir):
        raise FileNotFoundError(f"Chapter directory not found: {ch_dir}")
        
    meta_path = os.path.join(ch_dir, "meta.json")
    boss_path = os.path.join(ch_dir, "boss.json")
    phases_dir = os.path.join(ch_dir, "phases")
    teams_dir = os.path.join(ch_dir, "teams")
    
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Missing meta.json in {ch_dir}")
        
    with open(meta_path, "r", encoding="utf-8") as f:
        chapter = json.load(f)
        
    # Ingest boss strategy
    if os.path.exists(boss_path):
        with open(boss_path, "r", encoding="utf-8") as f:
            chapter["boss_strategy"] = json.load(f)
            
    # Ingest chronological phases -> routes
    routes = []
    if os.path.exists(phases_dir):
        phase_files = sorted(glob.glob(os.path.join(phases_dir, "*.json")))
        for pf in phase_files:
            with open(pf, "r", encoding="utf-8") as f:
                p_data = json.load(f)
                if isinstance(p_data, list):
                    routes.extend(p_data)
                elif isinstance(p_data, dict):
                    # If phase defines multiple routes or single route
                    if "routes" in p_data:
                        routes.extend(p_data["routes"])
                    else:
                        routes.append(p_data)
    chapter["routes"] = routes
    
    # Ingest starter teams
    teams = {}
    if os.path.exists(teams_dir):
        for s_key in ["bulbasaur", "charmander", "squirtle"]:
            t_path = os.path.join(teams_dir, f"team_{s_key}.json")
            if os.path.exists(t_path):
                with open(t_path, "r", encoding="utf-8") as f:
                    teams[s_key] = json.load(f)
    chapter["teams"] = teams
    
    return chapter

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        ch_in = sys.argv[1]
        try:
            res = assemble_chapter(ch_in)
            print(f"SUCCESS: Assembled chapter '{res.get('chapter_id')}' with {len(res.get('routes', []))} routes and {len(res.get('teams', {}))} starter tracks.")
            if len(sys.argv) >= 3 and sys.argv[2] == "--json":
                print(json.dumps(res, indent=2))
        except Exception as e:
            print(f"ERROR assembling chapter: {e}")
            sys.exit(1)
    else:
        print("Usage: python assemble_chapter.py <ch_id_or_path> [--json]")
