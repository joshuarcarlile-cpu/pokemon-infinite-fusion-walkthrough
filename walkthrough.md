# Pokémon Infinite Fusion Walkthrough: Complete 25-Chapter Definitive Campaign & Dashboard

## Act 4: Postgame Sandbox & Legendary Expeditions (Chapters 23–25)

---

### **1. Chapter 23: The Kanto & Johto Pantheon (Mewtwo, Birds & Beasts)**
- **Act**: 4 (Postgame Sandbox)
- **Hard Mode Level Cap**: 85
- **Gym Duel Limit**: 6 vs 6 Legendary Capture Trial
- **Milestone Boss**: Mewtwo (Lv. 70, Cerulean Cave Depths)
- **Badges Required**: 16 (All 8 Kanto + 6 Johto + Chuck + Jasmine)
- **Micro-Location Phases**:
  1. `23.1_cerulean_cave_depths_and_mewtwo.json`: Cerulean Cave multi-tier labyrinth, high-level wild Ditto/Chansey/Raichu, and crystalline depths confrontation with Mewtwo (Lv. 70).
  2. `23.2_mt_moon_observatory_and_mythical_mew.json`: Mt. Moon Summit observatory telescope puzzle, requiring 20+ Positive Karma and 8 Constellations to encounter Mythical Mew (Lv. 30).
  3. `23.3_kanto_legendary_birds_trio.json`: Ice Pick climb in Seafoam Islands B4F for Articuno (Lv. 50), Power Plant basement key for Zapdos (Lv. 50), and Mt. Ember caldera for Moltres (Lv. 50).
  4. `23.4_johto_roaming_beasts_and_eusine.json`: Ruins of Alph Chamber A encounter with fused beast Raicune (Lv. 50), followed by Johto weather tracking for roaming Entei and Raicune.
- **Roster & Counters (Cap 85)**:
  - Team Bulbasaur: `Venusaur/Charizard` (Lv. 85), `Lapras` (Lv. 84), `Kingler/Primeape` (Lv. 84), `Gyarados/Arbok` (Lv. 84), `Alakazam/Weezing` (Lv. 84), `Snorlax` (Lv. 84).
  - Team Charmander: `Charizard/Venusaur` (Lv. 85), `Alakazam/Raichu` (Lv. 84), `Lapras` (Lv. 84), `Primeape/Sandslash` (Lv. 84), `Gyarados/Nidoking` (Lv. 84), `Snorlax` (Lv. 84).
  - Team Squirtle: `Blastoise/Fearow` (Lv. 85), `Jolteon/Sandslash` (Lv. 84), `Lapras` (Lv. 84), `Arbok/Primeape` (Lv. 84), `Alakazam/Weezing` (Lv. 84), `Snorlax` (Lv. 84).

---

### **2. Chapter 24: Primordial Heavens & Abyssal Depths (Ho-Gia, Weather Trio & Creation)**
- **Act**: 4 (Postgame Sandbox)
- **Hard Mode Level Cap**: 92
- **Gym Duel Limit**: 6 vs 6 Primordial Dragon Trial
- **Milestone Boss**: Rayquaza (Lv. 70, Sky Pillar Apex)
- **Micro-Location Phases**:
  1. `24.1_navel_rock_and_sacred_ho_gia.json`: Chuck's Navel Ticket voyage to Navel Rock, scaling the hollow mountain to battle sacred fusion Ho-Gia (Ho-Oh & Lugia, Lv. 60).
  2. `24.2_abyssal_trenches_and_ruby_chamber.json`: Heat-protection cream expedition into Mt. Ember's Ruby Chamber for Groudon (Lv. 60), and Scuba Gear dive into Deep Sea Sapphire Cave for Kyogre (Lv. 60).
  3. `24.3_kin_island_sky_pillar_rayquaza.json`: Chartered ship from Kin Island harbor to the ancient Sky Pillar, scaling 5 floors of wild Dusclops/Metang to battle celestial sovereign Rayquaza (Lv. 70).
  4. `24.4_birth_island_and_creation_dragons.json`: Bond Bridge spaceship fragments and Birth Island triangular obelisk puzzle for Deoxys (Lv. 70); post-Silver Creation Trio (Dialga on Boon Island, Palkia in Blackthorn City, Giratina on Route 4).
- **Roster & Counters (Cap 92)**:
  - Starter tracks elevated to Level 91–92, utilizing Lapras's STAB 4x Ice Beam to cleanly suppress Rayquaza and Dragon defenders.

---

### **3. Chapter 25: The Apex Sandbox (Vermilion Arena, Level 100 League & Triple Fusions)**
- **Act**: 4 (Postgame Sandbox)
- **Hard Mode Level Cap**: 100
- **Gym Duel Limit**: 6 vs 6 Flat Level 100 Master Gauntlet
- **Milestone Boss**: Champion Blue (Tier 5 Level 100 Indigo Plateau Apex)
- **Micro-Location Phases**:
  1. `25.1_vermilion_arena_kanto_rematches.json`: Overworld schedule and competitive 6v6 rematches (Levels 80–85) for the 8 Kanto Leaders at Vermilion Arena.
  2. `25.2_vermilion_arena_johto_sevii_rematches.json`: Overworld schedule and competitive 6v6 rematches (Levels 82–86) for Johto & Sevii Leaders (Whitney, Kurt, Falkner, Morty, Pryce, Clair, Chuck, Jasmine).
  3. `25.3_indigo_plateau_tier_5_level_100.json`: Route 23 ascent and Indigo Plateau Tier 4 & 5 League Rematches scaling to flat Level 100 against Lorelei, Bruno, Agatha, Lance, and Champion Blue.
  4. `25.4_legendary_triple_fusions_mastery.json`: Super DNA Splicer mechanics, recipes, and custom base stats/typings for Zapmolcuno, Raienteicune, and Dialkiatina.
- **Roster & Counters (Cap 100)**:
  - All 3 starter tracks crowned at flat Level 100 with apex competitive builds, verified moves, and held items.

---

### **4. Dashboard UI Enhancements in `dist/index.html`**
1. **Act 4 Header Switcher**: Native `switchAct(4)` button dynamically filtering the sidebar for Chapters 23–25.
2. **Speedrun Cheat Sheet Modal**: Accessible via the `📋 Cheat Sheet` header button or keyboard shortcut `C`, displaying a master matrix of all 25 chapters with level caps, duel limits, boss aces, weaknesses, and key tools.
3. **Interactive Catch Tracker**: Integrated checkboxes on wild encounter tables persisted via `localStorage`.
4. **Interactive Splicer Sandbox**: In-drawer calculator computing asymmetric fusion stats, dual typings, and ability inheritance using the embedded `compact_base_stats`.
5. **Bundle Size**: **299,627 bytes** (well under the 350 KB ceiling; 72.3% reduction).

---

### **5. Comprehensive Automated Test Results**
- `scripts/verify_chapter.py`: **100% clean assertions** across all 25 chapters.
- `scripts/audit_bloat.py`: **PASSED** with 0 dead fields and 0 hard ceiling violations.
- `scripts/test_all_chapters.py`: **25/25 chapters PASSED**.
- `scripts/verify_bundle.py`: All 25 chapters successfully decompressed in memory.
