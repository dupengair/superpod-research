import json, re, os, pdfplumber, pypdfium2
from collections import defaultdict

PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"
entries = json.load(open("structure.json", encoding="utf-8"))
caps = [e for e in entries if e["kind"] == "caption"]
crops = {}

with pdfplumber.open(PDF) as pdf:
    for cap in caps:
        pno, cap_top, cap_bot = cap["page"], cap["top"], cap["bot"]
        page = pdf.pages[pno - 1]
        H, W = page.height, page.width
        objs = [(o["x0"], o["top"], o["x1"], o["bottom"])
                for coll in ["images", "curves", "rects", "lines"]
                for o in getattr(page, coll)]
        words = page.extract_words(x_tolerance=1.5, y_tolerance=3)
        wlines = defaultdict(list)
        for w in words:
            wlines[round(w["top"] / 9)].append(w)
        wbands = []
        for k in sorted(wlines):
            ws = wlines[k]
            wbands.append((min(w["x0"] for w in ws), min(w["top"] for w in ws),
                           max(w["x1"] for w in ws), max(w["bottom"] for w in ws)))
        m = re.match(r"^(Fig\.|Table)\s*(\d+)", cap["text"].replace(" ", ""))
        kind = "fig" if m.group(1) == "Fig." else "tab"
        num = int(m.group(2))

        if kind == "fig":
            # top-floated figure: from page top margin down to caption
            top_objs = [o[1] for o in objs if o[1] > 70] + [b[1] for b in wbands if b[1] > 70]
            t = min(top_objs) if top_objs else 79.7
            t = max(t, 74)
            b = cap_top - 4
        else:
            # table below caption: grow through graphics AND word lines,
            # hard stop at the next caption on the same page
            next_caps = [c2["top"] for c2 in caps
                         if c2["page"] == pno and c2["top"] > cap_bot + 2]
            stop = min(next_caps) - 6 if next_caps else H - 30
            cand = objs + wbands
            b = cap_bot + 4
            changed = True
            while changed:
                changed = False
                for (x0, ot, x1, ob) in cand:
                    if ot <= b + 14 and ob > b and ot > cap_bot and ob < stop:
                        b = ob; changed = True
            t = cap_bot + 4
        inside = [o for o in objs if o[1] >= t - 2 and o[3] <= b + 2]
        inw = [wb for wb in wbands if wb[1] >= t - 2 and wb[3] <= b + 2]
        xs = [o[0] for o in inside] + [o[2] for o in inside] + [w[0] for w in inw] + [w[2] for w in inw]
        x0, x1 = (min(xs), max(xs)) if xs else (45, W - 45)
        pad = 6
        bbox = (max(30, x0 - pad), max(20, t - pad), min(W - 30, x1 + pad), min(H - 15, b + pad))
        crops[f"{'fig' if kind == 'fig' else 'table'}{num:02d}"] = (pno, bbox)

json.dump(crops, open("crops.json", "w"))
doc = pypdfium2.PdfDocument(PDF)
for name, (pno, bbox) in sorted(crops.items()):
    page = doc[pno - 1]
    x0, y0, x1, y1 = bbox
    sc = 2.2
    full = page.render(scale=sc).to_pil()
    img = full.crop(tuple(int(round(v * sc)) for v in (x0, y0, x1, y1)))
    img.save(f"assets/{name}.png")
    print(f"{name}: p.{pno} y=({bbox[1]:.0f},{bbox[3]:.0f}) h={bbox[3]-bbox[1]:.0f}pt -> {img.size}")
