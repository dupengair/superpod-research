# nature-paper-trans 经验沉淀（tools/nature-paper-trans/nature-paper-trans-experiences.md）

运行 nature-paper-trans skill/command 前先读本文件。skill 官方说明见 [README.md](README.md)。

## 脚本清单

| 脚本 | 作用 |
|---|---|
| （暂无本地沉淀脚本；skill 自带 `scripts/pages.py`：prepare/status/reserve/record/fail/assemble，禁止替代实现） |

## 经验条目

1. **硬依赖：宿主内置 `image_gen` 工具**（2026-10-10 首次运行发现）。本 skill 的核心
   机制是每页一次 `image_gen` 生图（每页仅 1 次机会、最多 10 并发、无自动重试），
   Python 脚本只负责渲染/记账/拼装。**当前 Claude Code 环境没有 image_gen 工具**
   （analyze_image 只能读图），58 页全文翻译任务在准备阶段即被阻塞。
   - 运行前置检查：确认宿主已接入生图工具（如 Z.ai/Gemini 图像生成 MCP）后再执行；
   - PyMuPDF/Pillow 均已装好（pymupdf 装于 paper-card 阶段），pages.py 可正常运行；
   - 任务目录支持续跑（task.json 账本 + reserve/record 状态机），接入 image_gen 后
     从头执行即可，无需特殊处理。
2. **交付契约**：最终回复只给中文 PDF 一个交付物（无检查 Markdown/预览图）；缺页需
   `--allow-partial` 且标注 partial；这些约束在环境具备 image_gen 后仍要遵守。
3. **与 nature-reader 的分工**：本 skill 产出"版式保留的图片型中文 PDF"；仓库已有的
   nature-reader 双语 reader 是文本型对照阅读材料，二者不可互替。若用户只要中文内容
   而不要版式，从 reader 产物另出文本型 PDF 属于 skill 之外的替代方案，须用户明示。
4. **替代方案已落地（2026-10-10，用户明示选择）**：环境无 image_gen 时，经用户确认改出
   **文本排版中文 PDF**——`<论文目录>/nature-paper-trans/build_cn_pdf.py` 解析
   nature-reader/paper.md（中文块 + 图表卡 + 公式 + 术语表），weasyprint 排 A4
   （`pip install weasyprint`，本机 pango/cairo 可用；中文字体用 WenQuanYi Micro Hei）。
   产物 45 页/图 24+表 10 全嵌入/参考文献保留英文；QA 用 pypdf 抽取文本做随机段落
   抽查（注意：pypdf 抽取会加空格、`**` 已被 clean 剥离，探针要先归一化否则假阴性）。
   公式以 Unicode 文本呈现（𝓛 等字符字体缺字风险，用 <i>L</i>+sub/sup 更稳）。
   此方案须在 PDF 首页"译本说明"中显式声明为替代产物，不得冒充 skill 定义的原版式产物。

## 维护约定

- 新脚本入本目录后必须在上方"脚本清单"登记一行。
- 踩到新坑：先查本文件是否已有结论，解决后追加条目。
