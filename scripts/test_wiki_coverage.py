"""
Automated Wiki Knowledge Cache Coverage Test
Validates that all routes and key locations referenced across chapter specs
have an authoritative, non-empty, valid JSON cache in data/wiki/.
Supports auto-fetching via --fetch-missing.
"""

import os
import sys
import json
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(BASE_DIR, "data", "wiki")
SPECS_DIR = os.path.join(BASE_DIR, "specs")
sys.path.append(os.path.join(BASE_DIR, "scripts"))
from fetch_wiki_knowledge import fetch_wiki_page
from pif_utils import normalize_route_slug

def normalize_page_name(route_name):
    return normalize_route_slug(route_name)

def test_wiki_coverage(fetch_missing=False):
    errors = []
    checked_pages = set()
    
    # 1. Collect routes from all specs in specs/
    spec_files = glob.glob(os.path.join(SPECS_DIR, "spec_*.json"))
    for sf in spec_files:
        with open(sf, "r", encoding="utf-8") as f:
            data = json.load(f)
            routes = data.get("routes_covered", [])
            for r in routes:
                p_name = normalize_page_name(r)
                checked_pages.add(p_name)
                
    # 2. Add essential core systems
    checked_pages.update([
        "Quests_(Kanto)",
        "Karma",
        "Fusion_FAQs"
    ])
    
    missing = []
    invalid = []
    
    for page in sorted(checked_pages):
        cache_file = os.path.join(WIKI_DIR, f"{page}.json")
        if not os.path.exists(cache_file):
            if fetch_missing:
                print(f"Auto-fetching missing wiki page: '{page}'...")
                res = fetch_wiki_page(page)
                if not res:
                    missing.append(page)
            else:
                missing.append(page)
        else:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                if not c_data.get("sections") and not c_data.get("items") and not c_data.get("lead_summary"):
                    invalid.append(f"{page} (empty payload)")
            except Exception as e:
                invalid.append(f"{page} (corrupted JSON: {e})")
                
    if missing:
        errors.append(f"MISSING WIKI CACHE ({len(missing)} pages): {', '.join(missing)}")
    if invalid:
        errors.append(f"INVALID WIKI CACHE ({len(invalid)} pages): {', '.join(invalid)}")
        
    passed = (len(errors) == 0)
    return passed, checked_pages, errors

if __name__ == "__main__":
    fetch = "--fetch-missing" in sys.argv
    passed, checked, errs = test_wiki_coverage(fetch_missing=fetch)
    print(f"=== Wiki Knowledge Cache Coverage Test ===")
    print(f"Total Canonical Pages Audited: {len(checked)}")
    
    if passed:
        print("PASS: 100% of required chapter routes and systems have authoritative local wiki caches.")
        sys.exit(0)
    else:
        print(f"FAIL: {len(errs)} coverage violations detected:")
        for e in errs:
            print(f"  • {e}")
        if not fetch:
            print("\nTip: Run with --fetch-missing to automatically retrieve missing pages.")
        sys.exit(1)
