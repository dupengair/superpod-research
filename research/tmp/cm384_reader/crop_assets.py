import json, pdfplumber, pypdfium2, re
from collections import defaultdict

PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"
entries = json.load(open("structure.json", encoding="utf-8"))

caps = [e for e in entries if e["kind"] == "caption"]

def cluster(objs, seed_band, direction):
    """objs: list of (x0,top,x1,bottom). seed_band=(top_limit,bottom_limit).
    walk in direction collecting overlapping boxes within gap tolerance."""
    tol = 14
    cur_top, cur_bot = seed_band
    changed = True
    used = set()
    while changed:
        changed = False
        for i, (x0, t, x1, b) in enumerate(objs):
            if i in used: continue
            if direction == "up":
                if b > cur_top + 2 and t < cur_bot:  # overlaps or reaches into band
                    if b >= cur_top - tol:
                        cur_top = min(cur_top, t); used.add(i); changed = True
            else:
                if t < cur_bot + 2 and b > cur_top:
                    if t <= cur_bot + tol:
                        cur_bot = max(cur_bot, b); used.add(i); changed = True
    return cur_top, cur_bot

crops = {}  # name -> (page, bbox)
with pdfplumber.open(PDF) as pdf:
    for cap in caps:
        pno = cap["page"]
        page = pdf.pages[pno-1]
        objs = [(o["x0"], o["top"], o["x1"], o["bottom"]) for coll in ["images","curves","rects","lines"] for o in getattr(page, coll)]
        cap_top, cap_bot = cap["top"], cap["bot"]
        m = re.match(r"^(Fig\.|Table)\s*(\d+)", cap["text"].replace(" ", ""))
        kind = "fig" if m.group(1) == "Fig." else "tab"
        num = int(m.group(2))
        if kind == "fig":
            top, bot = cluster(objs, (0, cap_top - 3), "up")
        else:
            top, bot = cluster(objs, (cap_bot + 3, page.height), "down")
        # x-range: union of objects inside [top,bot]
        xs = [o for o in objs if o[1] >= top-2 and o[3] <= bot+2]
        x0 = min(o[0] for o in xs) if xs else 45; x1 = max(o[2] for o in xs) if xs else page.width-45
        # include figlabel text for figs
        if kind == "fig":
            for e in entries:
                if e["page"] == pno and e["kind"] == "figlabel" and e["top"] >= top-2 and e["bot"] <= bot+2:
                    x0 = min(x0, e["x0"]); x1 = max(x1, e["x1"])
        pad = 4
        bbox = (max(0,x0-pad), max(0,top-pad), min(page.width,x1+pad), min(page.height, bot+pad))
        name = f"{'fig' if kind=='fig' else 'table'}{num:02d}"
        crops[name] = (pno, bbox)

# equation crops: find body lines with eq numbers on p.22, p.37, p.38
eq_pages = {22: [(1,),(2,)], 37: [(3,)], 38: [(4,)]}
with pdfplumber.open(PDF) as pdf:
    for pno, nums in eq_pages.items():
        page = pdf.pages[pno-1]
        collected = defaultdict(list); collected_frag = defaultdict(list)
        lines = defaultdict(list)
        for ch in page.chars:
            lines[round(ch["top"]/3)].append(ch)
        for key in sorted(lines):
            chs = sorted(lines[key], key=lambda c: c["x0"])
            txt = "".join(c["text"] for c in chs)
            t = min(c["top"] for c in chs); b = max(c["bottom"] for c in chs)
            x0 = min(c["x0"] for c in chs); x1 = max(c["x1"] for c in chs)
            for (n,) in nums:
                collected[n].append((t, b, x0, x1, txt))
            if "experts_per_die" in txt or "max_tokens=local_batch" in txt.replace(" ",""):
                collected_frag[2].append((t, b, x0, x1, txt))
        for (n,) in nums:
            rows = collected.get(n) or collected_frag.get(n)
            if rows:
                t = min(r[0] for r in rows); b = max(r[1] for r in rows)
                x0 = min(r[2] for r in rows); x1 = max(r[3] for r in rows)
                name = f"eq{n:02d}"; pad = 5
                crops[name] = (pno, (x0-pad, t-pad, x1+pad, b+pad))
                print(f"eq({n}) p.{pno}: {' / '.join(r[4][:60] for r in rows)}")

json.dump(crops, open("crops.json","w"))
print(f"total crops: {len(crops)}")

# render
doc = pypdfium2.PdfDocument(PDF)
import os
os.makedirs("assets", exist_ok=True)
for name, (pno, bbox) in sorted(crops.items()):
    page = doc[pno-1]
    sc = 2.6 if name.startswith("eq") else 2.4
    x0, y0, x1, y1 = bbox
    pdfcrop = (x0, page.get_height() - y1, x1, page.get_height() - y0)
    img = page.render(scale=sc, crop=pdfcrop).to_pil()
    img.save(f"assets/{name}.png")
    print(f"{name}: p.{pno} bbox={tuple(round(v) for v in bbox)} size={img.size}")
