"""
Pokémon Infinite Fusion Shared Utilities & Route Alias Registry
Central single source of truth for route name normalization, wiki mapping,
and file resolution across all pipeline tools (preflight, linters, coverage, auditor).
"""

import os
import re

# Canonical MediaWiki page mapping for routes and locations
ROUTE_ALIASES = {
    # Kanto Routes with special wikitext page slugs
    "Route 2 (South)": "Route_2_(Before_the_Forest)",
    "Route 2 (North)": "Route_2_(After_the_Forest)",
    "Route 2 Before Forest": "Route_2_(Before_the_Forest)",
    "Route 2 (Before Forest)": "Route_2_(Before_the_Forest)",
    "Route 2 (Before the Forest)": "Route_2_(Before_the_Forest)",
    "Route 2 After Forest": "Route_2_(After_the_Forest)",
    "Route 2 (After Forest)": "Route_2_(After_the_Forest)",
    "Route 2 (After the Forest)": "Route_2_(After_the_Forest)",
    "Vermilion City": "Vermillion_City",
    "Vermilion Gym": "Vermillion_City",
    "Cerulean Gym": "Cerulean_City",
    "Pewter Gym": "Pewter_City",
    "Diglett's Cave": "Diglett's_Cave",
    "Digletts Cave": "Diglett's_Cave",
    "Pokemon Tower": "Pokémon_Tower",
    "Pokémon Tower": "Pokémon_Tower",
    "Silph Co": "Silph_Co._Head_Office",
    "Silph Co.": "Silph_Co._Head_Office",
    "Silph Co Head Office": "Silph_Co._Head_Office",
    "S.S. Anne": "S.S._Anne",
    "SS Anne": "S.S._Anne",
    "Secret Garden": "Secret_Garden",
    "Brine Road": "Brine_Road_(West_of_the_Old_Shipwreck)",
    "Brine Road West": "Brine_Road_(West_of_the_Old_Shipwreck)",
    "Brine Road (West)": "Brine_Road_(West_of_the_Old_Shipwreck)",
    "Brine Road East": "Brine_Road_(East_of_the_Old_Shipwreck)",
    "Brine Road (East)": "Brine_Road_(East_of_the_Old_Shipwreck)"
}

def normalize_route_slug(route_name: str) -> str:
    """
    Normalizes a human-readable route string (e.g. 'Route 1', 'Route 2 (South)')
    into its canonical MediaWiki page slug (e.g. 'Route_1', 'Route_2_(Before_the_Forest)').
    """
    clean_name = route_name.strip()
    if clean_name in ROUTE_ALIASES:
        return ROUTE_ALIASES[clean_name]
        
    for alias, canonical in ROUTE_ALIASES.items():
        if clean_name.lower() == alias.lower():
            return canonical
            
    # Default fallback: replace whitespace with underscores
    return re.sub(r'\s+', '_', clean_name)

def get_wiki_filepath(base_dir: str, route_name: str) -> str:
    """Returns absolute path to cached wiki JSON for a given route name."""
    slug = normalize_route_slug(route_name)
    return os.path.join(base_dir, "data", "wiki", f"{slug}.json")
