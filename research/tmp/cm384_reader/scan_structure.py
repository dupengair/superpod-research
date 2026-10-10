import json, re
pages = json.load(open("pages_text.json", encoding="utf-8"))

sec_re = re.compile(r'^(\d+(\.\d+)*)\s+([A-Z][A-Z0-9 \-,&/]+|[A-Z][a-zA-Z].{0,60})$')
cap_re = re.compile(r'^(Figure|Fig\.?|Table|TABLE)\s*(\d+)[\.:]?\s', re.I)

for p in sorted(pages, key=int):
    t = pages[p]
    lines = t.split("\n")
    hits = []
    for ln in lines:
        ls = ln.strip()
        if cap_re.match(ls):
            hits.append(("CAP", ls[:95]))
        elif re.match(r'^(I{1,3}V?|IV|V|VI{0,3}|IX|X)\s*\.?\s+[A-Z]{2,}', ls) or re.match(r'^[A-Z]\.\s+[A-Z][a-z]', ls):
            hits.append(("H?", ls[:80]))
        elif re.match(r'^\d+(\.\d+)*\.?\s+[A-Z][a-zA-Z]', ls) and len(ls) < 70 and not re.match(r'^\d+\.\d+%', ls):
            hits.append(("SEC", ls[:80]))
        elif re.match(r'^\(\d+\)$', ls):
            hits.append(("EQ", ls))
        elif ls.startswith("REFERENCES") or ls.startswith("APPENDIX") or ls.startswith("ACKNOWLEDG"):
            hits.append(("BACK", ls))
    if hits:
        print(f"--- p.{p} ---")
        for k, s in hits:
            print(f"  [{k}] {s}")
