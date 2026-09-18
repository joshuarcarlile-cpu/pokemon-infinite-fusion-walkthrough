"""
Organic Team Evolution & Moveset Currency Linter
Enforces that every starter track evolves organically across consecutive chapters:
- Must have >= 1 species/fusion delta (head or body changed), OR
- An updated moveset reflecting new level-up/TM legality at the higher cap, OR
- An explicit "no_change_rationale" justifying why the lineup was held.

Enforcement:
- Hard Gate on Remix teams (teams_remix/)
- Audit / Warning on Classic teams (teams/) during phased back-half refresh.
"""

import os
import sys
import glob
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

def load_json(p):
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def extract_team_signature(team_data):
    """
    Extracts a comparable signature from a team file:
    - Roster species (split into head/body components)
    - Reached movesets for all active members
    - no_change_rationale
    """
    if not team_data:
        return None
        
    roster = team_data.get("roster", [])
    members = []
    movesets = {}
    for slot in roster:
        sp = slot.get("species", "").strip()
        moves = tuple(sorted(slot.get("current_reached_moveset", [])))
        if sp:
            components = tuple(sp.split("/")) if "/" in sp else (sp,)
            members.append((sp, components))
            movesets[sp] = moves
            
    return {
        "species_list": [m[0] for m in members],
        "components": [m[1] for m in members],
        "movesets": movesets,
        "rationale": team_data.get("no_change_rationale", "").strip()
    }

def check_evolution(prev_sig, curr_sig):
    """
    Returns (is_evolved, reason):
    - True if species changed, component changed, moveset changed, or rationale provided.
    - False if identical roster, identical components, identical movesets, and no rationale.
    """
    if not prev_sig or not curr_sig:
        return True, "Initial chapter (no previous chapter to compare)"
        
    # Check for explicit rationale
    if curr_sig["rationale"]:
        return True, f"Explicit rationale provided: '{curr_sig['rationale']}'"
        
    # Check species list change (e.g. new member, removed member, different order)
    if prev_sig["species_list"] != curr_sig["species_list"]:
        return True, f"Roster delta detected ({prev_sig['species_list']} -> {curr_sig['species_list']})"
        
    # Check component delta (head or body changed)
    if prev_sig["components"] != curr_sig["components"]:
        return True, "Fusion component delta detected"
        
    # Check moveset currency (any move change across any member)
    moves_changed = False
    for sp, moves in curr_sig["movesets"].items():
        prev_moves = prev_sig["movesets"].get(sp)
        if prev_moves is not None and prev_moves != moves:
            moves_changed = True
            break
            
    if moves_changed:
        return True, "Moveset currency updated"
        
    return False, "Identical roster, identical fusion components, identical movesets, and missing 'no_change_rationale'."

def audit_evolution(mode="classic"):
    team_subfolder = "teams_remix" if mode == "remix" else "teams"
    ch_dirs = sorted([d for d in glob.glob(os.path.join(CHAPTERS_DIR, "ch*")) if os.path.isdir(d)])
    
    starters = ["bulbasaur", "charmander", "squirtle"]
    violations = []
    checked_transitions = 0
    
    prev_teams = {}
    
    for ch_dir in ch_dirs:
        cid = os.path.basename(ch_dir)
        t_dir = os.path.join(ch_dir, team_subfolder)
        
        # If remix and folder doesn't exist, skip (incremental rollout)
        if mode == "remix" and not os.path.exists(t_dir):
            continue
            
        curr_teams = {}
        for s in starters:
            t_file = os.path.join(t_dir, f"team_{s}.json")
            if os.path.exists(t_file):
                data = load_json(t_file)
                curr_teams[s] = extract_team_signature(data)
                
        if prev_teams:
            for s in starters:
                if s in prev_teams and s in curr_teams:
                    checked_transitions += 1
                    passed, reason = check_evolution(prev_teams[s], curr_teams[s])
                    if not passed:
                        violations.append({
                            "track": s,
                            "transition": f"{prev_cid} -> {cid}",
                            "error": reason
                        })
                        
        prev_teams = curr_teams
        prev_cid = cid
        
    return checked_transitions, violations

def main():
    print("==================================================================")
    print("  ORGANIC TEAM EVOLUTION & MOVESET CURRENCY AUDIT")
    print("==================================================================")
    
    # Check Remix (Hard Gate)
    rem_checked, rem_violations = audit_evolution("remix")
    print(f"\n[Remix Teams] Audited {rem_checked} transitions in teams_remix/...")
    if rem_violations:
        print(f"  ✗ FAIL: {len(rem_violations)} Remix transitions violate the Organic Evolution Rule:")
        for v in rem_violations:
            print(f"    • Track '{v['track']}' ({v['transition']}): {v['error']}")
    else:
        print(f"  ✓ PASS: All {rem_checked} Remix transitions exhibit organic progression.")
        
    # Check Classic (Phased Warning)
    cls_checked, cls_violations = audit_evolution("classic")
    print(f"\n[Classic Teams] Audited {cls_checked} transitions in teams/...")
    if cls_violations:
        print(f"  ⚠️ NOTICE: {len(cls_violations)} Classic transitions exhibit zero roster/moveset delta:")
        for v in cls_violations[:10]:
            print(f"    • Track '{v['track']}' ({v['transition']}): {v['error']}")
        if len(cls_violations) > 10:
            print(f"    ... and {len(cls_violations) - 10} more (scheduled for phased refresh).")
    else:
        print(f"  ✓ PASS: All {cls_checked} Classic transitions exhibit organic progression.")
        
    # Exit with code 1 if REMIX violations exist
    if rem_violations:
        sys.exit(1)
        
    print("\nVERDICT: Certified Clean.")
    sys.exit(0)

if __name__ == "__main__":
    main()
