import pdfplumber, json, re
from collections import defaultdict

PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"

doc = []
with pdfplumber.open(PDF) as pdf:
    print(f"pages={len(pdf.pages)}, size={pdf.pages[0].width}x{pdf.pages[0].height}")
    # inspect fonts on a body page to calibrate
    p = pdf.pages[8]  # p.9 pure text page
    fonts = defaultdict(lambda: [0, 0.0])
    for ch in p.chars:
        f = fonts[ch["fontname"]]
        f[0] += 1
        f[1] = max(f[1], ch["size"])
    for k, (n, s) in sorted(fonts.items(), key=lambda x: -x[1][0]):
        print(f"  font {k}: n={n} maxsize={s:.1f}")
    # check left margins / indent on p.9
    xs = sorted(set(round(w["x0"],1) for w in p.extract_words() ))
    print("  common x0s on p.9:", xs[:12])
