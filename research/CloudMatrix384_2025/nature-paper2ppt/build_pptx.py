#!/usr/bin/env python3
"""Build 12-slide Chinese group-meeting PPTX for CloudMatrix384 paper.
Reuses figure crops from ../nature-reader/assets (see asset_manifest.md)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image
import os

OUT = "output/final_presentation_cn.pptx"
FIG = "output/assets/figures"

# palette: restrained academic
INK = RGBColor(0x1A, 0x1A, 0x1A)
BLUE = RGBColor(0x1F, 0x4E, 0x79)
GREY = RGBColor(0x6E, 0x6E, 0x6E)
LGREY = RGBColor(0xB0, 0xB0, 0xB0)
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
BAND = RGBColor(0xF2, 0xF5, 0xF8)
ACCENT = RGBColor(0xC0, 0x50, 0x4D)

CN = "Microsoft YaHei"
EN = "Arial"

SW, SH = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width, prs.slide_height = SW, SH
BLANK = prs.slide_layouts[6]

def add_slide():
    return prs.slides.add_slide(BLANK)

def txt(slide, x, y, w, h, runs, size=14, color=INK, bold=False, font=CN,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.15, wrap=True):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    first = True
    if isinstance(runs, str):
        runs = [(runs, {})]
    for text, ov in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = ov.get("align", align)
        p.line_spacing = ov.get("ls", line_spacing)
        p.space_after = ov.get("sa", Pt(4))
        r = p.add_run()
        r.text = text
        f = r.font
        f.size = Pt(ov.get("size", size))
        f.bold = ov.get("bold", bold)
        f.color.rgb = ov.get("color", color)
        f.name = ov.get("font", font)
    return tb

def rect(slide, x, y, w, h, fill=PAPER, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(0.75)
    sp.shadow.inherit = False
    return sp

def title(slide, text, sub=None):
    txt(slide, Inches(0.6), Inches(0.32), Inches(12.1), Inches(0.9),
        text, size=27, bold=True, color=INK)
    # accent underline
    rect(slide, Inches(0.6), Inches(1.08), Inches(1.45), Pt(3.2), fill=BLUE)
    if sub:
        txt(slide, Inches(0.6), Inches(1.16), Inches(12.1), Inches(0.4),
            sub, size=11, color=GREY, font=EN)

def source(slide, text, x=None, y=None):
    x = x or Inches(0.6)
    y = y or Inches(7.06)
    txt(slide, x, y, Inches(8.5), Inches(0.3), text, size=8, color=GREY, font=EN)

def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text

def pic(slide, name, x, y, w=None, h=None):
    p = f"{FIG}/{name}.png"
    iw, ih = Image.open(p).size
    if w is not None:
        h = Emu(int(w * ih / iw))
    elif h is not None:
        w = Emu(int(h * iw / ih))
    return slide.shapes.add_picture(p, x, y, w, h), w, h

def bullet_lines(slide, x, y, w, items, size=14, gap=8, color=INK, ls=1.25):
    """simple text bullets, no card boxes"""
    tb = slide.shapes.add_textbox(x, y, w, Inches(0.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = ls
        p.space_after = Pt(gap)
        strong, rest = item
        r1 = p.add_run(); r1.text = "▪ " + strong
        r1.font.size = Pt(size); r1.font.bold = True; r1.font.color.rgb = INK; r1.font.name = CN
        if rest:
            r2 = p.add_run(); r2.text = rest
            r2.font.size = Pt(size); r2.font.color.rgb = RGBColor(0x40, 0x40, 0x40); r2.font.name = CN
    return tb

def metric_chip(slide, x, y, w, h, num, label, num_size=26, note=None):
    rect(slide, x, y, w, h, fill=BAND)
    txt(slide, x + Inches(0.14), y + Inches(0.10), w - Inches(0.28), Inches(0.55),
        num, size=num_size, bold=True, color=BLUE, font=EN)
    ly = y + Inches(0.10 + num_size / 72 * 0.95)
    txt(slide, x + Inches(0.14), ly, w - Inches(0.28), h - (Inches(0.10) + (ly - y)) - Inches(0.08),
        label, size=10.5, color=INK, line_spacing=1.1)

# ============================== S1 cover ==============================
s = add_slide()
rect(s, 0, 0, SW, SH, fill=PAPER)
rect(s, Inches(0.55), Inches(0.55), Pt(4), Inches(3.1), fill=BLUE)
txt(s, Inches(0.85), Inches(0.75), Inches(11.8), Inches(1.6),
    [("在华为 CloudMatrix384 超节点上", dict()),
     ("服务大语言模型", dict())],
    size=40, bold=True, color=INK, line_spacing=1.12)
txt(s, Inches(0.85), Inches(2.55), Inches(11.5), Inches(0.5),
    "Serving Large Language Models on Huawei CloudMatrix384",
    size=17, color=GREY, font=EN)
txt(s, Inches(0.85), Inches(3.35), Inches(11.5), Inches(0.4),
    "arXiv:2506.12708 · 华为 & SiliconFlow · 2025-06 · CC BY 4.0",
    size=12, color=GREY, font=EN)
# headline metrics band
bx, bw = Inches(0.85), Inches(3.75)
for i, (num, lab) in enumerate([
    ("6,688 / 1,943", "prefill / decode 吞吐（tokens/s/NPU）"),
    ("4.45 / 1.29", "prefill / decode 计算效率（tokens/s/TFLOPS）"),
    ("16 项基准", "INT8 量化精度与官方 API 相当"),
]):
    x = bx + i * (bw + Inches(0.25))
    rect(s, x, Inches(4.35), bw, Inches(1.15), fill=BAND)
    txt(s, x + Inches(0.18), Inches(4.50), bw - Inches(0.36), Inches(0.55),
        num, size=25, bold=True, color=BLUE, font=EN)
    txt(s, x + Inches(0.18), Inches(5.06), bw - Inches(0.36), Inches(0.35),
        lab, size=11, color=INK)
txt(s, Inches(0.85), Inches(6.75), Inches(11.5), Inches(0.4),
    "组会文献汇报 · 2026-10", size=12, color=LGREY)
notes(s, "这篇是华为 2025 年 6 月挂出的 CloudMatrix384 超节点系统论文，48 位作者，华为云与 SiliconFlow 合作。它回答一个问题：服务 6710 亿参数的 DeepSeek-R1，用什么硬件、什么软件栈效率最高。汇报分四块：动机、超节点架构、CloudMatrix-Infer 推理方案、评估结果。")

# ============================== S2 background ==============================
s = add_slide()
title(s, "参数、MoE、长上下文三重增长，把传统集群推向可扩展性极限")
bullet_lines(s, Inches(0.6), Inches(1.75), Inches(12.1), [
    ("万亿参数 MoE + 百万 token 上下文：", "算力强度、内存带宽、芯片间通信、时延约束同时收紧（§2.1）"),
    ("真实部署再叠加四类压力：", "变长输入、突发查询、专家激活不均衡，还要守住 SLO（§1）"),
    ("KV 缓存随并发数线性增长：", "如何在全系统分布、放置、访问 KV 缓存成为一级约束（§2.2）"),
], size=15.5, gap=14)
# bottom: the four constraints as a quiet strip
cons = [("计算强度", "密集 GEMM/注意力"), ("内存带宽", "KV 缓存读放大"), ("互连开销", "all-to-all 通信"), ("时延 SLO", "TPOT/TTFT 双指标")]
cw = Inches(2.95)
for i, (a, b) in enumerate(cons):
    x = Inches(0.6) + i * (cw + Inches(0.12))
    rect(s, x, Inches(4.85), cw, Inches(1.35), fill=BAND)
    txt(s, x + Inches(0.16), Inches(5.05), cw - Inches(0.32), Inches(0.4), a, size=15, bold=True, color=INK)
    txt(s, x + Inches(0.16), Inches(5.50), cw - Inches(0.32), Inches(0.6), b, size=11, color=GREY)
txt(s, Inches(0.6), Inches(6.45), Inches(12), Inches(0.4),
    "论文判断：这些约束叠加后，修补式扩展不再够用，需要软硬件协同的重新架构（§1）",
    size=12.5, color=BLUE)
source(s, "Source: §1-2, arXiv:2506.12708v3")
notes(s, "背景讲三层：模型侧三重增长；部署侧真实负载的四类压力；以及 KV 缓存线性增长这个新瓶颈。作者据此主张：传统集群的层次式架构到头了，要推翻重来。注意这页是全文动机，后面所有设计都对应这四个约束。")

# ============================== S3 problem ==============================
s = add_slide()
title(s, "层次式互连把通信密集操作卡在“节点边界”上")
bullet_lines(s, Inches(0.6), Inches(1.7), Inches(6.55), [
    ("带宽断崖：", "节点内 PCIe 约 256 GB/s，节点间仅约 25 GB/s（200 Gbps）"),
    ("调度被迫迁就局部性：", "Dynamo、Mooncake 等 KVCache 中心化架构把请求绑到缓存所在节点"),
    ("代价：", "调度复杂、动态负载下易失衡，解码节点 DRAM 成为孤岛（§4.1）"),
], size=14.5, gap=12)
p, w, h = pic(s, "fig01", Inches(0.6), Inches(3.98), w=Inches(5.95))
txt(s, Inches(0.6), Inches(6.80), Inches(6.5), Inches(0.3),
    "CloudMatrix 愿景：拆掉机柜/节点分层，全对等池化", size=10.5, color=GREY)
source(s, "Source: Fig. 1, arXiv:2506.12708v3", y=Inches(7.14))
# right rail: the claim
rect(s, Inches(7.55), Inches(1.75), Inches(5.15), Inches(4.9), fill=BAND)
txt(s, Inches(7.85), Inches(2.05), Inches(4.55), Inches(4.3),
    [("论文的核心主张", dict(size=12, color=GREY, sa=10)),
     ("“一切皆可池化、", dict(size=21, bold=True, color=INK, sa=2)),
     ("被平等对待、", dict(size=21, bold=True, color=INK, sa=2)),
     ("自由组合。”", dict(size=21, bold=True, color=INK, sa=14)),
     ("MoE 专家并行与分布式 KV 访问这两类通信密集操作，", dict(size=13, color=INK, sa=4)),
     ("最直接受益于全对等高带宽互连（§3.1）", dict(size=13, color=INK))],
    line_spacing=1.2)
notes(s, "问题页。左上是传统集群的数字：节点内外带宽差一个数量级，这是所有调度复杂度的根源。右栏是论文的原话，全对等三个关键词：池化、平等、自由组合。图 1 展示从分池分层到统一超节点的愿景。")

# ============================== S4 architecture ==============================
s = add_slide()
title(s, "CloudMatrix384：384 颗昇腾 910 + 192 颗鲲鹏组成全对等超节点")
p, w, h = pic(s, "fig02", Inches(1.45), Inches(1.5), w=Inches(10.4))
y = 1.5 + h / 914400 + 0.14
bullet_lines(s, Inches(0.9), Inches(y), Inches(11.6), [
    ("768 个 NPU 芯粒经统一总线（UB，灵衢）互连：", "任意芯粒间通信不跨层次，两跳直达"),
    ("算力、内存、网络均成为可池化资源：", "统一地址语义访问、按需独立扩展（§3.2）"),
], size=13, gap=5)
source(s, "Source: Fig. 2, arXiv:2506.12708v3", y=Inches(7.14))
notes(s, "方法总览。硬件上 384 颗 910（每颗双芯粒，共 768 die）+ 192 颗鲲鹏 CPU 打成一个超节点。关键不是规模数字，而是拓扑：UB 交换让任何两个芯粒之间都是对等关系，没有节点内/节点外的带宽断崖。")

# ============================== S5 UB fabric ==============================
s = add_slide()
title(s, "UB 平面把跨芯粒通信推到接近本地的语义与带宽")
p, w, h = pic(s, "fig05", Inches(0.6), Inches(1.7), w=Inches(12.1))
yb = 1.7 + h / 914400 + 0.25
cw = Inches(3.92)
for i, (num, lab) in enumerate([
    ("131 vs 46 GB/s", "Combine 每 rank 带宽（EP8），约为 H800 RDMA 的 3×"),
    ("118 vs 318 µs", "Combine 时延（EP8）；EP256 下仍 149 vs 360 µs"),
    ("103 vs 40 GB/s", "EP256 高并行度下 Combine 带宽仍 2.6×"),
]):
    x = Inches(0.6) + i * (cw + Inches(0.17))
    metric_chip(s, x, Inches(yb), cw, Inches(1.28), num, lab, num_size=19)
txt(s, Inches(0.6), Inches(6.78), Inches(12.1), Inches(0.3),
    "拓扑：板载 L1 + 机柜级 L2 两级 UB 交换，L2 无带宽收敛；7 个子平面 × 16 颗 L2 芯片 × 48 端口",
    size=10.5, color=GREY)
source(s, "Source: Fig. 5 & Table 6（CANN EP vs DeepSeek DeepEP on H800）", y=Inches(7.14))
notes(s, "UB 交换系统是全对等的物理基础。两个层次交换机，单跳语义。数据用通信算子对比：同样是 MoE 的 Combine，CANN 在 CM384 上每 rank 131 GB/s，H800 走 RDMA 只有 46，三倍差距；且高 EP 度下保持。诚实说明：Dispatch 在大 EP 度下带宽退化，作者自己指出是待优化点。")

# ============================== S6 PDC ==============================
s = add_slide()
title(s, "CloudMatrix-Infer：prefill、解码、缓存分离为三个资源池")
p, w, h = pic(s, "fig09", Inches(0.6), Inches(1.62), w=Inches(7.9))
txt(s, Inches(0.6), Inches(1.62 + h / 914400 + 0.1), Inches(7.9), Inches(0.3),
    "PDC 分离：三池各自扩展，经 UB 对等互通", size=10.5, color=GREY)
bullet_lines(s, Inches(8.85), Inches(1.75), Inches(3.9), [
    ("对等替代 KVCache 中心化：", "UB 上等带宽访问缓存，调度不再迁就局部性"),
    ("收益：", "调度简化、负载更均衡、缓存容量全池共享（§4.1）"),
    ("预分配双缓冲：", "消除动态形状带来的分配与同步开销"),
], size=12.5, gap=10)
source(s, "Source: Fig. 9, arXiv:2506.12708v3")
notes(s, "软件架构第一步：PDC 分离。与 Dynamo、Mooncake 的本质区别在于缓存访问不依赖局部性——因为 UB 让远程访问带宽接近本地。这页是论文第一项核心创新。")

# ============================== S7 LEP ==============================
s = add_slide()
title(s, "EP320 专家并行：每个 NPU 芯粒只放一个专家")
p, w, h = pic(s, "fig10", Inches(0.6), Inches(1.62), w=Inches(7.9))
txt(s, Inches(0.6), Inches(1.62 + h / 914400 + 0.1), Inches(7.9), Inches(0.3),
    "上：三次 all-to-all 的基本 MoE 流程；下：融合算子流程", size=10.5, color=GREY)
bullet_lines(s, Inches(8.85), Inches(1.75), Inches(3.9), [
    ("FusedDispatch / FusedCombine：", "融合算子替换三次 all-to-all，AIV 直连写入对端内存"),
    ("消息先行 INT8 量化：", "每 token 消息压到 7.5 KB，通信与计算重叠"),
    ("EP320：", "DeepSeek-R1 的 256 路由专家 + 冗余，逐芯粒单专家，解码低时延"),
], size=12.5, gap=10)
source(s, "Source: Fig. 10-12, arXiv:2506.12708v3")
notes(s, "第二项创新：大规模专家并行。DeepSeek-R1 有 256 个路由专家，CM384 用 EP320 把每个专家放到一个芯粒上，多出的部署冗余。通信侧用两个融合算子替换三次 all-to-all，直写远端 UBuffer，配合数据发送流水线隐藏地址计算。")

# ============================== S8 microbatch + MTP ==============================
s = add_slide()
title(s, "微批次流水线与 MTP：解码吞吐再拿 5.8%~9.4% 与 6%~49%")
# left: microbatch; right: MTP
lx, rx = Inches(0.6), Inches(6.85)
for x, (head, items) in zip((lx, rx), [
    ("微批次解码流水线（§4.2.3）", [
        "注意力流与 MoE 流按微批次重叠",
        "逐层时延降低约 10%",
        "batch 64/96/128 吞吐 +5.8% / +9.4% / +6.9%",
    ]),
    ("多 token 预测 MTP（§4.2.4）", [
        "单投机 token，接受率约 70%",
        "batch 越小收益越大：+6% ~ +49%",
        "DeepSeek-R1 原生特性，硬件侧流水化支持",
    ]),
]):
    rect(s, x, Inches(1.7), Inches(5.9), Inches(3.1), fill=BAND)
    txt(s, x + Inches(0.22), Inches(1.92), Inches(5.5), Inches(0.4), head, size=15.5, bold=True, color=INK)
    bullet_lines(s, x + Inches(0.22), Inches(2.5), Inches(5.46), [(t, "") for t in items], size=13, gap=8)
# bottom comparison note
rect(s, Inches(0.6), Inches(5.15), Inches(12.15), Inches(1.35), fill=PAPER, line=LGREY)
txt(s, Inches(0.85), Inches(5.38), Inches(11.7), Inches(1.0),
    [("对照：SGLang 在 NVIDIA H100 集群上称微批次收益可达 35%。", dict(size=13.5, bold=True, color=INK, sa=6)),
     ("CM384 上收益较小的原因：UB 平面的 MoE 分发/合并通信停顿本身就更低，可隐藏的开销天花板更低（§5.4.1）——",
      dict(size=12.5, color=GREY)),
     ("这从反面印证了互连质量：别人的优化项，在这里已是基线。", dict(size=12.5, color=BLUE))],
    line_spacing=1.25)
source(s, "Source: Fig. 20-22 & §5.4, arXiv:2506.12708v3")
notes(s, "两个解码加速器。微批次是把一条迭代切成微批重叠两条执行流；MTP 是投机解码的模型内建版。重点是底部对照：H100 上微批次能拿 35%，这里只有个位数——因为 UB 通信开销本来就小，可隐藏的空间小。这恰好说明互连才是根子。")

# ============================== S9 EMS ==============================
s = add_slide()
title(s, "UB 驱动的分布式缓存：冷启动 2,560s→320s，命中时 prefill 2.28×")
p, w, h = pic(s, "fig19", Inches(0.6), Inches(1.62), w=Inches(7.9))
txt(s, Inches(0.6), Inches(1.62 + h / 914400 + 0.1), Inches(7.9), Inches(0.3),
    "EMS 分离式内存池部署形态：UB 平面直连各节点 DRAM", size=10.5, color=GREY)
bullet_lines(s, Inches(8.85), Inches(1.7), Inches(3.9), [
    ("模型加载：", "8 实例争 2.5 GB/s OBS，2,560s → EMS 池化共享 320s"),
    ("模型切换：", "本地缓存命中率仅 12.5% 时 281s；EMS 约 5s"),
    ("上下文缓存：", "复用率 90% 时 prefill 2.28×、TTFT 降 59%"),
    ("内存占用：", "8 实例共享 1 份模型副本"),
], size=12.5, gap=9)
source(s, "Source: Fig. 19, Table 1 & Fig. 23, arXiv:2506.12708v3")
notes(s, "第三块创新：把全池 DRAM 当一层缓存。模型加载的数字最直观：不加缓存 8 个实例抢 2.5G 带宽要 2560 秒，EMS 共享加载只要 320 秒，8 倍。上下文缓存复用率 90% 时 prefill 吞吐 2.28 倍。这个设计只有 UB 带宽才做得起——VPC 平面同样配置明显更差。")

# ============================== S10 overall perf ==============================
s = add_slide()
title(s, "DeepSeek-R1 服务效率超过 H100/H800 已发表结果")
rows = [
    ("系统", "prefill 效率\n(tokens/s/TFLOPS)", "decode 效率\n(tokens/s/TFLOPS)", "decode 吞吐\n(tokens/s/GPU·NPU)"),
    ("SGLang @H100", "3.75（Perfect EPLB）", "1.10", "2,172（batch 128）"),
    ("DeepSeek(Profile) @H800", "3.96", "1.17", "2,325（batch 128）"),
    ("DeepSeek(Blog) @H800", "—", "0.93", "1,850"),
    ("CloudMatrix-Infer", "3.76 默认 / 4.45 Perfect EPLB", "1.29", "1,943（batch 96）"),
]
tw, th = Inches(12.1), Inches(3.2)
gt = s.shapes.add_table(5, 4, Inches(0.6), Inches(1.75), tw, th).table
gt.columns[0].width = Inches(3.4)
gt.columns[1].width = Inches(3.4)
gt.columns[2].width = Inches(2.5)
gt.columns[3].width = Inches(2.8)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = gt.cell(ri, ci)
        cell.margin_left = cell.margin_right = Inches(0.1)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tfc = cell.text_frame
        tfc.word_wrap = True
        lines = val.split("\n")
        for li, ln in enumerate(lines):
            para = tfc.paragraphs[0] if li == 0 else tfc.add_paragraph()
            para.alignment = PP_ALIGN.LEFT
            r = para.add_run(); r.text = ln
            r.font.size = Pt(13 if ri == 0 else 12.5)
            r.font.name = CN if ri == 0 or ci == 0 else EN
            r.font.bold = (ri == 0) or (ri == 4)
            r.font.color.rgb = PAPER if ri == 0 else (BLUE if ri == 4 else INK)
        if ri == 0:
            cell.fill.solid(); cell.fill.fore_color.rgb = BLUE
        elif ri == 4:
            cell.fill.solid(); cell.fill.fore_color.rgb = BAND
        else:
            cell.fill.solid(); cell.fill.fore_color.rgb = PAPER
# metric strip
cw = Inches(3.92)
for i, (num, lab) in enumerate([
    ("6,688", "prefill tokens/s/NPU @4K prompt（Perfect EPLB）"),
    ("1,943", "decode tokens/s/NPU，TPOT 49.4 ms（batch 96）"),
    ("538", "sub-15 ms 更严 SLO 下仍可维持的 decode 吞吐"),
]):
    x = Inches(0.6) + i * (cw + Inches(0.17))
    metric_chip(s, x, Inches(5.35), cw, Inches(1.35), num, lab, num_size=24)
source(s, "Source: Table 2-4 & §5.2；对比系统的 decode 批大小为 128（CM384 为 96）", y=Inches(6.95))
notes(s, "主结果。看效率列而不是绝对吞吐列：CM384 芯粒 FP16 算力低于 H100/H800，但每 TFLOPS 产出的 token 更多，prefill 4.45、decode 1.29 都是最高的。绝对吞吐略低于两个 batch 128 的系统，注意公平性脚注。左边默认配置 3.76 也已超过 SGLang 默认，差距来自 EPLB 负载均衡还有优化空间。")

# ============================== S11 accuracy ==============================
s = add_slide()
title(s, "INT8 量化：16 项基准精度与官方 API 相当")
bullet_lines(s, Inches(0.6), Inches(1.75), Inches(7.3), [
    ("五件套量化方案：", "混合精度划分、自适应缩放搜索、离群抑制、块级裁剪、误差补偿（§4.5）"),
    ("权重 INT8 + 激活逐 token INT8：", "矩阵乘内核用满昇腾整数算力单元"),
    ("验证：", "16 项基准（MMLU 90.82 vs 官方 91.05 等）整体持平（Table 5）"),
    ("算子层面：", "MLA 利用率 65.4%（FlashMLA@H800 66.7%）；INT8 GEMM 计算利用率 77.4%~82.7%"),
], size=14, gap=11)
# right rail: quant pipeline mini-diagram (text form)
rect(s, Inches(8.35), Inches(1.75), Inches(4.35), Inches(4.6), fill=BAND)
txt(s, Inches(8.6), Inches(1.98), Inches(3.9), Inches(0.35), "INT8 五步流水", size=13, bold=True, color=GREY)
steps = ["① 按敏感度划分精度（BF16/FP32 保留关键层）", "② 离线搜索最优缩放因子（Eq.3）", "③ 长尾离群抑制与结构变换", "④ 块级裁剪范围求解（Eq.4）", "⑤ 图中插入轻量误差补偿项"]
tb = txt(s, Inches(8.6), Inches(2.45), Inches(3.9), Inches(3.7),
         [(st, dict(size=12.5, sa=10)) for st in steps], line_spacing=1.2)
source(s, "Source: Table 5, 7-9 & §4.5, arXiv:2506.12708v3")
notes(s, "量化这页给两个信息：一是方案成体系，五个组件都在正文有公式与推导；二是验证充分，16 项基准跟官方 API 对齐，MMLU 只差 0.23 个点。算子利用率数据说明 INT8 内核确实吃满了昇腾的整数算力。")

# ============================== S12 takeaway ==============================
s = add_slide()
title(s, "超节点：用互连带宽换来的“单一节点抽象”")
bullet_lines(s, Inches(0.6), Inches(1.8), Inches(12.1), [
    ("硬件前提：", "全对等 UB 平面让池化、统一访问、独立扩展成为可能——互连即资源（§3）"),
    ("软件兑现：", "PDC 分离 + EP320 + 融合算子/微批次/INT8，把互连红利转成 4.45/1.29 的效率（§4）"),
    ("诚实边界：", "EPLB 未达理想、大 EP 度 Dispatch 带宽退化、VPC/RDMA 平面尚未统一（§5.4/§6）"),
], size=15, gap=13)
rect(s, Inches(0.6), Inches(4.35), Inches(12.15), Inches(1.9), fill=BAND)
txt(s, Inches(0.88), Inches(4.6), Inches(11.6), Inches(1.5),
    [("对本课题的参照价值", dict(size=12.5, color=GREY, sa=8)),
     ("CloudMatrix384 是“多节点设备管理统一性”路线的生产级样本：UB 的统一内存语义让 768 个芯粒在软件视角下可当作单一节点调度；",
      dict(size=14, color=INK, sa=6)),
     ("后续可对照其 6.1-6.2 节演进方向（更大规模、CPU 池化、组件级分离）审视统一性边界的推进节奏。",
      dict(size=14, color=INK))],
    line_spacing=1.3)
source(s, "arXiv:2506.12708v3 · 组会文献汇报 · 2026-10", y=Inches(6.85))
notes(s, "收尾三句话：互连是这类系统的第一性资源；软件栈的职责是把互连红利兑换成推理效率；论文自己承认的三个缺口值得跟踪。最后落到我们课题：这篇是统一性路线目前最完整的公开工程参照，六.一/六.二节的演进路线图与我们关注的问题直接相关。")

prs.save(OUT)
print(f"saved {OUT}: {len(prs.slides.__iter__.__self__._sldIdLst)} slides" if False else f"saved {OUT}")
import subprocess
