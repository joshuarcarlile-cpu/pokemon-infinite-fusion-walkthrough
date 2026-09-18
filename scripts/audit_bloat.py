#!/usr/bin/env python3
"""
scripts/audit_bloat.py - Automated Bloat Prevention & Architecture Linter

Enforces file size budgets, dead-field pruning, bundle limits, and root hygiene
across the Pokémon Infinite Fusion Walkthrough repository.

Exit codes:
  0: All gates passed cleanly (or with standard informational notices)
  1: One or more bloat or hygiene violations detected
"""

import os
import sys
import json
from pathlib import Path

# Safe Windows stdout encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent

# Gate Budgets (in bytes)
BUDGETS = {
    "phase_target": 2560,    # 2.5 KB
    "phase_max": 4096,       # 4.0 KB
    "team_target": 4608,     # 4.5 KB
    "team_max": 6144,        # 6.0 KB
    "boss_target": 4096,     # 4.0 KB
    "boss_max": 5632,        # 5.5 KB
    "meta_target": 1024,     # 1.0 KB
    "meta_max": 2048,        # 2.0 KB
    "dist_bundle_max": 550000, # 550 KB (Dual-Mode Bundle)
    "manifest_warn": 80000,  # 80 KB
}

DEAD_FIELDS = {
    "target_fusion",
    "target_types",
    "final_target_moveset",
    "endgame_roadmap",
}

ALLOWED_ROOT_FILES = {
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "PokemonInfiniteFusion-Launcher_1.1 (1).exe",
}

ALLOWED_ROOT_DIRS = {
    ".agents",
    ".git",
    "chapters",
    "data",
    "dist",
    "IF GAME",
    "scratch",
    "scripts",
    "specs",
    "src",
}


def scan_for_dead_fields(data, path=""):
    """Recursively search for deprecated/dead fields in parsed JSON data."""
    found = []
    if isinstance(data, dict):
        for k, v in data.items():
            curr_path = f"{path}.{k}" if path else k
            if k in DEAD_FIELDS:
                found.append(curr_path)
            found.extend(scan_for_dead_fields(v, curr_path))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            found.extend(scan_for_dead_fields(item, f"{path}[{idx}]"))
    return found


def main():
    print("==================================================================")
    print("  POKÉMON INFINITE FUSION - BLOAT & HYGIENE AUDIT SUITE")
    print("==================================================================")
    
    errors = []
    warnings = []

    # ------------------------------------------------------------------
    # Gate 1: Root Directory Hygiene
    # ------------------------------------------------------------------
    print("\n[Gate 1] Auditing Root Directory Hygiene...")
    root_items = list(ROOT_DIR.iterdir())
    for item in root_items:
        rel_name = item.name
        if item.is_dir():
            if rel_name not in ALLOWED_ROOT_DIRS and not rel_name.startswith("."):
                warnings.append(f"Unexpected directory in root: {rel_name}")
        else:
            if rel_name not in ALLOWED_ROOT_FILES:
                if rel_name.endswith((".txt", ".tmp", ".dump", ".py", ".json")):
                    errors.append(f"Root clutter detected: {rel_name} (must be in scripts/ or data/)")
                else:
                    warnings.append(f"Uncategorized file in root: {rel_name}")
    
    if not any("Root clutter" in e for e in errors):
        print("  ✓ Root directory clean and free of rogue dumps/scripts.")

    # ------------------------------------------------------------------
    # Gate 2: Chapter Sliced Architecture & File Size Budgets
    # ------------------------------------------------------------------
    print("\n[Gate 2] Auditing Sliced Architecture & File Size Budgets...")
    chapters_dir = ROOT_DIR / "chapters"
    if chapters_dir.exists():
        chapter_folders = sorted([d for d in chapters_dir.iterdir() if d.is_dir() and d.name.startswith("ch")])
        for ch in chapter_folders:
            # Meta
            meta_file = ch / "meta.json"
            if meta_file.exists():
                size = meta_file.stat().st_size
                if size > BUDGETS["meta_max"]:
                    errors.append(f"{meta_file.relative_to(ROOT_DIR)} exceeds max limit: {size} B > {BUDGETS['meta_max']} B")
                elif size > BUDGETS["meta_target"]:
                    warnings.append(f"{meta_file.relative_to(ROOT_DIR)} exceeds target: {size} B > {BUDGETS['meta_target']} B")

            # Boss (Classic & Remix)
            for b_name in ["boss.json", "boss_remix.json"]:
                b_file = ch / b_name
                if b_file.exists():
                    size = b_file.stat().st_size
                    if size > BUDGETS["boss_max"]:
                        errors.append(f"{b_file.relative_to(ROOT_DIR)} exceeds max limit: {size} B > {BUDGETS['boss_max']} B")
                    elif size > BUDGETS["boss_target"]:
                        warnings.append(f"{b_file.relative_to(ROOT_DIR)} exceeds target: {size} B > {BUDGETS['boss_target']} B")

            # Phases (Classic & Remix)
            for p_dir_name in ["phases", "phases_remix"]:
                p_dir = ch / p_dir_name
                if p_dir.exists():
                    for p_file in sorted(p_dir.glob("*.json")):
                        size = p_file.stat().st_size
                        if size > BUDGETS["phase_max"]:
                            errors.append(f"{p_file.relative_to(ROOT_DIR)} exceeds max limit: {size} B > {BUDGETS['phase_max']} B")
                        elif size > BUDGETS["phase_target"]:
                            warnings.append(f"{p_file.relative_to(ROOT_DIR)} exceeds target: {size} B > {BUDGETS['phase_target']} B")

            # Teams (Classic & Remix)
            for t_dir_name in ["teams", "teams_remix"]:
                t_dir = ch / t_dir_name
                if t_dir.exists():
                    for t_file in sorted(t_dir.glob("*.json")):
                        size = t_file.stat().st_size
                        if size > BUDGETS["team_max"]:
                            errors.append(f"{t_file.relative_to(ROOT_DIR)} exceeds max limit: {size} B > {BUDGETS['team_max']} B")
                        elif size > BUDGETS["team_target"]:
                            warnings.append(f"{t_file.relative_to(ROOT_DIR)} exceeds target: {size} B > {BUDGETS['team_target']} B")

        print(f"  ✓ Audited {len(chapter_folders)} chapters across all micro-sliced components.")

    # ------------------------------------------------------------------
    # Gate 3: Dead-Field & Endgame Roadmap Pruning
    # ------------------------------------------------------------------
    print("\n[Gate 3] Auditing Schema Cleanliness (Zero Dead-Fields)...")
    dead_field_hits = 0
    if chapters_dir.exists():
        for json_path in chapters_dir.rglob("*.json"):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                dead = scan_for_dead_fields(content)
                if dead:
                    errors.append(f"Dead fields found in {json_path.relative_to(ROOT_DIR)}: {', '.join(dead)}")
                    dead_field_hits += len(dead)
            except Exception as e:
                errors.append(f"Failed to parse {json_path.relative_to(ROOT_DIR)}: {e}")
    
    if dead_field_hits == 0:
        print("  ✓ Zero dead fields detected in chapter schemas (no legacy roadmap bloat).")

    # ------------------------------------------------------------------
    # Gate 4: Standalone HTML Bundle Budget
    # ------------------------------------------------------------------
    print("\n[Gate 4] Auditing Distribution Bundle Budget...")
    dist_file = ROOT_DIR / "dist" / "index.html"
    if not dist_file.exists():
        errors.append("dist/index.html does not exist. Run scripts/compile_dashboard.py first.")
    else:
        dist_size = dist_file.stat().st_size
        print(f"  Current dist/index.html size: {dist_size:,} bytes (Budget: {BUDGETS['dist_bundle_max']:,} bytes)")
        if dist_size > BUDGETS["dist_bundle_max"]:
            errors.append(f"dist/index.html exceeds bundle budget: {dist_size:,} B > {BUDGETS['dist_bundle_max']:,} B")
        else:
            pct = (dist_size / BUDGETS["dist_bundle_max"]) * 100
            print(f"  ✓ Bundle healthy at {pct:.1f}% of allowable max limit.")

    # ------------------------------------------------------------------
    # Gate 5: Preflight Manifest Context Budget
    # ------------------------------------------------------------------
    print("\n[Gate 5] Auditing Preflight Context Manifest Sizes...")
    specs_dir = ROOT_DIR / "specs"
    if specs_dir.exists():
        manifests = sorted(specs_dir.glob("manifest_ch*.json"))
        for m in manifests:
            size = m.stat().st_size
            if size > BUDGETS["manifest_warn"]:
                warnings.append(f"{m.relative_to(ROOT_DIR)} is large ({size:,} B > {BUDGETS['manifest_warn']:,} B)")
            else:
                print(f"  ✓ {m.name}: {size:,} bytes")

    # ------------------------------------------------------------------
    # Audit Summary & Verdict
    # ------------------------------------------------------------------
    print("\n==================================================================")
    print("  AUDIT SUMMARY")
    print("==================================================================")
    if warnings:
        print(f"  ⚠️  NOTICES / WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"     - {w}")
    else:
        print("  ✓ No warnings.")

    if errors:
        print(f"\n  ❌ VIOLATIONS ({len(errors)}):")
        for e in errors:
            print(f"     - {e}")
        print("\n  VERDICT: FAILED (Bloat or architectural violations detected)")
        return 1
    else:
        print("\n  VERDICT: PASSED (Repository adheres to all lean architecture limits)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
