"""Extract equipment tables from AP1000 DCD Rev 19 Tier 1 Chapter 2 files.
Captures every table containing a 'Tag No.' column, preserving all columns as attributes."""
import json
import re
import pdfplumber

FILES = {
    "ML11171A308": "Tier 1 2.1 Reactor",
    "ML11171A310": "Tier 1 2.2 Nuclear Safety Systems",
    "ML11171A311": "Tier 1 2.3 Auxiliary Systems",
    "ML11171A312": "Tier 1 2.4 Steam and Power Conversion",
    "ML11171A313": "Tier 1 2.5 Instrumentation and Control",
    "ML11171A314": "Tier 1 2.6 Electrical Power",
    "ML11171A316": "Tier 1 2.7 HVAC",
}

HEADING_RE = re.compile(r"^(2\.\d+\.\d+)\s+([A-Z][A-Za-z0-9 ,/&()'\-]+?)\s*$", re.M)
TABLE_NO_RE = re.compile(r"Table (2\.\d+\.\d+-\d+)")

def clean(cell):
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()

records = []
section_titles = {}

for ml, label in FILES.items():
    with pdfplumber.open(f"data/raw/{ml}.pdf") as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for m in HEADING_RE.finditer(text):
                sec, title = m.group(1), m.group(2).strip()
                # keep first-seen title; headings repeat in headers/ToC lines
                if sec not in section_titles and len(title) > 3 and not title.endswith("-"):
                    section_titles[sec] = title
            tables = page.extract_tables()
            if not tables:
                continue
            # table number(s) on this page — take the first as context
            tnos = TABLE_NO_RE.findall(text)
            tno = tnos[0] if tnos else None
            for table in tables:
                header = None
                header_cells = None
                for row in table:
                    cells = [clean(c) for c in row]
                    if not any(cells):
                        continue
                    # detect the header row containing Tag No.
                    joined = " ".join(cells).lower()
                    if header is None:
                        if re.search(r"tag no", joined):
                            header_cells = cells
                            header = [c if c else f"col{j}" for j, c in enumerate(cells)]
                            continue
                        else:
                            # might be a title/continuation row; check for tno
                            mt = TABLE_NO_RE.search(cells[0])
                            if mt:
                                tno = mt.group(1)
                            continue
                    # data row
                    if cells == header_cells:
                        continue
                    rec_attrs = {}
                    name, tag = "", ""
                    for j, col in enumerate(header):
                        val = cells[j] if j < len(cells) else ""
                        lc = col.lower()
                        if "equipment name" in lc or lc == "component name":
                            name = val
                        elif "tag no" in lc:
                            tag = val
                        else:
                            if val:
                                rec_attrs[col] = val
                    if not tag and not name:
                        continue
                    section = tno.split("-")[0] if tno else None
                    records.append({
                        "equipment_name": name,
                        "tag": tag,
                        "tier1_table": tno,
                        "section": section,
                        "section_title": None,  # filled below
                        "file": ml,
                        "area": label,
                        "attributes": rec_attrs,
                    })

for r in records:
    if r["section"]:
        r["section_title"] = section_titles.get(r["section"])

# de-duplicate identical rows (repeated headers across page breaks)
seen = set()
uniq = []
for r in records:
    key = (r["tag"], r["equipment_name"], r["tier1_table"], json.dumps(r["attributes"], sort_keys=True))
    if key in seen:
        continue
    seen.add(key)
    uniq.append(r)

json.dump({"section_titles": section_titles, "equipment": uniq},
          open("data/tier1_equipment.json", "w", encoding="utf-8"), indent=1)

from collections import Counter
print("tier1 records:", len(uniq))
print("by area:", Counter(r["area"] for r in uniq))
print("sections:", len(section_titles))
for s in sorted(section_titles)[:40]:
    print(" ", s, section_titles[s])
