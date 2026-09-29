"""Add the module level to data/master.json: a registry of publicly documented AP1000
construction modules (sources as [label, url] pairs for hyperlinking), plus module
assignments on components where public documents support the mapping."""
import json

d = json.load(open("data/master.json", encoding="utf-8"))

PSC = "https://psc.ga.gov/search/facts-document/?documentId="
NRC = "https://www.nrc.gov/docs/"
VCM11 = ["GA PSC VCM 11 (Aug 2014)", PSC + "154916"]
VCM12 = ["GA PSC VCM 12 (Feb 2015)", PSC + "157249"]
VCM910 = ["GA PSC VCM 9/10 (Feb 2014)", PSC + "152164"]
DCD38 = ["DCD Rev 19 Tier 2 sec. 3.8 (ML11171A431)", NRC + "ML1117/ML11171A431.pdf"]
SMCI_IR = ["NRC IR 99901439/2014-202 (ML14308A027)", NRC + "ML1430/ML14308A027.pdf"]
TOSHIBA = ["Toshiba, 5th MDEP Conf. (OECD-NEA, 2023)", "https://www.oecd-nea.org/mdep/events/conf-2023/presentations/S3/4.Toshiba.pdf"]

MODULES = [
 {"id": "CA01", "type": "Structural (containment internals)", "building": "Containment",
  "description": "T-shaped multicompartment module forming the central walls of the containment internal structures: refueling cavity/canal, reactor vessel compartment, and the two steam generator compartments (also houses the pressurizer compartment). ~88 ft long x 95 ft wide x 86 ft high, assembled on site from ~40 rail-shippable structural sub-modules (up to 12x12x80 ft, <=80 t), then concrete-filled.",
  "fabricator": "Sub-modules: Shaw/CB&I Lake Charles, LA (Unit 3); IHI + Toshiba, Japan (Unit 4); site assembly in the MAB",
  "origin": "Mixed (U3 Domestic / U4 sub-modules Foreign)",
  "sources": [["DCD Rev 19 Tier 2 sec. 3.8.3.6.1 (ML11171A431 pp. 40-41)", NRC + "ML1117/ML11171A431.pdf"], VCM11, TOSHIBA]},
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
  "description": "The reactor vessel cavity module, set inside the containment vessel bottom head.",
  "fabricator": "Fabricated on the Vogtle site (Unit 3 decision per VCM 9/10); SMCI RV-cavity formwork modules",
  "origin": "Domestic",
  "sources": [VCM910, SMCI_IR]},
 {"id": "CA05", "type": "Structural (containment internals)", "building": "Containment",
  "description": "Large structural composite wall and access tunnel module inside containment; provides separation between different trains of safety-related equipment. Eight sub-modules.",
  "fabricator": "Sub-modules: CB&I Lake Charles, LA; assembled in the MAB", "origin": "Domestic",
  "sources": [VCM11]},
 {"id": "CA20", "type": "Structural (auxiliary building)", "building": "Auxiliary Building",
  "description": "Largest AP1000 module: 72 sub-modules, >1,100 tons as lifted; auxiliary building structure containing the spent fuel pool, fuel transfer canal, and cask loading/washdown pit walls and floors.",
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
  "description": "Passive containment cooling water storage tank 'L' modules forming the PCCWST in the shield building roof.",
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
d["module_note"] = ("Module registry compiled from public sources (DCD Rev 19 sec. 3.8, GA PSC VCM reports, "
                    "NRC vendor inspection reports). The AP1000 uses roughly 106 structural + 52 mechanical modules "
                    "(~270-350 in total depending on counting method); the full module list and component-to-module "
                    "routing are Westinghouse-proprietary (APP-series drawings) and are NOT public. Component module "
                    "assignments here are limited to associations documented in public sources; blank does not mean "
                    "field-installed.")
json.dump(d, open("data/master.json", "w", encoding="utf-8"), indent=1)
print(f"modules: {len(MODULES)} | components assigned: {n}")
