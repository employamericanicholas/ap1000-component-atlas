"""Build AP1000_Domestic_Content_Analysis.xlsx — IRS domestic content bonus credit
(§§45Y/48E) categorization and Adjusted Percentage Rule analysis for an AP1000.

Method notes:
- Categorization follows Notice 2023-38 §3 with Table 2 / Notice 2024-41 hydro analogies.
- MP direct-cost estimates: INL/RPT-24-77048 companion database AP1000 columns
  (TIMCAT-basis NOAK, 2022 USD factory-equipment costs by GNCOA account), allocated to
  individual manufactured products with EEDB PWR12-ME sub-account factory-cost ratios
  (TIMCAT). Anomalous accounts cross-checked against PWR12-ME (2018 USD x ~1.17 CPI).
- Supplier origins: Employ America AP1000 supplier research (GA PSC docket 29849 VCM 1-12,
  NRC vendor inspection reports, press) -- see the AP1000_Component_Database.xlsx workbook.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ARIAL = "Arial"
HDR_FILL = PatternFill("solid", fgColor="1F3B57")
HDR_FONT = Font(name=ARIAL, bold=True, color="FFFFFF", size=10)
BASE = Font(name=ARIAL, size=10)
SMALL = Font(name=ARIAL, size=9)
BOLD = Font(name=ARIAL, size=10, bold=True)
TITLE = Font(name=ARIAL, size=15, bold=True, color="1F3B57")
NOTE = Font(name=ARIAL, size=9, italic=True, color="666666")
BLUE = Font(name=ARIAL, size=10, color="0000FF")
YELLOW = PatternFill("solid", fgColor="FFF2CC")
SI_FILL = PatternFill("solid", fgColor="E8D5D3")
MP_FILL = PatternFill("solid", fgColor="D6E4F0")
FLAG_FILL = PatternFill("solid", fgColor="FCE8D4")
THIN = Border(bottom=Side(style="thin", color="D9D9D9"))
WRAP = Alignment(vertical="top", wrap_text=True)

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

def body(ws, r0, r1, c1):
    for row in ws.iter_rows(min_row=r0, max_row=r1, max_col=c1):
        for cell in row:
            if cell.font == Font():
                pass
            cell.font = cell.font if cell.font.bold else SMALL
            cell.border = THIN
            cell.alignment = WRAP

# ================= README =================
ws = wb.active
ws.title = "README"
rows = [
    ("AP1000 DOMESTIC CONTENT BONUS CREDIT ANALYSIS", ""),
    ("", ""),
    ("Purpose", "Proposed categorization of AP1000 Applicable Project Components under the IRS domestic content bonus credit (26 USC 45Y(g)(11) / 48E(a)(3)(B)), with a Manufactured Product / MPC breakdown, direct-cost estimates, Vogtle 3&4-era supplier origins, and an Adjusted Percentage Rule calculator. Compiled September 27, 2026 by Employ America. ANALYTICAL WORK PRODUCT - NOT TAX OR LEGAL ADVICE."),
    ("", ""),
    ("LEGAL FRAMEWORK", ""),
    ("Statute", "45Y(g)(11) (PTC +10%) and 48E(a)(3)(B) (ITC +10 pts, with PWA); requirement: all structural steel/iron 100% US (49 CFR 661.5(b)-(c)) AND Manufactured Products deemed US under the Adjusted Percentage Rule."),
    ("Notice 2023-38", "Operative framework: definitions (APC, MP, MPC), Steel or Iron Requirement (sec. 3.02: 'construction materials made primarily of steel or iron [that] are structural in function'), Manufactured Products Requirement and direct-cost accounting (sec. 3.03), Table 2 classification safe harbor. Sources folder: General Guidance."),
    ("Notice 2024-41", "Added hydropower/pumped storage rows to Table 2 (closest official analog for a civil-works-heavy generation technology); created the New Elective Safe Harbor (solar/wind/BESS only - NOT available for nuclear)."),
    ("Notice 2025-08", "Updated elective safe harbor cost percentages (still no nuclear table). A nuclear project must therefore run actual manufacturer direct costs under Notice 2023-38 sec. 3.03(2)."),
    ("Notice 2026-15", "FEOC material assistance rules reuse the DC cost framework - see companion FEOC_Model_v2 workbook. Domestic sourcing decisions should be jointly optimized (a Korean vessel is FEOC-safe but hurts DC%; a Chinese subcomponent can be fatal to both)."),
    ("", ""),
    ("ADJUSTED PERCENTAGE (post-OBBBA)", ""),
    ("45Y (PTC)", "BOC before 2025: 40% | 2025: 45% | 2026: 50% | 2027+: 55%"),
    ("48E (ITC)", "BOC before 6/16/2025: 40% | 6/16/2025-12/31/2025: 45% | 2026: 50% | after 2026: 55%"),
    ("Planning basis", "A new AP1000 order realistically begins construction 2027+ -> 55% Domestic Cost Percentage target. Sheet 2 calculator tests 40/45/50/55."),
    ("", ""),
    ("KEY RULES DRIVING STRATEGY (Notice 2023-38)", ""),
    ("1.", "Steel/iron items that are structural in function must be 100% US-melted (except metallurgical additives). ONE foreign structural steel item kills the entire bonus - so keep anything with foreign steel OUT of the Steel/Iron category where a credible Manufactured Product classification exists (precedent: offshore-wind monopiles and transition pieces - massive welded steel - are classified Manufactured Product, while towers/jackets are Steel/Iron)."),
    ("2.", "Domestic Cost Percentage = (cost of US Manufactured Products + US-made MPCs of non-US MPs) / (total direct cost of all MPs). Costs = the MANUFACTURER'S direct materials + direct labor only (1.263A-1(e)(2)(i)). Site labor to INCORPORATE components into the project is excluded from both numerator and denominator."),
    ("3.", "A US-assembled MP with any foreign MPC is a NON-US MP: its own production cost drops out of the numerator; only its US MPCs count. Conversely 100% of a US MP's cost counts, including its US MPCs' cost embedded in it."),
    ("4.", "Open question flagged in Sheet 2: whether fabrication that happens ON SITE (containment vessel courses, module assembly in the MAB) is 'manufacturing' (counts) or 'incorporation' (excluded). Both treatments are shown."),
    ("", ""),
    ("SHEETS", ""),
    ("1. Applicable Project Components", "Every AP1000 APC, categorized Steel/Iron vs Manufactured Product, with function rationale, IRS Table 2 analogy, Vogtle-era supplier/origin, and strategy notes."),
    ("2. Manufactured Products & MPCs", "MP-by-MP breakdown: MPCs, direct-cost estimate ($M 2022, factory cost), Vogtle-era origin, domestic-$ under two scenarios, and the Domestic Cost Percentage calculator vs all four thresholds."),
    ("3. Strategy", "Ranked levers to reach 50-55%, with $-impact and legal basis/risk."),
    ("Sources", "Full citation list."),
    ("", ""),
    ("LEGEND", ""),
    ("Red-tinted rows", "Steel/Iron categorization (100% US melt/manufacture required)"),
    ("Blue-tinted rows", "Manufactured Product categorization (feeds the Adjusted Percentage calculation)"),
    ("Orange-tinted rows", "Classification judgment call - strategy-relevant, no direct IRS precedent"),
    ("Yellow cells", "User-adjustable assumptions"),
    ("", ""),
    ("Cost caveat", "Cost figures are ESTIMATES for strategy screening: INL/RPT-24-77048 companion database AP1000 NOAK columns (2022 USD, factory-equipment direct costs by GNCOA account), allocated to individual products using EEDB PWR12-ME sub-account ratios (MIT TIMCAT). They are not vendor quotes; an actual certification requires manufacturers' direct-cost data (Notice 2023-38 sec. 3.03(2), sec. 6)."),
]
for i, (a, b) in enumerate(rows, 1):
    ca = ws.cell(row=i, column=1, value=a)
    ca.font = BOLD if (b == "" or a.isupper() or (len(a) <= 3)) else BASE
    cb = ws.cell(row=i, column=2, value=b)
    cb.font = BASE
    cb.alignment = WRAP
ws.cell(row=1, column=1).font = TITLE
set_widths(ws, [34, 130])

# ================= 1. Applicable Project Components =================
ws = wb.create_sheet("1. Project Components")
ws.append(["AP1000 - Proposed Categorization of Applicable Project Components (analytic; no IRS nuclear table exists)"])
ws.cell(row=1, column=1).font = BOLD
ws.append(["Framework: Notice 2023-38 sec. 3.02/3.04 Table 2, as expanded by Notice 2024-41 sec. 3.02 (hydropower analogies). Categorizations for nuclear are NOT covered by the IRS classification safe harbor - each is a supported analytic position, with the analogy and function rationale shown."])
ws.cell(row=2, column=1).font = NOTE
hdr = ["#", "Applicable Project Component", "Proposed Categorization", "Function rationale (Steel/Iron test: construction material primarily steel/iron AND structural in function)",
       "IRS precedent / analogy", "Vogtle 3&4-era supplier (origin)", "Compliance note / risk", "Strategic note"]
ws.append(hdr)
style_header(ws, len(hdr), row=3)

SI = "Steel/Iron"
MP = "Manufactured Product"
FLAG = "Manufactured Product (judgment call)"
apc_rows = [
 # --- steel/iron ---
 (SI, "Steel or iron rebar in nuclear island basemat and building foundations",
  "Plain reinforcing steel embedded in structural concrete - squarely structural.",
  "Identical to every Table 2 row: 'Steel or iron rebar in foundation' (Notice 2023-38 Table 2, all four technologies).",
  "US rebar mills (commodity; Vogtle used domestic supply)",
  "LOW RISK: US-melted rebar (Nucor, CMC, Gerdau US mills) is abundant. Specify domestic melt in procurement.",
  "Keep in Steel/Iron - no benefit to arguing otherwise."),
 (SI, "Steel or iron rebar, embedded plates, and anchors in shield building, auxiliary, annex, turbine, radwaste buildings",
  "Embedments and anchors are structural connections to concrete.",
  "Notice 2024-41 hydro: 'embedded structure parts, foundation plates and anchors' = Steel/Iron.",
  "Cives Steel, Thomasville, GA (Domestic) - concrete embedments for Vogtle 3&4 (NRC ML13042A397)",
  "LOW RISK: Vogtle precedent is domestic (Cives, GA).",
  "Domestic supply chain proven; retain."),
 (SI, "Structural steel framing - turbine building, annex building, misc. steel",
  "Beams/columns/decking; classic structural steel.",
  "Notice 2024-41 hydro: 'Powerhouse structure' = Steel/Iron.",
  "US structural steel fabricators (Domestic)",
  "LOW RISK: commodity domestic structural steel.",
  "Retain in Steel/Iron."),
 (SI, "Shield building steel-composite (SC) wall panels, air inlet & tension ring panels",
  "SC panels are the shield building's structure (steel faceplates + concrete fill) - structural in function.",
  "Hydro 'powerhouse structure' analogy; panels are building structure, not equipment.",
  "Newport News Industrial, Newport News, VA (Domestic) - NRC IR 99901433/2017-201; GA PSC VCM 9/10",
  "MODERATE: plate must be US-melted; NNI fabrication is domestic. Verify plate melt origin in procurement.",
  "Vogtle precedent domestic end-to-end; low-risk to keep as Steel/Iron. (If plate melt is foreign, MP classification of panels-as-modules is the fallback argument.)"),
 (SI, "Spent fuel pool, IRWST and refueling canal liners (site-installed plate)",
  "Leak-tight liner plate on structural concrete.",
  "Hydro: steel 'in water conveyance' / embedded structure = Steel/Iron.",
  "US liner fabricators/site install (Domestic)",
  "LOW-MODERATE: stainless liner plate available from US mills.",
  "Specify domestic melt; retain."),
 # --- judgment calls ---
 (FLAG, "Containment vessel (CNS-MV-01): steel plates, ring courses, heads",
  "It is a factory/field-fabricated ASME III Class MC pressure vessel whose function is pressure containment - an engineered product, not a 'construction material.' Counter-argument: it is plausibly 'structural in function.'",
  "Offshore wind MONOPILE and TRANSITION PIECE - enormous welded steel structures - are classified Manufactured Product in Table 2. BESS 'battery container/housing' = MP. Adverse analogy: hydro spiral case/draft tube steel = Steel/Iron (but those are concrete-embedded conveyance).",
  "Plates/heads: IHI Corp., Yokohama, Japan (Foreign); on-site fabrication/assembly: CB&I, Waynesboro, GA (Domestic) - NRC ML102870167; VCM 7; NEI 8/2010",
  "CRITICAL: If categorized Steel/Iron, the Vogtle-pattern supply chain (Japanese plate) FAILS the 100% rule and kills the entire bonus. As MP, foreign plates only dilute the percentage.",
  "STRATEGY POSITION #1: categorize as Manufactured Product (monopile analogy). Better still: re-shore plate (SA-738 Gr.B from US mill) and count the whole vessel as a US MP - see Strategy sheet."),
 (FLAG, "Containment internal & auxiliary building structural modules (CA01, CA20, CA03, CA05...)",
  "Shop-fabricated engineered sub-modules (steel-plate composite walls/floors with embedded features), shipped and assembled - the product of a manufacturing process, though structural in final function.",
  "Monopile/transition-piece analogy (massive shop-welded steel = MP). Adverse: hydro 'embedded structure parts' = Steel/Iron.",
  "Shaw/CB&I Lake Charles, LA (Domestic); Unit 4 re-sourcing: Oregon Iron Works/Vigor (OR), SMCI (FL) - Domestic; IHI + Toshiba CA01 sub-modules (Japan - Foreign). GA PSC VCM 4-12; NRC ML12279A119",
  "CRITICAL (same logic as containment vessel): any foreign sub-module inside a Steel/Iron categorization = total failure. Vogtle Unit 4 actually used Japanese CA01 sub-modules.",
  "STRATEGY POSITION #2: categorize modules as Manufactured Products; their large domestic fabrication cost then WORKS FOR you in the percentage (Lake Charles/Vigor/SMCI are domestic manufacturers)."),
 (FLAG, "Safety-related and BOP piping systems (shop-fabricated spools), pipe racks aside",
  "Engineered, shop-fabricated pressure piping (bending, welding, heat treatment, NDE) - a manufacturing process; function is fluid conveyance, not structure.",
  "Adverse analogy exists: hydro 'steel piping in water conveyance (penstock)' = Steel/Iron. Distinguish: penstock is civil conveyance; ASME III/B31.1 spools are engineered pressure equipment. Table 2 treats similar fabricated items (monopile) as MP.",
  "RCL piping: IBF S.p.A., Italy under Tioga Pipe (US prime) - Foreign fab (NRC ML13200A220); other piping: CB&I Laurens SC, WEC Rock Hill SC (Domestic)",
  "HIGH-VALUE CALL: if piping were Steel/Iron, Italian RCL piping fails everything. As MP, it is a modest foreign line item.",
  "STRATEGY POSITION #3: piping spools = Manufactured Products. Document the engineered-product character (ASME III Code stamps)."),
 # --- manufactured products (clear) ---
 (MP, "Reactor pressure vessel + closure head (RCS-MV-01)", "ASME III Class 1 vessel - engineered equipment.",
  "Equipment = MP under every Table 2 technology.", "Doosan, Changwon, South Korea; forgings: Japan Steel Works, Muroran, Japan (Foreign) - NRC ML14260A350; VCM 4",
  "Foreign MP - dilutes percentage; no US MPCs to count.", "Re-shoring candidate (see Strategy: BWXT Mount Vernon IN / domestic forging gap)."),
 (MP, "Steam generators x2 (RCS-MB-01/02)", "Engineered heat-exchange equipment.", "Equipment = MP.",
  "Doosan, Changwon, South Korea (Foreign) - VCM 12; WNN 8/2017", "Foreign MP.", "Largest single NSSS foreign item after T-G; re-shoring candidate."),
 (MP, "Reactor coolant pumps x4 (RCS-MP-01A/B, 02A/B)", "Canned-motor pumps - equipment.", "Equipment = MP.",
  "Curtiss-Wright EMD, Cheswick, PA (Domestic; casings forged by Doosan) - NRC ML16350A067; GA Power 4/2016",
  "US MP if all MPCs US-origin; Doosan casing makes it a non-US-MP risk -> only US MPCs count. Verify casting/forging source.",
  "Re-shore the casing forging to make the RCP a clean US MP (100% of its cost counts)."),
 (MP, "Pressurizer (RCS-MV-02)", "ASME III vessel.", "Equipment = MP.", "Mangiarotti, Monfalcone, Italy (Foreign) - NRC ML12320A661; VCM 11",
  "Foreign MP.", "Re-shoring candidate - US heavy vessel shops can make this (see Strategy)."),
 (MP, "Reactor vessel internals (RXS-MI series) + CRDMs x69 (RXS-MV-11 series)", "Precision-machined equipment.", "Equipment = MP.",
  "Westinghouse Newington Operations, Newington, NH (Domestic) - NRC ML14328A138", "US MP (verify sub-tier: VC Summer core barrel came from Toshiba Keihin - keep US).",
  "Anchor domestic item - protect this sourcing."),
 (MP, "Integrated head package (RXS-MV-10)", "Fabricated equipment assembly.", "Equipment = MP.",
  "Premier Technology, Blackfoot, ID (Domestic) - NRC ML15132A142", "US MP.", "Protect."),
 (MP, "Passive core cooling equipment: core makeup tanks x2, accumulators x2, PRHR heat exchanger (PXS-MT/ME)",
  "ASME III vessels/heat exchangers.", "Equipment = MP.", "Mangiarotti, Italy (Foreign) - NRC ML12320A661; VCM 8",
  "Foreign MPs.", "PRIME re-shoring candidates: mid-size ASME III vessels well within US shop capability (Joseph Oat, Precision Custom Components, BWXT, Holtec - see Strategy)."),
 (MP, "Squib valves, safety/relief valves, check valves, MOVs/AOVs (plant-wide engineered valves)",
  "Engineered valve equipment.", "Equipment = MP.",
  "SPX Copes-Vulcan McKean PA; Pentair Mansfield MA; GE Consolidated Pineville LA; Enertech Brea CA; Fisher Marshalltown IA; ASCO Aiken SC (Domestic) - NRC vendor IRs",
  "Mostly US MPs already.", "Protect; specify US valve sourcing in BOP."),
 (MP, "Reactor coolant loop piping set (hot legs, cold legs, surge line)", "See piping judgment-call row; listed separately for costing.",
  "MP (per Strategy Position #3).", "IBF S.p.A., San Nicolo, Italy under Tioga Pipe (Philadelphia, PA prime) - Foreign fabrication (NRC ML13200A220; VCM 7)",
  "Non-US MP; Tioga's US role is distribution, not manufacture - does not count.", "Re-shoring candidate (US seamless heavy-wall SS pipe: gap - see Strategy)."),
 (MP, "Fuel handling equipment (refueling machine, fuel handling machine, transfer system) + polar crane + cranes",
  "Machinery.", "Equipment = MP.", "Westinghouse/PaR Nuclear, Shoreview, MN (Domestic, polar crane 'probable') - Power Eng. 2006; PAR 2026",
  "US MPs (confirm polar crane vendor).", "Protect."),
 (MP, "New & spent fuel storage racks (FHS-FS-01/02)", "Fabricated equipment.", "Equipment = MP.",
  "Holtec, Turtle Creek, PA (Domestic) - Holtec 2/2013", "US MP.", "Protect."),
 (MP, "Protection & safety monitoring system (PMS), DAS, plant control (PLS/Ovation), MCR panels",
  "I&C electronics.", "Inverter/BMS analogies = MP.", "Westinghouse Warrendale/Cranberry PA (integration); Common Q hardware is ABB AC160-heritage (Mixed); Emerson Ovation Pittsburgh PA (Domestic) - NRC ML17123A085",
  "US integration counts if hardware MPCs sourced US; imported boards make PMS a non-US MP (only US MPCs count).",
  "Push US-fabricated boards/cabinets to convert PMS to a clean US MP."),
 (MP, "Class 1E DC & UPS: batteries, chargers, inverters, switchgear, MCCs, penetrations, cabling",
  "Electrical equipment.", "Inverter analogy = MP.", "EnerSys, Hays, KS (batteries - Domestic, NRC ML14058A705); RSCC East Granby CT (1E cable - Domestic); others various",
  "Largely domestic already.", "Protect; specify US switchgear/penetrations."),
 (MP, "Main step-up / auxiliary transformers", "Electrical equipment.", "Hydro GSU transformer row = MP (Notice 2024-41).",
  "Vogtle vendor never publicly named (Unknown/likely Foreign)", "Large power transformers are a known US supply gap.",
  "Cheap win: US-BUILT LPTs exist - Hyundai Power Transformers (Montgomery, AL), Virginia Transformer (Roanoke, VA), Delta Star. DC test is WHERE manufactured, not ownership."),
 (MP, "Steam turbine-generator (HP + 3 LP + generator + MSR + turbine valves)", "Rotating machinery.", "Turbine = MP (hydro/wind analogies).",
  "Toshiba, Keihin Works, Yokohama, Japan (Foreign) - Toshiba MDEP 2023", "THE single largest foreign line item (~$325M factory cost).",
  "Highest-$ lever: US final assembly/localization or US STG partner converts the biggest denominator item (see Strategy)."),
 (MP, "Main condensers", "Heat-exchange equipment.", "Equipment = MP.", "Toshiba scope, fabricated by BHI, Sacheon, South Korea (Foreign) - Toshiba PR 12/2011",
  "Foreign MP.", "Easy re-shore: US condenser fabricators exist (Holtec HTS Camden NJ; TEi). Modular tube-bundle shipping is routine."),
 (MP, "Feedwater heaters, deaerator, condensate polishers, BOP heat exchangers", "Heat-exchange equipment.", "Equipment = MP.",
  "Toshiba turbine-island scope (Foreign, sub-fab unspecified) - Toshiba MDEP 2023", "Foreign under Vogtle pattern.",
  "US FWH/HX fabricators available (Holtec, Joseph Oat, Thermal Engineering) - specify US."),
 (MP, "Standby diesel generators x2 + ancillary DGs", "Rotating machinery.", "Equipment = MP.",
  "Vogtle vendor not publicly disclosed (Unknown)", "Unknown = treat as foreign in base case.",
  "Fairbanks Morse (Beloit, WI) is the historic US nuclear DG supplier; Caterpillar (US plants) - easy domestic spec."),
 (MP, "HVAC equipment: AHUs, chillers, fans, dampers, filtration units (V-systems)", "Equipment.", "Equipment = MP.",
  "US HVAC majors (largely Domestic; MCR filtration ASME AG-1 units US)", "Mostly domestic.", "Specify US."),
 (MP, "Radwaste processing skids (WLS/WGS/WSS), demineralizers, evaporators", "Process equipment.", "Equipment = MP.",
  "US skid fabricators (Domestic, typical)", "Mostly domestic.", "Specify US."),
 (MP, "CVS/CCS/SWS/RNS/SFS pumps, heat exchangers, tanks", "Process equipment.", "Equipment = MP.",
  "Flowserve, Vernon, CA (safety pumps - Domestic, NRC ML13119A154); US HX fabricators", "Mostly domestic.", "Protect."),
 (MP, "Circulating water pumps, screens, cooling tower fill & mechanicals", "Equipment (tower shell = concrete civil work, excluded).", "Equipment = MP.",
  "US suppliers (Domestic, typical)", "Domestic.", "Tower concrete/rebar handled under Steel/Iron + civil (excluded from MP math)."),
 (MP, "Nuclear fuel (first core, 157 assemblies)", "EXCLUDED from the facility analysis: fuel is consumable inventory, not a component of the qualified facility 'upon completion of construction.'",
  "No Table 2 analogy; flagged for completeness.", "Westinghouse Columbia, SC (Domestic) - Westinghouse 10/2022",
  "If ever included, it is a large domestic item.", "Confirm treatment with counsel; excluded from Sheet 2 math."),
]
r = 4
for i, (cat, apc, why, prec, sup, risk, strat) in enumerate(apc_rows, 1):
    ws.append([i, apc, cat, why, prec, sup, risk, strat])
    fill = SI_FILL if cat == SI else (FLAG_FILL if cat == FLAG else MP_FILL)
    for j in range(1, 9):
        c = ws.cell(row=r, column=j)
        c.fill = fill
        c.font = SMALL
        c.border = THIN
        c.alignment = WRAP
    r += 1
ws.freeze_panes = "A4"
ws.auto_filter.ref = f"A3:H{r-1}"
set_widths(ws, [4, 38, 20, 44, 42, 44, 44, 46])

# ================= 2. Manufactured Products & MPCs =================
ws = wb.create_sheet("2. Manufactured Products")
ws.append(["AP1000 Manufactured Products - MPC breakdown, direct-cost estimates, and Adjusted Percentage Rule calculator"])
ws.cell(row=1, column=1).font = BOLD
ws.append(["Costs = estimated MANUFACTURER direct costs (factory equipment cost proxy), $M 2022. Basis: INL/RPT-24-77048 companion database AP1000 NOAK columns by GNCOA account, allocated with EEDB PWR12-ME sub-account ratios (MIT TIMCAT). Rounded; screening quality. 'Base' = Vogtle 3&4-era sourcing; 'Strategic' = Strategy-sheet sourcing plan. Yellow cells are assumptions - edit them."])
ws.cell(row=2, column=1).font = NOTE
hdr = ["Manufactured Product (APC)", "GNCOA/EEDB acct", "Manufactured Product Components (MPCs)",
       "Est. direct cost ($M 2022)", "Cost basis", "Vogtle-era manufacturer (location)", "Origin",
       "2023-38 treatment (base case)", "Domestic $ - Base", "Domestic $ - Strategic", "Strategic action", "Source links"]
ws.append(hdr)
style_header(ws, len(hdr), row=3)

# rows: (mp, acct, mpcs, cost, basis, mfr, origin, treatment, dom_base, dom_strat, action, links)
NRC = "https://www.nrc.gov/docs/"
mp_rows = [
 ("Reactor pressure vessel + closure head + IHP", "221.1 (+IHP)", "Shell/head forgings, nozzles, safe ends, studs, CRDM penetrations, insulation; IHP shroud & lift rig",
  53, "INL acct 221 FE $129M x PWR12 221.1 share (41%)", "Doosan (Changwon, KR); forgings JSW (Muroran, JP); IHP: Premier Technology (Blackfoot, ID)", "Foreign (IHP US)",
  "Non-US MP; US MPC = IHP (~$8M) counts", 8, 8,
  "LONG-LEAD (Lever 6, excluded from Strategic column): re-shore vessel fabrication (BWXT Mount Vernon IN / US heavy shop revival); interim: maximize US MPCs shipped to vendor",
  NRC+"ML1426/ML14260A350.pdf; https://psc.ga.gov/search/facts-document/?documentId=134428"),
 ("Reactor vessel internals (upper + lower)", "221.3", "Core barrel, core shroud, upper/lower support structures, guide tubes, instrumentation grid",
  47, "INL 221 FE x PWR12 221.3 share (36%)", "Westinghouse Newington Operations (Newington, NH)", "Domestic",
  "US MP - full cost counts", 47, 47, "Protect sourcing (keep core barrel domestic - VC Summer's went to Toshiba Japan)",
  NRC+"ML1432/ML14328A138.pdf"),
 ("Control rod drive mechanisms (69)", "221.2", "Latch assemblies, drive rods, coil stacks, pressure housings",
  29, "INL 221 FE x PWR12 221.2 share (22%)", "Westinghouse Newington Operations (Newington, NH)", "Domestic",
  "US MP", 29, 29, "Protect", NRC+"ML1432/ML14328A138.pdf"),
 ("Reactor coolant pumps (4, canned-motor)", "222.11", "Casing, canned motor (rotor/stator/windings), impeller, flywheel, bearings",
  101, "INL 222 FE $238.6M x PWR12 222.11 share (42%)", "Curtiss-Wright EMD (Cheswick, PA); casings: Doosan (KR)", "Domestic (foreign casing MPC)",
  "Non-US-MPC risk: foreign casing makes RCP a non-US MP -> count US MPCs (~$85M motor/internals) only", 85, 101,
  "Re-shore casing forging/casting (Scot Forge/US foundry qualification) to make RCPs clean US MPs (+$16M)",
  NRC+"ML1635/ML16350A067.pdf"),
 ("Steam generators (2)", "222.13", "Tubesheet & channel head forgings, shell courses, Alloy 690 tube bundle, tube supports, moisture separators, FW ring",
  117, "INL 222 FE x PWR12 222.13 share (49%)", "Doosan (Changwon, KR)", "Foreign",
  "Non-US MP; negligible US MPCs", 0, 0, "LONG-LEAD (Lever 6, excluded from Strategic column): mid-term US SG line (BWXT/Holtec candidates)",
  NRC+"ML1426/ML14260A350.pdf"),
 ("Pressurizer", "222.14", "Forged shell, heater bundle, spray head, surge nozzle",
  8, "INL 222 FE x PWR12 222.14 share (3%)", "Mangiarotti (Monfalcone, IT)", "Foreign",
  "Non-US MP", 0, 8, "Re-shore: routine US heavy-vessel scope (Precision Custom Components York PA; Joseph Oat Camden NJ)",
  NRC+"ML1232/ML12320A661.pdf"),
 ("Reactor coolant loop piping set", "222.12", "Seamless SS heavy-wall hot/cold leg pipe, surge line, elbows/fittings",
  12, "INL 222 FE x PWR12 222.12 share (5%)", "IBF S.p.A. (San Nicolo, IT), prime: Tioga Pipe (Philadelphia, PA)", "Foreign",
  "Non-US MP (Tioga distributes, does not manufacture)", 0, 0, "LONG-LEAD (Lever 6, excluded from Strategic column): US seamless heavy-wall SS pipe capacity gap",
  NRC+"ML1320/ML13200A220.pdf"),
 ("PXS vessels: core makeup tanks (2), accumulators (2), PRHR HX", "223.1/.3", "Forged/plate shells, heads, internal baffles, C-tube bundle (PRHR)",
  15, "INL 223 FE $24.7M x PWR12 vessel share", "Mangiarotti (Monfalcone, IT)", "Foreign",
  "Non-US MPs", 0, 15, "Re-shore: mid-size ASME III vessels squarely in US shop capability (Joseph Oat, PCC, BWXT, Holtec)",
  NRC+"ML1232/ML12320A661.pdf"),
 ("Safeguards & plant engineered valves (squib, safety, relief, check, MOV/AOV)", "223.x6 + dist.", "Valve bodies, actuators, explosive initiators, internals",
  35, "INL 223 balance + valve share of system accts (PWR12 x26 valve lines)", "SPX Copes-Vulcan (McKean PA), Pentair (Mansfield MA), GE Consolidated (Pineville LA), Enertech (Brea CA), Fisher (Marshalltown IA), ASCO (Aiken SC); initiators: UTC (Fairfield CA)", "Domestic",
  "US MPs (dominant)", 32, 35, "Protect; close remaining import lines (some AOV/instrument valves)",
  NRC+"ML1215/ML12158A154.pdf; "+NRC+"ML1407/ML14073A652.pdf"),
 ("Radwaste processing equipment (WLS/WGS/WSS skids, evaporator, VR system)", "224", "Tanks, demineralizers, filters, compactor, skid piping/instruments",
  26, "INL 224 FE $26.2M", "US skid fabricators (typical; not publicly itemized)", "Domestic (assumed)",
  "US MPs (medium confidence)", 22, 26, "Confirm/specify US skid fab", "See Supplier Evidence sheet, AP1000_Component_Database.xlsx"),
 ("Fuel handling & storage: refueling machine, FHM, transfer system, racks", "225", "Machines, drives, controls; rack modules",
  6, "INL 225 FE $3.2M + racks (Holtec, est. $3M)", "Westinghouse/PaR Nuclear (Shoreview, MN); Holtec (Turtle Creek, PA)", "Domestic",
  "US MPs", 6, 6, "Protect", "https://holtecinternational.com/2013/02/22/...; Power Eng. 2006 (PaR)"),
 ("Other reactor plant equipment: CVS, CCS, SFS, RNS pumps/HX/tanks, VES", "226", "Pumps, heat exchangers, tanks, demineralizers",
  29, "INL 226 FE $28.8M", "Flowserve (Vernon, CA) safety pumps; US HX fabricators; misc.", "Domestic (majority)",
  "US MPs, some import exposure in HX/tanks", 24, 29, "Specify US HX/tank fab", NRC+"ML1311/ML13119A154.pdf"),
 ("Reactor plant I&C: PMS, DAS, MCR panels, monitoring, in-core instr.", "227", "Cabinets, processors (Common Q/AC160-heritage), flat panels, sensors, RMS detectors",
  32, "INL 227 FE $32.0M", "Westinghouse (Warrendale/Cranberry, PA integration); GA-ESI (San Diego, CA) RMS; hardware partly ABB-heritage", "Mixed",
  "US integration counts only if boards US - base: 60% US MPC share", 19, 29,
  "Convert PMS to clean US MP: US-fab boards/cabinets (strategy: I&C is high-margin, low-mass - ideal onshoring)",
  NRC+"ML1712/ML17123A085.pdf; "+NRC+"ML1316/ML13164A351.pdf"),
 ("Containment vessel (as Manufactured Product - Strategy Position #1)", "212 (part)", "SA-738 plates, ring courses, heads, penetrations, airlocks, equipment hatches",
  91, "INL 212 FE $91M (CV factory scope)", "Plates/heads: IHI (Yokohama, JP); course fab & assembly: CB&I on site (Waynesboro, GA)", "Mixed",
  "If on-site fab = manufacturing: non-US MP w/ US MPC (CB&I course fab ~ $46M) counts; if fab = 'incorporation', excluded entirely (shown in sensitivity row 'CV excluded')", 46, 91,
  "Re-shore plate (US SA-738 heavy plate: Nucor-Brandenburg / Cleveland-Cliffs Coatesville candidates) -> whole CV becomes US MP",
  NRC+"ML1028/ML102870167.pdf; https://psc.ga.gov/search/facts-document/?documentId=143954"),
 ("Structural / mechanical modules as MPs (CA01, CA20, CA03, CA05, Q2xx...)", "212/218 (part)", "Steel-plate composite sub-modules, embedded plates, mechanical module frames & piping",
  120, "Estimate: module shop-fab direct cost (VCM contract scale; INL 21x FE+SM part)", "Shaw/CB&I Lake Charles (LA), Vigor (Clackamas OR), SMCI (Lakeland FL), Greenberry (Vancouver WA) - Domestic; CA01 U4 sub-modules IHI/Toshiba (JP)", "Domestic (majority)",
  "US MPs except Japanese CA01 sub-modules (~$20M)", 100, 120,
  "Domestic module capacity now exists (post-Lake Charles recovery); dual-qualify shops to avoid Japan fallback",
  "https://psc.ga.gov/search/facts-document/?documentId=154916; "+NRC+"ML1227/ML12279A119.pdf"),
 ("Steam turbine-generator (TC6F-52) + MSRs + turbine valves", "231/232", "HP/LP rotors & casings, blades, generator (rotor/stator/exciter), MSRs, stop/control valves, EHC",
  325, "INL 232 FE $324.5M (= PWR12 231 FE $275.5M 2018 x CPI)", "Toshiba (Keihin Works, Yokohama, JP)", "Foreign",
  "Non-US MP - largest single denominator item", 0, 195,
  "Lever #1: US STG path - domestic final assembly + US generator (strategic est. 60% localized = $195M domestic); candidates: GE Vernova (Schenectady NY generators), US rotor forging gap persists",
  "https://www.oecd-nea.org/mdep/events/conf-2023/presentations/S3/4.Toshiba.pdf"),
 ("Main condensers", "233 (part)", "Shells, tube bundles (Ti/SS), waterboxes",
  35, "PWR12 233 condenser share (2022 $)", "Toshiba scope; fabricated by BHI (Sacheon, KR)", "Foreign",
  "Non-US MP", 0, 35, "Easy re-shore: Holtec HTS (Camden, NJ) / TEi build condensers today",
  "https://www.global.toshiba/ww/news/corporate/2011/12/pr0101.html"),
 ("Condensate/air removal & other condensing equipment", "233 (bal.)", "Condensate pumps, vacuum pumps, polishers",
  20, "PWR12 233 balance", "US suppliers (typical)", "Domestic", "US MPs", 17, 20, "Specify US", "-"),
 ("Feedwater heaters + deaerator", "234", "Shells, tube bundles, internals",
  47, "PWR12 234 FE $40.2M 2018 x CPI", "Toshiba T/I scope (sub-fab unspecified, JP)", "Foreign",
  "Non-US MPs", 0, 47, "Re-shore: US FWH fabricators (Holtec, Joseph Oat, TEi)", "Toshiba MDEP 2023"),
 ("Other turbine plant equipment (lube oil, seals, TG crane, aux boiler)", "235", "Misc. mechanical", 36, "PWR12 235 FE x CPI",
  "US suppliers (typical)", "Domestic", "US MPs (medium conf.)", 30, 36, "Specify US", "-"),
 ("Turbine island I&C (Ovation DCS)", "236", "Controllers, workstations, cabinets", 5, "PWR12 236 FE x CPI",
  "Emerson (Pittsburgh, PA)", "Domestic", "US MP", 5, 5, "Protect", "Westinghouse simulator datasheet"),
 ("Switchgear, MCCs, station service transformers, switchboards, protective equip.", "241-244", "Breakers, buses, MCC buckets, relays",
  30, "INL 241-243 FE + 244 est.", "US electrical majors (Vogtle vendors not itemized)", "Domestic (majority)",
  "US MPs, some imported breakers", 24, 30, "Specify US (Powell, Eaton, ABB US plants)", "-"),
 ("Class 1E DC/UPS: batteries, chargers, inverters, spare bank", "245 (part)", "Cells, racks, chargers, inverters",
  20, "INL 245 slice; EnerSys scope", "EnerSys (Hays, KS); chargers/UPS vendor unlisted", "Domestic (majority)",
  "Batteries US MP; chargers/UPS verify", 15, 20, "Specify US (AMETEK SolidState Controls, OH)", NRC+"ML1405/ML14058A705.pdf"),
 ("Cable & raceway: 1E and BOP power/control/instrument cable, penetrations", "245/246", "Cable, trays, electrical penetration assemblies",
  35, "INL 245/246 FE+SM slice", "RSCC (East Granby, CT) 1E cable; penetrations (Schott heritage - DE) ", "Domestic (majority)",
  "Cable US; penetrations foreign (~$4M)", 28, 35, "US penetration alternative (Conax? - verify)", NRC+"ML1416/ML14164A502.pdf"),
 ("Main step-up + unit aux transformers", "25x/24x", "Core (GOES), windings, tank, bushings, OLTC",
  35, "Estimate (LPT market pricing, 2x GSU + UATs)", "Vogtle vendor not publicly named", "Unknown (base=Foreign)",
  "Treat as non-US MP in base case", 0, 35, "Cheap win: US-BUILT LPTs (Hyundai Montgomery AL, Virginia Transformer Roanoke VA, Delta Star) - DC test is manufacture location, not ownership; GOES from Cleveland-Cliffs Butler PA",
  "GA PSC VCM (milestones only)"),
 ("Standby & ancillary diesel generators", "24x (part)", "Engines, generators, skids, controls",
  20, "Estimate (4 MW class x2 + ancillary)", "Not publicly disclosed", "Unknown (base=Foreign)",
  "Treat as non-US in base case", 0, 20, "Fairbanks Morse (Beloit, WI) / Caterpillar US - specify domestic", "-"),
 ("Cranes, hoists, misc. plant equipment, air & service water systems, comms", "251-255", "Polar crane, cask crane, compressors, misc.",
  50, "PWR12 25x FE x CPI", "PaR Nuclear (Shoreview, MN) cranes; US suppliers", "Domestic (majority)",
  "US MPs (polar crane vendor unconfirmed)", 42, 50, "Confirm crane vendor; specify US", "Power Eng. 2006 (PaR)"),
 ("HVAC equipment (V-systems): AHUs, chillers, fans, ASME AG-1 filtration", "21x equip.", "AHUs, chillers, fans, dampers, HEPA/charcoal units",
  25, "Estimate (INL 21x FE slice)", "US HVAC majors (typical)", "Domestic (majority)", "US MPs", 21, 25, "Specify US", "-"),
 ("Heat rejection: circ. water pumps, screens, cooling tower mechanicals & fill", "261-262", "CW pumps, motors, screens, fill, drives",
  30, "PWR12 26x equipment share x CPI", "US suppliers (typical; tower shell is site civil - excluded)", "Domestic (majority)",
  "US MPs", 25, 30, "Specify US", "-"),
]
r0 = 4
r = r0
for row in mp_rows:
    ws.append(list(row))
    for j in range(1, 13):
        c = ws.cell(row=r, column=j)
        c.font = SMALL
        c.border = THIN
        c.alignment = WRAP
    for j in (4, 9, 10):
        ws.cell(row=r, column=j).fill = YELLOW
        ws.cell(row=r, column=j).number_format = "#,##0"
    r += 1
last = r - 1
# totals + calculator
ws.append([])
r += 1
calc_rows = [
 ("TOTAL Manufactured Products direct cost ($M 2022)", f"=SUM(D{r0}:D{last})", None, None),
 ("Domestic Manufactured Products & Components cost - BASE (Vogtle-era sourcing)", f"=SUM(I{r0}:I{last})", None, None),
 ("Domestic Manufactured Products & Components cost - STRATEGIC", f"=SUM(J{r0}:J{last})", None, None),
 ("DOMESTIC COST PERCENTAGE - BASE", None, None, None),
 ("DOMESTIC COST PERCENTAGE - STRATEGIC", None, None, None),
]
tot_r = r
ws.cell(row=r, column=1, value=calc_rows[0][0]).font = BOLD
ws.cell(row=r, column=4, value=calc_rows[0][1]).font = BOLD
ws.cell(row=r, column=4).number_format = "#,##0"
r += 1
base_r = r
ws.cell(row=r, column=1, value=calc_rows[1][0]).font = BOLD
ws.cell(row=r, column=4, value=calc_rows[1][1].replace("I", "I").replace("SUM(I", "SUM(I")).font = BOLD
ws.cell(row=r, column=4, value=f"=SUM(I{r0}:I{last})")
ws.cell(row=r, column=4).number_format = "#,##0"
r += 1
strat_r = r
ws.cell(row=r, column=1, value=calc_rows[2][0]).font = BOLD
ws.cell(row=r, column=4, value=f"=SUM(J{r0}:J{last})").font = BOLD
ws.cell(row=r, column=4).number_format = "#,##0"
r += 1
pct_base_r = r
ws.cell(row=r, column=1, value="DOMESTIC COST PERCENTAGE - BASE").font = BOLD
ws.cell(row=r, column=4, value=f"=D{base_r}/D{tot_r}").number_format = "0.0%"
ws.cell(row=r, column=4).font = BOLD
r += 1
pct_strat_r = r
ws.cell(row=r, column=1, value="DOMESTIC COST PERCENTAGE - STRATEGIC").font = BOLD
ws.cell(row=r, column=4, value=f"=D{strat_r}/D{tot_r}").number_format = "0.0%"
ws.cell(row=r, column=4).font = BOLD
r += 1
ws.cell(row=r, column=1, value="Sensitivity: CV on-site fabrication treated as 'incorporation' (CV row excluded entirely)").font = SMALL
cv_row = r0 + 13  # containment vessel row index in mp_rows (0-based 13)
ws.cell(row=r, column=4, value=f"=(D{base_r}-I{cv_row})/(D{tot_r}-D{cv_row})").number_format = "0.0%"
r += 2
ws.cell(row=r, column=1, value="THRESHOLD TEST (Adjusted Percentage by begin-construction year)").font = BOLD
r += 1
ws.append(["Begin construction", "Adjusted %", "BASE pass?", "STRATEGIC pass?"])
style_header(ws, 4, row=r)
r += 1
for label, pct in (("Before 2025 (45Y) / before 6-16-2025 (48E)", 0.40), ("2025", 0.45), ("2026", 0.50), ("2027 and later", 0.55)):
    ws.cell(row=r, column=1, value=label).font = SMALL
    c = ws.cell(row=r, column=2, value=pct); c.number_format = "0%"; c.font = SMALL
    ws.cell(row=r, column=3, value=f'=IF(D{pct_base_r}>=B{r},"PASS","FAIL")').font = SMALL
    ws.cell(row=r, column=4, value=f'=IF(D{pct_strat_r}>=B{r},"PASS","FAIL")').font = SMALL
    r += 1
ws.freeze_panes = "A4"
ws.auto_filter.ref = f"A3:L{last}"
set_widths(ws, [40, 11, 44, 11, 30, 42, 13, 36, 11, 11, 46, 40])

# ================= 3. Strategy =================
ws = wb.create_sheet("3. Strategy")
ws.append(["Strategic plan: getting an AP1000 to the domestic content bonus"])
ws.cell(row=1, column=1).font = BOLD
hdr = ["Priority", "Lever", "Est. impact (pp of Domestic Cost %)", "Legal basis / risk", "Detail"]
ws.append(hdr)
style_header(ws, len(hdr), row=2)
strat = [
 ("0", "Classify fabricated steel as Manufactured Products, not Steel/Iron",
  "Existential (avoids automatic failure)",
  "Notice 2023-38 sec. 3.02 limits Steel/Iron to 'construction materials... structural in function'; Table 2 classifies monopiles/transition pieces (massive welded steel) as MPs. Risk: no nuclear ruling; hydro rows cut the other way for embedded steel.",
  "Containment vessel, CA modules, piping = MPs (Sheet 1, orange rows). Keep only rebar, embeds, framing, SC panels, liners in Steel/Iron - all provably US-melted (Nucor/CMC rebar; Cives GA embeds; NNI VA panels)."),
 ("1", "US turbine-generator path",
  "+14 pp (325 -> 195 domestic of ~1,414 total)",
  "Pure sourcing - no legal risk.",
  "Largest single denominator item (~$325M factory cost). Toshiba supplied Vogtle. Options: US final assembly + US generator (GE Vernova Schenectady); negotiate localization like wind nacelle plants; rotor forgings remain a JSW/Doosan/Saarschmiede import in any scenario (acceptable as MPC dilution if final manufacture is US)."),
 ("2", "Treat on-site fabrication as manufacturing + re-shore CV plate",
  "+3 to +6 pp",
  "Open interpretive question (Sheet 2 sensitivity row). If on-site course fabrication = manufacturing, CB&I's direct labor counts; US SA-738 plate makes the CV a US MP.",
  "US heavy-plate candidates: Nucor-Brandenburg (KY) and Cleveland-Cliffs Coatesville (PA) roll heavy plate; SA-738 Gr.B qualification is the gap to close. Modules: domestic shops (Lake Charles LA, Vigor OR, SMCI FL, Greenberry WA) already proven at Vogtle."),
 ("3", "Re-shore mid-size ASME III vessels (pressurizer, CMTs, accumulators, PRHR HX, FWHs, condensers)",
  "+7 pp (~105M)",
  "Pure sourcing.",
  "These do NOT need ultra-heavy forging capacity - plate-welded and mid-size forged vessels are in-capability for Joseph Oat (Camden NJ), Precision Custom Components (York PA), BWXT (Mount Vernon IN restart), Holtec (Camden NJ - also builds condensers/FWHs). Mangiarotti/Toshiba-BHI scope is the target."),
 ("4", "Cheap wins: transformers, diesels, chargers, penetrations, I&C boards",
  "+6 pp (~85M)",
  "Pure sourcing.",
  "US-BUILT large power transformers (Hyundai Montgomery AL, Virginia Transformer Roanoke VA, Delta Star) - location, not ownership, controls; GOES from Cleveland-Cliffs Butler PA. Fairbanks Morse (Beloit WI) diesels. AMETEK (OH) chargers/UPS. US-fab PMS boards converts a $32M Mixed item to clean US MP."),
 ("5", "Convert RCPs to clean US MPs",
  "+1 pp, robustness",
  "Non-US MPC (Doosan casing) currently taints an otherwise US product - only US MPCs count within it.",
  "Qualify a US casing forging/casting source (Scot Forge, North American Forgemasters?) so 100% of the ~$101M RCP cost counts unconditionally."),
 ("6", "RPV & SGs: accept foreign short-term, build US capacity mid-term",
  "+12 pp further upside (~175M)",
  "Pure sourcing; longest lead.",
  "No current US LWR ultra-heavy forging/vessel line. Nearest paths: BWXT Mount Vernon (IN) large-component restart; Doosan casing/vessel machining transplant; JSW/Doosan forgings remain imports (as MPCs of a US-fabricated vessel they only dilute, not disqualify). Without this lever the plan still clears 55% - with it there is margin."),
 ("7", "Guard the denominator",
  "Definitional",
  "Notice 2023-38 sec. 3.03(2)(c).",
  "Only MP direct costs enter the math. Steel/Iron items, site civil work, EPC indirects, land, and installation labor are excluded. Do not let a consultant put $2B of site construction in the denominator - the real MP pool is ~$1.4B, which is what makes 55% reachable."),
 ("8", "Joint FEOC optimization",
  "Compliance interlock",
  "Notice 2026-15 (see FEOC_Model_v2 workbook).",
  "Re-shoring for DC% also cuts FEOC exposure. Where domestic sourcing is impossible (rotor forgings, some SS pipe), prefer allied non-FEOC suppliers (JP/KR/IT are non-FEOC) - they dilute DC% but keep MACR safe."),
 ("", "RESULT", "",
  "",
  "Base (Vogtle-era) ~44%: PASSES only the 40% tier (pre-2025 BOC), FAILS 45/50/55. Strategic plan (levers 0-5, WITHOUT re-shoring RPV/SGs/RCL piping) ~78%: clears 55% with ~23 pp margin. Lever 6 (RPV/SG/RCL) adds a further ~12 pp of headroom. See Sheet 2 calculator."),
]
r = 3
for row in strat:
    ws.append(list(row))
    for j in range(1, 6):
        c = ws.cell(row=r, column=j)
        c.font = SMALL if row[0] != "" else BOLD
        c.border = THIN
        c.alignment = WRAP
    r += 1
set_widths(ws, [8, 40, 22, 48, 90])
ws.freeze_panes = "A3"

# ================= Sources =================
ws = wb.create_sheet("Sources")
ws.append(["Source", "What it provides", "Link / location"])
style_header(ws, 3)
src = [
 ("IRS Notice 2023-38 (May 2023)", "Operative DC framework: definitions, Steel/Iron test, Adjusted Percentage Rule direct-cost accounting, Table 2", "Sources/General Guidance; https://www.irs.gov/pub/irs-drop/n-23-38.pdf"),
 ("IRS Notice 2024-41 (May 2024)", "Hydropower Table 2 rows (closest civil-heavy analog); elective safe harbor (not available for nuclear)", "Sources/General Guidance; irs.gov/pub/irs-drop/n-24-41.pdf"),
 ("IRS Notice 2025-08 (Jan 2025)", "Updated safe harbor tables (solar/wind/BESS only)", "Sources/General Guidance"),
 ("IRS Notice 2026-15 (Feb 2026)", "FEOC material assistance rules (interlock with DC sourcing)", "Sources/General Guidance; FEOC_Model_v2_FINAL_06-02-2026.xlsx"),
 ("OBBBA (P.L. 119-21, July 2025)", "48E adjusted percentage schedule alignment (40/45/50/55)", "https://www.grantthornton.com/insights/alerts/tax/2025/insights/energy-incentives-under-obbba-what-you-need-to-know; https://www.sidley.com/en/insights/newsupdates/2025/07/the-one-big-beautiful-bill-act-navigating-the-new-energy-landscape"),
 ("CRS R48358", "Domestic content requirements overview", "https://www.congress.gov/crs-product/R48358"),
 ("Supplier & origin research (88 sourced claims)", "GA PSC docket 29849 VCM reports 1-12; 38 NRC vendor inspection reports; press/industry", "AP1000_Component_Database.xlsx - Suppliers & Supplier Evidence sheets; data/external/"),
 ("Cost basis: INL/RPT-24-77048 companion database (2024)", "AP1000 per-GNCOA-account factory equipment / site labor / site material costs, 2022 USD (TIMCAT NOAK + Stewart estimates)", "https://www.osti.gov/biblio/2371533; data/external/osti_2371533_tables.csv"),
 ("Cost basis: MIT TIMCAT (EEDB PWR12-ME)", "Sub-account factory-cost ratios used to split accounts into individual products (2018 USD)", "https://github.com/mit-crpg/TIMCAT; data/external/timcat_ap1000_accounts.csv"),
 ("AP1000 component inventory", "2,087-component DCD Rev 19 database (tags, classes, suppliers)", "AP1000_Component_Database.xlsx; https://employamericanicholas.github.io/ap1000-component-atlas/"),
 ("Employ America FEOC model", "AP1000 component taxonomy, cost shares, FEOC exposure", "Sources/FEOC_Model_v2_FINAL_06-02-2026.xlsx"),
]
r = 2
for row in src:
    ws.append(list(row))
    for j in range(1, 4):
        c = ws.cell(row=r, column=j)
        c.font = SMALL
        c.border = THIN
        c.alignment = WRAP
    r += 1
set_widths(ws, [42, 60, 80])

wb.save("AP1000_Domestic_Content_Analysis.xlsx")
print("saved AP1000_Domestic_Content_Analysis.xlsx")
print("MP rows:", len(mp_rows), "| total cost:", sum(x[3] for x in mp_rows),
      "| base dom:", sum(x[8] for x in mp_rows), "| strat dom:", sum(x[9] for x in mp_rows))
print("base DCP:", round(sum(x[8] for x in mp_rows)/sum(x[3] for x in mp_rows)*100,1), "%",
      "| strat DCP:", round(sum(x[9] for x in mp_rows)/sum(x[3] for x in mp_rows)*100,1), "%")
