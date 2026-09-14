"""
Pokémon Infinite Fusion Chapter Scaffolder
Generates atomic, sliced chapter folder structure and boilerplate JSON files (<= 2 KB each):
- meta.json
- boss.json
- phases/
- teams/ (team_bulbasaur.json, team_charmander.json, team_squirtle.json)
"""

import os
import sys
import json
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

def scaffold_chapter(chapter_id, cap, act, title, synopsis="", duel_limit=2):
    ch_dir = os.path.join(CHAPTERS_DIR, chapter_id)
    phases_dir = os.path.join(ch_dir, "phases")
    teams_dir = os.path.join(ch_dir, "teams")
    
    os.makedirs(phases_dir, exist_ok=True)
    os.makedirs(teams_dir, exist_ok=True)
    
    # 1. meta.json
    meta = {
        "chapter_id": chapter_id,
        "title": title or f"Act {act} - Segment: {chapter_id.upper()}",
        "act": act,
        "hard_mode_level_cap": cap,
        "synopsis": synopsis or f"Navigate the segment and overcome the gym challenge under Level {cap} Hard Mode cap."
    }
    with open(os.path.join(ch_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        
    # 2. boss.json
    boss = {
        "leader": "Gym Leader",
        "title": "Gym Leader",
        "badge": "Badge",
        "hard_mode_level_cap": cap,
        "gym_duel_limit": duel_limit,
        "recommended_party_level": cap - 1,
        "gym_trainers": [],
        "leader_team": [],
        "threat_analysis": "",
        "tactical_counter_plan": [],
        "rewards": []
    }
    with open(os.path.join(ch_dir, "boss.json"), "w", encoding="utf-8") as f:
        json.dump(boss, f, indent=2)
        
    # 3. teams boilerplate
    starters = [
        ("bulbasaur", "Bulbasaur", "Team Bulbasaur: Grass Momentum & Status Control", "Fast physical setup sweepers, sleep & Leech Seed attrition, Grass/Flying hybrid coverage."),
        ("charmander", "Charmander", "Team Charmander: Hyper-Offense & Fighting Wallbreakers", "High-velocity physical breakers, Mankey/Primeape low-kick counters, and Flying priority."),
        ("squirtle", "Squirtle", "Team Squirtle: Bulky Balance & Regenerator Pivot", "High physical defense, Tangela/Regenerator recovery cores, and Water/Ground/Steel pivots.")
    ]
    
    for s_key, s_name, t_name, arch in starters:
        team_data = {
            "starter": s_name,
            "name": t_name,
            "archetype": arch,
            "gym_duel_core": list(range(1, duel_limit + 1)),
            "gym_duel_rationale": "",
            "roster": [],
            "flex_bench": [],
            "fusion_lifecycle": {
                "active_fusions": [],
                "unfuse_recommendations": [],
                "upcoming_fusions": []
            }
        }
        with open(os.path.join(teams_dir, f"team_{s_key}.json"), "w", encoding="utf-8") as f:
            json.dump(team_data, f, indent=2)
            
    print(f"Scaffolded clean atomic chapter structure in {ch_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold sliced chapter folder")
    parser.add_argument("chapter_id", help="Chapter ID (e.g. ch01)")
    parser.add_argument("--cap", type=int, default=14, help="Hard Mode Level Cap")
    parser.add_argument("--duel-limit", type=int, default=2, help="Gym Duel Core Limit")
    parser.add_argument("--act", type=int, default=1, help="Act Number (1, 2, or 3)")
    parser.add_argument("--title", default="", help="Chapter title")
    parser.add_argument("--synopsis", default="", help="Chapter synopsis")
    args = parser.parse_args()
    
    scaffold_chapter(args.chapter_id, args.cap, args.act, args.title, args.synopsis, args.duel_limit)
