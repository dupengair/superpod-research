# superpod-research

AI 基础设施**超节点（Supernode / SuperPod）**方向的论文调研仓库：围绕超节点硬件体系架构与多节点设备管理统一性，系统检索、筛选并归纳前沿论文，产出可回溯、可复现的中文调研报告。

## 研究课题

**核心研究问题**：如何通过超节点实现对多节点设备管理的统一性——在软件视角下，将多个节点上的设备看作单一节点进行资源管理和通信，例如通过灵衢总线（UnifiedBus / UB）的统一内存语义与高带宽通信。

**优先级规则**：凡涉及灵衢总线（UB）或华为超节点体系（CloudMatrix、昇腾 SuperPOD 等）的论文，一律最高优先级摘录，置于报告首组。

课题关键词矩阵（检索式构造起点）：

| 概念维度 | 代表检索词 |
|---------|-----------|
| 超节点本体 | supernode, superpod, scale-up domain, rack-scale |
| 灵衢/华为体系（最高优先级） | UnifiedBus, CloudMatrix, Ascend SuperPOD, unified memory semantics |
| 设备管理统一性 | unified device abstraction, resource disaggregation, composable infrastructure |
| 互联互通 | scale-up fabric, CXL, collective communication, interconnect topology |
| 软硬协同 | communication library, parallelism strategy, distributed runtime |

## 目录结构

```
.
├── CLAUDE.md                          # 项目规范入口（@import 引入检索工作流）
├── research/                          # 调研工作目录
│   ├── CLAUDE.md                      # 检索工作流定义（课题背景、平台边界、报告模板）
│   ├── 超节点硬件系统结构论文调研_2024以来Top20.md
│   ├── 超节点多节点设备管理统一性论文调研_2022以来Top19.md
│   └── tmp/
│       ├── download/                  # 开放获取论文 PDF（19 篇）
│       └── superpod_search/           # 检索脚本与中间数据（arXiv/OpenAlex）
└── tools/skills/                      # 检索工具链（git 子模块）
    ├── academic-search/               # 学术检索 Skill（arXiv/S2/OpenAlex/CNKI 等平台）
    └── research-superpower/           # 研究工作流插件（文献筛选、引用追溯等子技能）
```

## 已有调研报告

| 报告 | 时间范围 | 核心论文 | 检索平台 |
|------|---------|---------|---------|
| [超节点硬件系统结构论文调研](research/超节点硬件系统结构论文调研_2024以来Top20.md) | 2024-01 至今 | Top 20 | arXiv API + OpenAlex |
| [超节点多节点设备管理统一性论文调研](research/超节点多节点设备管理统一性论文调研_2022以来Top19.md) | 2022-01 至今 | Top 19 | OpenAlex API（arXiv 源过滤） |

报告均按主题分组（灵衢/华为超节点体系固定为首组），每篇核心论文附中文简介与课题相关性分析，文末含检索方法说明与局限声明。

## 检索方法与工具链

- **平台分层**：arXiv / Semantic Scholar / OpenAlex（REST API）为主；Google Scholar / CNKI 知网经 CDP 直连浏览器（中英文并重策略下知网为必查平台）；ACM DL / IEEE 尽力而为；Scopus / Web of Science 不在覆盖范围。
- **工具**：[academic-search skill](tools/skills/academic-search/README.md) 负责检索、元数据提取、引用数与 OA PDF 判定；相关性分析、主题归纳与引用规范化（GB/T 7714）由 Agent 基于检索元数据完成。
- **引用可回溯**：所有参考文献来自检索实际返回的元数据（arXiv ID / DOI / CNKI 链接），禁止凭记忆生成。
- **PDF 获取**：仅下载合法开放获取（OA）论文。

## 使用说明

```bash
git clone --recurse-submodules git@github.com:dupengair/superpod-research.git
```

调研工作流详见 [CLAUDE.md](CLAUDE.md)（经 `@import` 引入 [research/CLAUDE.md](research/CLAUDE.md) 的完整定义）：课题解析 → 检索式构造 → 轻量摘要表 → 深拉元数据 → 分析撰写 → 引用规范化，以及两个用户确认点与降级规则（CDP 不可用、Semantic Scholar 限流等）。

`research/tmp/` 为检索过程的中间产物（论文 PDF、脚本、JSON 数据），随仓库保留以便回溯。
