#!/usr/bin/env python3
"""
scripts/test_all_chapters.py - Comprehensive Multi-Chapter Verification Suite
Executes the 6-Gate TDD Verification Suite across all chapters in the walkthrough.
Exits 0 if all chapters pass cleanly, 1 if any gate fails.
"""

import os
import sys
import glob
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts"))

from verify_chapter import verify_chapter

def run_suite():
    chapters_dir = BASE_DIR / "chapters"
    specs_dir = BASE_DIR / "specs"
    
    chapter_dirs = sorted([d for d in chapters_dir.iterdir() if d.is_dir() and d.name.startswith("ch")])
    
    total = len(chapter_dirs)
    passed_count = 0
    failures = {}
    
    print("=" * 68)
    print("  POKÉMON INFINITE FUSION - COMPREHENSIVE 6-GATE TDD TEST SUITE")
    print("=" * 68)
    
    for ch_path in chapter_dirs:
        ch_id = ch_path.name
        spec_path = specs_dir / f"spec_{ch_id}.json"
        
        if not spec_path.exists():
            print(f"[{ch_id.upper()}] MISSING SPEC: {spec_path}")
            failures[ch_id] = [f"Missing spec file: {spec_path}"]
            continue
            
        passed, errs = verify_chapter(str(spec_path), str(ch_path))
        if passed:
            print(f"  ✓ {ch_id.upper()}: PASSED (All 6 Gates Verified Clean)")
            passed_count += 1
        else:
            print(f"  ✗ {ch_id.upper()}: FAILED ({len(errs)} gate violations)")
            failures[ch_id] = errs
            
    print("=" * 68)
    print(f"  SUMMARY: {passed_count}/{total} chapters passed.")
    print("=" * 68)
    
    if failures:
        print("\nDETAILED VIOLATIONS:")
        for ch_id, err_list in failures.items():
            print(f"\n--- [{ch_id.upper()}] ---")
            for e in err_list:
                print(f"  • {e}")
        return False
    else:
        print("\nAll chapters certified 100% compliant with Game Ground Truth!")
        return True

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
