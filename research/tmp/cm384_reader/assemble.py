import json, re, os
import pdfplumber
import pypdfium2
from collections import defaultdict

PDF = "/home/dupengair/shared/work/superpod/research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"
CAP_FAMS = {"LinBiolinumT", "LinBiolinumTI", "Inconsolatazi4-Regular"}
SYM_OK = lambda f: (not f.startswith("LinLibertine") and not f.startswith("Arial"))
EQ_PAGES = {22, 37, 38}
def is_eq_line(t):
    return (re.search(r"\((\d)\)\s*$", t) and len(t) < 150
            and any(m in t for m in ("=", "min", "||", "|"))
            and not t.rstrip().endswith(("include: (1)", "operations; (2)", "concurrently; (3)")))
RUNNING = re.compile(r"^Serving Large Language Models on Huawei CloudMatrix384\s*\d+$")

lines_all = []  # dict(page,top,bot,x0,x1,words=[(text,font,size,x0,x1)])
with pdfplumber.open(PDF) as pdf:
    PAGES = pdf.pages
    for pno, page in enumerate(pdf.pages, 1):
        if pno in (2, 3):  # arXiv TOC
            continue
        words = [w for w in page.extract_words(x_tolerance=1.5, y_tolerance=3, extra_attrs=["fontname", "size"])
                 if w.get("upright", True) or w["x0"] >= 30]
        buckets = defaultdict(list)
        for w in words:
            mid = (w["top"] + w["bottom"]) / 2
            buckets[round(mid / 5.2)].append(w)
        # merge neighbor buckets with close baselines
        keys = sorted(buckets)
        cur = None
        for k in keys:
            ws = buckets[k]
            top = min(w["top"] for w in ws); bot = max(w["bottom"] for w in ws)
            cx0 = min(w["x0"] for w in ws); cx1 = max(w["x1"] for w in ws)
            if cur is None:
                for w in ws: w["_lseq"] = 0
                cur = dict(page=pno, top=top, bot=bot, words=list(ws), x0=cx0, x1=cx1, seq=0)
                continue
            t_ws = " ".join(w["text"] for w in ws).strip()
            eq_like = bool(re.search(r"\(\d\)$", t_ws)) and any(m in t_ws for m in ("=", "min", "||", "|"))
            t_cur = " ".join(w["text"] for w in cur["words"]).strip()
            eq_cur = bool(re.search(r"\(\d\)$", t_cur)) and any(m in t_cur for m in ("=", "min", "||", "|"))
            v_overlap = top < cur["bot"] - 2
            if v_overlap and (top - cur["top"]) < 13 and not (eq_like or eq_cur):
                cur["seq"] += 1
                for w in ws: w["_lseq"] = cur["seq"]
                cur["words"] += ws
                cur["top"] = min(cur["top"], top); cur["bot"] = max(cur["bot"], bot)
                cur["x0"] = min(cur.get("x0", cx0), cx0); cur["x1"] = max(cur.get("x1", cx1), cx1)
            else:
                if cur: lines_all.append(cur)
                for w in ws: w["_lseq"] = 0
                cur = dict(page=pno, top=top, bot=bot, words=list(ws), x0=cx0, x1=cx1, seq=0)
        if cur: lines_all.append(cur)

for ln in lines_all:
    ws = sorted(ln["words"], key=lambda w: (w.get("_lseq", 0), w["x0"]))
    ln["words"] = ws
    ln["x0"] = ws[0]["x0"]; ln["x1"] = max(w["x1"] for w in ws)
    ln["text"] = " ".join(w["text"] for w in ws)
    fams = set(w["fontname"].split("+")[-1] for w in ws)
    ln["fams"] = fams
    ln["size"] = round(max(w["size"] for w in ws), 1)
    ln["minsize"] = round(min(w["size"] for w in ws), 1)

# ---- classify lines
for ln in lines_all:
    t = ln["text"].strip()
    kind = "body"
    if RUNNING.match(t) and ln["top"] < 75:
        kind = "skip"
    elif re.fullmatch(r"\d{1,3}", t) and (ln["top"] < 75 or ln["bot"] > 680):
        kind = "skip"
    elif re.match(r"^\d{1,3}\s*$", t):
        kind = "skip"
    elif ln["page"] == 1:
        kind = "front"  # handle p.1 later
    elif (re.match(r"^(Fig\.|Table)\s*\d+", t) and ln["fams"] & {"LinBiolinumT"}
          and all(f in CAP_FAMS or f == "LinBiolinumTB" or SYM_OK(f) for f in ln["fams"])
          and ln["minsize"] >= 8.8):
        kind = "caption"
    elif (ln["size"] >= 9.9 and len(t) < 90 and
          (("LinBiolinumTB" in ln["fams"] or "LinBiolinumTI" in ln["fams"]) and
           ln["fams"] <= {"LinBiolinumTB", "LinBiolinumTI", "LinBiolinumT"}) and
          (re.match(r"^\d+(\.\d+)+\s+\S", t) or not re.match(r"^\d+\s+[A-Z]", t))):
        kind = "heading"
    ln["kind"] = kind

# caption continuation absorption (forward)
by_page = defaultdict(list)
for ln in lines_all: by_page[ln["page"]].append(ln)
for pg in by_page: by_page[pg].sort(key=lambda l: l["top"])

for pg, lns in by_page.items():
    i = 0
    while i < len(lns):
        if lns[i]["kind"] == "caption":
            j = i + 1
            while j < len(lns):
                nxt = lns[j]
                if (nxt["kind"] == "body" and nxt["minsize"] >= 8.8 and nxt["size"] <= 9.5
                        and all(f in CAP_FAMS or SYM_OK(f) for f in nxt["fams"]) and nxt["x0"] < 60
                        and 0 <= nxt["top"] - lns[j-1]["bot"] < 4.5):
                    nxt["kind"] = "caption_cont"
                    j += 1
                else:
                    break
            i = j
        else:
            i += 1

# equations
for ln in lines_all:
    if ln["page"] in EQ_PAGES and is_eq_line(ln["text"].strip()):
        ln["kind"] = "equation"

# ---- figure / table bands
figband, tabband = {}, {}
crops = {}
for pg, lns in by_page.items():
    caps = [l for l in lns if l["kind"] == "caption"]
    page = PAGES[pg - 1]
    objs = [(o["x0"], o["top"], o["x1"], o["bottom"]) for coll in ("images", "curves", "rects", "lines") for o in getattr(page, coll)]
    for ci, cap in enumerate(caps):
        m = re.match(r"^(Fig\.|Table)\s*(\d+)", cap["text"])
        if not m: continue
        num = int(m.group(2))
        conts = [l for l in lns if l["kind"] == "caption_cont" and l["top"] > cap["top"] and (ci + 1 >= len(caps) or l["top"] < caps[ci+1]["top"])]
        cap["conts"] = conts
        cap_bot = conts[-1]["bot"] if conts else cap["bot"]
        cap["capbot"] = cap_bot
        if m.group(1) == "Fig.":
            tops = [o[1] for o in objs if o[1] > 74] + [l["top"] for l in lns if l["kind"] not in ("skip",) and l["top"] > 74]
            t0 = max(74, min(tops)) if tops else 79.7
            figband.setdefault(pg, []).append((t0, cap["top"] - 3, num))
        else:
            nxt_caps = [c2["top"] for c2 in caps if c2["top"] > cap_bot + 2]
            nxt_head = [l["top"] for l in lns if l["kind"] == "heading" and l["top"] > cap_bot + 2]
            stop = min(nxt_caps + nxt_head + [page.height - 25]) - 6
            b = cap_bot + 4
            cand = objs + [(l["x0"], l["top"], l["x1"], l["bot"]) for l in lns if l["kind"] not in ("skip", "heading", "caption")]
            ch = True
            while ch:
                ch = False
                for (x0, ot, x1, ob) in cand:
                    if ot <= b + 22 and ob > b and ot > cap_bot and ob < stop:
                        b = ob; ch = True
            tabband.setdefault(pg, []).append((cap_bot + 4, b, num))

def in_any(bands, pg, top, bot):
    for (t0, t1, *_) in bands.get(pg, []):
        if top >= t0 - 2 and bot <= t1 + 2:
            return True
    return False

# ---- drop figure/table interior lines from body flow
for ln in lines_all:
    if ln["kind"] in ("body", "note"):
        if in_any(figband, ln["page"], ln["top"], ln["bot"]):
            ln["kind"] = "fig_interior"
        elif in_any(tabband, ln["page"], ln["top"], ln["bot"]) and ln["kind"] != "caption":
            ln["kind"] = "tab_interior"

# ---- p.1 front matter split
p1 = by_page[1]
for ln in p1:
    t = ln["text"].strip()
    if ln["kind"] == "skip": continue
    if "LinBiolinumTB" in ln["fams"] and ln["size"] > 12:
        ln["kind"] = "title"
    elif t == "Abstract":
        ln["kind"] = "abs_heading"
    elif ln["top"] < 250 and ln["size"] >= 10.4:
        ln["kind"] = "authors"
    elif ln["top"] > 590:
        ln["kind"] = "footnote"
    elif ln["size"] <= 9.4:
        ln["kind"] = "abstract"
    else:
        ln["kind"] = "front_misc"

# ---- references pages 54-58
for ln in lines_all:
    if ln["page"] >= 54 and ln["kind"] == "body":
        ln["kind"] = "refentry"

# ---- group body into paragraphs
blocks = []  # final
sid = 0
cid = 0

import unicodedata
MATHR = re.compile(r"[\U0001D400-\U0001D7FF](?:[\U0001D400-\U0001D7FF ][\U0001D400-\U0001D7FF])*")

def tidy(s):
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.;:!?%\)])", r"\1", s)
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"([A-Za-z])- ([a-z])", r"\1-\2", s)
    s = s.replace("(cid:66)", "✉")
    def mat(m):
        return "$" + unicodedata.normalize("NFKC", m.group(0)).replace(" ", "") + "$"
    s = MATHR.sub(mat, s)
    return s.strip()

def render_words(ln):
    out, bold, ital = [], False, False
    for w in ln["words"]:
        f = w["fontname"].split("+")[-1]
        b = f in ("LinLibertineTB",)
        i = f in ("LinLibertineTI",)
        txt = w["text"]
        if b and not bold: out.append("**"); bold = True
        elif not b and bold: out.append("**"); bold = False
        if i and not ital: out.append("*"); ital = True
        elif not i and ital: out.append("*"); ital = False
        out.append(txt + " ")
    if bold: out.append("**")
    if ital: out.append("*")
    s = "".join(out)
    return re.sub(r"\s+", " ", s).replace(" )", ")").replace("( ", "(").replace(" **", "**").replace("** ", "** ").strip()

def new_para_check(prev, ln):
    if prev is None: return True
    x0 = ln["x0"]
    if 54.0 <= x0 <= 62.5: return True      # paragraph indent or list-item start
    if x0 >= 50.5: return False             # hanging-indent continuation (e.g. x0=76)
    if ln["top"] - prev["bot"] > 16.5: return True
    return False

cur_words = []
cur_meta = None
front_acc = None
def flush():
    global cur_words, cur_meta, sid
    if not cur_words or cur_meta is None: return
    text = tidy(" ".join(cur_words))
    sid += 1
    blocks.append(dict(id=f"S{sid:03d}", page=cur_meta["page"], type="paragraph",
                       role=cur_meta.get("role"), order=len(blocks) + 1, text=text,
                       bbox=[round(cur_meta["x0"], 1), round(cur_meta["top"], 1), 0, 0],
                       confidence="high"))

def flush_front():
    global front_acc, sid
    if front_acc is None: return
    sid += 1
    blocks.append(dict(id=f"S{sid:03d}", page=front_acc["page"], type="paragraph",
                       role=front_acc["role"], order=len(blocks) + 1,
                       text=tidy(" ".join(front_acc["parts"])),
                       bbox=[round(front_acc["x0"], 1), round(front_acc["top"], 1), 0, 0],
                       confidence="high"))
    front_acc = None

prev = None
for ln in lines_all:
    k = ln["kind"]
    if k in ("skip", "fig_interior", "tab_interior", "caption", "caption_cont"):
        flush(); flush_front(); cur_words, cur_meta = [], None
        prev = ln
        continue
    if k == "heading":
        flush(); flush_front(); cur_words, cur_meta = [], None
        sid += 1
        blocks.append(dict(id=f"S{sid:03d}", page=ln["page"], type="heading",
                           order=len(blocks) + 1, text=ln["text"].strip(),
                           bbox=[round(ln["x0"], 1), round(ln["top"], 1), 0, 0], confidence="high"))
        prev = ln; continue
    if k == "equation":
        flush(); flush_front(); cur_words, cur_meta = [], None
        m = re.search(r"\((\d)\)\s*$", ln["text"].strip())
        blocks.append(dict(id=f"E{int(m.group(1)):03d}", page=ln["page"], type="equation",
                           order=len(blocks) + 1, text=ln["text"].strip(),
                           bbox=[round(ln["x0"], 1), round(ln["top"], 1), 0, 0], confidence="medium"))
        prev = ln; continue
    if k in ("title", "authors", "abs_heading", "abstract", "footnote", "front_misc", "refentry", "note", "body"):
        if k == "refentry":
            flush_front()
            if cur_meta is None or cur_meta.get("role") != "refs":
                flush(); cur_words = []
                cur_meta = dict(ln); cur_meta["role"] = "refs"
            cur_words.append(ln["text"])
            prev = ln; continue
        if k == "body":
            flush_front()
            if new_para_check(prev, ln):
                flush(); cur_words = []
                cur_meta = dict(ln)
            cur_words.append(render_words(ln))
            prev = ln; continue
        # front matter & notes: accumulate consecutive same-role lines into one block
        if re.fullmatch(r"[✉∗*\s]+", ln["text"].replace("(cid:66)", "✉").strip()):
            prev = ln; continue
        role = {"title": "title", "authors": "authors", "abs_heading": "abs_heading",
                "abstract": "abstract", "footnote": "footnote", "front_misc": "front",
                "note": "note"}[k]
        fams_ok = front_acc is not None and (front_acc["fams"] & ln["fams"] or
                   (role != "authors" and abs(front_acc["size"] - ln["size"]) < 0.6))
        if (front_acc is None or front_acc["role"] != role or ln["page"] != front_acc["page"]
                or ln["top"] - front_acc["bot"] > 20 or not fams_ok):
            flush_front()
            front_acc = dict(role=role, page=ln["page"], top=ln["top"], bot=ln["bot"],
                             parts=[ln["text"]], x0=ln["x0"], fams=set(ln["fams"]), size=ln["size"])
        else:
            front_acc["parts"].append(ln["text"])
            front_acc["bot"] = ln["bot"]
            front_acc["fams"] |= set(ln["fams"])
        prev = ln; continue
flush()
flush_front()

# merge per-page refentry blocks into single refs block
final = []
refs_buf = []
for b in blocks:
    if b.get("role") == "refs":
        refs_buf.append(b["text"])
    else:
        final.append(b)
sid = len([b for b in final])
final.append(dict(id=f"S{sid+1:03d}", page=54, type="references", order=len(final)+1,
                  text="\n".join(refs_buf), bbox=[0, 0, 0, 0], confidence="high"))
blocks = final

# ---- captions with continuations
capno = 0
for pg, lns in by_page.items():
    for ln in lns:
        if ln["kind"] == "caption":
            capno += 1
            full = " ".join([ln["text"]] + [c["text"] for c in ln.get("conts", [])])
            full = tidy(full)
            blocks.append(dict(id=f"C{capno:03d}", page=pg, type="caption",
                               order=len(blocks) + 1, text=full,
                               bbox=[round(ln["x0"], 1), round(ln["top"], 1), 0, 0],
                               confidence="high"))

json.dump(blocks, open("blocks_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- render crops (figures: page-top..capbot; tables: captop..band_bottom)
import pypdfium2 as pdfium
doc = pdfium.PdfDocument(PDF)
crops = {}
for pg, bands in list(figband.items()) + []:
    for (t0, t1, num) in bands:
        crops[f"fig{num:02d}"] = (pg, (30, max(20, t0 - 6), PAGES[pg-1].width - 30, t1 + 2))
for pg, bands in tabband.items():
    for (t0, t1, num) in bands:
        page = PAGES[pg-1]
        objs = [(o["x0"], o["top"], o["x1"], o["bottom"]) for coll in ("images","curves","rects","lines") for o in getattr(page, coll)]
        wls = [(l["x0"], l["top"], l["x1"], l["bot"]) for l in by_page[pg] if l["kind"] not in ("skip",)]
        inside = [o for o in objs + wls if o[1] >= t0 - 2 and o[3] <= t1 + 2]
        x0 = min((o[0] for o in inside), default=45); x1 = max((o[2] for o in inside), default=page.width - 45)
        crops[f"table{num:02d}"] = (pg, (max(30, x0 - 6), max(20, t0 - 2), min(page.width - 30, x1 + 6), min(page.height - 15, t1 + 4)))
os.makedirs("assets", exist_ok=True); os.makedirs("assets/equations", exist_ok=True)
for name, (pg, bbox) in sorted(crops.items()):
    page = doc[pg - 1]
    sc = 2.2
    full = page.render(scale=sc).to_pil()
    img = full.crop(tuple(int(round(v * sc)) for v in bbox))
    img.save(f"assets/{name}.png")
json.dump({k: [v[0], list(v[1])] for k, v in crops.items()}, open("crops.json", "w"))
print("crops:", len(crops))
import pickle
dbg = [dict(page=l["page"], top=round(l["top"]), kind=l["kind"], minsize=l["minsize"],
            fams=sorted(l["fams"]), text=l["text"][:60]) for l in lines_all]
pickle.dump(dbg, open("dbg_lines.pkl", "wb"))
caplines = [d for d in dbg if re.match(r"^(Fig\.|Table)\s*\d+", d["text"])]
print(f"lines starting Fig./Table: {len(caplines)}")
for d in caplines:
    print(f"  p.{d['page']} top={d['top']} kind={d['kind']} minsz={d['minsize']} | {d['text'][:55]}")
print(f"blocks: {len(blocks)}")
from collections import Counter
print(Counter(b["type"] for b in blocks))
print("captions:", sum(1 for b in blocks if b["type"] == "caption"))
heads = [b for b in blocks if b["type"] == "heading"]
print(f"headings: {len(heads)}")
for h in heads: print(f"  {h['id']} p.{h['page']}: {h['text'][:60]}")
