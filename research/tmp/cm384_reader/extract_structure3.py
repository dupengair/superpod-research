import pdfplumber, json, re
from collections import defaultdict

PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"

with pdfplumber.open(PDF) as pdf:
    p = pdf.pages[7]  # p.8
    lines = defaultdict(list)
    for ch in p.chars:
        key = round((ch["top"] - 0.5*ch["size"])/4)
        lines[key].append(ch)
    prev_key=None
    for key in sorted(lines):
        chs = sorted(lines[key], key=lambda c: c["x0"])
        txt = "".join(c["text"] for c in chs)[:64]
        fams = set(c["fontname"].split("+")[-1] for c in chs)
        sz = round(max(c["size"] for c in chs),1)
        x0 = chs[0]["x0"]
        print(f"top~{key*4:3d} x0={x0:5.1f} sz={sz:4} {sorted(fams)} | {txt}")
