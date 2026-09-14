"""
Authoritative Pokémon Infinite Fusion Bulk Wiki Sync Engine
Maintains a canonical registry of all Kanto locations, dungeons, sidequests, and mechanics.
Queries the MediaWiki API via fetch_wiki_knowledge, resolving redirects and caching
clean structured JSON into data/wiki/{page}.json.
"""

import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "scripts"))
from fetch_wiki_knowledge import fetch_wiki_page

CANONICAL_PAGES = [
    # Key Systems & Overarching Mechanics
    "Quests_(Kanto)",
    "Karma",
    "Fusion_FAQs",
    "Poké_Radar",
    "Pokédex/Kanto/Classic",
    "List_of_Gift_Pokémon_and_Trades",
    "List_of_Static_Encounters",
    
    # Cities & Towns
    "Pallet_Town",
    "Viridian_City",
    "Pewter_City",
    "Cerulean_City",
    "Vermillion_City",
    "Celadon_City",
    "Fuchsia_City",
    "Saffron_City",
    "Cinnabar_Island",
    "Lavender_Town",

    # Routes (Kanto Core)
    "Route_1",
    "Route_2",
    "Route_3",
    "Route_4",
    "Route_5",
    "Route_6",
    "Route_7",
    "Route_8",
    "Route_9",
    "Route_10",
    "Route_11",
    "Route_12",
    "Route_13",
    "Route_14",
    "Route_15",
    "Route_16",
    "Route_17",
    "Route_18",
    "Route_19",
    "Route_20",
    "Route_21",
    "Route_22",
    "Route_23",
    "Route_24",
    "Route_25",

    # Dungeons & Landmarks
    "Viridian_Forest",
    "Secret_Garden",
    "Mt._Moon",
    "Mt._Moon_Summit",
    "Diglett's_Cave",
    "S.S._Anne",
    "Rock_Tunnel",
    "Pokémon_Tower",
    "Silph_Co.",
    "Team_Rocket_Hideout",
    "Rocket_Warehouse",
    "Celadon_Sewers",
    "Pinkan_Island",
    "Safari_Zone",
    "Seafoam_Islands",
    "Power_Plant",
    "Victory_Road",
    "Cerulean_Cave"
]

def sync_all(force_refresh=False, sleep_sec=0.2):
    print(f"Starting bulk sync of {len(CANONICAL_PAGES)} canonical wiki pages...")
    success_count = 0
    fail_count = 0
    
    for i, page in enumerate(CANONICAL_PAGES, 1):
        print(f"[{i}/{len(CANONICAL_PAGES)}] Syncing '{page}'...")
        try:
            res = fetch_wiki_page(page, force_refresh=force_refresh)
            if res:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"Error syncing {page}: {e}")
            fail_count += 1
            
        time.sleep(sleep_sec)
        
    print(f"\nBulk sync completed: {success_count} succeeded, {fail_count} failed.")
    return fail_count == 0

if __name__ == "__main__":
    force = "--force" in sys.argv
    sync_all(force_refresh=force)
