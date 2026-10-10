import pdfplumber, json, re
from collections import defaultdict

PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"

with pdfplumber.open(PDF) as pdf:
    for pno in [8, 36, 4]:
        p = pdf.pages[pno-1]
        print(f"===== p.{pno} =====")
        # group chars into lines by (top rounded)
        lines = defaultdict(list)
        for ch in p.chars:
            lines[round(ch["top"]/3)*3].append(ch)
        for top in sorted(lines):
            chs = sorted(lines[top], key=lambda c: c["x0"])
            txt = "".join(c["text"] for c in chs)[:70]
            fams = set(c["fontname"].split("+")[1] for c in chs)
            szs = set(round(c["size"],1) for c in chs)
            x0 = chs[0]["x0"]
            if any("Biolinum" in f for f in fams) or "TB" in "+".join(fams) or any(s>10.5 for s in szs):
                print(f"  top={top} x0={x0:.0f} sz={sorted(szs)} {sorted(fams)} | {txt}")
