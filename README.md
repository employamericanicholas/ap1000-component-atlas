# AP1000 Component Atlas

A component-level database and interactive 3D atlas of the Westinghouse AP1000 pressurized
water reactor, built entirely from public U.S. NRC licensing records — created to support
domestic content requirement analysis.

**Live site:** the `docs/` folder is served by GitHub Pages (Settings → Pages → deploy from
branch `main`, folder `/docs`).

## What's here

| Path | Contents |
|---|---|
| `docs/` | The website: three.js 3D general-arrangement model + searchable component browser |
| `docs/data/plant.json` | The merged dataset the site runs on |
| `AP1000_Component_Database.xlsx` | Excel workbook: 2,087 components, systems, structures, class definitions, 174-document index, TIMCAT/INL cost accounts, and blank domestic-content categorization columns (also at `docs/AP1000_Component_Database.xlsx`) |
| `data/master.json` / `data/master.csv` | The merged master dataset |
| `data/components_3_2_3.*` | Raw extraction of DCD Table 3.2-3 |
| `data/tier1_equipment.json` | Raw extraction of Tier 1 Chapter 2 equipment tables |
| `data/external/` | TIMCAT (EEDB cost accounts) and INL GAIN meta-analysis extracts |
| `scripts/` | The full extraction pipeline (download → parse → clean → merge → export) |

## Data sources

1. **Westinghouse AP1000 Design Control Document Rev. 19** (June 2011), NRC ADAMS package
   [ML11171A500](https://www.nrc.gov/docs/ML1117/ML11171A500.html) — 174 documents.
   - Core: Tier 2 **Table 3.2-3**, "Classification of Mechanical and Fluid Systems, Components,
     and Equipment" (ML11171A425): 1,454 tagged components across 67 systems with AP1000
     equipment class, seismic category, and construction code.
   - Tier 1 Chapter 2 ITAAC equipment tables (7 documents): 1,171 records adding electrical,
     I&C and qualification attributes; 633 components not itemized in Table 3.2-3.
2. **MIT TIMCAT** ([github.com/mit-crpg/TIMCAT](https://github.com/mit-crpg/TIMCAT)) — EEDB
   code-of-accounts nuclear construction cost model; factory-equipment vs. site-labor cost
   split per account, plus an AP1000-surrogate ("LPSR") component input model.
3. **INL/RPT-24-77048** ([osti.gov/biblio/2371533](https://www.osti.gov/biblio/2371533)) —
   2024 GAIN meta-analysis of advanced reactor costs; three per-account AP1000 estimates and
   an EEDB↔GNCOA account crosswalk.

Source PDFs (~99 MB, `data/raw/`) are not committed; rerun `scripts/download_all.sh` to fetch
all 174 from NRC.gov.

## Rebuilding

```bash
pip install pdfplumber openpyxl
bash scripts/download_all.sh          # fetch the DCD package from NRC ADAMS
python scripts/extract_table_3_2_3.py # parse Table 3.2-3 (75 sheets)
python scripts/clean_and_enrich.py    # repair column shifts, extract notes
python scripts/extract_tier1.py       # parse Tier 1 equipment tables
python scripts/build_master.py        # merge into data/master.json + .csv
python scripts/export_web.py          # write docs/data/plant.json
python scripts/build_xlsx.py          # build the Excel workbook
```

## Caveats

- Extraction is automated; verify critical values against the source PDF (every component
  links to its ML document).
- The 3D model is a schematic general arrangement from published DCD dimensions, not
  fabrication geometry (which Westinghouse does not publish).
- Turbine-island systems designated wholesale as "Class E" have no itemized parts list in
  the DCD; they appear in system notes.
- TIMCAT's LPSR model is an AP1000 surrogate (e.g., 193 vs. 157 fuel assemblies).

Not affiliated with Westinghouse Electric Company or the U.S. NRC.
