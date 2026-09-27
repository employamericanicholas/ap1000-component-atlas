"""Export minified plant.json for the website."""
import json
import os

os.makedirs("web/data", exist_ok=True)
d = json.load(open("data/master.json", encoding="utf-8"))
# strip verbose per-component source strings down; keep everything else
json.dump(d, open("web/data/plant.json", "w", encoding="utf-8"), separators=(",", ":"))
print("web/data/plant.json:", round(os.path.getsize("web/data/plant.json") / 1e6, 2), "MB")
