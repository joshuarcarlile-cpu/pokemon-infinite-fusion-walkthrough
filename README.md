# Pokémon Infinite Fusion Walkthrough & Offline Dashboard

A complete, test-driven walkthrough and interactive companion dashboard for **Pokémon Infinite Fusion** (Classic Mode, Hard Mode Level Caps).

---

## Project Structure

```text
Pokemon IF Walkthrough/
├── chapters/
│   ├── ch01/                      # Act 1 - Segment 1: Boulder Badge (Brock)
│   └── ch02/                      # Act 1 - Segment 2: Cascade Badge (Misty)
├── data/
│   ├── encounters/kanto/          # Partitioned 2 KB route encounter slices
│   ├── items/                     # 9 HM replacements, key items, static encounters
│   ├── mechanics/                 # Decrypted learnsets, base stats, custom TMs, evolution methods
│   ├── quests/                    # Master quests (31 Kanto quests, Rocket double-agent, missables)
│   ├── trainers_classic.json      # 687 Decrypted Classic Mode trainers
│   ├── trainers_expert.json       # 650 Decrypted Expert Mode trainers
│   └── wiki/                      # Authoritative local cache of canonical MediaWiki API articles
├── specs/                         # TDD Chapter Test Contracts (spec_chXX) & Preflight Manifests
├── scripts/
│   ├── preflight_chapter.py       # Context manifest generator (routes, bosses, quests, missables)
│   ├── fusion_calc.py             # Deterministic asymmetric stats, dual typing & legal moves engine
│   ├── learnset_lookup.py         # Move legality lookup by level cap
│   ├── scaffold_chapter.py        # Ultra-sliced chapter directory scaffolder
│   ├── assemble_chapter.py        # Validates and bundles sliced sub-files into unified chapter
│   ├── verify_chapter.py          # Automated 5-Gate TDD test linter
│   ├── test_wiki_coverage.py      # Audits local wiki knowledge caches
│   └── compile_dashboard.py       # Standalone compiler generating dist/index.html
├── src/
│   └── template.html              # Reactive, zero-dependency Second-Screen Companion UI
└── dist/
    └── index.html                 # Standalone, offline HTML Dashboard (166.7 KB)
```

---

## Core Systems & Information Truth Standards

### 1. Three Starter Tracks (Dynamic & Evolving Fusions)
Every chapter tracks three distinct starter progression tracks, featuring accessible, evolving fusions from early route catches rather than rigid Best-in-Slot clones:
* **Team Bulbasaur**: Grass momentum, sleep & Leech Seed attrition, aerial tanks (`Ivysaur/Pidgeotto`).
* **Team Charmander**: High-velocity physical and special wallbreakers (`Charmeleon/Kadabra`, `Butterfree/Beedrill`).
* **Team Squirtle**: Bulky defensive pivots, Water/Grass/Steel tanks (`Wartortle/Tangela`).

### 2. Team Species Clause (Zero Duplicates Rule)
No single starter team roster may feature duplicate Pokémon species or members of the same evolutionary family across its 6 active slots, nor on its flex bench. Fusions count both Head and Body evolutionary lines. Cross-team sharing between different starter paths is permitted (e.g. both Team Bulbasaur and Team Charmander can catch a Pidgey), but within any given team, each species line may only appear once.

### 3. Formalized Gym Duelist Rule (Party Size Limits)
In Hard Mode, Gym Leader battles enforce equal party sizes:
* **Brock & Misty**: Strict 2 vs 2
* **Lt. Surge & Erika**: Strict 3 vs 3
* **Koga, Sabrina & Blaine**: Strict 4 vs 4
* **Giovanni**: Strict 5 vs 5
Every team roster defines its **Top Duelists** (`gym_duel_core: [1, 2]`) with gold `⭐ GYM DUELIST` badges and strategic duel rationale.

### 4. Mechanically Hardened Evolution Methods
* **Trade Evolutions**: Evolve naturally at **Level 40** (or via Linking Cord directly from Bag).
* **Happiness Elimination**: Friendship is replaced by static level thresholds (Babies at Lv. 15, Buneary at Lv. 25, Riolu at Lv. 30, Golbat at Lv. 40, Chansey at Lv. 42).
* **9 HM Replacements**: Replaces all HM field moves (Shears at Route 2 Before Forest via Diglett's Cave; Lantern after 10 Hotel Quests; Teleport field move after Badge 3).

### 5. Interactive Second-Screen Dashboard (`dist/index.html`)
* **Sticky Chapter Subnav**: Instant quick-jump pills for every route and gym duel.
* **Chapter Completion HUD**: Real-time counter of route pickups, trainers, caught Pokémon, and dynamic progress meter.
* **Global Catch Tracker**: Checkbox catch tracking synchronized document-wide with Time-of-Day and `Uncaught Only` filtering.
* **Quests & Missables Drawer**: Tracks 31+ sidequests, Hotel quest milestones, and Team Rocket undercover informant double-agent progression (+10 Karma per police report, Mythical Diancie raid).
* **Zero Dependencies**: 100% offline, local storage persisted, with 1-click JSON export/import backups.
