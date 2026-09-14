"""
Pokémon Infinite Fusion Ground Truth Oracle & Fact-Checking CLI
Instant lookup tool for agents and developers to query authoritative local
game code, MediaWiki caches, and quest registries before writing chapter content.
"""

import os
import sys
import json
import argparse
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "scripts"))
from pif_utils import normalize_route_slug, get_wiki_filepath

DATA_DIR = os.path.join(BASE_DIR, "data")
QUESTS_FILE = os.path.join(DATA_DIR, "quests", "master_quests.json")
DIVERGENCE_FILE = os.path.join(DATA_DIR, "references", "infinite_fusion_differences.md")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def query_route(route_name):
    slug = normalize_route_slug(route_name)
    wiki_path = get_wiki_filepath(BASE_DIR, route_name)
    
    print(f"\n=================================================================")
    print(f" GROUND TRUTH: {route_name.upper()} (Canonical: {slug}.json)")
    print(f"=================================================================")
    
    if not os.path.exists(wiki_path):
        print(f"❌ Wiki cache not found at: {wiki_path}")
        print(f"Run: python scripts/test_wiki_coverage.py --fetch-missing")
        return
        
    w_data = load_json(wiki_path)
    
    # 1. Lead Summary
    lead = w_data.get("lead_summary", "").strip()
    print(f"\n📖 [CANONICAL WIKI SUMMARY]")
    if lead:
        print(lead)
    else:
        print("No lead summary extracted.")
        
    # 2. Key Items on Route
    items = w_data.get("items", [])
    print(f"\n🎒 [ITEMS & GIFTS ({len(items)} found)]")
    for it in items[:12]:
        name = it.get("name", "Unknown")
        loc = it.get("location_details", "")
        print(f"  • {name}: {loc}")
    if len(items) > 12:
        print(f"  ... and {len(items) - 12} more items")
        
    # 3. Quests & Missables on this Route
    quests = load_json(QUESTS_FILE).get("quests", [])
    route_quests = []
    for q in quests:
        q_loc = q.get("location", "").lower()
        if route_name.lower() in q_loc or slug.lower() in q_loc.replace(" ", "_"):
            route_quests.append(q)
            
    print(f"\n📜 [REGISTERED QUESTS & EVENTS ({len(route_quests)} found)]")
    if route_quests:
        for q in route_quests:
            is_miss = q.get("is_missable", False)
            miss_tag = "⚠️ PERMANENTLY MISSABLE" if is_miss else "✅ Non-Missable"
            print(f"  • [{q.get('type')}] {q.get('title')} ({miss_tag})")
            if is_miss:
                print(f"    - DEADLINE: {q.get('missable_deadline')}")
            print(f"    - Objective: {q.get('objectives', [''])[0]}")
    else:
        print("  No registered master quests found for this location.")
        
    # 4. Special Divergence Precedents
    norm_lower = route_name.lower()
    if "anne" in norm_lower:
        print(f"\n🚨 [SPECIAL DIVERGENCE ALERT: S.S. ANNE]")
        print(f"  • The S.S. Anne NEVER leaves port in Infinite Fusion.")
        print(f"  • Remains permanently docked in Vermilion City for cabin healing and quests.")
    elif "vermilion" in norm_lower or "vermillion" in norm_lower:
        print(f"\n🚨 [SPECIAL DIVERGENCE ALERT: VERMILION CITY]")
        print(f"  • Shears (Cut Tool) are obtained in Route 2 Before Forest via Diglett's Cave.")
        print(f"  • Building Materials Quest at construction site is missable before Elite Four.")
        print(f"  • Thunder Badge allows Teleport move to act as Fly fast-travel!")

def list_missables():
    print(f"\n=================================================================")
    print(f" CLOSED REGISTRY OF AUTHORITATIVE PERMANENTLY MISSABLE EVENTS")
    print(f" Source: data/quests/master_quests.json")
    print(f"=================================================================")
    quests = load_json(QUESTS_FILE).get("quests", [])
    missables = [q for q in quests if q.get("is_missable")]
    
    print(f"Found {len(missables)} total missable events across Kanto/Johto:\n")
    for q in missables:
        print(f"⚠️ [{q.get('id')}] {q.get('title')}")
        print(f"   Location: {q.get('location')}")
        print(f"   Chapter: {q.get('chapter_introduced')} (Resolvable: {q.get('chapter_resolvable')})")
        print(f"   Deadline: {q.get('missable_deadline')}")
        print(f"   Reward: {', '.join(q.get('rewards', []))}")
        print(f"   Notes: {q.get('objectives', [''])[-1]}\n")

def check_statement(text: str):
    print(f"\n=================================================================")
    print(f" ANTI-VANILLA FACT-CHECKER")
    print(f" Testing: \"{text}\"")
    print(f"=================================================================")
    
    t_lower = text.lower()
    violations = []
    
    def has_affirmative_match(pattern, text):
        for m in re.finditer(pattern, text):
            # Inspect preceding 40 characters for negation
            start_idx = max(0, m.start() - 40)
            prefix = text[start_idx:m.start()].lower()
            if any(neg in prefix for neg in ["not ", "never ", "doesn't ", "does not ", "won't ", "no "]):
                continue
            return True
        return False

    # Check 1: S.S. Anne Departure claim
    if has_affirmative_match(r'\b(ship (will )?depart|ship (will )?leave|leaves port|sails away|ship departs)\b', t_lower):
        violations.append("FALSE CLAIM: S.S. Anne does NOT leave port in Infinite Fusion! It stays permanently moored.")
        
    # Check 2: Friendship evolution claim
    if has_affirmative_match(r'\b(friendship evolution|happiness evolution|requires high friendship|requires high happiness)\b', t_lower):
        violations.append("FALSE CLAIM: Friendship evolutions are completely eliminated in Infinite Fusion (replaced with static level thresholds).")
        
    # Check 3: Trade evolution at 37
    if has_affirmative_match(r'\b(evolves? at (level )?37|trade evolution at 37)\b', t_lower):
        violations.append("FALSE CLAIM: Trade evolutions in Infinite Fusion evolve at Level 40 or via Linking Cord (not Level 37).")
        
    # Check 4: HM Slave instruction
    if has_affirmative_match(r'\b(hm slave|cut slave|flash slave)\b', t_lower):
        violations.append("PROHIBITED INSTRUCTION: Infinite Fusion eliminates HM slaves with 9 reusable Key Item tools.")
        
    if violations:
        print(f"❌ FAIL: {len(violations)} Ground Truth Violation(s) detected:")
        for v in violations:
            print(f"  • {v}")
        return False
    else:
        print("✅ PASS: No vanilla hallucination patterns detected.")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query ground truth databases")
    parser.add_argument("--route", help="Route or location name to query")
    parser.add_argument("--missables", action="store_true", help="List all authoritative missables")
    parser.add_argument("--check", help="Statement to check against anti-vanilla database")
    args = parser.parse_args()
    
    if args.route:
        query_route(args.route)
    elif args.missables:
        list_missables()
    elif args.check:
        check_statement(args.check)
    else:
        parser.print_help()
