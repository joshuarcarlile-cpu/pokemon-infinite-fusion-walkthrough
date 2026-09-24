# Pokémon Infinite Fusion: Ground Truth & Anti-Vanilla Rules

This rule is mandatory and automatically active across all Antigravity agents, subagents, and sessions in this repository.

---

## 1. The Anti-Vanilla Prior Axiom
* **Vanilla Pokémon (Gen 1 / FireRed / LeafGreen) assumptions are strictly UNTRUSTED heuristics.**
* Agents must NEVER assume an event, NPC behavior, item location, evolution method, or area access follows mainline Pokémon games.
* Infinite Fusion deliberately redesigns many vanilla bottlenecks to improve quality of life and support sidequests.

## 2. The Mandatory Citation Protocol
* Every definitive assertion regarding:
  - Missable content or deadlines
  - Area locking or departures
  - Tool or HM requirements
  - Evolution levels and methods
  - Quest rewards or karma consequences
  MUST cite an authoritative local repository source before being stated:
  1. Local MediaWiki Cache: `data/wiki/<Page>.json`
  2. Game Source Code & Scripts: `IF GAME/InfiniteFusion/Data/Scripts/`
  3. Master Registry: `data/quests/master_quests.json` or `data/mechanics/*.json`
  4. Master Divergence Guide: `data/references/infinite_fusion_differences.md`

## 3. Ground Truth Precedents to Remember
* **S.S. Anne NEVER Leaves Port**: The ship remains permanently docked in Vermilion City harbor. It provides free cabin healing and hosts multiple ongoing quests, a post-Gym 3 gift Torkoal, and late-game Darkrai events.
* **Zero HM Slaves**: 9 Key Item tools replace all field moves (Shears for Cut, Lantern for Flash, Pickaxe for Rock Smash, etc.). Never instruct players to teach Cut or Flash to a party Pokémon.
* **Happiness Eliminated**: All friendship evolutions are replaced with static level-up thresholds (Baby mons at Lv. 15; Buneary at Lv. 25; Riolu/Munchlax at Lv. 30; Golbat at Lv. 40; Chansey at Lv. 42).
* **Trade Evolutions at Level 40**: Trade evolutions evolve naturally at Level 40 OR via Linking Cord (NOT Level 37).
* **Engine Level Caps Ground Truth (`001_Settings.rb`)**: Level caps strictly follow `LEVEL_CAPS_KANTO = [12, 22, 26, 35, 38, 45, 51, 54, 62, 62, 63, 64, 64, 65, 67, 68]` (Hard Mode `floor(Base * 1.1)`). EXP drops to 0 when `pokemon.level >= current_max_level`. Brock's cap is strictly Level 12 Normal / 13 Hard (never vanilla FRLG Lv. 14).
* **STAB on Damaging Moves Only**: STAB (Same-Type Attack Bonus) mechanically applies exclusively to damaging attacks (`cat != 2 && pwr > 0`), never to Status moves (`Leech Seed`, `Sleep Powder`, `Thunder Wave`).
* **Gym Party Selection (Built-in Game Function, No PC Deposit Needed)**: Gym battle party sizes are hard-coded by the game itself across all modes to match the Leader's roster (not a Hard Mode rule). The game automatically prompts the player to choose which Pokémon to bring into the arena. Players do NOT have to deposit Pokémon into the PC storage box before challenging the Gym. Refer to them as "Pokémon" or the designated "Gym battle team", never "duelists".
* **Closed Missables Registry**: Only events listed in `data/quests/master_quests.json` with `is_missable: true` may be flagged with a `⚠️ PERMANENTLY MISSABLE ALERT` warning card. Unverified missable claims are strictly prohibited.
* **Campaign Act Structure Ground Truth**:
  - **Act 1: The Complete Kanto Campaign (Chapters 1–9)**: Everything up to and including the first Elite Four and Champion victory at Indigo Plateau is strictly **Act 1**. All 9 Kanto segments must specify `"act": 1` and `"title": "Act 1 - Segment X: ..."`. Under no circumstances may Kanto Gyms (such as Koga, Sabrina, Blaine, Giovanni) or the League be placed into Act 2.
  - **Act 2: The Johto Campaign**: Begins post-Kanto League from New Bark Town through all 8 Johto Gyms.
  - **Act 3: Sevii Islands & True Endgame**: Sevii Islands, Mt. Silver, and ultimate endgame battles (Gold / Red).
