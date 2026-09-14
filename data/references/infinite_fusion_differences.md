# Pokémon Infinite Fusion: Master Mechanical Divergence Reference
**Authoritative Ground Truth Matrix: Vanilla FRLG Assumptions vs. Pokémon Infinite Fusion Facts**

This document details all fundamental mechanical, progression, and event differences between mainline Pokémon (FireRed/LeafGreen) and Pokémon Infinite Fusion (v5.0+, Gen 7 mechanics). 

Agents must consult this document before authoring walkthrough text, strategy cards, or warning banners.

---

## 1. Locations, Ships & Traversal Mechanics

| Feature | Vanilla FRLG Assumption | Pokémon Infinite Fusion Ground Truth | Authoritative Citation |
| :--- | :--- | :--- | :--- |
| **S.S. Anne** | Ship sets sail and leaves permanently once the player receives HM01 Cut and steps off the deck. | **The S.S. Anne NEVER leaves port.** It remains permanently moored in Vermilion City harbor. The player has a private cabin for unlimited free healing. It remains accessible throughout the game for Hotel Quest 3 (steamed Krabby legs), field restaurant quests, a post-Gym 3 gift Torkoal, and the late-game Darkrai mythical event. | [`data/wiki/S.S._Anne.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/wiki/S.S._Anne.json#L142)<br>[`Quests.rb`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/IF%20GAME/InfiniteFusion/Data/Scripts/052_InfiniteFusion/Gameplay/Quests/Quests.rb#L106-L108) |
| **HM Slaves & Field Moves** | Required HM slaves to carry Cut, Flash, Rock Smash, Surf, Strength, etc. | **HM slaves are 100% eliminated.** 9 permanent Key Item tools replace all field moves: **Shears** (Cut), **Lantern** (Flash), **Pickaxe** (Rock Smash), **Surfboard** (Surf), etc. Players should NEVER be instructed to teach Cut or Flash to a party member. | [`data/items/hm_replacements.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/items/hm_replacements.json) |
| **Route 2 Shears (Cut Tool)** | Cut is received on S.S. Anne and taught to a Pokémon to chop the Vermilion Gym tree. | HM01 is obtained from the Captain, but players should proceed through **Diglett's Cave** to Route 2 Before Forest to complete "The Lumberjack!" quest and receive the **✂️ Shears**. | [`data/wiki/Route_2_(Before_the_Forest).json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/wiki/Route_2_(Before_the_Forest).json) |
| **Teleport Field Move** | Teleport returns the player only to the last visited Pokémon Center. | Outside battle, Teleport acts as **Fly** (fast-travel to any previously visited Pokémon Center on the map) as soon as the **Thunder Badge** is acquired! | Game Scripts / [`Fusion_FAQs.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/wiki/Fusion_FAQs.json) |
| **Bicycle** | Costs 1,000,000 Pokedollars; must get Bike Voucher from Vermilion Fan Club. | Bike Voucher is obtained from the Pokémon Fan Club Chairman in Vermilion City and redeemed at Cerulean Bike Shop. | [`data/wiki/Vermillion_City.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/wiki/Vermillion_City.json) |

---

## 2. Evolution Mechanics & Level-Up Thresholds

| Feature | Vanilla FRLG Assumption | Pokémon Infinite Fusion Ground Truth | Authoritative Citation |
| :--- | :--- | :--- | :--- |
| **Trade Evolutions** | Requires linking/trading with another game, or evolves at Level 37 in romhacks. | Kadabra, Machoke, Graveler, Haunter, and Phantump evolve naturally at **Level 40 OR via Linking Cord**. They do NOT evolve at Level 37. | [`data/mechanics/evolution_methods.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/mechanics/evolution_methods.json) |
| **Trade Evolution Items** | Metal Coat, Protector, Dragon Scale, Electirizer, Magmarizer require trade. | In Infinite Fusion, all evolution trade items act as **consumable stones directly from the Bag**, OR the Pokémon evolves naturally at a static level threshold (Onix/Scyther at Lv. 40; Electabuzz/Magmar/Seadra at Lv. 50; Rhydon at Lv. 55). | [`data/mechanics/evolution_methods.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/mechanics/evolution_methods.json) |
| **Friendship / Happiness** | Baby Pokémon, Golbat, Chansey, Buneary, Riolu require maximum friendship. | **Happiness/Friendship evolutions are completely eliminated.** Replaced with static level thresholds: Baby Pokémon (Pichu, Cleffa, Igglybuff, Togepi, Budew, Azurill) at **Lv. 15**; Buneary at **Lv. 25**; Riolu & Munchlax at **Lv. 30**; Golbat at **Lv. 40**; Chansey at **Lv. 42**. | [`data/mechanics/evolution_methods.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/mechanics/evolution_methods.json) |
| **Pre-Evolution Move Retention** | Evolving early causes species to permanently lose pre-evolution moves (e.g. Raichu missing Nasty Plot/Thunderbolt). | In Infinite Fusion, pre-evolution moves can be recalled via the Move Relearner or inherited during fusion splicing. | [`data/mechanics/pre_evolutions.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/mechanics/pre_evolutions.json) |

---

## 3. DNA Splicing, Fusions & Mart Unfusing

| Feature | Description & Rules | Authoritative Citation |
| :--- | :--- | :--- |
| **DNA Splicers** | Available starting in Viridian City Mart ($500) and given by Youngster Mustafa / Rival on Route 22. Standard splicer averages IVs. | [`specs/manifest_ch01.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/specs/manifest_ch01.json) |
| **Super Splicers** | Unlocked at **Cerulean City Mart** ($300 at any Mart after reaching Cerulean). Takes the higher IV of each stat from either parent, maximizing fusion power. | [`data/wiki/Cerulean_City.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/wiki/Cerulean_City.json) |
| **Mart Unfuse ($300)** | Any fused Pokémon can be unfused at any Poké Mart counter for a nominal fee of $300. Both base Pokémon are returned with their original levels intact. Walkthrough chapters use this to rotate early utility fusions into mid-game powerhouses! | [`AGENTS.md`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/AGENTS.md) |
| **Ability Selection** | Upon splicing, the player explicitly selects either the Head's primary ability, the Body's secondary ability, or the hidden ability (if unlocked). | [`scripts/fusion_calc.py`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/scripts/fusion_calc.py) |

---

## 4. Closed Registry of True Permanently Missable Events (Kanto)

Only events listed in this table may be flagged as `⚠️ PERMANENTLY MISSABLE ALERT` in chapter walkthroughs. All entries must match an entry in [`data/quests/master_quests.json`](file:///c:/Users/joshu/OneDrive/Desktop/Pokemon%20IF%20Walkthrough/data/quests/master_quests.json) with `is_missable: true`.

| Quest / Event ID | Title & Location | Hard Deadline | Consequence of Missing |
| :--- | :--- | :--- | :--- |
| `q_field_secret_garden` | **Secret Garden Rival Battle**<br>(Route 22) | **Before defeating Brock (Gym 1)** | Blue departs from Route 22 after Brock is defeated. If not battled before Brock, access to the Secret Garden (early wild starters, Ralts, Eevee, Pichu) is permanently lost for that playthrough! |
| `q_rocket_join_nugget_bridge` | **Team Rocket Recruitment**<br>(Route 24, Nugget Bridge) | **Before defeating Giovanni (Gym 8)** | Accepting the Grunt's offer unlocks the Rocket disguise, undercover quests, and the high-karma police informant path (+20 Karma for Diancie). Defeating Giovanni permanently disbands the local grunt. |
| `q_field_building_materials` | **Building Materials Quest**<br>(Vermilion City Construction Site) | **Before defeating the Elite Four** | After the Elite Four is defeated, the construction site automatically completes and becomes the **Fighting Arena** for Gym Leader rematches. The quest can no longer be turned in, permanently locking out the **Rocky Helmet** reward. |

*Note: S.S. Anne, Route 25 Bill events, Vermilion Fan Club Bike Voucher, and Fossil restoration are NOT permanently missable.*
