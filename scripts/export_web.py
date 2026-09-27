"""Export minified plant.json for the website."""
import json
import os

os.makedirs("docs/data", exist_ok=True)
d = json.load(open("data/master.json", encoding="utf-8"))
json.dump(d, open("docs/data/plant.json", "w", encoding="utf-8"), separators=(",", ":"))
print("docs/data/plant.json:", round(os.path.getsize("docs/data/plant.json") / 1e6, 2), "MB")
