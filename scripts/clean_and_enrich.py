"""Clean Table 3.2-3 extraction: fix column-shifted rows, drop header bleed,
extract table notes and class definitions."""
import json
import re
import pdfplumber

d = json.load(open("data/components_3_2_3.json", encoding="utf-8"))
comps = d["components"]

VALID_CLASS = {"A", "B", "C", "D", "E", "F", "L", "P", "R", "W"}
VALID_SEISMIC = {"I", "II", "NS", "1", "C-I", "C-II"}

cleaned = []
for c in comps:
    tag = re.sub(r"\s+", "", c["tag"]) if c["tag"] else ""
    # drop header bleed-through rows
    if tag.lower().startswith("tagnumber") or c["description"] == "Description":
        continue
    # fix right-shifted rows: class empty, real class sitting in seismic col
    if c["ap1000_class"] == "" and c["seismic_category"] in VALID_CLASS:
        c["ap1000_class"] = c["seismic_category"]
        c["seismic_category"] = c["construction_code"]
        c["construction_code"] = c["comments"]
        c["comments"] = ""
    # fix rows where class holds 'Note N' and seismic slid into construction col
    if c["seismic_category"] == "" and c["construction_code"] in VALID_SEISMIC:
        c["seismic_category"] = c["construction_code"]
        c["construction_code"] = c["comments"]
        c["comments"] = ""
    if c["seismic_category"] == "1":
        c["seismic_category"] = "I"
    cleaned.append(c)

# inherit attributes for rows still fully blank whose description mirrors the previous row
for i, c in enumerate(cleaned):
    if c["ap1000_class"] == "" and c["seismic_category"] == "" and i > 0:
        prev = cleaned[i - 1]
        a = re.sub(r"\b[AB12]\b", "", c["description"])
        b = re.sub(r"\b[AB12]\b", "", prev["description"])
        if a == b and prev["ap1000_class"]:
            c["ap1000_class"] = prev["ap1000_class"]
            c["seismic_category"] = prev["seismic_category"]
            c["construction_code"] = prev["construction_code"]
            c["comments"] = (c["comments"] + " [attributes inherited from paired item]").strip()

# ---- extract the notes block at the end of Table 3.2-3 and class definitions ----
notes_text = []
class_defs_text = []
with pdfplumber.open("data/raw/ML11171A425.pdf") as pdf:
    # last sheet(s) carry the numbered notes
    for pageno in (92, 93):
        t = pdf.pages[pageno].extract_text() or ""
        m = re.search(r"Notes?:\s*(.*)", t, re.S)
        if m:
            notes_text.append(m.group(1))
    # section 3.2.2 prose defines equipment classes A-F etc. (pages 4-13)
    for pageno in range(3, 16):
        t = pdf.pages[pageno].extract_text() or ""
        class_defs_text.append(t)

d["components"] = cleaned
d["table_notes"] = "\n".join(notes_text)
json.dump(d, open("data/components_3_2_3.json", "w", encoding="utf-8"), indent=1)
open("data/class_definitions_raw.txt", "w", encoding="utf-8").write("\n\n".join(class_defs_text))

import csv
with open("data/components_3_2_3.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(cleaned[0].keys()))
    w.writeheader()
    w.writerows(cleaned)

from collections import Counter
print("components:", len(cleaned))
print("classes:", Counter(x["ap1000_class"] for x in cleaned).most_common())
print("seismic:", Counter(x["seismic_category"] for x in cleaned).most_common(8))
print("systems:", len({x["system_code"] for x in cleaned if x["system_code"]}))
print("notes chars:", len(d["table_notes"]))
