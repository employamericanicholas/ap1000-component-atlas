"""Add the module level to data/master.json: a registry of publicly documented AP1000
construction modules (sources as [label, url] pairs for hyperlinking), plus module
assignments on components where public documents support the mapping.
Curated major-module entries are enriched/extended with the two-agent harvest CSVs in
data/external/modules_harvest/ (NRC construction & vendor inspection records; literature)."""
import csv
import json
import os

d = json.load(open("data/master.json", encoding="utf-8"))

PSC = "https://psc.ga.gov/search/facts-document/?documentId="
NRC = "https://www.nrc.gov/docs/"
VCM11 = ["GA PSC VCM 11 (Aug 2014)", PSC + "154916"]
VCM12 = ["GA PSC VCM 12 (Feb 2015)", PSC + "157249"]
VCM910 = ["GA PSC VCM 9/10 (Feb 2014)", PSC + "152164"]
DCD38 = ["DCD Rev 19 Tier 2 sec. 3.8 (ML11171A431)", NRC + "ML1117/ML11171A431.pdf"]
SMCI_IR = ["NRC IR 99901439/2014-202 (ML14308A027)", NRC + "ML1430/ML14308A027.pdf"]
TOSHIBA = ["Toshiba, 5th MDEP Conf. (OECD-NEA, 2023)", "https://www.oecd-nea.org/mdep/events/conf-2023/presentations/S3/4.Toshiba.pdf"]
CUMMINS = ["Cummins (Westinghouse), AP1000 Plant Overview, LAS-ANS 2014 (illustrated module deck)",
           "https://las-ans.org.br/wp-content/uploads/2019/04/Panel-6-Ed-Cummins-July22-1600-1730.pdf"]
VOGTLE_FAB_DECK = ["Vogtle Supplier Compliance On/Offsite Fabrication deck (ML14322A365)",
                   NRC + "ML1432/ML14322A365.pdf"]

MODULES = [
 {"id": "CA01", "type": "Structural (containment internals)", "building": "Containment",
  "description": "T-shaped multicompartment 'super module' forming the central walls of the containment internal structures: refueling cavity/canal, reactor vessel compartment, and the two steam generator compartments (also houses the pressurizer compartment). 47 structural sub-modules (rail-shippable, up to 12x12x80 ft); ~92 ft x 96 ft x 76 ft per Westinghouse (DCD text: ~88x95x86 ft, ~40 sub-modules); lift weight ~1,069 t (2,357,000 lb).",
  "fabricator": "Sub-modules: Shaw/CB&I Lake Charles, LA (Unit 3); IHI + Toshiba, Japan (Unit 4); site assembly in the MAB",
  "origin": "Mixed (U3 Domestic / U4 sub-modules Foreign)",
  "sources": [["DCD Rev 19 Tier 2 sec. 3.8.3.6.1 (ML11171A431 pp. 40-41)", NRC + "ML1117/ML11171A431.pdf"], VCM11, CUMMINS, VOGTLE_FAB_DECK]},
 {"id": "CA02", "type": "Structural (containment internals)", "building": "Containment",
  "description": "Containment internal structures wall module forming part of the in-containment refueling water storage tank (IRWST); set with CA01/CA05 (joint license amendment at Vogtle).",
  "fabricator": "Shaw/CB&I Lake Charles, LA", "origin": "Domestic",
  "sources": [VCM11, DCD38]},
 {"id": "CA03", "type": "Structural (containment internals)", "building": "Containment",
  "description": "Forms the southwest wall of the in-containment refueling water storage tank (IRWST).",
  "fabricator": "Sub-modules: SMCI, Lakeland, FL (Unit 3 per VCM 11); Lake Charles scope",
  "origin": "Domestic",
  "sources": [VCM11]},
 {"id": "CA04", "type": "Structural (containment internals)", "building": "Containment",
  "description": "The reactor vessel cavity module, set inside the containment vessel bottom head. 5 sub-modules; 6.4 x 6.4 x 8.1 m; lift ~35.9 t (79,200 lb) per Westinghouse.",
  "fabricator": "Fabricated on the Vogtle site (Unit 3 decision per VCM 9/10); SMCI RV-cavity formwork modules",
  "origin": "Domestic",
  "sources": [VCM910, SMCI_IR]},
 {"id": "CA05", "type": "Structural (containment internals)", "building": "Containment",
  "description": "Large structural composite wall and access tunnel module inside containment; provides separation between different trains of safety-related equipment. Eight sub-modules.",
  "fabricator": "Sub-modules: CB&I Lake Charles, LA; assembled in the MAB", "origin": "Domestic",
  "sources": [VCM11]},
 {"id": "CA20", "type": "Structural (auxiliary building)", "building": "Auxiliary Building",
  "description": "Largest AP1000 module ('Auxiliary Building Areas 5 and 6 Module'): 72 sub-modules, >1,100 t as lifted (905 t / 1,996,000 lb bare steel; 20.5 x 14.2 x 21 m); auxiliary building structure containing the spent fuel pool, fuel transfer canal, and cask loading/washdown pit walls and floors.",
  "fabricator": "Sub-modules: CB&I Lake Charles, LA and Oregon Iron Works/Vigor, Clackamas, OR (Unit 4 split); assembled in the MAB",
  "origin": "Domestic",
  "sources": [VCM11, VCM12, ["NRC IR 99901425/2014-202 (ML14352A127)", NRC + "ML1435/ML14352A127.pdf"], DCD38]},
 {"id": "CB65", "type": "Structural (containment sump)", "building": "Containment",
  "description": "Containment sump module, set inside the containment vessel bottom head with CA04.",
  "fabricator": "Module program (Lake Charles/site)", "origin": "Domestic",
  "sources": [VCM11]},
 {"id": "CB66", "type": "Structural (containment sump)", "building": "Containment",
  "description": "Containment sump module, set inside the containment vessel bottom head with CA04.",
  "fabricator": "Module program (Lake Charles/site)", "origin": "Domestic",
  "sources": [VCM11]},
 {"id": "CB20", "type": "Structural (shield building)", "building": "Shield Building",
  "description": "Passive containment cooling water storage tank 'L' modules forming the PCCWST in the shield building roof; ~419 t as lifted, 26 m diameter x 10 m high (holds >3,000 t of water).",
  "fabricator": "Vigor Works LLC (formerly Oregon Iron Works), Clackamas, OR", "origin": "Domestic",
  "sources": [["NRC IR 99901448/2017-201 (ML17226A340)", NRC + "ML1722/ML17226A340.pdf"]]},
 {"id": "CH80", "type": "Structural steel (turbine island)", "building": "Turbine Building",
  "description": "First turbine-island structural steel module; with CH81A/CH81C/CH82, supports the turbine deck.",
  "fabricator": "Not publicly identified", "origin": "Unknown",
  "sources": [VCM910, VCM12]},
 {"id": "CH81A", "type": "Structural steel (turbine island)", "building": "Turbine Building",
  "description": "Turbine-island structural steel module supporting the turbine deck.",
  "fabricator": "Not publicly identified", "origin": "Unknown",
  "sources": [VCM910]},
 {"id": "CH81C", "type": "Structural steel (turbine island)", "building": "Turbine Building",
  "description": "Turbine-island structural steel module supporting the turbine deck.",
  "fabricator": "Not publicly identified", "origin": "Unknown",
  "sources": [VCM910]},
 {"id": "CH82", "type": "Structural steel (turbine island)", "building": "Turbine Building",
  "description": "Turbine-island structural steel module supporting the turbine deck.",
  "fabricator": "Not publicly identified", "origin": "Unknown",
  "sources": [VCM910]},
 {"id": "Q223", "type": "Mechanical equipment module", "building": "Containment",
  "description": "Direct vessel injection (DVI) line mechanical module (PXS); one of the Q-series mechanical modules combining piping, valves and supports.",
  "fabricator": "Aecon Industrial, Cambridge, Ontario, Canada", "origin": "Foreign",
  "sources": [["NRC IR 99901444/2016-201 (ML16228A086)", NRC + "ML1622/ML16228A086.pdf"]]},
 {"id": "(Piping modules)", "type": "Piping modules (various)", "building": "Various",
  "description": "Shop-fabricated safety-related piping modules (multiple IDs, not publicly enumerated).",
  "fabricator": "CB&I Laurens, SC (formerly B.F. Shaw); Westinghouse CES, Rock Hill, SC", "origin": "Domestic",
  "sources": [["NRC IR 99901432/2013-201 (ML13263A411)", NRC + "ML1326/ML13263A411.pdf"],
              ["NRC IR 99901438/2014-201 (ML14155A399)", NRC + "ML1415/ML14155A399.pdf"]]},
 {"id": "(Containment floor modules)", "type": "Structural (containment internals)", "building": "Containment",
  "description": "Safety-related containment floor section modules (IDs not publicly enumerated).",
  "fabricator": "Greenberry Industrial, Vancouver, WA / Corvallis, OR", "origin": "Domestic",
  "sources": [["NRC IR 99901480/2017-201 (ML17181A238)", NRC + "ML1718/ML17181A238.pdf"]]},
 {"id": "(IRWST/cavity formwork modules)", "type": "Structural formwork", "building": "Containment",
  "description": "Remain-in-place steel formwork modules for the IRWST walls and reactor vessel cavity.",
  "fabricator": "SMCI (MetalTek), Lakeland, FL", "origin": "Domestic",
  "sources": [SMCI_IR]},
]

# ---------------- merge the two-agent module harvest ----------------
HARVEST_FILES = [
    "data/external/modules_harvest/nrc/nrc_modules.csv",
    "data/external/modules_harvest/lit/lit_modules.csv",
]
TYPE_MAP = {"structural": "Structural", "mechanical": "Mechanical equipment module",
            "piping": "Piping module"}
FAB_MAP = {  # only where the sourcing is clear from the inspection reports
    "CA55": ("Greenberry Industrial, Vancouver, WA / Corvallis, OR", "Domestic"),
    "CA56": ("Greenberry Industrial, Vancouver, WA / Corvallis, OR", "Domestic"),
    "CA57": ("Greenberry Industrial, Vancouver, WA / Corvallis, OR", "Domestic"),
    "CA58": ("Greenberry Industrial, Vancouver, WA / Corvallis, OR", "Domestic"),
    "Q233": ("Aecon Industrial, Cambridge, Ontario (Q-series DVI pair with Q223)", "Foreign"),
    "Q240": ("Aecon Industrial, Cambridge, Ontario", "Foreign"),
    "Q305": ("Aecon Industrial, Cambridge, Ontario", "Foreign"),
    "Q601": ("Aecon Industrial, Cambridge, Ontario", "Foreign"),
    "KB36": ("Aecon Industrial, Cambridge, Ontario", "Foreign"),
    "KB37": ("CB&I Lake Charles, LA", "Domestic"),
    "R219": ("CB&I Lake Charles, LA", "Domestic"),
}
CONF_RANK = {"high": 2, "medium": 1, "low": 0}
curated = {m["id"]: m for m in MODULES}
agg = {}
for path in HARVEST_FILES:
    if not os.path.exists(path):
        continue
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        mid = (r.get("module_id") or "").strip().upper()
        # main modules only (skip sub-module rows and the counts pseudo-row)
        if not mid or "-" in mid or "(" in mid or "/" in mid:
            continue
        src = ((r.get("source_doc") or "").strip()[:80], (r.get("source_url") or "").strip())
        conf = CONF_RANK.get((r.get("confidence") or "").strip().lower(), 0)
        desc = (r.get("description_from_context") or "").strip()
        dims = (r.get("weight_or_dimensions") or "").strip()
        if mid in curated:
            m = curated[mid]
            if src[1] and src[1] not in [s[1] for s in m["sources"]] and len(m["sources"]) < 5:
                m["sources"].append(list(src))
            continue
        e = agg.setdefault(mid, {"best": (-1, ""), "dims": "", "cls": "", "bldg": "", "sources": []})
        if (conf, len(desc)) > (e["best"][0], len(e["best"][1])):
            e["best"] = (conf, desc)
            e["cls"] = (r.get("class") or "").strip().lower()
            e["bldg"] = (r.get("building_or_area") or "").strip()
        if dims and not e["dims"]:
            e["dims"] = dims
        if src[1] and src[1] not in [s[1] for s in e["sources"]] and len(e["sources"]) < 4:
            e["sources"].append(list(src))

for mid in sorted(agg):
    e = agg[mid]
    fab, org = FAB_MAP.get(mid, ("Not stated in public sources", "Unknown"))
    desc = e["best"][1] or "Module identified in public inspection records; function not described."
    if e["dims"]:
        desc += f" [{e['dims']}]"
    conf_note = " (LOW-CONFIDENCE ID: seen only in document prefixes)" if e["best"][0] == 0 else ""
    MODULES.append({
        "id": mid,
        "type": TYPE_MAP.get(e["cls"], "Module (class not stated)"),
        "building": e["bldg"] or "Not stated",
        "description": desc + conf_note,
        "fabricator": fab,
        "origin": org,
        "sources": e["sources"] or [["(no URL captured)", ""]],
    })
print(f"harvest merged: +{len(agg)} modules beyond curated {len(curated)}")

# component -> (module, relationship); only where public documents support the association
ASSIGN = {
    "RCS-MB-01": ("CA01", "Housed in module compartment (SG compartment)"),
    "RCS-MB-02": ("CA01", "Housed in module compartment (SG compartment)"),
    "RCS-MV-02": ("CA01", "Housed in module compartment (pressurizer compartment)"),
    "RCS-MP-01A": ("CA01", "Housed in module compartment (SG compartment)"),
    "RCS-MP-01B": ("CA01", "Housed in module compartment (SG compartment)"),
    "RCS-MP-02A": ("CA01", "Housed in module compartment (SG compartment)"),
    "RCS-MP-02B": ("CA01", "Housed in module compartment (SG compartment)"),
    "RCS-MP-01A/B": ("CA01", "Housed in module compartment (SG compartment)"),
    "RCS-MP-02A/B": ("CA01", "Housed in module compartment (SG compartment)"),
    "RCS-MV-01": ("CA04", "Housed in module (reactor vessel cavity)"),
    "RXS-MV-01": ("CA04", "Housed in module (reactor vessel cavity)"),
    "RXS-MN-01": ("CA04", "Installed on module walls (RV cavity reflective insulation)"),
    "PXS-MT-03": ("CA02/CA03", "Tank formed by module walls (IRWST)"),
    "PXS-MT-04": ("CA02/CA03", "Attached to IRWST structure (gutter)"),
    "PXS-ME-01": ("CA02/CA03", "Located inside the IRWST"),
    "PXS-MY-Y01A": ("CA02/CA03", "Located inside the IRWST (screen)"),
    "PXS-MY-Y01B": ("CA02/CA03", "Located inside the IRWST (screen)"),
    "PXS-MY-Y01C": ("CA02/CA03", "Located inside the IRWST (screen)"),
    "FHS-FS-01": ("CA20", "Housed in module (new fuel storage area)"),
    "FHS-FS-02": ("CA20", "Housed in module (spent fuel pool)"),
    "FHS-MY-Y01": ("CA20", "Installed in module structure (spent fuel transfer gate)"),
    "FHS-MY-Y02": ("CA20", "Installed in module structure (cask loading pit gate)"),
    "FHS-MT-02": ("CA20", "Formed by module structure (fuel transfer canal)"),
    "FHS-FT-01": ("CA20", "Penetrates module structure (fuel transfer tube)"),
    "PCS-MT-01": ("CB20", "Tank formed by module sections (PCCWST L-modules)"),
}

n = 0
for c in d["components"]:
    t = c.get("tag")
    if t in ASSIGN:
        mod, rel = ASSIGN[t]
        c["module"], c["module_relationship"] = mod, rel
        n += 1
    else:
        c["module"], c["module_relationship"] = "", ""

d["modules"] = MODULES
d["module_note"] = ("Module registry compiled from public sources: DCD Rev 19 sec. 3.8; GA PSC VCM reports; NRC "
                    "construction & vendor inspection reports (Vogtle 3&4 and V.C. Summer 2&3); the illustrated "
                    "Westinghouse module deck (Cummins, LAS-ANS 2014) which gives the official count - 122 structural "
                    "+ 154 piping + 55 mechanical + 11 electrical = 342 modules; and trade press. This registry holds "
                    "every module ID found in the public record (~47 main modules plus ~128 sub-module IDs preserved "
                    "in data/external/modules_harvest/); the complete per-ID list and component-to-module routing "
                    "remain Westinghouse-proprietary (APP-series drawings). Component module assignments are limited "
                    "to associations documented in public sources; blank does not mean field-installed.")
json.dump(d, open("data/master.json", "w", encoding="utf-8"), indent=1)
print(f"modules: {len(MODULES)} | components assigned: {n}")
