"""Apply curated supplier mapping (data/supplier_map.json) to data/master.json.

supplier_map.json schema:
{
  "suppliers": {
     "<id>": {"name":..., "manufacturing_location":..., "other_locations":...,
              "origin": "Domestic"|"Foreign"|"Mixed", "sources":[{"url":..., "doc":..., "quote":...}]}
  },
  "rules": [   # evaluated in order; first match wins
     {"match": {"type": "tag_exact"|"tag_prefix"|"tag_regex"|"system_keyword"|"system",
                "value": ..., "system": ..., "keywords": [...], "exclude_keywords": [...]},
      "supplier": "<id>", "scope_note": ..., "confidence": "high"|"medium"|"low"}
  ]
}
"""
import json
import re

d = json.load(open("data/master.json", encoding="utf-8"))
m = json.load(open("data/supplier_map.json", encoding="utf-8"))
SUP = m["suppliers"]
RULES = m["rules"]

def rule_matches(rule, c):
    mt = rule["match"]
    t = mt["type"]
    tag = (c.get("tag") or "").upper()
    desc = (c.get("description") or "").lower()
    sysc = c.get("system_code") or ""
    if t == "tag_exact":
        vals = mt["value"] if isinstance(mt["value"], list) else [mt["value"]]
        return tag in [v.upper() for v in vals]
    if t == "tag_prefix":
        vals = mt["value"] if isinstance(mt["value"], list) else [mt["value"]]
        return any(tag.startswith(v.upper()) for v in vals)
    if t == "tag_regex":
        return re.search(mt["value"], tag) is not None
    if t == "system_keyword":
        systems = mt["system"] if isinstance(mt["system"], list) else [mt["system"]]
        if sysc not in systems:
            return False
        if any(k.lower() in desc for k in mt.get("exclude_keywords", [])):
            return False
        return any(k.lower() in desc for k in mt["keywords"])
    if t == "system":
        systems = mt["value"] if isinstance(mt["value"], list) else [mt["value"]]
        return sysc in systems
    raise ValueError(f"unknown match type {t}")

matched = 0
by_rule = {}
for c in d["components"]:
    hit = None
    for i, rule in enumerate(RULES):
        if rule_matches(rule, c):
            hit = (i, rule)
            break
    if hit:
        i, rule = hit
        s = SUP[rule["supplier"]]
        c["supplier_name"] = s["name"]
        c["supplier_mfg_location"] = s.get("manufacturing_location", "")
        c["supplier_other_locations"] = s.get("other_locations", "")
        c["supplier_origin"] = s.get("origin", "")
        srcs = s.get("sources", [])
        c["supplier_source"] = "; ".join(x["url"] for x in srcs[:3])
        basis = f'{rule["match"]["type"]}: {rule.get("scope_note") or ""}'.strip().rstrip(":")
        c["supplier_basis"] = f'{basis} [{rule.get("confidence","medium")} confidence]'
        matched += 1
        by_rule[i] = by_rule.get(i, 0) + 1
    else:
        c["supplier_name"] = "Not publicly disclosed"
        c["supplier_mfg_location"] = ""
        c["supplier_other_locations"] = ""
        c["supplier_origin"] = "Unknown"
        c["supplier_source"] = ""
        c["supplier_basis"] = ""

d["supplier_map"] = m
json.dump(d, open("data/master.json", "w", encoding="utf-8"), indent=1)
print(f"matched {matched} / {len(d['components'])} components to suppliers")
unused = [i for i in range(len(RULES)) if i not in by_rule]
if unused:
    print("RULES WITH ZERO MATCHES (check them):")
    for i in unused:
        print("  ", RULES[i]["match"], "->", RULES[i]["supplier"])
from collections import Counter
print(Counter(c["supplier_origin"] for c in d["components"]))
