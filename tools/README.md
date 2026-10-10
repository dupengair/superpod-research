# tools/ — skill/command 工具与经验资产

本目录按 skill/command 名管理各技能在本项目使用过程中沉淀的工具脚本与经验文档。
**每次运行某个 skill/command 之前，先查看 `tools/<skill名>/<skill名>-experiences.md` 是否有相关经验与工具。**

## 目录结构

```
tools/
├── README.md                       # 本文件：管理规范
├── <skill名>/                      # 每个 skill 一个目录（单层）
│   ├── README.md                   # skill 官方 README（直接从 skill 目录拷贝，便于随上游更新覆盖）
│   ├── <skill名>-experiences.md    # 经验沉淀：工具脚本清单 + 使用过程踩坑记录
│   └── *.py / *.sh                 # 该 skill 的通用工具脚本
```

> `nature-skills/` 目录同理：其 README.md 即 nature-skills 全库 21 个 skill 的官方总览。

现有资产：

| 目录 | README.md | 经验文件 |
|---|---|---|
| `nature-reader/` | skill 官方说明 | `nature-reader-experiences.md`（提取流水线 4 脚本 + 11 条调参经验，含 generate_reader.py 装配器） |
| `nature-skills/` | 全库 21 个 skill 官方总览 | 不适用（参考件） |
| `academic-search/` | skill 官方说明 | 尚未沉淀 |
| `nature-paper2ppt/` | skill 官方说明 | `nature-paper2ppt-experiences.md`（9 条经验：EMU/英寸混算、布局预算、复用链等） |
| `nature-paper-card/` | skill 官方说明（单篇论文结构化精读卡片） | 尚未沉淀 |
| `nature-paper-trans/` | skill 官方说明（整篇/指定页中文翻译为图片型 PDF） | 尚未沉淀 |
| `nature-paper-xray/` | skill 官方说明（论文透视精读，组会/读书会用） | 尚未沉淀 |
| `research-superpower/` | 研究工作流插件官方说明 | 尚未沉淀 |

## 管理规则（对所有会话生效）

1. **先查后用**：运行任一 skill/command 前，先读 `tools/<skill名>/<skill名>-experiences.md`；没有该文件则表示尚无沉淀，运行后按规则 3 创建。处理**论文**时还须先查 `research/log.md`（论文操作日志），确保在同一论文目录、同一 skill 子目录内操作。
2. **工具落位**：某次 skill/command 运行中产生的**通用性**工具脚本（可复用于未来论文/任务）存入 `tools/<skill名>/`；一次性、任务特定的中间产物留在 `research/<论文目录>/<skill名>/build/` 或 `research/tmp/`，不得混入 tools。
3. **经验登记**：每次 skill/command 运行结束（或产生新脚本/新结论）时更新对应 `<skill名>-experiences.md`：新脚本加进清单表，新经验追加条目（先查重，避免重复记录）。
4. **不硬编码项目路径**：tools/ 下的脚本一律通过 argv/环境变量接收路径，保证跨论文复用。
5. **命名**：目录名与 skill/command 名完全一致（注意拼写，如 `academic-search` 不是 `acedemic-search`）；目录内 `README.md` 固定为 skill 官方说明，经验文件固定为 `<skill名>-experiences.md`，不得另起名（如 OFFICIAL.md、NOTES.md）。
