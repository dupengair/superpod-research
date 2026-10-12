# 翻译与提取说明（translation_notes）

Reader 对象：*HyperOffload: Graph-Driven Hierarchical Memory Management for Large Language Models on SuperNode Architectures*（arXiv:2602.00748，17 页，预印本）。
生成日期：2026-10-11。流程：`pdf_structure_extract.py --profile times`（US Letter/NimbusRomNo9L 模板，本次新增的 profile）→ 分块翻译（A/B/C/D 四块并行 + Z 修正）→ 装配校验。

## 术语与翻译约定

- 术语表锁定于 `paper.md` 顶部与 `source_map.json.glossary`；核心译法：offloading→卸载、operatorization→算子化、prefetch→预取、cache operator→缓存算子、execution-order optimization→执行序优化、SuperNode→超节点。
- 系统名（HyperOffload/MindIR/MindSpore/CANN）、模型名（LLaMA-8B/DeepSeek-V3）、算法名（NSA/ZeRO/H2O 等）不译；昇腾（Ascend）首次标注。
- 数学/伪代码不译：Algorithm 1 的 Require/Ensure/for/end for 结构保留英文关键词，注释性说明译中文。
- 引用 `[N]`、`§N`、`Figure N`/`Table N` 保持英文形式。

## 提取范围与结构性说明

1. **无编号显示公式**：本文无 Eq.(N) 编号公式，数学内容为行内符号与 Algorithm 1 伪代码（S038 块，关键字+符号原样保留）；reader 无 E 块与公式索引，符合实际。
2. **代码/算法块**：p.8-9 的 Algorithm 伪代码与 Python 示例代码中，非等宽字体的伪代码行进入正文块（S038），Calibri/DengXian 字体的代码展示区归入图区（Figure 5 裁图含三种使用方式代码）。
3. **图表**：6 图 + 6 表裁图全部经视觉模型与文本层双重核验（表格为小体量表，2-5 数据行，边界正确）。数值 1.73×、−13.78% 等仅存在于 Table 3/4 图内，正文未引用，故 paper.md 正文无这些数字（非遗漏）。
4. **References**：39 条保留英文不译；原文 [35] 条目作者名 "Sang-hai" 存在跨行断字，列表渲染处有轻微粘连（源 PDF 原样）。
5. **论文原文笔误**：§4.1 首段 "Figure xxx"（S034）为原文笔误，照译保留。
6. **§8 尾段（S080）**：初版提取时被 refs 页级判定误吞，修复为 top 级判定后恢复为正文块，由主线直接补译（chunk_Z_fixes.zh）。
7. front matter：p.1 的标题/作者/单位/摘要/脚注（贡献声明+通信作者）均成块；脚注块以引用格式（`>`）渲染、无独立锚点，属装配器既定设计。

## 置信度

- 正文段落/标题/图注：high（可选中文本层提取，行覆盖检测 hyphen-aware 零丢失）。
- 图表裁剪：12/12 双重核验（视觉模型 + 表区文本边界）。
- Algorithm 1 伪代码块：medium（多行结构压平为单块，语义按原文顺序完整保留）。

## 锚点体系

- `Sxxx` 正文段落/标题；`Cxxx` 图注（12 条）；`Fxxx`/`Txxx` 图/表卡片；无 `Exxx`。
- `source_map.json` 与 `paper.md` 的 `<a id>` 互查；heading 块不进 source_map（装配器既定行为，同 CloudMatrix384 reader）。

## 已知局限

- 表格数据不提供中文转写（保留裁图原文）；图内英文标签不译。
- 逐字审校未做（分块翻译 + 主线抽校 + 数值保留自检）；建议阅读时对关键数字对照表格裁图。
