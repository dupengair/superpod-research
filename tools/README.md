# tools/ — skill/command 工具与经验资产

本目录按 skill/command 名管理各技能在本项目使用过程中沉淀的工具脚本与经验文档。
**每次运行某个 skill/command 之前，先查看 `tools/<skill名>/README.md` 是否有相关经验与工具。**

## 目录结构

```
tools/
├── README.md                  # 本文件：管理规范
├── nature-skills-overview.md  # nature-skills 全库 21 个 skill 的官方总览（参考件）
├── <skill名>/                 # 每个 skill 一个目录（单层）
│   ├── README.md              # ① 工具脚本清单 ② 使用过程沉淀的经验/踩坑记录
│   │                          #    （可含官方说明摘录，实践结论优先）
│   ├── OFFICIAL.md            # （可选）官方 README 拷贝/摘录
│   └── *.py / *.sh            # 该 skill 的通用工具脚本
```

现有资产：

| 目录 | 说明 |
|---|---|
| `nature-reader/` | PDF→中英对照 reader 的结构化提取流水线（4 脚本 + 11 条调参经验），含 generate_reader.py 装配器 |
| `academic-search/` | 检索 skill 官方说明（实践经验待沉淀） |
| `research-superpower/` | 文献综述工具包官方说明（实践经验待沉淀） |

## 管理规则（对所有会话生效）

1. **先查后用**：运行任一 skill/command 前，先读 `tools/<skill名>/README.md`；没有该目录则表示尚无沉淀，运行后按规则 3 创建。
2. **工具落位**：某次 skill/command 运行中产生的**通用性**工具脚本（可复用于未来论文/任务）存入 `tools/<skill名>/`；一次性、任务特定的中间产物留在 `research/<论文目录>/<skill名>/build/` 或 `research/tmp/`，不得混入 tools。
3. **经验登记**：每次 skill/command 运行结束（或产生新脚本/新结论）时更新对应 README.md：新脚本加进清单表，新经验追加条目（先查重，避免重复记录）。
4. **不硬编码项目路径**：tools/ 下的脚本一律通过 argv/环境变量接收路径，保证跨论文复用。
5. **命名**：目录名与 skill/command 名完全一致（注意拼写，如 `academic-search` 不是 `acedemic-search`）。
