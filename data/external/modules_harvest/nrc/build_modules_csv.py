"""Build nrc_modules.csv from candidates.jsonl using curated module verdicts.

Only IDs whose module identity is supported by source context are emitted.
False positives (QA report prefixes Q445-*, WPS/PQR numbers CS-6xx, procedure
numbers QP-CA-2xx, PO numbers D100.CA00x, welding machines R350, CMTR revision
suffixes Rxx, PWHT charts CH113) are excluded.
"""
import csv, json, pathlib, re
from collections import defaultdict

base = pathlib.Path(__file__).parent

# ---- curated main-module verdicts -----------------------------------------
# id: (class, description_from_context, building_or_area, confidence, preferred_mls)
MAIN = {
 "CA01": ("structural", "Containment Building Area 1 Module CA01 (steel structural module forming steam generator/refueling compartment walls; ~48 sub-modules)", "Containment (containment internal structures)", "high", ["ML14311A666", "ML14072A315", "ML16132A557", "ML22059A049"]),
 "CA02": ("structural", "structural module CA02, the north-east wall of the in-containment refueling water storage tank (IRWST)", "Containment (IRWST)", "high", ["ML15223B074", "ML15223B361"]),
 "CA03": ("structural", "Containment Building Module CA03 (IRWST wall module; main assembly modules 2 through 16)", "Containment (IRWST)", "high", ["ML16035A439", "ML15301A424"]),
 "CA04": ("structural", "reactor vessel cavity wall (Seismic Category I steel structure)", "Containment (reactor vessel cavity)", "high", ["ML15223B074", "ML13304A907", "ML14311A666"]),
 "CA05": ("structural", "Containment Building Area 3 Module CA05; wall module (CA05-08 is the north-south wall east of the CVS room)", "Containment", "high", ["ML14218A414", "ML15301A424"]),
 "CA20": ("structural", "CA20 Auxiliary Building module (Areas 5 & 6), large multi-wall structural module around spent fuel pool area; dozens of wall sub-modules", "Auxiliary Building Areas 5 & 6", "high", ["ML14308A463", "ML15124A857", "ML13312A316"]),
 "CA22": ("structural", "structural module (CA22) making up the composite floor system of the demineralizer/filter area (Room 12251), installed in advance of concrete placement", "Auxiliary Building (Room 12251)", "high", ["ML15309A177"]),
 "CA30": ("structural", "CA30 Module (E&DCR 'Clarification of CA30 Module Connection Details'; CA3X floor module series)", "Containment (floor modules)", "medium", ["ML17132A351", "ML17226A034"]),
 "CA31": ("structural", "Module CA31 (design change proposal APP-GW-GEE-4949, 'Incorporate E&DCR's into Module CA31')", "unknown", "medium", ["ML15364A548"]),
 "CA32": ("structural", "containment internal structures floor module (calc 'Design of Floor Modules CA32, CA33, CA34, CA35, CA36, CA37 and CA01 Submodules CA01-35 and CA01-38')", "Containment (floor at El. 107'-2\")", "high", ["ML17132A351", "ML17226A034"]),
 "CA33": ("structural", "containment internal structures floor module (same design calculation series as CA32)", "Containment (floor modules)", "high", ["ML17132A351"]),
 "CA34": ("structural", "containment internal structures floor module (same design calculation series as CA32)", "Containment (floor modules)", "high", ["ML17132A351"]),
 "CA35": ("structural", "containment internal structures floor module (same design calculation series as CA32)", "Containment (floor modules)", "high", ["ML17132A351", "ML17257A407"]),
 "CA36": ("structural", "containment internal structures floor module; fabrication documentation and physical attributes reviewed as submodules CA32, CA36, CA37", "Containment (floor modules)", "high", ["ML17132A351"]),
 "CA37": ("structural", "Containment Building Area 4 CA37 Floor El. 107'-2\" (floor module)", "Containment Area 4, floor El. 107'-2\"", "high", ["ML17132A351", "ML17226A034"]),
 "CA50": ("structural", "CA50 floor module (E&DCRs 'Clarification of CA50 Module Connection Details', 'CA50 Floors to CA01 Connection')", "Containment (floor modules)", "medium", ["ML17226A034"]),
 "CA55": ("structural", "containment internal floor module at elevation 135'-3\" above the IRWST; duplex stainless steel structural module", "Containment (El. 135'-3\" above IRWST)", "high", ["ML17226A074", "ML17181A238"]),
 "CA56": ("structural", "Containment Building Area 1 & 2 CA56 Floor EL. 135'-3\" (floor module)", "Containment Areas 1 & 2, floor El. 135'-3\"", "high", ["ML17226A074", "ML18045A476"]),
 "CA57": ("structural", "duplex stainless steel structural module CA57 (containment floor module)", "Containment (floor modules)", "high", ["ML17181A238", "ML17226A034"]),
 "CA58": ("structural", "structural module CA58 (welded at Greenberry's Vancouver facility for Vogtle Unit 4; containment floor module series)", "Containment (floor modules)", "high", ["ML17181A238"]),
 "CB11": ("structural", "CB11 module set on embed plates in room 11207", "Containment (room 11207)", "medium", ["ML15223B074", "ML16132A557"]),
 "CB12": ("structural", "CB12 module set on embed plates in room 11206", "Containment (room 11206)", "medium", ["ML15223B074"]),
 "CB20": ("structural", "CB20 Passive Containment Cooling Water Tank module (Shield Building Roof Area 8; includes Flat Bottom Ring sub-modules)", "Shield Building roof (PCCWST)", "high", ["ML17226A340"]),
 "CB21": ("structural", "CB21 module (N&D 'CB21 Fillet Connection to CA01')", "Containment", "medium", ["ML16032A554"]),
 "CB34": ("structural", "CB34 module (E&DCR 'Optional Vertical Construction Joint for Behind CB34 and In-Between CA01/05 from 96'-0\" to 105'-2\"/107'-2\"')", "Containment", "low", ["ML17226A034"]),
 "CB63": ("unknown", "CB63 module (E&DCR 'CB63 Piping Penetration Dimension Change')", "unknown", "low", ["ML15364A548"]),
 "CB65": ("structural", "structural module CB65 ('structural module welds on modules CA04, CB65, and CB66'; 'CB65 Module Welding Details')", "Nuclear Island / Containment", "high", ["ML14311A666", "ML14017A101", "ML18045A476"]),
 "CB66": ("structural", "structural module CB66 ('structural module welds on modules CA04, CB65, and CB66')", "Nuclear Island / Containment", "high", ["ML14311A666", "ML18045A476"]),
 "CH59": ("unknown", "CH59 (E&DCR APP-CH59-GEF-850013 'Thermal Cutting Maximum Hardness' among structural module fabrication documents)", "unknown", "low", ["ML17132A351"]),
 "CS15": ("structural", "Unit 3 CS15 Stair Module (weld map: 'CS15 Stair Module Beam Seats to CA01 Module Weld Map for Containment')", "Containment", "high", ["ML18045A476"]),
 "KB04": ("mechanical", "KB04 module (N&D 'KB04 Dimensional Discrepancies')", "unknown", "low", ["ML14303A481"]),
 "KB10": ("mechanical", "KB10 (E&DCR 'KB10 & KB13 as Construction Drain')", "unknown", "low", ["ML15037A406"]),
 "KB13": ("mechanical", "KB13 (E&DCR 'KB10 & KB13 as Construction Drain')", "unknown", "low", ["ML15037A406"]),
 "KB14": ("mechanical", "KB14 module (N&D 'KB14 Pipe Slope')", "unknown", "low", ["ML14303A481"]),
 "KB16": ("mechanical", "KB16 module ('KB16 WLS Piping and Component Design Parameter Discrepancy')", "unknown (WLS liquid radwaste system)", "medium", ["ML15120A400"]),
 "KB36": ("mechanical", "Module No. KB36 (Aecon Industrial mechanical module, commercial-grade dedication with modules Q223, Q240, Q305, Q601)", "unknown", "high", ["ML17254A117"]),
 "KB37": ("mechanical", "Module No. KB37 for Vogtle (fabricated at CB&I Lake Charles; PIC tickets and parts lists reviewed for material traceability)", "unknown", "high", ["ML14072A315"]),
 "KQ10": ("mechanical", "Module 1112-KQ-10 Reactor Coolant Drain Tank Structural Interfaces", "Containment (reactor coolant drain tank room)", "high", ["ML13304A907"]),
 "KQ11": ("mechanical", "Module KQ11, reactor cavity sump / Module 1110-KQ-11 WLS Sump Pump", "Containment (reactor cavity sump)", "high", ["ML15037A445", "ML15037A406"]),
 "Q223": ("mechanical", "direct vessel injection (DVI) mechanical module Q223, placed in containment", "Containment", "high", ["ML17044A539", "ML17132A351", "ML16228A086"]),
 "Q233": ("mechanical", "direct vessel injection (DVI) mechanical module Q233 ('Modules Q223 and Q233 which form portions of the DVI lines were set in containment')", "Containment", "high", ["ML17044A539", "ML17226A034"]),
 "Q240": ("mechanical", "ASME III Mechanical Module Q-240, 'Residual Heat Removal Module' (Aecon-fabricated; FAA by WECTEC)", "unknown (RNS)", "high", ["ML17132A351", "ML17254A117", "ML16228A086"]),
 "Q305": ("piping", "Module Q305, 'Piping Assembly Series I Y05'; contains CVS, PXS, and Liquid Radwaste System (WLS) isolation valves", "Containment", "high", ["ML17254A117", "ML17226A034"]),
 "Q601": ("mechanical", "Q601 mechanical module fabricated to ASME B&PV Code Section III (support box beams for piping; ring girder assembly)", "unknown", "high", ["ML17254A117"]),
 "R106": ("unknown", "R106 (drawing APP-R106-13-106-000-10603 among CB&I Lake Charles sub-module weld map drawings)", "unknown", "low", ["ML14072A315"]),
 "R219": ("mechanical", "mechanical sub-module R219 for Vogtle (material traceability traveler at CB&I Lake Charles)", "unknown", "high", ["ML14072A315"]),
}

# parents whose two-level sub-modules we also emit
SUB_OK = {"CA01", "CA02", "CA03", "CA04", "CA05", "CA20", "CA55", "CB20"}
SUB_REJECT = {
    "CA20-75",   # only appears as CA20-75A fragment
    "CA03-001",  # part number CA03-001-F, not a sub-module
    "CA05-15",   # weld number VS2-CA05-15... line-break artifact
}

def url(ml):
    return f"https://www.nrc.gov/docs/ML{ml[2:6]}/{ml}.pdf"

meta = {}
for line in (base / "doc_meta.tsv").read_text(encoding="utf-8").splitlines():
    ml, _, rep = line.partition("\t")
    meta[ml] = rep.strip()

def source_doc(ml):
    rep = meta.get(ml, "")
    return f"IR {rep} ({ml})" if rep else f"({ml})"

cands = [json.loads(l) for l in (base / "candidates.jsonl").read_text(encoding="utf-8").splitlines()]

def score(m):
    s = 0
    idx = m["ctx"].find(m["id"].split("-")[0])
    window = m["ctx"][max(0, idx - 80): idx + 100]
    if re.search(r"sub-?\s?module", window, re.I): s += 3
    if re.search(r"module", window, re.I): s += 3
    if re.search(r"structural|mechanical|piping", m["ctx"], re.I): s += 2
    if re.search(r"lift|rigging|placement|setting|fabricat", m["ctx"], re.I): s += 1
    return s

def quote(m, ident, maxlen=300):
    ctx = m["ctx"]
    idx = ctx.find(ident)
    if idx < 0:
        idx = ctx.find(ident.replace("-", "_"))
    if idx < 0:
        idx = len(ctx) // 2
    lo = max(0, idx - maxlen // 2)
    q = ctx[lo:lo + maxlen]
    return ("..." + q if lo > 0 else q)[:300]

# group candidates
def norm_id(i):
    i = i.replace("_", "-")
    parts = i.split("-")
    # zero-padded 3-digit sub numbers are the same sub-module (CA01-031 == CA01-31)
    if len(parts) >= 2 and len(parts[1]) == 3 and parts[1].startswith("0") and parts[0] != "CB20":
        parts[1] = parts[1].lstrip("0").zfill(2)
    return "-".join(parts)

by_id_ml = defaultdict(list)
for m in cands:
    by_id_ml[(norm_id(m["id"]), m["ml"])].append(m)

rows = []

# main module rows
for mid, (cls, desc, bld, conf, mls) in MAIN.items():
    emitted = 0
    for ml in mls:
        pool = by_id_ml.get((mid, ml), [])
        # also allow evidence where mid appears as parent of a sub match
        if not pool:
            pool = [m for (i, l), ms in by_id_ml.items() if l == ml and i.startswith(mid + "-") for m in ms]
        if not pool:
            continue
        best = max(pool, key=score)
        rows.append({
            "module_id": mid, "class": cls, "description_from_context": desc,
            "building_or_area": bld, "evidence_quote": quote(best, mid),
            "source_doc": source_doc(ml), "source_url": url(ml), "confidence": conf,
        })
        emitted += 1
        if emitted >= 3:
            break
    if emitted == 0:
        print("WARNING: no evidence found for", mid, "in preferred MLs", mls)

# sub-module rows (two-level only)
sub_ids = sorted(set(i for (i, _) in by_id_ml
                     if re.fullmatch(r"[A-Z]{1,2}\d{2,3}-\d{2,3}", i)
                     and i.split("-")[0] in SUB_OK and i not in SUB_REJECT))
for sid in sub_ids:
    parent = sid.split("-")[0]
    num = sid.split("-")[1]
    if len(num) == 3 and not num.startswith("0"):
        continue  # 3-digit non-zero-padded = drawing/sheet numbers
    pcls, pdesc, pbld, _, _ = MAIN[parent]
    pool = [m for (i, ml), ms in by_id_ml.items() if i == sid for m in ms]
    best = max(pool, key=score)
    idx = best["ctx"].replace("_", "-").find(sid)
    window = best["ctx"].replace("_", "-")[max(0, idx - 70): idx + 70] if idx >= 0 else ""
    conf = "high" if re.search(r"sub-?\s?module|module", window, re.I) else "medium"
    # try to pull a short descriptive phrase: quoted title containing the id
    desc = ""
    mt = re.search(r"[\"“]([^\"”]{0,140}" + re.escape(sid) + r"[^\"”]{0,140})[\"”]",
                   best["ctx"].replace("_", "-"))
    if mt:
        desc = mt.group(1).strip()[:180]
    if not desc:
        desc = f"sub-module of {parent}"
    rows.append({
        "module_id": sid, "class": pcls, "description_from_context": desc,
        "building_or_area": pbld, "evidence_quote": quote(best, sid),
        "source_doc": source_doc(best["ml"]), "source_url": url(best["ml"]), "confidence": conf,
    })

rows.sort(key=lambda r: (r["module_id"].split("-")[0][:2], r["module_id"]))

out = base / "nrc_modules.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["module_id", "class", "description_from_context",
                                      "building_or_area", "evidence_quote", "source_doc",
                                      "source_url", "confidence"])
    w.writeheader()
    w.writerows(rows)

mains = sorted(set(r["module_id"] for r in rows if "-" not in r["module_id"]))
subs = sorted(set(r["module_id"] for r in rows if "-" in r["module_id"]))
print(f"wrote {len(rows)} rows: {len(mains)} main modules, {len(subs)} sub-modules")
print("mains:", ", ".join(mains))
