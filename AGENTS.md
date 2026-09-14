# Pokémon Infinite Fusion: Workspace Rules & Constraints

These rules are mandatory and automatically loaded for all Antigravity agents, subagents, and pair-programming sessions operating within this repository.

---

## 1. Non-Negotiable Game Standards & Information Truth
* **Classic Mode Only**: Encounters, trainer rosters, and item locations must strictly match **Classic Mode**. Modern Mode and Remix spawns are strictly prohibited.
* **Hard Mode Level Caps**: The gym leader level cap for each segment is an absolute upper bound:
  - No recommended party level may exceed the cap.
  - No Pokémon may evolve if its evolution level exceeds the cap (e.g. Starter Lv. 16 evolution is prohibited before Brock's Lv. 14 cap).
  - All moves in `current_reached_moveset` must be legally learnable at or below the cap via natural level-up, currently obtainable TMs, or currently available Move Tutors.
* **Deterministic Move Legality**: Agents must NEVER hallucinate or assume move availability. Run `python scripts/learnset_lookup.py <Species> <Level_Cap>` to verify legal moves before writing team data.
* **Trade Evolution Ground Truth**:
  - In Pokémon Infinite Fusion v5.0+ (Gen 7 rules), trade evolutions (Kadabra, Machoke, Graveler, Haunter, Phantump) evolve naturally at **Level 40 OR via Linking Cord**, NOT Level 37.
  - Metal Coat (Onix, Scyther) evolves at **Level 40 or item**.
  - Dragon Scale (Seadra) evolves at **Level 50 or item**.
  - Protector (Rhydon) evolves at **Level 55 or item**.
  - Electirizer / Magmarizer (Electabuzz, Magmar) evolve at **Level 50 or item**.
  - Evolution trade items act as consumable stones directly from the Bag.
* **Happiness Mechanics Elimination**:
  - Friendship evolutions are completely eliminated in Infinite Fusion; all replaced with static level-up thresholds: Baby Pokémon (Pichu, Cleffa, Igglybuff, Togepi, Budew, Azurill) at **Lv. 15**; Buneary at **Lv. 25**; Riolu & Munchlax at **Lv. 30**; Golbat at **Lv. 40**; Chansey at **Lv. 42**.
* **Campaign Act Structure Ground Truth**:
  - **Act 1: The Complete Kanto Campaign (Chapters 1–9)**: Everything up to and including the first Elite Four and Champion victory at Indigo Plateau is strictly **Act 1** (`"act": 1`, titled `"Act 1 - Segment X: ..."`).
  - **Act 2: The Johto Campaign (Act 2 - Chapters 1–8 / ch10–ch17)**: Begins post-Kanto League via the Saffron Magnet Train to Goldenrod City. Covers the entire Johto Mainland across 8 chapters: Chapter 1 (Whitney / Plain Badge), Chapter 2 (Kurt / Hive Badge), Chapter 3 (Falkner / Zephyr Badge), Chapter 4 (Ruins of Alph & Elm's Lab Johto Starter), Chapter 5 (Morty / Fog Badge), Chapter 6 (Pryce / Glacier Badge), Chapter 7 (Clair / Rising Badge), and Chapter 8 (Route 45/46 Mountain Descent & Johto Finale). All chapters specify `"act": 2` and `"title": "Act 2 - Chapter X: ..."`.
  - **Act 3: Sevii Islands & True Endgame**: Sevii Islands exploration, Chuck (Boon Island / Storm Badge), Jasmine (Bond Bridge / Mineral Badge), Chrono Island, Mt. Silver, and the ultimate endgame battles (Gold / Red).
* **Johto Built-in Gym Party Limits**:
  - Whitney, Kurt, Falkner, Morty, Pryce, and Clair all feature **5 vs 5 Party Selection** (the game prompts the player to select 5 Pokémon from their active party upon initiating the battle).
* **HM Tool Replacements & Field Moves**:
  - 9 HM replacement tools eliminate HM slaves.
  - **Shears (Cut)**: Obtained in Route 2 Before Forest via Diglett's Cave from Vermilion City in Chapter 3 (requires Boulder Badge).
  - **Lantern (Flash)**: Obtained at any Hotel after completing 10 Hotel Quests (before entering Rock Tunnel).
  - **Teleport Field Move**: Outside battle, the move Teleport acts as Fly (fast-travel to any visited Center) as soon as the Thunder Badge is obtained.

---

## 2. Gym Battle Party Limits (Built-in Game Function)
* **Equal Party Sizes in Gym Battles**: Gym team size is hard-coded by the game itself across Infinite Fusion (not an exclusive Hard Mode rule). For every Gym Leader challenge, the game prompts the player to choose which Pokémon from their active party to bring into the arena to match the Leader's roster. No PC box deposits required:
  - **Brock**: 2 vs 2
  - **Misty**: 2 vs 2
  - **Lt. Surge**: 3 vs 3
  - **Erika**: 3 vs 3
  - **Koga**: 4 vs 4
  - **Sabrina**: 4 vs 4
  - **Blaine**: 4 vs 4
  - **Giovanni**: 5 vs 5
* **Gym Team Selection Specification**: Every starter team in `teams/*.json` must define a `gym_duel_core` array containing the exact active slot numbers for the designated Gym battle Pokémon (e.g. `[1, 2]`), matching `gym_duel_limit`, accompanied by `gym_duel_rationale` explaining the strategic matchup against the Gym Leader.

---

## 3. The Evolving Starter Core Framework (Threshold-Centric Showcases)
* **Three Starter Tracks**: Every chapter must track all three starter paths:
  1. **Team Bulbasaur** (Grass Momentum & Status Control)
  2. **Team Charmander** (Hyper-Offense & Fighting Wallbreaker)
  3. **Team Squirtle** (Bulky Balance & Regenerator Pivot)
* **The Starter is the Sole Permanent Anchor**:
  - Across all chapters, only the chosen starter line (Bulbasaur/Ivysaur/Venusaur, Charmander/Charmeleon/Charizard, Squirtle/Wartortle/Blastoise, or their later fused forms) is a permanent fixture of that track.
  - All supporting teammates are fluid, rotating, and evolve as the player travels through Kanto and Johto.
* **No Upfront Endgame Roadmaps**:
  - We do NOT plan out a rigid 6-slot endgame fusion team from the beginning of the guide.
  - Strictly forbid dead upfront roadmap fields (`target_fusion`, `target_types`, `final_target_moveset`) in team JSON schemas. Only active threshold members, moves, and flex benches are authored.
  - Each chapter showcases an authentic, threshold-specific party built strictly from Pokémon and tools obtainable *up to that specific chapter/routes*.
  - Party sizes scale organically: early segments feature tight 2–4 member squads (matching gym duel caps like Brock and Misty's 2v2 arenas), expanding naturally to 5–6 as the mid-game unfolds.
* **Creative & Accessible Splices**:
  - Introduce the first fusions once Super Splicers unlock at Cerulean Mart ($300 at any Mart).
  - Showcase accessible, creative fusions made from route catches (e.g. `Bellsprout/Butterfree`, `Pikachu/Geodude`, `Charmeleon/Kadabra`, `Wartortle/Fearow`).
  - Provide explicit **Fusion Lifecycle Alerts** instructing the player when to unfuse ($300 at any Mart), rotate previous members to the PC box, and splice with new powerhouses.
* **The Team Species Clause (Zero Duplicates Rule)**:
  - **Single-Team Scope**: No single starter team roster may feature duplicate Pokémon species or members of the same evolutionary family across its active threshold party, nor on its flex bench.
  - **Fusion Components Count**: For any fusion (`Head/Body`), both the `Head` species family and the `Body` species family count as used. Neither family may appear in any other slot or fusion on that team in that chapter.
  - **Cross-Team Allowed**: Different starter tracks CAN share species (e.g. Team Bulbasaur, Team Charmander, and Team Squirtle can each catch their own Pidgey or Mankey). The restriction is strictly intra-team.
* **Active Threshold Party + Flex Bench**:
  - Each starter track defines an **Active Threshold Party** ($\ge \text{Gym Duel Limit}$ up to 6) specifically tuned for that segment.
  - Each starter track defines a **Flex Bench (2–3 Mons)** of contextual tech counters caught along the way (with zero duplicate families of active members).

---

## 4. Quests, Missables & Karma Protocol
* **Authoritative Wiki Knowledge**: The official MediaWiki API at `infinitefusion.fandom.com` is cached locally in `data/wiki/*.json`. Run `python scripts/test_wiki_coverage.py` before writing chapters.
* **Permanently Missable Triggers**: Must be prominently alerted in chapter walkthroughs with pulsing warning cards:
  - Chapter 1: **Secret Garden** (Route 22 Rival battle before Brock; permanently locked out if Brock is defeated first).
  - Chapter 2: **Oak's Aide Field Research Part 1** (Poké Radar).
  - Chapter 3: **Building Materials Quest** (must complete before Elite Four before site turns into Fighting Arena).
  - **S.S. Anne Permanently Docked**: In Infinite Fusion, the S.S. Anne does *NOT* depart after speaking to the Captain or getting HM01 Cut. It remains permanently moored in Vermilion City for player cabin healing, hotel Krabby legs quest, waiter field quest, post-Gym 3 gift Torkoal, and Darkrai events.
* **Team Rocket Double-Agent Strategy**:
  - Guide the player to join Team Rocket on Route 24 to obtain the Rocket Uniform disguise and sidequests.
  - BUT instruct the player to report all crimes to Officer Jenny in Cerulean and Celadon for **+10 Karma each**, unlocking the Police raid and the **Mythical Diancie** event!
* **Hotel Quest Pacing**:
  - Target 10 Hotel Quests before Rock Tunnel for the **🏮 Lantern** (Flash tool).
  - Target 15 Hotel Quests for **🔗 Linking Cord x3** (trade evolutions).

---

## 5. The Ultra-Sliced File Architecture (Anti-Bloat Protocol)
* **Never create monolithic chapter files**. All chapter content must be authored in `chapters/chXX/` sliced into atomic files with strict byte budgets:
  - `phases/` micro-locations: Target $\le 2.5$ KB (Hard ceiling: $4.0$ KB without sub-slicing).
  - `teams/` starter files: Target $\le 4.5$ KB (Hard ceiling: $6.0$ KB for full mid/late-game rosters + bench).
  - `boss.json` strategy cards: Target $\le 4.0$ KB (Hard ceiling: $5.5$ KB for multi-starter duels).
  - `meta.json` segment metadata: Target $\le 1.0$ KB (Hard ceiling: $2.0$ KB).
* **Bundle & Context Ceilings**:
  - Standalone Offline Dashboard (`dist/index.html`): Strict budget $\le 350$ KB (enforced via native client-side Gzip decompression using `DecompressionStream('gzip')` and Base64 embedding, keeping full multi-act campaigns under ~200–250 KB).
  - Preflight Context Manifests (`specs/manifest_chXX.json`): Target $\le 60$ KB (Hard ceiling: $65$ KB).
* **Subagent Token Protection & Loop Prohibition**:
  - Subagents must be ephemeral, read only the target 1–4 KB file, and return receipts under 30 tokens.
  - Hard step ceiling of $\le 5$ tool calls per subagent.
  - **Absolute Ban on Browser Loops**: Never launch a `browser_subagent` for routine UI/dashboard verification. Browser verification must never execute exploratory DOM search or scrolling loops. If explicitly requested by the user, browser tasks have a hard limit of $\le 3$ steps total (open, capture, exit). See `.agents/rules/subagent_token_guardrails.md`.

---

## 6. Automation & Testing Toolchain
* Always use the project-wide scripts in `scripts/`:
  - `audit_bloat.py`: Automated **Anti-Bloat & Hygiene Linter** (file budgets, zero dead-fields, bundle budget, root cleanliness).
  - `preflight_chapter.py`: Context manifest generator pulling lean route encounters, boss data from `gym_leaders.json`, items, and quests into `specs/manifest_chXX.json`.
  - `learnset_lookup.py`: Move legality check by level cap.
  - `fusion_calc.py`: Base stats, typing, and abilities math (supports `--cap <Level>`).
  - `scaffold_chapter.py`: Directory and template scaffolding.
  - `assemble_chapter.py`: Bundles sliced files into validated chapter payloads.
  - `verify_chapter.py`: Automated **6-Gate test runner** (Cap/Duel, Spawns, Tools, Teams & Moves, Missables & Wiki, Chronological Obtainability & Evolution).
  - `obtainability.py`: Deterministic **Chronological Obtainability & Evolution Validator** against game PBS/binary data.
  - `test_all_chapters.py`: Comprehensive test suite running all 6 gates across every chapter.
  - `test_wiki_coverage.py`: Audits local wiki cache completeness.
  - `compile_dashboard.py`: Lean compiler generating `dist/index.html`.
