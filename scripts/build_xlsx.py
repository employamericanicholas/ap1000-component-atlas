"""Build AP1000_Component_Database.xlsx from data/master.json."""
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

d = json.load(open("data/master.json", encoding="utf-8"))
comps = d["components"]
systems = d["systems"]
docs = d["documents"]

ARIAL = "Arial"
HDR_FILL = PatternFill("solid", fgColor="1F3B57")
HDR_FONT = Font(name=ARIAL, bold=True, color="FFFFFF", size=10)
BASE = Font(name=ARIAL, size=10)
BOLD = Font(name=ARIAL, size=10, bold=True)
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
BLUE = Font(name=ARIAL, size=10, color="0000FF")
THIN = Border(bottom=Side(style="thin", color="D9D9D9"))

wb = Workbook()

def style_header(ws, ncols, row=1):
    for j in range(1, ncols + 1):
        c = ws.cell(row=row, column=j)
        c.font = HDR_FONT
        c.fill = HDR_FILL
        c.alignment = Alignment(vertical="center", wrap_text=True)

def set_widths(ws, widths):
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w

# ---------------- README ----------------
ws = wb.active
ws.title = "README"
rows = [
    ("AP1000 COMPONENT DATABASE", ""),
    ("", ""),
    ("Source", "Westinghouse AP1000 Design Control Document Rev. 19 (June 2011), NRC ADAMS package ML11171A500"),
    ("Core table", "Tier 2, Table 3.2-3 'Classification of Mechanical and Fluid Systems, Components, and Equipment' (ML11171A425)"),
    ("Enrichment", "Tier 1 Chapter 2 ITAAC equipment tables (7 documents: ML11171A308/310/311/312/313/314/316)"),
    ("Extracted", d["meta"]["extracted"] + " by automated table parsing; verify critical values against the linked source PDF"),
    ("Components", str(len(comps))),
    ("Systems", str(len(systems))),
    ("", ""),
    ("SHEETS", ""),
    ("Modules", "TOP LEVEL: registry of publicly documented AP1000 construction modules (structural CA/CB/CH, mechanical Q-series, piping) with fabricator, origin, and sources. The full ~350-module list and component-to-module routing are Westinghouse-proprietary; component assignments are made only where public documents support them."),
    ("Components", "Master component list. One row per component/equipment item. Columns G-H link each component to its module where publicly documented. Supplier columns U-Z are researched assignments (see basis column); yellow columns AA-AC are YOURS to fill in."),
    ("Suppliers", "Curated supplier list: manufacturer, plant location(s), Domestic/Foreign origin, scope, sources. Applied to Components via documented match rules."),
    ("Supplier Evidence", "Every raw sourced claim from the research (Georgia PSC Vogtle docket, NRC vendor inspection reports, press/industry) with verbatim quotes and URLs."),
    ("Systems", "One row per plant system, with component counts by class (live COUNTIFS formulas)."),
    ("Structures", "Seismic classification of buildings and structures (Table 3.2-2)."),
    ("Class Definitions", "AP1000 class crosswalk to ASME/ANS/quality group (Table 3.2-1) and Table 3.2-3 notes."),
    ("Documents", "All 174 documents of the DCD Rev. 19 package, hyperlinked to NRC.gov."),
    ("Cost Accounts (TIMCAT)", "EEDB code-of-accounts cost data from MIT TIMCAT (github.com/mit-crpg/TIMCAT): PWR12-ME basis + AP1000-surrogate (LPSR) component parameters. Factory vs site cost split supports domestic-content decomposition."),
    ("AP1000 Cost Est. (INL)", "Per-account AP1000 cost estimates from INL/RPT-24-77048 (GAIN meta-analysis, 2024; osti.gov/biblio/2371533) - Stewart FOAK/NOAK and Shirvan TIMCAT estimates in GNCOA accounts."),
    ("", ""),
    ("HOW TO USE FOR DOMESTIC CONTENT WORK", ""),
    ("1.", "Filter the Components sheet (row 1 has AutoFilter) by system, class, or building."),
    ("2.", "Fill the yellow input columns: 'DC Category', 'Supply Origin', 'DC Notes'. Everything else is source data - leave it intact."),
    ("2b.", "Supplier columns: assignments are package-level (e.g., all SGS-MB tags -> Doosan) and Vogtle 3&4-era; 'Not publicly disclosed' means no public source names a vendor for that tag. Check 'Supplier Match Basis' for confidence before relying on a row."),
    ("3.", "Classes A-C are safety-related (10 CFR 50 App. B nuclear QA) - the hardest to source domestically."),
    ("4.", "Turbine-island systems marked 'Class E' in Systems notes have no itemized parts list in the DCD."),
    ("", ""),
    ("Example of expected input format (illustrative only):", ""),
    ("DC Category", "NSSS major equipment   |   Supply Origin: Domestic - Doosan/IHI historically   |   DC Notes: RPV forgings imported for Vogtle"),
    ("", ""),
    ("LEGEND", ""),
    ("Yellow fill", "Cells you are expected to edit"),
    ("Blue text", "Hardcoded values entered by hand (all other data extracted programmatically)"),
]
for i, (a, b) in enumerate(rows, 1):
    ws.cell(row=i, column=1, value=a).font = BOLD if (b == "" or a.isupper() or a.endswith(".")) else BASE
    ws.cell(row=i, column=2, value=b).font = BASE
ws.cell(row=1, column=1).font = Font(name=ARIAL, size=16, bold=True, color="1F3B57")
ws.cell(row=24, column=1).fill = INPUT_FILL
set_widths(ws, [26, 120])

# ---------------- Modules (top level) ----------------
ws = wb.create_sheet("Modules")
MAX_SRC = max(len(m["sources"]) for m in d.get("modules", []))
mh = (["Module ID", "Type", "Building", "Description", "Fabricator (Vogtle 3&4 era)",
       "Origin", "Components mapped (see Components cols G-H)"]
      + [f"Source {k+1}" for k in range(MAX_SRC)])
ws.append([d.get("module_note", "")])
ws.cell(row=1, column=1).font = Font(name=ARIAL, size=9, italic=True, color="666666")
ws.append(mh)
style_header(ws, len(mh), row=2)
LINK_FONT = Font(name=ARIAL, size=10, color="0563C1", underline="single")
mrow = 3
CN_M = len(comps) + 1
for m in d.get("modules", []):
    ws.append([m["id"], m["type"], m["building"], m["description"], m["fabricator"],
               m["origin"],
               f'=COUNTIF(Components!$G$2:$G${CN_M},"*"&A{mrow}&"*")' if not m["id"].startswith("(") else 0])
    for k, src in enumerate(m["sources"]):
        label, url = src
        c = ws.cell(row=mrow, column=8 + k, value=label)
        c.hyperlink = url
        c.font = LINK_FONT
    for cell in ws[mrow]:
        if cell.font != LINK_FONT:
            cell.font = BASE
        cell.border = THIN
        cell.alignment = Alignment(vertical="top", wrap_text=True)
    mrow += 1
ws.freeze_panes = "A3"
ws.auto_filter.ref = f"A2:{get_column_letter(len(mh))}{mrow-1}"
set_widths(ws, [12, 30, 18, 80, 46, 12, 14] + [40] * MAX_SRC)

# ---------------- Components ----------------
ws = wb.create_sheet("Components")
headers = ["Tag", "Description", "System Code", "System Name", "Location", "Buildings",
           "Module", "Module Relationship",
           "AP1000 Class", "Seismic Category", "Construction Code", "Comments",
           "In Table 3.2-3", "In Tier 1", "Tier 1 Table", "ASME III (T1)", "Class 1E/Harsh (T1)",
           "Remote Valve (T1)", "Active Function (T1)", "Loss-of-Power Position (T1)",
           "Supplier Name", "Supplier Mfg Location", "Supplier Other Locations",
           "Supplier Origin (Domestic/Foreign)", "Supplier Source URL(s)", "Supplier Match Basis",
           "DC Category", "Supply Origin", "DC Notes",
           "Other Tier 1 Attributes", "Source", "Source Doc URL"]
ws.append(headers)
style_header(ws, len(headers))
import re as _re
for c in comps:
    mls = _re.findall(r"ML\d{8}[A-Z]\d{3}", c.get("source", ""))
    url = f"https://www.nrc.gov/docs/{mls[0][:6]}/{mls[0]}.pdf" if mls else ""
    ws.append([
        c.get("tag"), c.get("description"), c.get("system_code"), c.get("system_name"),
        c.get("location"), "; ".join(c.get("buildings") or []),
        c.get("module"), c.get("module_relationship"),
        c.get("ap1000_class"), c.get("seismic_category"), c.get("construction_code"),
        c.get("comments"),
        "Yes" if c.get("in_table_3_2_3") else "No", "Yes" if c.get("in_tier1") else "No",
        c.get("tier1_table"), c.get("tier1_asme_III"), c.get("tier1_class_1E_harsh"),
        c.get("tier1_remote_valve"), c.get("tier1_active_function"),
        c.get("tier1_loss_power_position"),
        c.get("supplier_name"), c.get("supplier_mfg_location"), c.get("supplier_other_locations"),
        c.get("supplier_origin"), c.get("supplier_source"), c.get("supplier_basis"),
        "", "", "",
        c.get("tier1_other"), c.get("source"), url,
    ])
n = len(comps) + 1
for row in ws.iter_rows(min_row=2, max_row=n):
    for cell in row:
        cell.font = BASE
        cell.border = THIN
    for j in (27, 28, 29):  # user input columns AA,AB,AC
        row[j - 1].fill = INPUT_FILL
ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{n}"
ws.freeze_panes = "C2"
set_widths(ws, [17, 42, 9, 30, 26, 24, 12, 30, 9, 9, 15, 22, 8, 8, 10, 10, 12, 10, 10, 12,
                26, 26, 26, 14, 40, 30, 16, 16, 24, 28, 34, 30])

# ---------------- Systems ----------------
# Suggested EEDB (Energy Economic Data Base) cost-account mapping for cost/domestic-content
# rollups. Only assigned where the mapping is unambiguous; verify before relying on it.
EEDB_MAP = {
    "RXS": "221 Reactor Equipment", "RCS": "222 Main Heat Transport", "SGS": "222 Main Heat Transport",
    "PXS": "223 Safeguards Systems", "RNS": "223 Safeguards Systems", "VES": "223 Safeguards Systems",
    "WLS": "224 Radwaste Processing", "WGS": "224 Radwaste Processing", "WSS": "224 Radwaste Processing",
    "WRS": "224 Radwaste Processing", "RDS": "224 Radwaste Processing",
    "FHS": "225 Fuel Handling & Storage",
    "SFS": "226 Other Reactor Plant Equip.", "CVS": "226 Other Reactor Plant Equip.",
    "CCS": "226 Other Reactor Plant Equip.", "PSS": "226 Other Reactor Plant Equip.",
    "CNS": "221/222 (containment vessel under 21x structures)",
    "PMS": "227 Reactor Instrumentation & Control", "DAS": "227 Reactor Instrumentation & Control",
    "IIS": "227 Reactor Instrumentation & Control", "PLS": "227 Reactor Instrumentation & Control",
    "DDS": "227 Reactor Instrumentation & Control", "OCS": "227 Reactor Instrumentation & Control",
    "RMS": "227 Reactor Instrumentation & Control",
    "MTS": "231 Turbine Generator", "GSS": "231 Turbine Generator", "LOS": "231 Turbine Generator",
    "TCS": "231 Turbine Generator", "ZAS": "231 Turbine Generator", "ZVS": "231 Turbine Generator",
    "CDS": "233 Condensing Systems", "CMS": "233 Condensing Systems", "CES": "233 Condensing Systems",
    "CPS": "233 Condensing Systems",
    "FWS": "234 Feedwater Heating", "HDS": "234 Feedwater Heating",
    "ASS": "235 Other Turbine Plant Equip.", "BDS": "235 Other Turbine Plant Equip.",
    "HSS": "235 Other Turbine Plant Equip.", "SSS": "235 Other Turbine Plant Equip.",
    "MSS": "235 Other Turbine Plant Equip.",
    "ECS": "24x Electric Plant Equipment", "IDS": "24x Electric Plant Equipment",
    "EDS": "24x Electric Plant Equipment", "ELS": "24x Electric Plant Equipment",
    "EGS": "24x Electric Plant Equipment", "ZOS": "24x Electric Plant Equipment",
    "ZBS": "24x Electric Plant Equipment",
    "SWS": "26x Heat Rejection", "CWS": "26x Heat Rejection",
}
ws = wb.create_sheet("Systems")
sh = ["Code", "System Name", "Location", "Buildings", "Components", "Class A", "Class B",
      "Class C", "Class D", "Other/Notes cls", "Tier 1 only", "EEDB Account (suggested)", "System Notes"]
ws.append(sh)
style_header(ws, len(sh))
CN = len(comps) + 1
for i, s in enumerate(sorted(systems, key=lambda x: x["code"]), start=2):
    code = s["code"]
    rng = f"Components!$C$2:$C${CN}"
    cls = f"Components!$I$2:$I${CN}"
    ws.cell(row=i, column=1, value=code)
    ws.cell(row=i, column=2, value=s["name"])
    ws.cell(row=i, column=3, value=s.get("location"))
    ws.cell(row=i, column=4, value="; ".join(s.get("buildings") or []))
    ws.cell(row=i, column=5, value=f'=COUNTIF({rng},$A{i})')
    for j, k in ((6, "A"), (7, "B"), (8, "C"), (9, "D")):
        ws.cell(row=i, column=j, value=f'=COUNTIFS({rng},$A{i},{cls},"{k}")')
    ws.cell(row=i, column=10, value=(
        f'=E{i}-SUM(F{i}:I{i})-K{i}'))
    ws.cell(row=i, column=11, value=f'=COUNTIFS({rng},$A{i},{cls},"")')
    ws.cell(row=i, column=12, value=EEDB_MAP.get(code, ""))
    ws.cell(row=i, column=13, value=s.get("notes") or "")
for row in ws.iter_rows(min_row=2, max_row=len(systems) + 1):
    for cell in row:
        cell.font = BASE
        cell.border = THIN
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:M{len(systems)+1}"
set_widths(ws, [8, 40, 30, 30, 12, 9, 9, 9, 9, 13, 11, 34, 60])

# ---------------- Structures ----------------
ws = wb.create_sheet("Structures")
ws.append(["Structure", "Seismic Category", "Source"])
style_header(ws, 3)
for s in d["structures"]:
    ws.append([s["name"], s["seismic"], "DCD Tier 2 Table 3.2-2 (ML11171A425)"])
for row in ws.iter_rows(min_row=2, max_row=len(d["structures"]) + 1):
    for cell in row:
        cell.font = BASE
        cell.border = THIN
set_widths(ws, [60, 16, 40])

# ---------------- Class Definitions ----------------
ws = wb.create_sheet("Class Definitions")
ws.append(["AP1000 Class", "ANS Safety Class", "Seismic", "ASME III Class", "NRC Quality Group", "10 CFR 50 App. B QA"])
style_header(ws, 6)
for r in d["class_definitions"]:
    ws.append([r["ap1000_class"], r["ans_safety_class"], r["seismic"], r["asme_iii_class"],
               r["quality_group"], r["appendix_b"]])
ws.append([])
ws.append(["Table 3.2-3 notes:"])
ws.cell(row=ws.max_row, column=1).font = BOLD
for line in (d.get("table_notes") or "").split("\n"):
    if line.strip():
        ws.append([line.strip()])
for row in ws.iter_rows(min_row=2):
    for cell in row:
        if cell.font != BOLD:
            cell.font = BASE
ws.append([])
ws.append(["Source: DCD Tier 2 Table 3.2-1 and Table 3.2-3 notes (ML11171A425)"])
set_widths(ws, [20, 18, 10, 14, 18, 18])

# ---------------- Documents ----------------
ws = wb.create_sheet("Documents")
ws.append(["ML Accession No.", "Title", "Link"])
style_header(ws, 3)
for i, doc in enumerate(docs, start=2):
    ws.cell(row=i, column=1, value=doc["ml"]).font = BASE
    ws.cell(row=i, column=2, value=doc["title"]).font = BASE
    c = ws.cell(row=i, column=3, value=f'=HYPERLINK("{doc["url"]}","open PDF")')
    c.font = Font(name=ARIAL, size=10, color="0563C1", underline="single")
ws.freeze_panes = "A2"
set_widths(ws, [18, 110, 12])

# ---------------- Suppliers (curated) ----------------
if "supplier_map" in d:
    sm = d["supplier_map"]
    ws = wb.create_sheet("Suppliers", 2)
    sh = ["Supplier", "Manufacturing Location", "Other Locations", "Origin (Domestic/Foreign)",
          "Supplies (scope of mapped components)", "Components Matched", "Source URLs", "Key Evidence"]
    ws.append(sh)
    style_header(ws, len(sh))
    # scope text per supplier from rules
    scope = {}
    for r in sm["rules"]:
        scope.setdefault(r["supplier"], []).append(r.get("scope_note") or str(r["match"].get("value", "")))
    for sid, s in sm["suppliers"].items():
        srcs = s.get("sources", [])
        cnt = sum(1 for c in comps if c.get("supplier_name") == s["name"])
        ws.append([
            s["name"], s.get("manufacturing_location", ""), s.get("other_locations", ""),
            s.get("origin", ""), "; ".join(dict.fromkeys(scope.get(sid, []))), cnt,
            "\n".join(x["url"] for x in srcs),
            "\n".join(f'{x.get("doc","")}: "{x.get("quote","")}"' for x in srcs if x.get("quote")),
        ])
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = BASE
            cell.border = THIN
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:H{ws.max_row}"
    set_widths(ws, [30, 30, 30, 14, 44, 12, 50, 70])

# ---------------- external cost data sheets ----------------
import csv

def csv_sheet(name, path, note, widths=None, number_cols=()):
    ws = wb.create_sheet(name)
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    ws.append([note])
    ws.cell(row=1, column=1).font = Font(name=ARIAL, size=9, italic=True, color="666666")
    for r_i, r in enumerate(rows):
        out = []
        for c_i, v in enumerate(r):
            if r_i > 0 and c_i in number_cols and v not in ("", None):
                try:
                    v = float(v)
                except ValueError:
                    pass
            out.append(v)
        ws.append(out)
    style_header(ws, len(rows[0]), row=2)
    for row in ws.iter_rows(min_row=3):
        for cell in row:
            cell.font = BASE
            if isinstance(cell.value, float):
                cell.number_format = "#,##0"
    ws.freeze_panes = "A3"
    from openpyxl.utils import get_column_letter as gcl
    ws.auto_filter.ref = f"A2:{gcl(len(rows[0]))}{len(rows)+1}"
    if widths:
        set_widths(ws, widths)
    return ws

# ---------------- Supplier Evidence (raw research rows) ----------------
import os
EVIDENCE = [
    ("Georgia PSC (Vogtle docket)", "data/external/gapsc/ga_psc_suppliers.csv"),
    ("NRC vendor inspections", "data/external/nrc_vendors/nrc_vendor_suppliers.csv"),
    ("Press / industry reports", "data/external/press/press_suppliers.csv"),
]
ev_rows = []
for label, path in EVIDENCE:
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            rd = csv.DictReader(f)
            for r in rd:
                r["research_source"] = label
                ev_rows.append(r)
if ev_rows:
    ws = wb.create_sheet("Supplier Evidence", 3)
    cols = ["research_source", "component_or_package", "supplier_name", "manufacturing_location",
            "other_locations", "origin", "evidence_quote", "source_doc", "source_url", "confidence"]
    ws.append(["Raw research evidence rows (one per sourced claim); the Suppliers sheet is the curated view applied to the Components sheet."])
    ws.cell(row=1, column=1).font = Font(name=ARIAL, size=9, italic=True, color="666666")
    ws.append(cols)
    style_header(ws, len(cols), row=2)
    for r in ev_rows:
        ws.append([r.get(k, "") for k in cols])
    for row in ws.iter_rows(min_row=3):
        for cell in row:
            cell.font = BASE
            cell.border = THIN
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = f"A2:J{ws.max_row}"
    set_widths(ws, [22, 34, 28, 26, 26, 12, 60, 34, 44, 11])

csv_sheet("Cost Accounts (TIMCAT)", "data/external/timcat_ap1000_accounts.csv",
          "MIT TIMCAT (github.com/mit-crpg/TIMCAT): EEDB PWR12-ME cost basis (2018 USD) + LPSR AP1000-surrogate component parameters. "
          "Factory equipment cost vs site labor/material = manufactured vs on-site split for domestic-content analysis.",
          widths=[13, 44, 16, 20, 12, 12, 16, 14, 14, 14, 14, 16, 16, 26, 18],
          number_cols=(4, 5, 6, 7, 8, 9, 10, 11, 12))
csv_sheet("AP1000 Cost Est. (INL)", "data/external/osti_2371533_tables.csv",
          "INL/RPT-24-77048 GAIN meta-analysis (2024), osti.gov/biblio/2371533: AP1000 cost estimates by GNCOA account "
          "(Stewart 2020 FOAK/NOAK; Shirvan TIMCAT NOAK). PDF Appendix A values 2017 USD; MASTER_DATA_MAPPED values 2022 USD.",
          widths=[13, 44, 20, 16, 12, 34, 14, 22, 30],
          number_cols=(3,))

wb.save("AP1000_Component_Database.xlsx")
print("saved AP1000_Component_Database.xlsx")
