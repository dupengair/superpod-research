import json, re, pdfplumber, pypdfium2, os
from collections import defaultdict

PDF = "/home/dupengair/shared/work/pd..."  # placeholder replaced below
PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"
entries = json.load(open("structure.json", encoding="utf-8"))
caps = [e for e in entries if e["kind"] == "caption"]

def collect_band(objs, seed_t, seed_b, tol=14, up=True):
    """grow band [t,b] in one direction with gap tolerance"""
    t, b = seed_t, seed_b
    changed = True
    while changed:
        changed = False
        for (x0, ot, x1, ob) in objs:
            if up:
                if ot < t and ob >= t - tol:
                    t = min(t, ot); changed = True
            else:
                if ob > b and ot <= b + tol:
                    b = max(b, ob); changed = True
    return t, b

crops = {}
with pdfplumber.open(PDF) as pdf:
    for cap in caps:
        pno, cap_top, cap_bot = cap["page"], cap["top"], cap["bot"]
        page = pdf.pages[pno-1]
        H, W = page.height, page.width
        objs = [(o["x0"], o["top"], o["x1"], o["bottom"])
                for coll in ["images", "curves", "rects", "lines"]
                for o in getattr(page, coll)]
        m = re.match(r"^(Fig\.|Table)\s*(\d+)", cap["text"].replace(" ", ""))
        kind = "fig" if m.group(1) == "Fig." else "tab"
        num = int(m.group(2))
        if kind == "fig":
            t, b = collect_band(objs, cap_top - 4, cap_top - 4, up=True)
        else:
            t, b = collect_band(objs, cap_bot + 4, cap_bot + 4, up=False)
        inside = [o for o in objs if o[1] >= t - 2 and o[3] <= b + 2]
        if not inside:
            inside = objs
        x0 = min(o[0] for o in inside); x1 = max(o[2] for o in inside)
        if kind == "fig":  # include figure-internal Arial labels
            for e in entries:
                if e["page"] == pno and e["kind"] == "figlabel" and t - 3 <= e["top"] and e["bot"] <= b + 3:
                    x0 = min(x0, e["x0"]); x1 = max(x1, e["x1"])
        pad = 5
        bbox = (max(20, x0 - pad), max(20, t - pad), min(W - 20, x1 + pad), min(H - 10, b + pad))
        if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
            print(f"SKIP {kind}{num}: invalid bbox {bbox}"); continue
        crops[f"{'fig' if kind == 'fig' else 'table'}{num:02d}"] = (pno, bbox)

    # --- equations by line text match
    EQ_SPEC = [
        (22, 1, r"buffer_size\s*=\s*rank_num\s*×\s*max_tokens"),
        (22, 2, r"max_tokens\s*=\s*local_batch"),
        (37, 3, r"arg\s*min"),
        (38, 4, r"Block\(𝑋"),
    ]
    for pno, num, pat in EQ_SPEC:
        page = pdf.pages[pno - 1]
        words = page.extract_words(x_tolerance=1.5, y_tolerance=3, use_text_flow=False)
        lines = defaultdict(list)
        for w in words:
            lines[round((w["top"] + w["bottom"]) / 2 / 6)].append(w)
        for key in sorted(lines):
            ws = sorted(lines[key], key=lambda w: w["x0"])
            txt = " ".join(w["text"] for w in ws)
            if re.search(pat, txt) and len(txt) < 200:
                t = min(w["top"] for w in ws); b = max(w["bottom"] for w in ws)
                x0 = min(w["x0"] for w in ws); x1 = max(w["x1"] for w in ws)
                bbox = (40, max(0, t - 5), min(page.width - 40, x1 + 8), min(page.height, b + 5))
                crops[f"eq{num:02d}"] = (pno, bbox)
                print(f"eq{num:02d} p.{pno}: {txt[:90]}")
                break

json.dump(crops, open("crops.json", "w"))
print(f"total crops: {len(crops)}")

os.makedirs("assets", exist_ok=True)
os.makedirs("assets/equations", exist_ok=True)
doc = pypdfium2.PdfDocument(PDF)
for name, (pno, bbox) in sorted(crops.items()):
    page = doc[pno - 1]
    x0, y0, x1, y1 = bbox
    sc = 2.6 if name.startswith("eq") else 2.2
    full = page.render(scale=sc).to_pil()
    px = tuple(int(round(v * sc)) for v in (x0, y0, x1, y1))
    img = full.crop(px)
    subdir = "equations" if name.startswith("eq") else ""
    path = os.path.join("assets", subdir, f"{name}.png")
    img.save(path)
    print(f"{name}: p.{pno} bbox={tuple(round(v,1) for v in bbox)} -> {img.size}")
