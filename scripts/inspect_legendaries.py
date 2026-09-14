import json
import re

def inspect_legendaries():
    with open("data/wiki/Legendary_Pokemon.json", "r", encoding="utf-8") as f:
        d = json.load(f)

    html = d.get("text", {}).get("*", "")

    targets = [
        "Raikou", "Suicune", "Ho-Oh", "Lugia",
        "Dialga", "Palkia", "Giratina", "Darkrai", "Cresselia",
        "Regigigas", "Arceus", "Necrozma"
    ]

    for name in targets:
        m = re.search(rf'id="{name}[^"]*"(.*?)(?=<h3|<h2|$)', html, re.DOTALL | re.IGNORECASE)
        if m:
            clean = re.sub(r'<[^>]+>', ' ', m.group(1))
            clean = " ".join(clean.split())
            print(f"=== {name} ===")
            print(clean[:350])
            print()

if __name__ == "__main__":
    inspect_legendaries()
