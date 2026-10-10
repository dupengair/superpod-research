# pdf-reader-tools — PDF 论文 → 中英对照 Reader 的结构化提取流水线

配合 `nature-reader` skill 使用的确定性提取层：把可选中文 PDF 论文解析成
带稳定锚点的结构块（段落 S / 图注 C / 公式 E）并裁出全部图表资产，
供后续人工/Agent 翻译与 paper.md 装配。2026-10 在 CloudMatrix384 论文
（58 页 arXiv tex2pdf）上调试通过：312 块 / 34 图注 / 24 图 + 10 表 / 4 公式，
全部裁图经视觉模型逐一核验。

## 用法

```bash
python3 pdf_structure_extract.py <paper.pdf> <out_dir>
# 产物：blocks_raw.json（源图数据）、crops.json、assets/figNN|tableNN.png、dbg_lines.pkl

python3 crop_equations.py       # 公式行定位裁剪（需在脚本内指定 PDF/页码/模式）
python3 montage_check.py        # 拼接 assets/ 为 contact sheet，供视觉模型批量核验
```

依赖：`pdfplumber`（文字层+图元 bbox）、`pypdfium2`（渲染）。无可用的
`pdftotext/pymupdf` 时的替代组合。

## 调参经验（踩坑记录，换模板前必读）

1. **用 word 级提取而非 char 级拼串**：LaTeX PDF 常无空格字符，
   char 拼接会丢所有空格。`extract_words(extra_attrs=["fontname","size"])`
   同时拿到字体属性做行分类。
2. **行分组**：word 按 `round(mid/5.2)` 分桶后仍需合并被拆开的同视觉行。
   合并判据用**垂直重叠**（`next.top < cur.bot - 2`），不要用 x 不相交——
   粗体 run-in 引导句的词与后续常规词 x 区间互相嵌套但属同一行。
   合并时给子桶打 `_lseq` 序号，重排按 `(lseq, x0)`，否则两行词按 x 混排打乱语序。
3. **公式行保护**：数学行因上下标纵向偏高，会与邻行垂直重叠而误合并；
   合并前检查双方文本是否 `结尾 (N) 且含 =/min/||`，是则禁止合并。
4. **旋转水印**：arXiv 左侧竖排水印用 `upright=False` 识别，但**数学斜体字
   也常被判非 upright**，过滤条件应为 `not upright AND x0 < 30`（仅页边）。
5. **多行图注**：首行含粗体 "Table N." 前缀导致字体集合不同、续行（斜体/
   等宽/符号字体混排）被误判为正文。识别规则：以 `^(Fig\.|Table)\d+` 开头 +
   主体字体为 caption 字族；符号字体（txsys/txmiaX/MathMI）要放行。
6. **段落切分按缩进带**，不能一刀切 `x0 >= 50`：本模板正文续行 45.8、
   段首缩进 55.8、列表项起始 60.4、列表悬挂续行 76.0。规则：
   `54–62.5 → 新段；>= 50.5 → 续行（悬挂）；垂直间距 > 16.5 → 新段`。
7. **图表区域**：图=页顶浮动（裁 `[页顶, 图注上边界]`），表=图注下方
   （`[图注下边界, 聚类底]`）。表格聚类要在**图元+文字行**上做（纯图元会
   在表格文字行处断开），并以**下一个图注/标题的 top 为硬停止边界**，
   否则容差会把后文正文吞进来。图注文字本身不进裁剪（caption 单独成块）。
8. **渲染裁剪**：`pypdfium2` 的 `render(crop=...)` 坐标语义易错（底原点），
   稳妥做法：整页 `render(scale)` 后用 PIL 按像素 `crop`。
9. **视觉核验闭环**：裁 30+ 张图后，拼 contact sheet（montage_check.py），
   用视觉模型批量判"完整性/是否混入正文"。本环境 Read 图片只返回 CDN URL，
   需将 URL 喂给 `analyze_image` 类工具完成核验。
10. **文本清洗**：`tidy()` 统一处理——标点前空格、行尾连字符
    `([A-Za-z])- ([a-z])`、`(cid:66)`→✉、Unicode 数学斜体
    （U+1D400 区）NFKC 归一后包 `$...$`。

## 与 nature-reader skill 的关系

skill 负责 reader 的规范与交付物（paper.md / source_map.json /
translation_notes.md）；本工具只做其中"确定性提取"这一段，
翻译与装配仍由 Agent 按 skill 工作流完成。
