import json, re, pdfplumber
pages = json.load(open("pages_text.json", encoding="utf-8"))
PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"

# 1) find all section-like headings with broader pattern
print("== missed headings check (3.2 / 4.1 / refs) ==")
for p in sorted(pages, key=int):
    for ln in pages[p].split("\n"):
        ls = ln.strip()
        if re.match(r'^(3\.2|4\.1|5\.4|7|References|REFERENCES|Appendix|APPENDIX|Acknowledg)', ls) and len(ls)<75:
            print(f"  p.{p}: {ls}")

# 2) equations: look for right-aligned (N) lines or formula-ish lines
print("\n== display equations ==")
eqpat = re.compile(r'\(\d+\)\s*$')
for p in sorted(pages, key=int):
    for ln in pages[p].split("\n"):
        if eqpat.search(ln) and len(ln) < 120:
            print(f"  p.{p}: {ln.strip()[:110]}")

# 3) raster vs vector objects on figure pages
print("\n== page objects (images/curves/rects/lines) on fig pages ==")
with pdfplumber.open(PDF) as pdf:
    for pno in [8,9,10,11,12,13,19,20]:
        pg = pdf.pages[pno-1]
        print(f"  p.{pno}: images={len(pg.images)} curves={len(pg.curves)} rects={len(pg.rects)} lines={len(pg.lines)} chars={len(pg.chars)}")
        for im in pg.images:
            print(f"     img bbox=({im['x0']:.0f},{im['top']:.0f},{im['x1']:.0f},{im['bottom']:.0f})")
