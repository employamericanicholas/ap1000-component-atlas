"""Extract text from downloaded NRC PDFs into txt/ (skip existing)."""
import sys, pathlib
from pypdf import PdfReader

base = pathlib.Path(__file__).parent
pdfs = base / "pdfs"
txts = base / "txt"
txts.mkdir(exist_ok=True)

for pdf in sorted(pdfs.glob("*.pdf")):
    out = txts / (pdf.stem + ".txt")
    if out.exists() and out.stat().st_size > 100:
        continue
    try:
        r = PdfReader(str(pdf))
        text = "\n".join((p.extract_text() or "") for p in r.pages)
        out.write_text(text, encoding="utf-8", errors="replace")
        print(f"{pdf.stem}: {len(r.pages)} pages, {len(text)} chars")
    except Exception as e:
        print(f"{pdf.stem}: ERROR {e}")
