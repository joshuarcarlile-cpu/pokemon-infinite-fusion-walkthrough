---
name: pif-walkthrough-engine
description: >-
  Standard operating procedure for authoring, auditing, and compiling chapters for the
  Pokémon Infinite Fusion Walkthrough and Standalone Offline HTML Dashboard. Use whenever
  creating or modifying walkthrough segments, route encounters, boss strategy cards, or
  the 3-starter team rosters.
---

# Pokémon Infinite Fusion Walkthrough Engine

This skill guides agents through the standardized 7-stage micro-pipeline for building authoritative, test-driven walkthrough chapters for *Pokémon Infinite Fusion* (Classic Mode, Hard Mode Level Caps).

---

## The 7-Stage Chapter Production Pipeline

```mermaid
flowchart LR
    S0["0. Preflight<br/>(preflight_chapter.py)"] --> S1["1. Scaffold<br/>(scaffold_chapter.py)"]
    S1 --> S2["2. Populate Slices<br/>(phases & teams)"]
    S2 --> S3["3. Move Legality<br/>(learnset_lookup.py)"]
    S3 --> S4["4. Assemble<br/>(assemble_chapter.py)"]
    S4 --> S5["5. Audit (5 Gates)<br/>(verify_chapter.py)"]
    S5 --> S6["6. Compile<br/>(compile_dashboard.py)"]
```

### Stage 0: Preflight Context Pack Generation
Before writing any chapter, pull canonical route encounters, decrypted boss rosters, items, quests, and local wiki caches into a single consolidated manifest:
```bash
python scripts/test_wiki_coverage.py --fetch-missing
python scripts/preflight_chapter.py specs/spec_<ch_id>.json
```
This writes `specs/manifest_<ch_id>.json` containing exact wild spawn rates, boss moves, active quests, and missable alerts so the agent never hallucinates.

### Stage 0.5: Ground Truth & Divergence Audit
Audit the routes against the master divergence reference and query tool:
```bash
python scripts/query_ground_truth.py --route "<Route_Name>"
```
Verify:
- Are there any false vanilla assumptions (e.g. S.S. Anne departure, happiness evolutions, HM slaves)?
- Check `data/references/infinite_fusion_differences.md` for known divergences.
- Confirm any planned missable alerts match `master_quests.json` with `is_missable: true`.

### Stage 1: Scaffold Segment
Run `scaffold_chapter.py` to create the ultra-sliced folder layout:
```bash
python scripts/scaffold_chapter.py <ch_id> --cap <level_cap> --duel-limit <duel_limit> --act <act_num>
```
This generates:
- `chapters/<ch_id>/meta.json`
- `chapters/<ch_id>/boss.json`
- `chapters/<ch_id>/phases/`
- `chapters/<ch_id>/teams/`

### Stage 2: Ingest Route Slices & Boss Details
1. Read the relevant route slice files from `data/encounters/kanto/` (only 1.5–2 KB per file) or `specs/manifest_<ch_id>.json`.
2. Populate the chronological phase files in `chapters/<ch_id>/phases/` with pickups, trainers, wild tables, and navigation warnings.
3. Populate `chapters/<ch_id>/boss.json` with:
   - Gym leader team, levels, abilities, and movesets.
   - `gym_duel_limit`: Strict party size cap matching leader (Brock 2, Misty 2, Surge 3, Erika 3, Koga 4, Sabrina 4, Blaine 4, Giovanni 5).
   - Sturdy ability warnings and AI switch behavior.
   - Turn-by-turn counter plans.

### Stage 3: Populate 3-Starter Teams & Verify Move Legality
Every chapter tracks **Three Starter Paths** under the **Evolving Starter Core Framework**:
1. `teams/team_bulbasaur.json` (Grass Momentum & Status Control)
2. `teams/team_charmander.json` (Hyper-Offense & Wallbreaker)
3. `teams/team_squirtle.json` (Bulky Balance & Regenerator Pivot)

Each team file must define:
- **Starter Anchor (Slot 1)**: The starter line is the sole permanent member across all chapters.
- **Dynamic Threshold Squad**: Party size scales naturally ($\ge \text{Gym Duel Limit}$ up to 6 members), tuned for the upcoming Gym Leader. No dummy "Upcoming" placeholders.
- **`gym_duel_core`**: Array of exact active slot numbers (e.g. `[1, 2]`) chosen to enter the gym arena under the `gym_duel_limit`, plus `gym_duel_rationale`.
- **Team Species Clause (Zero Duplicates)**: Zero duplicate species or evolutionary family members across active slots and the flex bench. Cross-team sharing between different starter paths is fully allowed.
- **Creative Accessible Fusions**: Showcase dynamic fusions from route catches (e.g., `Butterfree/Beedrill`, `Mankey/Spearow`, `Charmeleon/Kadabra`, `Wartortle/Tangela`).
- **`current_reached_moveset`**: Exactly 4 moves legally reachable at or below the Cap.
- **`ability` & `held_item`**: Fully specified for all active members.
- **Flex Bench (2–3 Mons)**: Situational tech choices (with zero duplicate families of active members).
- **`fusion_lifecycle`**: Clear guidance on *Active Splices*, *Mart Unfuse ($300)*, and *Next Chapter Splices*.

**MANDATORY MOVE LEGALITY AUDIT**:
Before saving any move into `current_reached_moveset`, verify legal reachability:
```bash
python scripts/learnset_lookup.py <Species> <Level_Cap>
```
For fusions, calculate base stats, abilities, and legal dual movepool with:
```bash
python scripts/fusion_calc.py <Head_Species> <Body_Species> --cap <Level_Cap>
```

### Stage 4: Assemble Chapter
Bundle and validate the modular files into a compiled chapter object:
```bash
python scripts/assemble_chapter.py <ch_id>
```

### Stage 5: Run 6-Gate Automated Linter
Audit the chapter against its TDD specification and ground-truth rules:
```bash
python scripts/verify_chapter.py specs/spec_<ch_id>.json chapters/<ch_id>/
```
Must satisfy all 6 Gates:
- **Gate 1**: Hard Mode Level Cap ($\le \text{Cap}$) & Gym Duel Limit.
- **Gate 2**: Classic Mode wild spawns only (no Modern/Remix).
- **Gate 3**: Tool sequence constraints (no premature HM tool instructions).
- **Gate 4**: 3 Starter teams ($\ge \text{Gym Duel Limit}$ slots, starter as permanent anchor, 4 reached moves $\le$ Cap, dual-species legal moves, `gym_duel_core` validation, and Team Species Clause zero-duplicate enforcement across roster & bench).
- **Gate 5**: Ground Truth & Missables Integrity (all missables registered in `master_quests.json`, zero vanilla hallucinations, and route wiki caches present).
- **Gate 6**: Team Chronological Species Obtainability & Evolution Legality (every roster and bench species must belong to an evolutionary family obtainable by that chapter; evolution levels must not exceed the Cap; trade/stone evolutions must have obtainable trigger items).

To verify all chapters across the entire guide at once:
```bash
python scripts/test_all_chapters.py
```

Must result in: `PASS: 100% assertions verified. Chapter certified clean.`

### Stage 6: Compile Dashboard
Inject all verified chapters into the standalone offline dashboard:
```bash
python scripts/compile_dashboard.py
```
Verify that `dist/index.html` builds with 0 errors.
