#!/usr/bin/env python3
"""Generate paper.md + source_map.json from blocks_raw.json + chunk_*.zh translations."""
"""Assemble paper.md + source_map.json from blocks_raw.json + chunk_*.zh.

Usage: python3 generate_reader.py <work_dir> [out_dir]
  work_dir  dir containing blocks_raw.json and chunk_*.zh translations
  out_dir   output bundle dir (default: <parent of work_dir>)
Outputs: paper.md, source_map.json, assets/ (copied from work_dir/assets).
"""
import json, re, os, glob, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
WORK = os.path.abspath(sys.argv[1])
OUTDIR = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(WORK)

# ---- load blocks
blocks = json.load(open(f"{WORK}/blocks_raw.json", encoding="utf-8"))

# ---- load translations
trans = {}
for f in sorted(glob.glob(f"{WORK}/chunk_*.zh")):
    for ln in open(f, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip():
            continue
        parts = ln.split("\t", 1)
        if len(parts) == 2:
            trans[parts[0].strip()] = parts[1].strip()

# ---- equation transcriptions (verified against crops)
EQ_LATEX = {}

# ---- figure/table registry from captions
fig_reg = {}   # num -> caption block
tab_reg = {}
for b in blocks:
    if b["type"] == "caption":
        m = re.match(r"^(Fig\.|Figure|Table)\s*(\d+)", b["text"])
        if m:
            reg = fig_reg if m.group(1) in ("Fig.", "Figure") else tab_reg
            reg[int(m.group(2))] = b

# ---- first substantive mention index for placement
mention = {}   # ("fig", n) or ("tab", n) -> S-id of first mentioning paragraph
for b in blocks:
    if b["type"] != "paragraph" or b.get("role"):
        continue
    txt = b["text"]
    for m in re.finditer(r"(?:Figure|Fig\.)\s*(\d+)", txt):
        k = ("fig", int(m.group(1)))
        if k not in mention and b["id"] in trans:
            mention[k] = b["id"]
    for m in re.finditer(r"Table\s*(\d+)", txt):
        k = ("tab", int(m.group(1)))
        if k not in mention and b["id"] in trans:
            mention[k] = b["id"]
# fallback: anchor to an S-block on the caption's own page
def fallback_anchor(reg_entry):
    pg = reg_entry["page"]
    for b in blocks:
        if b["page"] == pg and b["type"] in ("paragraph", "heading") and b["id"] in trans:
            return b["id"]
    return None

# ---- build S-block rendering list in doc order; captions inserted after mention anchor
heading_level = lambda t: 2 if re.match(r"^\d+\s+\S", t) else (3 if re.match(r"^\d+\.\d+", t) else 4)

def esc_cell(s):
    return s.replace("|", "\\|")

md_blocks = []      # list of (kind, payload)
smap_blocks = []    # source map entries
order = 0

# caption -> markdown card
def fig_card(num):
    reg = fig_reg[num]
    cap_en = reg["text"]
    cap_zh = trans.get(reg["id"], "")
    asset = f"fig{num:02d}"
    near = mention.get(("fig", num)) or fallback_anchor(reg)
    return f'''<a id="F{num:03d}"></a>
### 图 {num}

**Placed near:** {near or '?'}
**Source:** p.{reg['page']} {reg['id']}

![Figure {num}](assets/{asset}.png)

**Original caption:** {cap_en}

**中文图注:** {cap_zh}
'''

def tab_card(num):
    reg = tab_reg[num]
    cap_en = reg["text"]
    cap_zh = trans.get(reg["id"], "")
    asset = f"table{num:02d}"
    near = mention.get(("tab", num)) or fallback_anchor(reg)
    return f'''<a id="T{num:03d}"></a>
### 表 {num}

**Placed near:** {near or '?'}
**Source:** p.{reg['page']} {reg['id']}

![Table {num}](assets/{asset}.png)

**Original caption:** {cap_en}

**中文图注:** {cap_zh}
'''

# cards keyed by the S-id after which they render
insert_after = {}
for n in fig_reg:
    k = mention.get(("fig", n)) or fallback_anchor(fig_reg[n])
    insert_after.setdefault(k, []).append(fig_card(n))
for n in tab_reg:
    k = mention.get(("tab", n)) or fallback_anchor(tab_reg[n])
    insert_after.setdefault(k, []).append(tab_card(n))

# ---- markdown assembly
md = []
md.append("# UBEP: Re-architecting Expert Parallelism Communication Library for Production Superpods")
md.append("")
md.append("> **中文题名**：UBEP：面向生产级超节点的专家并行通信库重构")
md.append("> **作者**：Yipeng Liu, Chang Liu, Si Shen, Jiaqi Zheng, et al.（上海交通大学 & 华为等）")
md.append("> **来源**：[arXiv:2607.06202](https://arxiv.org/abs/2607.06202)（SIGCOMM '26，预印本）")
md.append("> **Reader 生成**：2026-10-12 · nature-reader 工作流（sigconf 双栏模板提取 + 分块翻译 + 装配校验）")
md.append("> **说明**：段落级中英对照；`Sxxx`=原文块、`Fxxx`=图、`Txxx`=表，锚点与 `source_map.json` 互查。本文无编号公式；Algorithm 1 伪代码以正文块呈现。双栏提取的部分段首粗体引导词可能有位置异常，已在译文中按语义归位。")
md.append("")

# TOC of sections
md.append("## 目录")
md.append("")
for b in blocks:
    if b["type"] == "heading" and b["id"] in trans and not b["text"].startswith(("1 AIV", "2 ", "3 ", "4 ", "5 ") or ()):
        pass
sec_heads = [b for b in blocks if b["type"] == "heading" and re.match(r"^\d+(\.\d+)*\s+\S", b["text"]) and b["id"] in trans]
for b in sec_heads:
    lvl = heading_level(b["text"])
    indent = "  " * (lvl - 2)
    anchor = b["id"]
    md.append(f"{indent}- [{b['text']}](#{anchor}) → {trans[b['id']]}")
md.append("")

# equation index
md.append("## 公式索引")
md.append("")
for eid in sorted(EQ_LATEX):
    latex, eqno, conf, desc = EQ_LATEX[eid]
    eb = next(b for b in blocks if b["id"] == eid)
    md.append(f"- [E{eid[1:]} · Eq. {eqno}](#{eid}) — p.{eb['page']}，{desc}")
md.append("")

# terminology table
md.append("## 术语表")
md.append("")
md.append("| 英文术语 | 中文译法 | 说明 |")
md.append("|---|---|---|")
for en, zh, note in [
    ("UBEP", "不译", "专家并行通信库（本文系统）"),
    ("superpod / supernode", "超节点", ""),
    ("UB (Unified Bus)", "统一总线（UB，灵衢）", "CM384 互连"),
    ("operatorization / fusing", "算子化 / 融合", ""),
    ("kernel decomposition", "核分解", "MoE FFN 拆解"),
    ("hierarchical token-level scheduling", "分层 token 级调度", ""),
    ("Data-as-Flag", "数据即标志（Data-as-Flag）", "同步机制"),
    ("dispatch / combine", "分发 / 合并", "MoE 通信两阶段"),
    ("all-to-all", "all-to-all", ""),
    ("UGAS", "统一全局地址空间", "unified global address space"),
    ("SyncAll / sentinel / flag polling", "不译 / 哨兵值 / 标志轮询", ""),
    ("AIC / AIV / UBuf", "不译", "昇腾执行单元/向量单元/统一缓冲"),
    ("DP / TP / PP / EP", "数据/张量/流水线/专家并行", ""),
    ("one-hop / two-hop", "一跳 / 两跳", "跨交换层级数"),
]:
    md.append(f"| {en} | {zh} | {note} |")
md.append("")
md.append("---")
md.append("")

# ---- body render
def s_block(b, zh, role_note=None):
    global order
    order += 1
    smap_blocks.append(dict(id=b["id"], page=b["page"], type=b["type"],
                            role=b.get("role"), order=order,
                            original_text=b["text"], translation=zh,
                            confidence="high", refs=[]))
    parts = [f'<a id="{b["id"]}"></a>', f'**Source:** p.{b["page"]} {b["id"]}', "",
             f"**Original:** {b['text']}", "", f"**中文:** {zh}", ""]
    return "\n".join(parts)

pending = md  # alias
for b in blocks:
    bid = b["id"]
    if b["type"] == "heading":
        if bid not in trans:
            continue
        lvl = heading_level(b["text"])
        md.append(f'<a id="{bid}"></a>')
        md.append("#" * lvl + f" {b['text']} / {trans[bid]}")
        md.append("")
    elif b["type"] == "paragraph":
        role = b.get("role")
        zh = trans.get(bid)
        if zh is None:
            continue
        if role == "title":
            continue  # already in header
        if role == "authors":
            md.append(f'<a id="{bid}"></a>')
            md.append(f"**Source:** p.{b['page']} {bid}（作者列表）")
            md.append("")
            md.append(f"**Original:** {b['text']}")
            md.append("")
            md.append(f"**中文:** {zh}")
            md.append("")
        elif role == "abs_heading":
            md.append(f"### 摘要 / Abstract")
            md.append("")
        elif role == "abstract":
            md.append(s_block(b, zh))
        elif role == "footnote":
            md.append(f"> {b['text']}  \n> **中文:** {zh}")
            md.append("")
        else:
            md.append(s_block(b, zh))
    elif b["type"] == "equation":
        if bid in EQ_LATEX:
            latex, eqno, conf, desc = EQ_LATEX[bid]
            smap_blocks.append(dict(id=bid, page=b["page"], type="equation", order=order,
                                    original_text=b["text"], translation=desc,
                                    confidence=conf,
                                    equation_number=eqno.lstrip("(").rstrip(")"),
                                    latex=latex, image_path=None))
            md.append(f'<a id="{bid}"></a>')
            md.append(f"**Source:** p.{b['page']} {bid} · Eq. {eqno}")
            md.append("")
            md.append(f"$$")
            md.append(latex)
            md.append(f"$$")
            md.append("")
            md.append(f"**中文说明：** {desc}（符号保持原样，已对照原 PDF 裁片核验。）")
            md.append("")
    if None in insert_after and b["type"] == "references":
        for card in insert_after[None]:
            md.append(card)
            import re as _re
            m = _re.search(r'id="(F|T)(\d+)"', card)
            mm = _re.search(r"Source:\s*p\.(\d+)\s*(C\d+)", card)
            if m and mm:
                kind, num = m.group(1), int(m.group(2))
                smap_blocks.append(dict(id=f"{kind}{num:03d}", page=int(mm.group(1)), type="caption",
                                        order=order, original_text="", translation="",
                                        confidence="high", refs=[mm.group(2)],
                                        image_path=f"assets/{'fig' if kind=='F' else 'table'}{num:02d}.png"))
    if b["type"] == "references":
        refs = re.split(r"(?=\[\d+\]\s)", b["text"])
        refs = [r.strip() for r in refs if r.strip()]
        md.append(f'<a id="{bid}"></a>')
        md.append(f"## References / 参考文献")
        md.append("")
        md.append(f"**Source:** p.54–58 {bid}（共 {len(refs)} 条，保留英文原文不译）")
        md.append("")
        for r in refs:
            md.append(f"- {r}")
        md.append("")
    # insert cards anchored after this block
    if bid in insert_after:
        for card in insert_after[bid]:
            md.append(card)
            # register fig/tab in source map
            m = re.search(r'id="(F|T)(\d+)"', card)
            mm = re.search(r'Source:\s*p\.(\d+)\s*(C\d+)', card)
            if m and mm:
                kind, num = m.group(1), int(m.group(2))
                page, cid = int(mm.group(1)), mm.group(2)
                smap_blocks.append(dict(id=f"{kind}{num:03d}", page=page, type="caption",
                                        order=order, original_text="", translation="",
                                        confidence="high", refs=[cid],
                                        image_path=f"assets/{'fig' if kind=='F' else 'table'}{num:02d}.png"))

os.makedirs(OUTDIR, exist_ok=True)
os.makedirs(f"{OUTDIR}/assets/equations", exist_ok=True)
open(f"{OUTDIR}/paper.md", "w", encoding="utf-8").write("\n".join(md))
print(f"paper.md: {len(md)} lines")

# ---- source_map.json
figs = []
for n, reg in sorted(fig_reg.items()):
    near = mention.get(("fig", n)) or fallback_anchor(reg)
    figs.append(dict(id=f"F{n:03d}", page=reg["page"], caption_id=reg["id"],
                     image_path=f"assets/fig{n:02d}.png",
                     placement_hint="near_first_mention", placed_after=near,
                     alt_text=reg["text"][:80]))
tabs = []
for n, reg in sorted(tab_reg.items()):
    near = mention.get(("tab", n)) or fallback_anchor(reg)
    tabs.append(dict(id=f"T{n:03d}", page=reg["page"], caption_id=reg["id"],
                     image_path=f"assets/table{n:02d}.png",
                     placement_hint="near_first_mention", placed_after=near,
                     alt_text=reg["text"][:80]))

glossary = [dict(term=en, translation=zh, note=note) for en, zh, note in [
    ("Unified Bus (UB)", "统一总线（UB，灵衢）", "华为超节点统一互连总线"),
    ("supernode", "超节点", ""),
    ("prefill", "预填充", "保留英文"),
    ("decode", "解码", ""),
    ("PDC disaggregation", "prefill-解码-缓存分离", ""),
    ("expert parallelism", "专家并行", ""),
    ("KV cache", "KV 缓存", ""),
    ("MLA", "多头潜在注意力", ""),
    ("MTP", "多 token 预测", ""),
    ("TPOT", "每 token 输出时间", ""),
    ("TTFT", "首 token 时间", ""),
    ("microbatch", "微批次", ""),
    ("AIV-direct", "AIV 直连通信", ""),
    ("SDMA", "SDMA（系统 DMA）", ""),
    ("FusedDispatch/FusedCombine", "不译", "融合分发/合并算子"),
    ("EMS", "弹性内存服务", ""),
    ("die", "芯粒", ""),
    ("scale-up", "纵向扩展", ""),
    ("UB plane", "UB 平面", ""),
    ("operator", "算子", ""),
]]

smap = dict(
    paper=dict(
        title="Serving Large Language Models on Huawei CloudMatrix384",
        venue="arXiv:2506.12708v3 (2025-06), CC BY 4.0",
        source_type="pdf", language="en",
        source_path="research/tmp/download/2025_Serving_Large_Language_Models_on_Huawei_CloudMatrix384_1fc88b9a8c2f.pdf"),
    blocks=smap_blocks,
    pages=[],
    figures=figs,
    equations=[dict(id=eid, page=next(b["page"] for b in blocks if b["id"] == eid),
                    equation_number=EQ_LATEX[eid][1].strip("()"),
                    latex=EQ_LATEX[eid][0], confidence=EQ_LATEX[eid][2],
                    image_path=None) for eid in sorted(EQ_LATEX)],
    glossary=glossary,
)
json.dump(smap, open(f"{OUTDIR}/source_map.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"source_map.json: {len(smap_blocks)} blocks, {len(figs)} figs, {len(tabs)} tabs")

# copy assets
import shutil
for f in glob.glob(f"{WORK}/assets/*.png"):
    shutil.copy(f, f"{OUTDIR}/assets/")
for f in glob.glob(f"{WORK}/assets/equations/*.png"):
    shutil.copy(f, f"{OUTDIR}/assets/equations/")
print("assets copied")
