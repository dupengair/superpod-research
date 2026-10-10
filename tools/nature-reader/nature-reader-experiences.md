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

## 维护约定

- 新脚本入本目录后必须在上方"脚本清单"登记一行。
- 踩到新坑：先查本文件是否已有结论，解决后追加条目。
