"""Harvest AP1000 module IDs with context from NRC texts.

Pass A: scan txt dirs, collect candidate matches + context.
Outputs:
  candidates.jsonl  - every kept match (after keyword filter)
  review_ids.txt    - per unique ID, up to N distinct best snippets (for manual review)
  doc_meta.tsv      - ML -> detected report number(s)
"""
import json, pathlib, re, sys
from collections import defaultdict

base = pathlib.Path(__file__).parent
dirs = [base / "txt", base.parent.parent / "nrc_vendors" / "txt"]

# main module ID: prefix + 2-3 digits, optional trailing letter
MAIN = re.compile(r"\b(CA|CB|CH|CS|KQ|KB|Q|R)\s?-?(\d{2,3})([A-Z])?\b")
# sub-module: CA20-11, CA01-37, CB20-040, CA20-27-200
SUB = re.compile(r"\b((?:CA|CB|CH|CS|KQ|KB|Q|R)\d{2,3})\s?[-_]\s?(\d{1,3})(?:[-_](\d{1,4}))?\b")

MODULE_KW = re.compile(
    r"sub-?\s?module|module|lift(ed|ing)?\b|rigging|fabricat|assembl|erection|"
    r"placement|structural|weld|setting of|hoist|leak chase|panel", re.I)

# hard rejects: steel grades, CFR/section refs, common non-module tokens
REJECT_ID = {"Q235", "Q345", "Q195", "Q215", "CA95", "CA90"}
# reject when immediately preceded/followed by these context markers
REJECT_NEAR = re.compile(
    r"10 CFR|C\.F\.R|Room [A-Z0-9]|Grade Q|ASTM|ASME Section|drawing no", re.I)

def clean(s):
    return re.sub(r"\s+", " ", s).strip()

matches = []   # dicts
docs_meta = {}

REPNUM = re.compile(r"0520002[5-8][/-]\s?20\d{2}[-/]?0\d{2}|9990\d{4}/20\d{2}-\d{3}")

for d in dirs:
    if not d.exists():
        print("missing dir:", d); continue
    for f in sorted(d.glob("*.txt")):
        text = f.read_text(encoding="utf-8", errors="replace").replace("\x00", " ")
        ml = f.stem
        reps = sorted(set(clean(x).replace(" ", "") for x in REPNUM.findall(text[:6000])))
        if not reps:
            reps = sorted(set(clean(x).replace(" ", "") for x in REPNUM.findall(text)))[:3]
        docs_meta[ml] = ";".join(reps[:3])
        seen_spans = set()
        for m in list(SUB.finditer(text)) + list(MAIN.finditer(text)):
            span = (m.start(), m.end())
            # avoid MAIN re-reporting inside a SUB match
            if any(s <= m.start() < e for s, e in seen_spans):
                continue
            seen_spans.add(span)
            if m.re is SUB:
                mid = f"{m.group(1)}-{m.group(2)}" + (f"-{m.group(3)}" if m.group(3) else "")
                parent = m.group(1)
            else:
                mid = f"{m.group(1)}{m.group(2)}{m.group(3) or ''}"
                parent = mid
            if mid.upper() in REJECT_ID or parent.upper() in REJECT_ID:
                continue
            lo, hi = max(0, m.start() - 300), min(len(text), m.end() + 300)
            ctx = clean(text[lo:hi])
            near = clean(text[max(0, m.start() - 60):m.end() + 60])
            if REJECT_NEAR.search(near):
                continue
            if not MODULE_KW.search(ctx):
                continue
            matches.append({"id": mid, "parent": parent, "ml": ml, "ctx": ctx})

print(f"{len(matches)} matches kept")

with open(base / "candidates.jsonl", "w", encoding="utf-8") as f:
    for m in matches:
        f.write(json.dumps(m) + "\n")

with open(base / "doc_meta.tsv", "w", encoding="utf-8") as f:
    for ml, rep in sorted(docs_meta.items()):
        f.write(f"{ml}\t{rep}\n")

# review file: per unique parent ID, up to 3 distinct snippets (favor ones with 'module' close by)
def score(m):
    s = 0
    idx = m["ctx"].find(m["id"])
    window = m["ctx"][max(0, idx - 80): idx + 80]
    if re.search(r"sub-?module", window, re.I): s += 3
    if re.search(r"module", window, re.I): s += 3
    if re.search(r"structural|mechanical|piping", m["ctx"], re.I): s += 2
    if re.search(r"lift|rigging|placement|setting", m["ctx"], re.I): s += 1
    return -s

by_parent = defaultdict(list)
for m in matches:
    by_parent[m["parent"]].append(m)

with open(base / "review_ids.txt", "w", encoding="utf-8") as f:
    for pid in sorted(by_parent):
        ms = sorted(by_parent[pid], key=score)
        subs = sorted(set(m["id"] for m in ms if m["id"] != pid))
        mls = sorted(set(m["ml"] for m in ms))
        f.write(f"\n===== {pid}  ({len(ms)} mentions; docs: {', '.join(mls)})\n")
        if subs:
            f.write(f"  submodules: {', '.join(subs)}\n")
        used = set()
        n = 0
        for m in ms:
            key = m["ctx"][:100]
            if key in used: continue
            used.add(key)
            f.write(f"  [{m['ml']}] ...{m['ctx'][:450]}...\n")
            n += 1
            if n >= 3: break
print("wrote review_ids.txt")
