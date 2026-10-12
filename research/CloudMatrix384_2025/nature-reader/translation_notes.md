# 翻译与提取说明（translation_notes）

> **⚠️ 2026-10-12 重建说明**：初版提取存在"翻页悬空丢段"bug（页首行被误判为前页段落的延续、
> 且此前无已开段落时整段被静默丢弃），导致初版 paper.md 丢失部分正文段落（如 §2 开篇段、
> 若干小节首段；当时"4.9% 字符差=图内文字"的收支解释部分掩盖了该问题）。已修复提取器
> （tools/nature-reader 经验第 13 条）并重建：正文块 273 段、行级覆盖检测零真实丢失、
> 翻译由旧译（309 块）+ 补译（50 块）+ 接缝修剪合并而成。**注意**：重建后 S 块 ID 体系
> 与初版不同——paper-card / paper2ppt / paper-xray 中引用的旧 S-id 对应旧编号，存档于
> `build_legacy/`；其 PDF 页码/图表编号引用不受影响（数值均直接取自图表，经核验无误）。
> 中文全文 PDF（../nature-paper-trans/）已基于重建版重新生成（52 页）。

Reader 对象：*Serving Large Language Models on Huawei CloudMatrix384*（arXiv:2506.12708v3，58 页，CC BY 4.0）。
生成日期：2026-10-10。流程：字体/缩进感知的结构化提取（`tools/nature-reader/`，经验见其 `nature-reader-experiences.md`）→ 分块人工级翻译 → 装配校验。

## 术语与翻译约定

- 全文术语表锁定于 `paper.md` 顶部"术语表"一节及 `source_map.json` 的 `glossary`，同一术语全文只用一种译法。
- 系统名（CloudMatrix / CloudMatrix384 / CloudMatrix-Infer / FusedDispatch / FusedCombine / UBuffer / CANN / HCCL）不译；昇腾/鲲鹏首次出现括注英文。
- 数学内容不译：变量、单位、公式原样；中文说明仅解释 surrounding prose。
- 引用编号 `[56]`、章节引用 `§4.2.1`、图表引用 `Fig. 10` / `Table 2` 保持英文形式（便于回查 PDF）。

## 提取范围与结构性说明

1. **p.2–3 为 arXiv 自动生成的目录页，未纳入 reader**（与正文内容重复）。
2. **References（p.54–58，68 条）保留英文原文不译**，见 `paper.md` 末尾 References 一节；逐条以 `[n]` 分行，可按编号回溯。
3. **图表内部文字**（柱状图图例、坐标轴刻度、架构图内小标签）未进入正文文本流，完整保留在 `assets/figNN.png` / `assets/tableNN.png` 裁图中。经逐页字符收支核对，此类内容约占正文页字符的 4.9%，全部属于图表内部，无正文段落丢失。
4. **公式**共 4 个（E001–E004）。E001/E002 为代码风格变量等式（high confidence）；E003/E004 由可选中文本重建并对照原 PDF 裁片视觉核验（medium confidence），裁片存于 `assets/equations/eq01.png`–`eq04.png`。
5. p.38 S195 段末尾的 `$XWXQWα$` 序列为 PDF 数学斜体提取伪影（对应 Eq. (4) 前的行内符号 X、W、Q(W;α)），公式本体已在 E004 正确转写；不影响语义。
6. p.21 S169 与 p.25 S219 两处段落在 PDF 换行处被切分为两个连续 S 块（句子跨块延续），文字完整无缺失，阅读时按顺序连读即可。
7. 章节标题在原文中有 7 处以行内形式嵌在段落中（版式提取噪声），已全部拆分为独立标题块（S500/S502/S510–S514），编号与原文一致。
8. §6 导语一段被 Table 9 区域截断的尾部（"needs of emerging workloads…"）已找回并入 S503；§7 结论第三段跨页尾部（"frameworks like SGLang…"）已找回并入 S272，"Looking forward…" 段恢复为 S505。

## 置信度

- 正文段落 / 标题 / 图注：high（可选中文本层直接提取，字体级结构校验）。
- 公式：E001/E002 high，E003/E004 medium（视觉核验后转写）。
- 图表裁图：34/34 经视觉模型逐一核验完整性（无截断、无正文混入）；图注与图形按 skill 规范分离，图注以中英卡片形式随图。

## 锚点体系

- `Sxxx` 正文段落/标题（p.N + 块 ID 定位）；`Cxxx` 图注；`Exxx` 公式；`Fxxx`/`Txxx` 图/表卡片。
- `source_map.json` 含全部块的 page / type / order / original_text / translation / confidence，以及 figures、equations、glossary 索引，可与 `paper.md` 的 `<a id>` 锚点互查。

## 已知局限

- 影响因子、CCF 分级等 venue 元数据不在本 reader 范围（论文为 arXiv 预印本）。
- 图表内部文字不提供中文翻译（保留原图，阅读图内英文标签即可）。
- 参考文献[1]为数据集引用（数学奥赛题集），非论文，按原文保留。
