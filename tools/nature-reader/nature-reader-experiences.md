# nature-reader 经验沉淀（tools/nature-reader/nature-reader-experiences.md）

运行 nature-reader skill/command 前先读本文件。本目录保存该 skill 在本项目使用过程中
沉淀的确定性工具脚本与调参经验；skill 官方说明见 [README.md](README.md)（直接取自 skill 目录）。

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `pdf_structure_extract.py` | PDF → 结构块 + 图表裁剪。`python3 pdf_structure_extract.py <paper.pdf> <out_dir>`，产出 `blocks_raw.json`（S/C/E 块）、`crops.json`、`assets/figNN\|tableNN.png`、`dbg_lines.pkl` |
| `generate_reader.py` | 装配 paper.md + source_map.json。`python3 generate_reader.py <work_dir> [out_dir]`，读取 `<work_dir>/blocks_raw.json` 与 `chunk_*.zh` 翻译分块 |
| `montage_check.py` | 把 assets/ 拼成 contact sheet 供视觉模型批量核验裁图质量 |
| `crop_equations.py` | 公式行定位裁剪（需按论文指定页码/模式，作参考模板用） |

依赖：`pdfplumber`、`pypdfium2`（无可用的 pdftotext/pymupdf 时的替代组合）。

## 标准流水线（在论文目录 `<论文>/<skill名>/build/` 中操作）

1. `pdf_structure_extract.py <pdf> build/` → 结构块与图表裁剪
2. 视觉核验裁图（montage + analyze_image 类工具）
3. 按章节切分翻译分块（chunk_*.en），翻译产出 chunk_*.zh（术语表锁定，格式 `ID\t译文`）
4. `generate_reader.py build/ ..` → paper.md + source_map.json
5. `validate_reader_math.py`（skill 自带）校验

实战样例：`research/CloudMatrix384_2025/nature-reader/`（构建产物在其 `build/`）。

## 调参经验（踩坑记录，换 PDF 模板前必读）

以下针对 arXiv tex2pdf 模板（Linux Libertine/Biolinum 字体、7×10in 书版、
图顶浮动、图注在图下/表注在表上）。换模板先跑 `build_structure.py` 式探查确认字体签名。

1. **用 word 级提取而非 char 级拼串**：LaTeX PDF 常无空格字符，char 拼接丢所有空格。
   `extract_words(extra_attrs=["fontname","size"])` 同时拿字体属性做行分类。
2. **行合并判据用垂直重叠**（`next.top < cur.bot - 2`），不要用 x 不相交——粗体 run-in
   引导句与后续常规词 x 区间互相嵌套但属同一视觉行。合并时给子桶打 `_lseq` 序号，
   重排按 `(lseq, x0)`，否则两行词按 x 混排打乱语序。
3. **公式行保护**：数学行因上下标纵向偏高会与邻行垂直重叠而误合并；合并前检查双方
   文本是否 `结尾 (N) 且含 =/min/||`，是则禁止合并。
4. **旋转水印过滤**：arXiv 左侧竖排水印 `upright=False`，但数学斜体也常被判非 upright，
   过滤条件应为 `not upright AND x0 < 30`（仅页边）。
5. **多行图注续行**（斜体/等宽/符号字体混排）会被误判为正文。识别规则：`^(Fig\.|Table)\d+`
   开头 + 主体字体为 caption 字族；符号字体（txsys/txmiaX/MathMI）要放行。
6. **段落切分按缩进带**，不能一刀切 `x0 >= 50`：正文续行 45.8、段首缩进 55.8、列表项
   起始 60.4、列表悬挂续行 76.0。规则：`54–62.5 → 新段；>= 50.5 → 悬挂续行；垂直间距 > 16.5 → 新段`。
7. **图表区域**：图=页顶浮动（裁 `[页顶, 图注上边界]`），表=图注下方（`[图注下边界, 聚类底]`）。
   表格聚类要在**图元+文字行**上做（纯图元会在表格文字行处断开），并以**下一个图注/标题
   的 top 为硬停止边界**，否则容差会把后文正文吞进来。图注不进裁剪。
8. **渲染裁剪**：`pypdfium2` 的 `render(crop=...)` 坐标语义易错（底原点），稳妥做法：
   整页 `render(scale)` 后用 PIL 按像素 crop。
9. **视觉核验闭环**：裁 30+ 张图后拼 contact sheet，用视觉模型批量判完整性。
   本环境 Read 图片只返回 CDN URL，需将 URL 喂给 `analyze_image` 类工具完成核验。
10. **翻译分块工程**：`ID\t类型\t英文` → 分块并行翻译（`ID\t中文`，术语表锁定）→ 装配。
    注意：**装配脚本加载翻译必须 `sorted(glob(...))`**，否则修正覆盖文件（Z 后缀）加载
    顺序不确定被原分块覆盖；拆分段落时易产生重复 ID 块，装配前需去重；章节标题常以
    行内形式嵌在段落里（版式噪声），需扫描拆分。
11. **文本清洗** `tidy()`：标点前空格、行尾连字符 `([A-Za-z])- ([a-z])`、`(cid:66)`→✉、
    Unicode 数学斜体（U+1D400 区）NFKC 归一后包 `$...$`。

12. **times profile（arXiv article 类模板，2026-10-11 HyperOffload 实战新增）**：
    `--profile times` + `--skip-pages`/`--eq-pages` 可选参数。模板签名：US Letter（612×792）、
    正文 NimbusRomNo9L-Regu 10pt、节标题 Medi 12pt、小节 Medi 10pt（与正文同号仅粗体，
    需编号白名单防表格表头误判）、图注 "Figure N:"（**冒号**，且字体与正文相同——必须用
    冒号判据否则 "Figure 2 provides..." 正文行全部误判图注）、代码/算法块 Calibri/DengXian
    （→fig_interior）、**页码在页脚**（libertine 在页顶）。
13. **翻页悬空丢段 bug（严重，2026-10-11 发现并修复）**：页首 body 行的 prev 是前页末行时
    gap 为负 → new_para_check 判 False → 若此前无已开段落（cur_meta=None，典型：p.1 全
    front 后接正文），整页/多页累积被 flush 静默丢弃。修复：`if cur_meta is None or
    new_para_check(...)` 强制开段。**libertine 模板侥幸免疫**（页顶页码 skip 行 gap≈17>16.5
    恰好触发开段），所以 CM384 首跑未暴露——但 CM384 交付版实测仍受影响（§2 等段落丢失），
    需重建（见 research/HyperOffload 任务记录）。**教训：行覆盖检测必须用 hyphen-aware
    norm 且清理 markdown 符号，"字符收支差=图内文字"的解释要先排除丢段**。
14. **refs 起始页**：以 "References" heading 所在页为准（脚本已改为自动检测），不再硬编码
    页码；CM384 的 >=54 是其专有值。
15. **p.1 footnote 判据**：`top>590` 只适用 720pt 页高；Letter(792) 页须加字号条件
    （`size<=9`）防正文误判。
16. **行级 trace 调试**：`TRACE=<页码>` 环境变量输出该页每行的分类与段落累积事件
    （NEWPARA/ACC），定位丢行/误分块时先开 trace 再推理。
17. **回归基线更新**：CM384 修复后 360 块（paragraph 273）——旧的 312 基线本身带丢段 bug，
    修复验证以"body 行零丢失"为准而不是块数对齐。

18. **重建时的 ID 体系一致性（2026-10-12 CM384 重建实战）**：修复丢段后重提取会产生新 ID
    体系，与旧 chunk_*.zh 的 ID 不兼容。合并流程：① 新提取为基底；② 旧译按
    `norm(旧块text)[:60]` 建映射（非 ID）挂到新块；③ 旧版手工修复块（嵌段中拆出的标题）
    按前缀替换回新流并重新连续编号；④ 跨页拆分段落的接缝译文要修剪前块尾部/补本块开头，
    且 **tmap.json 修改后必须当场持久化**（本次接缝脚本改了内存 tmap 却只写了 chunk 文件，
    下一步从磁盘重载导致 S325 译文丢失，二次返工）；⑤ generate_reader 读的是
    `blocks_raw.json`——把合并后的块写回该文件名，否则 ID 错位、译文张冠李戴。

19. **sigconf profile（ACM SIGCOMM 双栏，2026-10-12 UBEP 实战新增）**：`--profile sigconf`。
    模板签名：US Letter 双栏（中线 306，左栏 x0≈53.5/右栏 317.7）、正文 LinLibertine 9pt、
    图注 LinLibertineTB 粗体 "Figure N:"、图内字 Calibri/DejaVu/Liberation、页眉在页顶
    （两种形态，统一 top<75 skip）、页码在页脚。
    - **分栏必须先行**（本 profile 的核心）：桶合并前按 word x0 分栏（键 `(col, bucket)`），
      否则同 y 的左右栏行被垂直重叠规则合并成错乱行；行级 col 赋值阈值要松（x0 < 中线+6），
      本例右栏 317.7 曾被 306+12=318 的阈值误判左栏；
    - **阅读序**：(page, col, top) 排序；new_para_check 中栏切换强制开新段；
    - 段落无垂直间隙（间隙=行距），段切分纯靠栏内缩进带（本例 1.4–9pt 偏移）；
    - 图注判据用**最大字号**（合并行内 4-6pt 图内小字会拉低 minsize）；CAP_RE 去掉 ^ 锚
      （图轴标签 𝑘 可能粘在图注行首）；数学字体（LibertineMathMI/NewTXMI）要放行；
    - **裁图/表带列感知**：obj/行按图注所在栏过滤后再聚类，x 范围限制在栏内；
    - 覆盖检测：**不能用 pdfplumber.extract_text 的整页行**（双栏同高行会被拼成一行→假阴性），
      要用提取器 dbg_lines（栏内正确分组）做行级核对；
    - tidy() 新增相邻数学段合并（`$a$$b$`→`$ab$`），否则被 validate 误判为 display math。

## 维护约定

- 新脚本入本目录后必须在上方"脚本清单"登记一行。
- 踩到新坑：先查本文件是否已有结论，解决后追加条目。
