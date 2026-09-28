"""Extract Table 3.2-3 from the Rev 20 public DCD (ML26086A412, one 6,514-page PDF)
using the same parsing logic as the Rev 19 extraction, then save for diffing."""
import json
import re
import pdfplumber

PDF = "data/raw/ML26086A412.pdf"
SCAN_FROM, SCAN_TO = 1060, 1220  # bracket found by sampling

SYS_RE = re.compile(r"^(?P<name>[^()]+?)\s*\((?P<code>[A-Z]{2,4})\)\s*(?:Location:\s*(?P<loc>.+))?$")
CONT_RE = re.compile(r"^(?P<name>.+?)\s*\(Continued\)$")

def clean(cell):
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()

components, system_notes = [], []
current_system = {"name": None, "code": None, "location": None}
systems_seen = {}
t323_pages = []

with pdfplumber.open(PDF) as pdf:
    # find exact pages carrying Table 3.2-3 (whitespace-insensitive: kerning varies)
    for i in range(SCAN_FROM, min(SCAN_TO, len(pdf.pages))):
        t = re.sub(r"\s+", "", pdf.pages[i].extract_text() or "")
        if re.search(r"Table3\.2-3\(Sheet\d+of\d+\)", t):
            t323_pages.append(i)
    print("Table 3.2-3 pages:", t323_pages[0], "..", t323_pages[-1], f"({len(t323_pages)} pages)")

    for pageno in t323_pages:
        for table in pdf.pages[pageno].extract_tables():
            for row in table:
                cells = [clean(c) for c in row]
                if not any(cells):
                    continue
                first = cells[0]
                if first.startswith("Table 3.2-3") or re.sub(r"\s+", "", first).lower().startswith("tagnumber"):
                    continue
                if all(not c for c in cells[1:]):
                    m = SYS_RE.match(first)
                    mc = CONT_RE.match(first)
                    if m:
                        name, code = clean(m.group("name")), m.group("code")
                        loc = clean(m.group("loc") or "")
                        current_system = {"name": name, "code": code, "location": loc or None}
                        if code not in systems_seen:
                            systems_seen[code] = {"name": name, "code": code, "location": loc or None, "notes": []}
                        elif loc:
                            systems_seen[code]["location"] = loc
                    elif mc:
                        pass
                    else:
                        code = current_system.get("code")
                        system_notes.append({"system_code": code, "note": first})
                        if code in systems_seen:
                            systems_seen[code]["notes"].append(first)
                    continue
                tag, desc, ap_class, seismic, ccode, comments = (cells + [""] * 6)[:6]
                if not desc and not ap_class:
                    continue
                components.append({
                    "tag": tag, "description": desc,
                    "system_name": current_system.get("name"),
                    "system_code": current_system.get("code"),
                    "location": current_system.get("location"),
                    "ap1000_class": ap_class, "seismic_category": seismic,
                    "construction_code": ccode, "comments": comments,
                })

# same cleaning as Rev 19 (clean_and_enrich.py)
VALID_CLASS = {"A", "B", "C", "D", "E", "F", "L", "P", "R", "W"}
VALID_SEISMIC = {"I", "II", "NS", "1", "C-I", "C-II"}
cleaned = []
for c in components:
    tag = re.sub(r"\s+", "", c["tag"]) if c["tag"] else ""
    if tag.lower().startswith("tagnumber") or c["description"] == "Description":
        continue
    if c["ap1000_class"] == "" and c["seismic_category"] in VALID_CLASS:
        c["ap1000_class"], c["seismic_category"], c["construction_code"], c["comments"] = \
            c["seismic_category"], c["construction_code"], c["comments"], ""
    if c["seismic_category"] == "" and c["construction_code"] in VALID_SEISMIC:
        c["seismic_category"], c["construction_code"], c["comments"] = \
            c["construction_code"], c["comments"], ""
    if c["seismic_category"] == "1":
        c["seismic_category"] = "I"
    c["tag"] = tag.upper() if tag and tag.upper() != "N/A" else "n/a"
    cleaned.append(c)
for i, c in enumerate(cleaned):
    if c["ap1000_class"] == "" and c["seismic_category"] == "" and i > 0:
        prev = cleaned[i - 1]
        a = re.sub(r"\b[AB12]\b", "", c["description"])
        b = re.sub(r"\b[AB12]\b", "", prev["description"])
        if a == b and prev["ap1000_class"]:
            c["ap1000_class"], c["seismic_category"], c["construction_code"] = \
                prev["ap1000_class"], prev["seismic_category"], prev["construction_code"]

json.dump({"systems": systems_seen, "components": cleaned, "notes": system_notes,
           "source": "Rev 20 public DCD (ML26086A412), Table 3.2-3"},
          open("data/components_3_2_3_rev20.json", "w", encoding="utf-8"), indent=1)
from collections import Counter
print("rev20 components:", len(cleaned))
print("systems:", len(systems_seen))
print("classes:", Counter(x["ap1000_class"] for x in cleaned).most_common(8))
