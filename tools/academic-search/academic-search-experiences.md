# academic-search 经验沉淀（tools/academic-search/academic-search-experiences.md）

运行 academic-search skill/command 前先读本文件。skill 官方说明见 [README.md](README.md)。

## 经验条目

1. **下载完整性必须入库前校验**（2026-10-12 发现）。首批检索下载的 19 篇 OA PDF 中
   **6 篇截断损坏**（31%），全部是 2026-08-31 同一批下载的残留——pypdf 报
   `PdfStreamError / EOF marker not found`，文件尾无 `%%EOF`，三个库
   （pypdf/pdfplumber/pypdfium2）全部打不开。文件名/大小正常，肉眼不可辨。
   - 校验方法：`PdfReader(f).pages` 能打开 + 文件尾 2KB 内含 `%%EOF` 两条同时满足；
   - 修复：按 `original_papers/INDEX.md` 的 arXiv ID 从 `https://arxiv.org/pdf/<id>`
     重新下载（文件名保持不变），重下后全部正常且体积普遍变大（如 T-Rex 1.6MB→11.8MB）；
   - 教训：**批量下载的入库流程应把"打开校验"作为登记 INDEX.md 的前置步骤**，
     损坏文件应当时即重下，而不是等下游 skill 使用时才暴露。
2. **沙箱下的 heredoc 陷阱**：在 Claude Code 沙箱里，`python3 - <<EOF` 式脚本的
   `glob.glob`/`os.listdir` 可能静默返回空（不报错）——批量校验脚本要用 shell
   `ls > 列表文件` 枚举后传给 python，或改用 `python3 -c` 内联。

## 维护约定

- 新脚本入本目录后必须在上方"脚本清单"登记一行（当前无本地脚本）。
- 踩到新坑：先查本文件是否已有结论，解决后追加条目。
