"""
Automated Ground Truth & Anti-Vanilla Static Analysis Auditor
Audits chapter payloads, files, and markdown text against authoritative game data:
1. Anti-Vanilla Hallucination Checks (affirmative polarity regex for S.S. Anne departure,
   friendship evolutions, level 37 trade evolutions, HM slaves).
2. Missable Integrity Check: Any event claimed as permanently missable MUST be registered
   in data/quests/master_quests.json with is_missable: true.
"""

import os
import sys
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
QUESTS_FILE = os.path.join(DATA_DIR, "quests", "master_quests.json")

def load_master_missables():
    if not os.path.exists(QUESTS_FILE):
        return {}
    with open(QUESTS_FILE, "r", encoding="utf-8") as f:
        quests = json.load(f).get("quests", [])
    # Map lowercase keywords / titles / IDs to quest object
    missable_registry = {}
    for q in quests:
        if q.get("is_missable"):
            q_id = q.get("id", "").lower()
            q_title = q.get("title", "").lower()
            missable_registry[q_id] = q
            missable_registry[q_title] = q
            # Also index by key phrases
            if "secret_garden" in q_id:
                missable_registry["secret garden"] = q
            elif "rocket" in q_id:
                missable_registry["team rocket"] = q
                missable_registry["rocket"] = q
            elif "building_materials" in q_id:
                missable_registry["building materials"] = q
    return missable_registry

def has_affirmative_match(pattern, text):
    for m in re.finditer(pattern, text, re.IGNORECASE):
        # Inspect preceding 40 characters for negation
        start_idx = max(0, m.start() - 40)
        prefix = text[start_idx:m.start()].lower()
        if any(neg in prefix for neg in ["not ", "never ", "doesn't ", "does not ", "won't ", "no "]):
            continue
        return True, m.group(0)
    return False, None

def audit_text_content(text: str, context_label: str = "Chapter"):
    """
    Audits a string of text (e.g. JSON dump of chapter or markdown) for ground truth violations.
    Returns (passed, errors)
    """
    errors = []
    t_lower = text.lower()
    
    # 1. Anti-Vanilla Traps
    # Check A: S.S. Anne Departure claim
    found, match_str = has_affirmative_match(r'\b(ship (will )?depart|ship (will )?leave|leaves port|sails away|ship departs)\b', text)
    if found:
        errors.append(f"GROUND TRUTH VIOLATION ({context_label}): Found false assertion '{match_str}'. S.S. Anne NEVER leaves port in Infinite Fusion!")
        
    # Check B: Friendship evolution claim
    found, match_str = has_affirmative_match(r'\b(friendship evolution|happiness evolution|requires high friendship|requires high happiness)\b', text)
    if found:
        errors.append(f"GROUND TRUTH VIOLATION ({context_label}): Found false assertion '{match_str}'. Friendship evolutions are completely eliminated in Infinite Fusion.")
        
    # Check C: Trade evolution at 37
    found, match_str = has_affirmative_match(r'\b(evolves? at (level )?37|trade evolution at 37)\b', text)
    if found:
        errors.append(f"GROUND TRUTH VIOLATION ({context_label}): Found false assertion '{match_str}'. Trade evolutions evolve at Level 40 or via Linking Cord (not Level 37).")
        
    # Check D: HM Slave instruction
    found, match_str = has_affirmative_match(r'\b(hm slave|cut slave|flash slave)\b', text)
    if found:
        errors.append(f"GROUND TRUTH VIOLATION ({context_label}): Prohibited instruction '{match_str}'. Infinite Fusion eliminates HM slaves with 9 reusable Key Item tools.")

    # 2. Missable Claims Verification
    # Search for any warning claiming something is permanently missable
    missable_registry = load_master_missables()
    # Find patterns like "permanently missable", "missable trigger", "missable alert"
    missable_matches = re.finditer(r'(?:permanently missable|missable warning|missable alert)[:\s\-]+([^\n\.\,\!\<\>]{4,80})', text, re.IGNORECASE)
    for mm in missable_matches:
        claim_snippet = mm.group(1).strip().lower()
        # Verify that this snippet matches at least one registered missable
        matches_any = any(k in claim_snippet for k in missable_registry.keys())
        # Check special case: if claim explicitly mentions false claims like "s.s. anne"
        if "anne" in claim_snippet:
            errors.append(f"GROUND TRUTH VIOLATION ({context_label}): Claimed '{mm.group(0)}' is false! S.S. Anne is permanently moored and not missable.")
        elif not matches_any:
            errors.append(
                f"UNVERIFIED MISSABLE WARNING ({context_label}): Found missable claim '{mm.group(0)}'. "
                f"This event is NOT registered as a verified missable in data/quests/master_quests.json!"
            )
            
    return (len(errors) == 0), errors

def audit_chapter_target(target_path):
    if os.path.isdir(target_path):
        # Scan all JSON files in chapter directory
        all_text = ""
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".json") or file.endswith(".md"):
                    with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                        all_text += f.read() + "\n"
        return audit_text_content(all_text, os.path.basename(target_path))
    elif os.path.isfile(target_path):
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return audit_text_content(content, os.path.basename(target_path))
    else:
        return False, [f"Target path not found: {target_path}"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit_ground_truth.py <chapter_dir_or_file>")
        sys.exit(1)
        
    target = sys.argv[1]
    passed, errors = audit_chapter_target(target)
    if passed:
        print(f"PASS: Ground truth audit verified for {target}. Zero vanilla hallucinations or false missables.")
        sys.exit(0)
    else:
        print(f"FAIL: {len(errors)} Ground Truth Violation(s) in {target}:")
        for err in errors:
            print(f"  • {err}")
        sys.exit(1)
