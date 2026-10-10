import pdfplumber, json, sys

PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"

out = {}
with pdfplumber.open(PDF) as pdf:
    for i, page in enumerate(pdf.pages, 1):
        # use layout=True-ish extraction: words then reconstruct lines with x-order
        text = page.extract_text(x_tolerance=1.5, y_tolerance=3) or ""
        out[i] = text

with open("pages_text.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

# print page 1 to inspect
for p in ["1"]:
    print(f"===== PAGE {p} =====")
    print(out[int(p)])
