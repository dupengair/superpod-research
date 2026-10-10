# nature-paper2ppt 经验沉淀（tools/nature-paper2ppt/nature-paper2ppt-experiences.md）

运行 nature-paper2ppt skill/command 前先读本文件。skill 官方说明见 [README.md](README.md)。
首次实战：2026-10-10 CloudMatrix384 论文 12 页组会 PPT
（`research/CloudMatrix384_2025/nature-paper2ppt/`）。

## 脚本清单

| 脚本 | 作用 |
|---|---|
| （暂无本地沉淀脚本；生成脚本随论文目录走：`<论文目录>/nature-paper2ppt/build_pptx.py`，可作下篇论文的起手模板） |

## 经验条目

1. **复用链是最大加速器**：若论文已有 nature-reader 产物，**跳过全部图表提取步骤**——
   `../nature-reader/assets/figNN.png` 已是视觉核验过的裁片，直接复制到
   `output/assets/figures/` 并在 asset_manifest.md 登记"复用"即可；双语对照 paper.md
   里的数值（含 Table 数据）可直接 grep 取用，术语沿用其翻译。
2. **先查 log.md 定目录**：按项目规范，操作目录 = `research/<关键词>_<年>/nature-paper2ppt/`，
   完成后登记 `research/log.md`。
3. **python-pptx 单位陷阱（本次 high 级缺陷）**：`Inches(4.35 + h + Inches(0.08))` 这类
   表达式会把 EMU（int）与英寸 float 直接相加，产生 2.6e12 EMU 级的巨大坐标，文本框飞出
   页面。规则：**坐标运算先统一成英寸 float，最后只做一次 Inches()**；不要对 Emu 对象
   做算术后再传入 Inches()。
4. **宽高比驱动的布局预算**：全宽图（12.1in）高 = 12.1/ratio；ratio<2.4 的图全宽会吃掉
   >5in 高度，正文就没地方放（本次 Fig.2 3.32 比例全宽越界，缩到 10.4in 居中解决）。
   写代码前先按 ratio 算一遍页面预算（标题区 1.5in + 图 + 正文 + source 条 ≤ 7.5in）。
5. **audit 脚本闭环**：`audit_pptx_quality.py --report output/pptx_audit.md`，high 是
   blocker；修完重跑直到 high=0。near-miss 对齐的 low 提示多为设计性偏移（如 metric 组内
   数字与标签错位排布），评估后在 qa_report 记录即可，不必强清零。
6. **无渲染器环境的自审替代**：本机无 LibreOffice 时按 skill 政策降级——audit 脚本 +
   重开 PPTX 的对象级检查（页数/媒体数/备注数/越界 shape 数）+ 数值溯源抽查，并在
   qa_report 中明确"rendered preview unavailable"。
7. **内容自审比版式自审更重要**：本次抓到一个 high 级事实错误——备注里凭印象写了
   "16 个机柜"，论文实际无此说法（16 是每个子平面的 L2 交换芯片数）。凡写入备注/正文
   的数字，逐个回 paper.md grep 核对；拿不准的规模性描述直接删。
8. **pip 环境缺 python-pptx**：`pip install python-pptx`（1.0.2）即可，无需 venv。
9. **结构模板（methods 弧线 12 页）**：标题(带 3 个 headline 数字条) → 背景压力(四约束
   chip 条) → 问题定位(claim 引用栏+愿景图) → 架构总览(全宽图) → 互连(图+3 metric
   chips) → 核心设计×3(图 65%+右窄栏) → 无图对比页(原生数字卡) → 性能对比(原生表格+
   metric 条) → 精度/消融 → 总结(含对本课题启示)。构图节奏：cover/claim/figure/
   process/原生表格交替，避免连续同构。

## 维护约定

- 新脚本入本目录后必须在上方"脚本清单"登记一行。
- 踩到新坑：先查本文件是否已有结论，解决后追加条目。
