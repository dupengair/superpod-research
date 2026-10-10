#!/usr/bin/env python3
"""Build text-layout Chinese full-text PDF from nature-reader paper.md.

用户明示的替代方案：本环境无 image_gen，nature-paper-trans 的图片型逐页
PDF 不可产；改为用已核验的中文译文排 A4 文本型 PDF（含全部图表）。
"""
import re, os
from weasyprint import HTML

BASE = "/home/dupengair/shared/work/superpod/research/CloudMatrix384_2025"
MD = f"{BASE}/nature-reader/paper.md"
ASSETS = f"{BASE}/nature-reader/assets"
OUT = f"{BASE}/nature-paper-trans/CloudMatrix384_中文全文.pdf"

md = open(MD, encoding="utf-8").read()
lines = md.splitlines()

EQ_UNICODE = {
    "E001": ("buffer_size = rank_num × max_tokens × msg_size", "(1)"),
    "E002": ("max_tokens = local_batch × min(topK, experts_per_die)", "(2)"),
    "E003": ('s<sup>*</sup> = arg min<sub>s</sub> <i>L</i>(s)，其中 <i>L</i>(s) = ‖<i>Q</i>(<i>W</i>·<i>s</i>)(<i>s</i><sup>−1</sup>·<i>X</i>) − <i>W</i><i>X</i>‖', "(3)"),
    "E004": ('arg min<sub>α</sub> ‖Block(<i>X</i>;<i>W</i>) − Block(<i>X</i>;<i>Q</i>(<i>W</i>;<i>α</i>))‖', "(4)"),
}

def clean(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"\$(.+?)\$", r"<i>\1</i>", t)
    t = t.replace("`", "")
    return t

html = []
in_refs = False
i = 0
n = len(lines)
while i < n:
    ln = lines[i]

    # figure / table cards
    m = re.match(r"^### (Fig\.|Table) (\d+)\. ", ln)
    if m:
        kind, num = m.group(1), int(m.group(2))
        asset = f"{'fig' if kind=='Fig.' else 'table'}{num:02d}"
        cap_zh, src = "", ""
        j = i
        while j < n and not (lines[j].startswith("**Original caption:**")):
            if lines[j].startswith("**Source:**"):
                src = lines[j].replace("**Source:**", "").strip()
            j += 1
        while j < n and not lines[j].startswith("**中文图注:**"):
            j += 1
        if j < n:
            cap_zh = lines[j].replace("**中文图注:**", "").strip()
        path = f"file://{ASSETS}/{asset}.png"
        html.append(f'<figure><img src="{path}"/><figcaption>{clean(cap_zh)}<br/><span class="src">来源：{src}（原文 {kind} {num}）</span></figcaption></figure>')
        i = j + 1
        continue

    # equations
    m = re.match(r'^<a id="(E00\d)"></a>$', ln)
    if m:
        eid = m.group(1)
        while i < n and not lines[i].startswith("**中文说明：**"):
            i += 1
        expl = lines[i].replace("**中文说明：**", "").strip() if i < n else ""
        u, no = EQ_UNICODE[eid]
        html.append(f'<div class="eq"><span class="eqno">{no}</span>{u}<div class="eqx">{clean(expl)}</div></div>')
        i += 1
        continue

    # headings: "## 1 Introduction / 1 引言"
    m = re.match(r"^(#{2,4}) (.+?) / (.+)$", ln)
    if m:
        lvl = len(m.group(1)) - 1  # h2->h1 within body? keep h2
        zh = m.group(3).strip()
        html.append(f"<h{lvl}>{zh}</h{lvl}>")
        i += 1
        continue
    if re.match(r"^#{2,4} ", ln):  # untranslated headings
        i += 1
        continue

    # references section
    if ln.startswith("## References"):
        in_refs = True
        html.append("<h2>参考文献（保留英文原文）</h2>")
        i += 1
        continue
    if in_refs and ln.startswith("- "):
        html.append(f'<div class="ref">{ln[2:]}</div>')
        i += 1
        continue

    # bilingual S-blocks: take 中文 only
    if ln.startswith("**中文:** "):
        zh = ln.replace("**中文:** ", "").strip()
        # footnote quotes use "> **中文:**"
        html.append(f"<p>{clean(zh)}</p>")
        i += 1
        continue

    # terminology table (render simply)
    if ln.startswith("| 英文术语 |"):
        html.append('<table class="term"><tr><th>英文术语</th><th>中文译法</th><th>说明</th></tr>')
        i += 1
        while i < n and lines[i].startswith("|"):
            cells = [c.strip() for c in lines[i].strip("|").split("|")]
            if cells[0] != "英文术语" and not set(cells[0]) <= {"-", " ", ":"}:
                html.append("<tr>" + "".join(f"<td>{clean(c)}</td>" for c in cells[:3]) + "</tr>")
            i += 1
        html.append("</table>")
        continue

    i += 1

CSS = """
@page { size: A4; margin: 2.2cm 2cm;
  @bottom-center { content: counter(page) " / " counter(pages); font-size: 8pt; color: #888;
                   font-family: "WenQuanYi Micro Hei"; } }
body { font-family: "WenQuanYi Micro Hei", sans-serif; font-size: 10.5pt; line-height: 1.65; color: #1a1a1a; }
h1 { font-size: 20pt; color: #1f4e79; margin: 0.2em 0 0.6em; }
h2 { font-size: 14.5pt; color: #1f4e79; border-bottom: 1.5pt solid #1f4e79; padding-bottom: 2pt; margin: 1.4em 0 0.6em; page-break-after: avoid; }
h3 { font-size: 12.5pt; color: #1a1a1a; margin: 1.2em 0 0.5em; page-break-after: avoid; }
h4 { font-size: 11pt; color: #404040; margin: 1em 0 0.4em; page-break-after: avoid; }
p { margin: 0.45em 0; text-align: justify; }
p:first-child { font-weight: normal; }
figure { margin: 0.9em 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; }
figcaption { font-size: 9pt; color: #444; margin-top: 4pt; text-align: center; }
figcaption .src { font-size: 8pt; color: #888; }
.eq { margin: 0.7em 0 0.7em 1.5em; font-family: serif; font-size: 11.5pt; position: relative; padding: 4pt 8pt; background: #f4f6f8; }
.eqno { float: right; color: #666; }
.eqx { font-family: "WenQuanYi Micro Hei"; font-size: 9.5pt; color: #444; margin-top: 3pt; }
table.term { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 0.6em 0; }
table.term th, table.term td { border: 0.5pt solid #bbb; padding: 3pt 5pt; text-align: left; }
table.term th { background: #eef2f6; }
.ref { font-size: 8.5pt; color: #333; margin: 0.15em 0; padding-left: 1em; text-indent: -1em; }
.cover { text-align: left; margin-top: 3.5cm; }
.cover .zh-title { font-size: 24pt; font-weight: bold; color: #1a1a1a; line-height: 1.35; }
.cover .en-title { font-size: 13pt; color: #555; margin-top: 0.8em; font-family: serif; }
.cover .meta { font-size: 10.5pt; color: #666; margin-top: 1.2em; }
.cover .notice { font-size: 9.5pt; color: #8a6d3b; background: #fcf8e3; border: 0.5pt solid #e0d0a0;
                 padding: 8pt 10pt; margin-top: 2em; line-height: 1.6; }
"""

body = "\n".join(html)

doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="cover">
  <div class="zh-title">在华为 CloudMatrix384 超节点上<br/>服务大语言模型</div>
  <div class="en-title">Serving Large Language Models on Huawei CloudMatrix384</div>
  <div class="meta">Pengfei Zuo 等 48 人 · 华为 &amp; SiliconFlow<br/>
  arXiv:2506.12708v3 · 2025-06 · CC BY 4.0<br/>
  中文全文译本 · 2026-10-10</div>
  <div class="notice"><b>译本说明</b>：本 PDF 为<b>文本排版中文译本</b>（替代方案，非 nature-paper-trans 的逐页版式保留图片型产物——当前环境无 image_gen 生图工具）。译文取自本项目 nature-reader 全文精读产物（术语表锁定、数值已逐条回源核验）；正文图 24 幅、表 10 幅按原文出现位置插入并附中文图注；公式 Eq.(1)–(4) 以 Unicode 文本呈现；参考文献保留英文原文。</div>
</div>
<h2>术语对照表</h2>
{body}
</body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
HTML(string=doc, base_url=BASE).write_pdf(OUT)
print("saved:", OUT, os.path.getsize(OUT), "bytes")
