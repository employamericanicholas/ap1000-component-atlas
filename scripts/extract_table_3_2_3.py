"""Extract AP1000 DCD Rev 19 Tier 2 Table 3.2-3 (Classification of Mechanical and
Fluid Systems, Components, and Equipment) from ML11171A425.pdf into structured data."""
import json
import re
import csv
import pdfplumber

PDF = "data/raw/ML11171A425.pdf"
OUT_JSON = "data/components_3_2_3.json"
OUT_CSV = "data/components_3_2_3.csv"

# System header examples:
#   "Component Cooling Water System (Continued)"
#   "Condensate System (CDS) Location: Turbine Building"
#   "Main and Startup Feedwater System (FWS) Location: Turbine Building, Auxiliary Building"
SYS_RE = re.compile(r"^(?P<name>[^()]+?)\s*\((?P<code>[A-Z]{2,4})\)\s*(?:Location:\s*(?P<loc>.+))?$")
CONT_RE = re.compile(r"^(?P<name>.+?)\s*\(Continued\)$")

def clean(cell):
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()

components = []
system_notes = []
current_system = {"name": None, "code": None, "location": None}
systems_seen = {}

with pdfplumber.open(PDF) as pdf:
    for pageno in range(19, len(pdf.pages)):  # pages 20..94
        page = pdf.pages[pageno]
        tables = page.extract_tables()
        if not tables:
            continue
        for table in tables:
            for row in table:
                cells = [clean(c) for c in row]
                non_empty = [c for c in cells if c]
                if not non_empty:
                    continue
                first = cells[0]
                # skip table title & column header rows
                if first.startswith("Table 3.2-3"):
                    continue
                if first == "Tag Number":
                    continue
                # spanning rows: system headers or notes
                rest_empty = all(not c for c in cells[1:])
                if rest_empty:
                    m = SYS_RE.match(first)
                    mc = CONT_RE.match(first)
                    if m:
                        name = clean(m.group("name"))
                        code = m.group("code")
                        loc = clean(m.group("loc") or "")
                        current_system = {"name": name, "code": code, "location": loc or None}
                        if code not in systems_seen:
                            systems_seen[code] = {"name": name, "code": code,
                                                  "location": loc or None, "notes": []}
                        elif loc:
                            systems_seen[code]["location"] = loc
                    elif mc:
                        # continuation header; keep current system (name may lack code)
                        pass
                    else:
                        # a note row like "Balance of system components are Class E"
                        note = first
                        code = current_system.get("code")
                        system_notes.append({"system_code": code, "note": note})
                        if code in systems_seen:
                            systems_seen[code]["notes"].append(note)
                    continue
                # component rows (tag may be "n/a" for unnumbered items)
                tag, desc, ap_class, seismic, ccode, comments = (cells + [""] * 6)[:6]
                if not desc and not ap_class:
                    continue
                components.append({
                    "tag": tag,
                    "description": desc,
                    "system_name": current_system.get("name"),
                    "system_code": current_system.get("code"),
                    "location": current_system.get("location"),
                    "ap1000_class": ap_class,
                    "seismic_category": seismic,
                    "construction_code": ccode,
                    "comments": comments,
                    "source": "DCD Rev 19 Tier 2 Table 3.2-3 (ML11171A425)",
                })

print(f"systems: {len(systems_seen)}")
print(f"components: {len(components)}")
print(f"notes: {len(system_notes)}")

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"systems": systems_seen, "components": components,
               "notes": system_notes}, f, indent=1)

with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(components[0].keys()))
    w.writeheader()
    w.writerows(components)

# quick sanity
from collections import Counter
print(Counter(c["ap1000_class"] for c in components).most_common(10))
print("sample:", components[0])
print("sample:", components[-1])
