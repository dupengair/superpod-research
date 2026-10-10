import pdfplumber, json, re
from collections import defaultdict

PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"
OUT = open("structure.json", "w", encoding="utf-8")

def fam(ch): return ch["fontname"].split("+")[-1]

def line_key(ch): return round(ch["top"]/3)

entries = []   # {kind, page, top, bottom, text}
graphic_boxes = defaultdict(list)  # page -> list of (x0,top,x1,bottom)
cap_index = {}  # (page, 'Fig 1') -> entry

with pdfplumber.open(PDF) as pdf:
    for pno, page in enumerate(pdf.pages, 1):
        # --- group chars into lines
        lines = defaultdict(list)
        for ch in page.chars:
            if not ch.get("upright", True):   # skip rotated arXiv stamp
                continue
            lines[line_key(ch)].append(ch)
        page_lines = []
        for key in sorted(lines):
            chs = sorted(lines[key], key=lambda c: c["x0"])
            fams = set(fam(c) for c in chs)
            sz = round(max(c["size"] for c in chs), 1)
            x0 = min(c["x0"] for c in chs); x1 = max(c["x1"] for c in chs)
            top = min(c["top"] for c in chs); bot = max(c["bottom"] for c in chs)
            txt = "".join(c["text"] for c in chs)
            page_lines.append(dict(key=key, x0=x0, x1=x1, top=top, bot=bot, sz=sz, fams=fams, text=txt))
        # merge adjacent line groups that are same style (caption wraps)
        merged = []
        for ln in page_lines:
            if merged and merged[-1]["fams"] == ln["fams"] and abs(merged[-1]["bot"] - ln["top"]) < 4 \
               and merged[-1]["sz"] == ln["sz"] and merged[-1]["x0"] < 47 and ln["x0"] < 60 \
               and (ln["fams"] & {"LinBiolinumT"}):
                m = merged[-1]
                m["text"] += " " + ln["text"]; m["bot"] = ln["bot"]; m["key2"] = ln["key"]
            else:
                merged.append(dict(ln))
        for ln in merged:
            fams, sz, txt = ln["fams"], ln["sz"], ln["text"]
            kind = None
            if sz == 8.0 and fams == {"LinBiolinumT"} and re.fullmatch(r"\d+", txt.strip()):
                continue  # page number
            if "LinBiolinumTB" in fams and len(txt.strip()) < 90 and not txt.strip().startswith("Fig"):
                kind = "heading"
            elif "Arial" in "+".join(fams):
                kind = "figlabel"  # inside figures
            elif "LinBiolinumT" in fams and re.match(r"^(Fig\.|Table)\s*\d+", txt.strip()):
                kind = "caption"
            elif sz == 8.0 and "LinBiolinum" in "+".join(fams):
                kind = "note"      # small footnote lines
            else:
                kind = "body"
            entries.append(dict(kind=kind, page=pno, top=round(ln["top"],1), bot=round(ln["bot"],1),
                                x0=round(ln["x0"],1), x1=round(ln["x1"],1), sz=ln["sz"],
                                fams=sorted(fams), text=txt))
        # --- graphics
        for coll_name in ["images", "curves", "rects", "lines"]:
            for obj in getattr(page, coll_name):
                graphic_boxes[pno].append((obj["x0"], obj["top"], obj["x1"], obj["bottom"]))

json.dump(entries, OUT, ensure_ascii=False, indent=0)
OUT.close()

# quick stats
from collections import Counter
c = Counter(e["kind"] for e in entries)
print(c)
caps = [e for e in entries if e["kind"]=="caption"]
heads = [e for e in entries if e["kind"]=="heading"]
print(f"captions={len(caps)}, headings={len(heads)}")
for e in caps: print(f"  p.{e['page']} top={e['top']:.0f} {e['text'][:60]}")
