import re
import base64
import gzip
import json

def verify_bundle():
    with open("dist/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    m = re.search(r'const COMPRESSED_APP_DATA = "([^"]+)";', html)
    if not m:
        print("ERROR: COMPRESSED_APP_DATA payload not found in dist/index.html")
        return False

    b64_data = m.group(1)
    raw_gz = base64.b64decode(b64_data)
    decomp = gzip.decompress(raw_gz).decode("utf-8")
    payload = json.loads(decomp)
    chapters = payload.get("chapters", [])
    
    print(f"SUCCESS: Successfully decompressed and parsed {len(chapters)} chapters from dist/index.html!")
    for ch in chapters:
        ch_id = ch.get("id") or ch.get("chapter_id")
        title = ch.get("title") or ch.get("name")
        act = ch.get("act")
        cap = ch.get("hard_mode_level_cap") or ch.get("level_cap")
        print(f"  {ch_id}: Act {act} (Cap {cap}) - {title}")
    return True

if __name__ == "__main__":
    verify_bundle()
