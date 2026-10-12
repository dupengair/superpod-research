# 翻译与提取说明（translation_notes）

Reader 对象：*UBEP: Re-architecting Expert Parallelism Communication Library for Production Superpods*（arXiv:2607.06202，SIGCOMM '26，18 页）。
生成日期：2026-10-12。流程：`pdf_structure_extract.py --profile sigconf`（ACM 双栏模板，本次新增的 profile）→ 分块翻译（A/B/C/D 四块并行）→ 装配校验。

## 重要前置说明：源 PDF 曾经损坏

original_papers 中的源文件原为**截断损坏**（1.18MB 无 EOF，三个 PDF 库均无法打开，属 2026-08-31 批量下载残留）。已按 INDEX.md 的 arXiv ID 从官方重新下载（1.41MB，18 页完整）后处理，文件名保持不变。同批另有 5 篇损坏 PDF 一并修复（见 `tools/academic-search/academic-search-experiences.md`）。

## 术语与翻译约定

- 术语表锁定于 `paper.md` 顶部与 `source_map.json.glossary`。核心译法：dispatch/combine→分发/合并、kernel decomposition→核分解、hierarchical token-level scheduling→分层 token 级调度、Data-as-Flag→数据即标志、UGAS→统一全局地址空间。
- 专名不译：UBEP、CM384、AIC/AIV、UBuf、SyncAll、CalCumsum、CANN、DeepSeek/LLaMA/Mixtral、NVLink/IB/RoCE。
- Algorithm 1 伪代码关键字（while/do/if/then/break/return）保留英文；附录 A/B 的证明正文正常翻译。

## 双栏提取的结构性说明

1. **阅读序**：按"页 → 左栏 → 右栏"重排（物理 y 序在双栏下会交错）。已验证 §4（左栏底）先于 §5（右栏顶）等跨栏章节顺序正确。
2. **行合并分栏先行**：同 y 的左右栏行不再合并成一个错乱行（修复前 "5 EVALUATION" 与左栏正文粘连即此因）。
3. **粗体引导词错位**：双栏窄栏宽导致 `**xxx.**` 引导词在提取中偶有断行错位（如 "Schedul-**ing**"），译文已按语义归位；原文块保留提取原貌以便溯源。
4. **图注**：19 条（图 1–14 + 表 1–5）全部识别。Figure 13 图注首的数学前缀 𝑘（与图轴标签合并所致）已清除。
5. **公式**：本文公式 (1)/(1a)-(1c) 与附录式 (2)–(14) 的 PDF 数学层提取为 `(cid:XXX)` 乱码（LaTeX 字体无 Unicode 映射），译文按语义重建为行内数学 `$...$`（medium confidence，未逐字符核对原式）；正文非数学部分不受影响。
6. **附录**：p.16-18 含 Appendix A（讨论）与 B（NP-hard 证明）及 Figure 13/14，均收录。
7. **参考文献**：44 条保留英文不译；尾部混入的残段已清理。

## 置信度

- 正文段落/标题/图注：high（栏内行覆盖检测 729/771≈94.7%，缺失行几乎全为公式 cid 数学行的检测噪声）。
- 数学重建：medium（cid 乱码按语义复原，建议对照原 PDF 核对公式细节）。
- 图表裁剪：18 张经目检（图完整、少量表脚注随表裁入，可接受）。

## 锚点体系

`Sxxx` 正文段落/标题、`Cxxx` 图注（19 条）、`Fxxx`/`Txxx` 图/表卡片；无 `Exxx`（公式未做独立锚块，见上）。Figure 13/14 卡片置于 References 之前（正文未显式提及，无首提锚点）。

## 已知局限

- 双栏窄行距下的个别断词（如 "Schedul-ing"）在原文块中保留连字符原貌；译文已拼接。
- 附录公式的 LaTeX 重建未经渲染核验（源层无可用文本）。
