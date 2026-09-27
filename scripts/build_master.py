"""Merge Table 3.2-3 + Tier 1 equipment into the master AP1000 component dataset.
Outputs data/master.json (also copied to web/data/plant.json) and data/master.csv."""
import json
import re
import csv
from collections import Counter, defaultdict

d323 = json.load(open("data/components_3_2_3.json", encoding="utf-8"))
t1 = json.load(open("data/tier1_equipment.json", encoding="utf-8"))

BUILDINGS = ["Containment", "Shield Building", "Auxiliary Building", "Annex Building",
             "Turbine Building", "Diesel Generator Building", "Radwaste Building", "Yard"]

def norm_tag(t):
    return re.sub(r"\s+", "", (t or "")).upper()

def buildings_from_location(loc):
    if not loc:
        return []
    out = []
    l = loc.lower()
    if "containment" in l and "shield" not in l:
        out.append("Containment")
    if "shield" in l:
        out.append("Shield Building")
        if "containment" in l:
            out.insert(0, "Containment")
    if "aux" in l:
        out.append("Auxiliary Building")
    if "annex" in l:
        out.append("Annex Building")
    if "turbine" in l:
        out.append("Turbine Building")
    if "diesel" in l:
        out.append("Diesel Generator Building")
    if "radwaste" in l:
        out.append("Radwaste Building")
    if "yard" in l or "intake" in l:
        out.append("Yard")
    if not out:
        out.append("Various")
    return out

# ---- normalize Tier 1 attribute column names ----
ATTR_MAP = {
    "seismic cat. i": "tier1_seismic_cat_I",
    "seismic cat 1": "tier1_seismic_cat_I",
    "seismic category i": "tier1_seismic_cat_I",
    "asme code section iii": "tier1_asme_III",
    "asme code section iii classification": "tier1_asme_III",
    "class 1e/ qual. for harsh envir.": "tier1_class_1E_harsh",
    "class 1e/ qual. harsh envir.": "tier1_class_1E_harsh",
    "class 1e/ qual for harsh envir.": "tier1_class_1E_harsh",
    "remotely operated valve": "tier1_remote_valve",
    "active function": "tier1_active_function",
    "safety- related display": "tier1_safety_display",
    "safety-related display": "tier1_safety_display",
    "loss of motive power position": "tier1_loss_power_position",
    "component location": "tier1_location",
    "location": "tier1_location",
    "control pms/ das": "tier1_control_pms_das",
    "control pms/das": "tier1_control_pms_das",
    "control pms/das(1)": "tier1_control_pms_das",
    "control pms": "tier1_control_pms",
}

def norm_attrs(attrs):
    out = {}
    other = {}
    for k, v in attrs.items():
        nk = ATTR_MAP.get(k.lower().strip())
        if nk:
            out[nk] = v
        else:
            other[k] = v
    if other:
        out["tier1_other"] = "; ".join(f"{k}={v}" for k, v in other.items())
    return out

# ---- index Tier 1 by tag ----
t1_by_tag = defaultdict(list)
for r in t1["equipment"]:
    nt = norm_tag(r["tag"])
    if nt and nt not in ("N/A", "-", "NA"):
        t1_by_tag[nt].append(r)

# ---- base records from 3.2-3 ----
master = []
seen_tags = set()
for c in d323["components"]:
    nt = norm_tag(c["tag"])
    rec = {
        "tag": nt if nt and nt != "N/A" else "n/a",
        "description": c["description"],
        "system_code": c["system_code"],
        "system_name": c["system_name"],
        "location": c["location"],
        "buildings": buildings_from_location(c["location"]),
        "ap1000_class": c["ap1000_class"],
        "seismic_category": c["seismic_category"],
        "construction_code": c["construction_code"],
        "comments": c["comments"],
        "in_table_3_2_3": True,
        "in_tier1": False,
        "tier1_table": None,
        "source": "DCD Tier 2 Table 3.2-3 (ML11171A425)",
    }
    hits = t1_by_tag.get(nt, [])
    if hits:
        rec["in_tier1"] = True
        rec["tier1_table"] = hits[0]["tier1_table"]
        rec["source"] += f"; Tier 1 {hits[0]['tier1_table']} ({hits[0]['file']})"
        merged = {}
        for h in hits:
            merged.update(norm_attrs(h["attributes"]))
        rec.update(merged)
        if not rec["description"] and hits[0]["equipment_name"]:
            rec["description"] = hits[0]["equipment_name"]
    master.append(rec)
    if nt and nt != "N/A":
        seen_tags.add(nt)

# ---- system code -> name map (3.2-3 first, Tier 1 section titles as fallback) ----
sys_names = {code: s["name"] for code, s in d323["systems"].items()}
sys_locs = {code: s["location"] for code, s in d323["systems"].items()}
FALLBACK_SYS = {
    "ECS": "Main AC Power System", "IDS": "Class 1E DC and UPS System",
    "EDS": "Non-Class 1E DC and UPS System", "PMS": "Protection and Safety Monitoring System",
    "DAS": "Diverse Actuation System", "PLS": "Plant Control System",
    "DDS": "Data Display and Processing System", "OCS": "Operation and Control Centers System",
    "RMS": "Radiation Monitoring System", "EGS": "Grounding and Lightning Protection System",
    "ELS": "Plant Lighting System", "EQS": "Special Process Heat Tracing System",
    "ZAS": "Main Generation System", "ZBS": "Transmission Switchyard and Offsite Power System",
    "ZVS": "Excitation and Voltage Regulation System", "ZRS": "Onsite Standby Power System",
}

def sys_for_tag(tag, section_title):
    seg = tag.split("-")[0]
    m = re.match(r"([A-Z]{2,3})", seg)
    code = m.group(1) if m else seg
    # IDS trains: IDSA/IDSB/... -> IDS
    if seg.startswith("IDS"):
        code = "IDS"
    name = sys_names.get(code) or FALLBACK_SYS.get(code) or section_title or f"System {code}"
    return code, name

# ---- add Tier 1-only equipment ----
for nt, hits in t1_by_tag.items():
    if nt in seen_tags:
        continue
    h0 = hits[0]
    code, name = sys_for_tag(nt, h0["section_title"])
    merged = {}
    for h in hits:
        merged.update(norm_attrs(h["attributes"]))
    loc = merged.get("tier1_location") or sys_locs.get(code)
    rec = {
        "tag": nt,
        "description": h0["equipment_name"],
        "system_code": code,
        "system_name": name,
        "location": loc,
        "buildings": buildings_from_location(loc),
        "ap1000_class": "",
        "seismic_category": "I" if merged.get("tier1_seismic_cat_I", "").lower().startswith("yes") else "",
        "construction_code": merged.get("tier1_asme_III", ""),
        "comments": "",
        "in_table_3_2_3": False,
        "in_tier1": True,
        "tier1_table": h0["tier1_table"],
        "source": f"DCD Tier 1 {h0['tier1_table']} ({h0['file']})",
    }
    rec.update(merged)
    master.append(rec)

# ---- structures (Table 3.2-2) ----
structures = [
    {"name": "Nuclear Island Basemat / Containment Interior Structures", "seismic": "C-I"},
    {"name": "Containment Vessel", "seismic": "C-I"},
    {"name": "Shield Building", "seismic": "C-I"},
    {"name": "Auxiliary Building", "seismic": "C-I"},
    {"name": "Plant Vent and Stair Structure", "seismic": "C-II"},
    {"name": "Turbine Building - first bay adjacent to Nuclear Island", "seismic": "C-II"},
    {"name": "Turbine Building - remainder", "seismic": "NS"},
    {"name": "Annex Building (Columns A-E)", "seismic": "NS"},
    {"name": "Annex Building (Columns E-...)", "seismic": "C-II"},
    {"name": "Radwaste Building", "seismic": "NS"},
    {"name": "Diesel-Generator Building", "seismic": "NS"},
    {"name": "Circulating Water Pumphouse and Towers", "seismic": "NS"},
]

# ---- class definition crosswalk (Table 3.2-1) ----
class_defs = [
    {"ap1000_class": "A", "ans_safety_class": "SC-1", "seismic": "I", "asme_iii_class": "1", "quality_group": "A", "appendix_b": "Yes"},
    {"ap1000_class": "B", "ans_safety_class": "SC-2", "seismic": "I", "asme_iii_class": "2", "quality_group": "B", "appendix_b": "Yes"},
    {"ap1000_class": "C", "ans_safety_class": "SC-3", "seismic": "I", "asme_iii_class": "3", "quality_group": "C", "appendix_b": "Yes"},
    {"ap1000_class": "D", "ans_safety_class": "NNS", "seismic": "NA", "asme_iii_class": "NA", "quality_group": "D", "appendix_b": "No"},
    {"ap1000_class": "E/L/P/R/W (Other)", "ans_safety_class": "NNS", "seismic": "NA", "asme_iii_class": "NA", "quality_group": "NA", "appendix_b": "No"},
]

# ---- systems summary ----
sys_summary = {}
for r in master:
    code = r["system_code"] or "?"
    s = sys_summary.setdefault(code, {
        "code": code,
        "name": r["system_name"],
        "location": sys_locs.get(code) or r["location"],
        "buildings": [],
        "component_count": 0,
        "class_counts": Counter(),
    })
    s["component_count"] += 1
    s["class_counts"][r["ap1000_class"] or "(Tier 1 only)"] += 1
    for b in r["buildings"]:
        if b not in s["buildings"]:
            s["buildings"].append(b)
for code, s in d323["systems"].items():
    if code not in sys_summary:
        sys_summary[code] = {"code": code, "name": s["name"], "location": s["location"],
                             "buildings": buildings_from_location(s["location"]),
                             "component_count": 0, "class_counts": Counter()}
    sys_summary[code]["notes"] = "; ".join(s.get("notes", []))
for s in sys_summary.values():
    s["class_counts"] = dict(s["class_counts"])
    s.setdefault("notes", "")

# ---- document index ----
docs = []
for line in open("data/raw/dcd_manifest.tsv", encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if len(parts) != 2:
        continue
    title, url = parts
    ml = url.split("/")[-1].replace(".pdf", "")
    docs.append({"ml": ml, "title": title.split(" - ", 1)[-1] if " - " in title else title, "url": url})

out = {
    "meta": {
        "title": "AP1000 Component Database",
        "source": "Westinghouse AP1000 Design Control Document Rev. 19 (NRC ADAMS package ML11171A500)",
        "extracted": "2026-09-27",
        "component_count": len(master),
        "system_count": len(sys_summary),
    },
    "class_definitions": class_defs,
    "table_notes": d323.get("table_notes", ""),
    "structures": structures,
    "systems": sorted(sys_summary.values(), key=lambda s: s["code"]),
    "components": master,
    "documents": docs,
}
json.dump(out, open("data/master.json", "w", encoding="utf-8"), indent=1)

# CSV
cols = ["tag", "description", "system_code", "system_name", "location", "buildings",
        "ap1000_class", "seismic_category", "construction_code", "comments",
        "in_table_3_2_3", "in_tier1", "tier1_table", "tier1_asme_III", "tier1_seismic_cat_I",
        "tier1_class_1E_harsh", "tier1_remote_valve", "tier1_active_function",
        "tier1_safety_display", "tier1_loss_power_position", "tier1_location",
        "tier1_control_pms_das", "tier1_control_pms", "tier1_other", "source"]
with open("data/master.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in master:
        r2 = dict(r)
        r2["buildings"] = "; ".join(r["buildings"])
        w.writerow(r2)

print("master components:", len(master))
print("  from 3.2-3:", sum(1 for r in master if r["in_table_3_2_3"]))
print("  tier1-only:", sum(1 for r in master if not r["in_table_3_2_3"]))
print("  in both:", sum(1 for r in master if r["in_table_3_2_3"] and r["in_tier1"]))
print("systems:", len(sys_summary))
print("docs:", len(docs))
print("buildings:", Counter(b for r in master for b in r["buildings"]))
