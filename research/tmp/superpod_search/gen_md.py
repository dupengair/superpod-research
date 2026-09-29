#!/usr/bin/env python3
"""生成 arxiv_results.md：按 E1/E2/E3 分组轻量摘要表 + 检索方法说明。"""
import json, os, re, sys

OUT_DIR = "/home/dupengair/shared/work/superpod/research/tmp/superpod_search"
d = json.load(open(os.path.join(OUT_DIR, "arxiv_final.json"), encoding="utf-8"))
results = d["results"]

KNOWN = {"2506.12708": "CloudMatrix384 服务", "2508.02520": "CloudMatrix384 MaaS", "2607.20145": "SLAI T-Rex"}


def ym_from_aid(aid):
    m = re.match(r"(\d{4})\.", aid or "")
    if not m:
        return ""
    s = m.group(1)
    return f"20{s[:2]}-{s[2:4]}"


def esc(s):
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def mark(r):
    tags = []
    if r.get("ub_priority"):
        tags.append("[UB-优先]")
    if r.get("arxiv_id") in KNOWN:
        tags.append("[前次已收]")
    return " ".join(tags) if tags else "-"


def sort_key(r):
    ub = 0 if r.get("ub_priority") else 1
    known = 0 if r.get("arxiv_id") in KNOWN else 1
    cite = -(r.get("cited_by_count") or 0)
    try:
        ym_neg = -int(ym_from_aid(r.get("arxiv_id") or "").replace("-", ""))
    except Exception:
        ym_neg = 0
    return (ub, known, cite, ym_neg)


def table_row(i, r):
    aid = r.get("arxiv_id", "")
    title = esc(r.get("title") or "")
    link = f"[{aid}](https://arxiv.org/abs/{aid})" if aid else "-"
    ym = ym_from_aid(aid) or str(r.get("year") or "")
    cite = r.get("cited_by_count")
    cite_s = str(cite) if cite is not None else "-"
    return f"| {i} | {title} | {link} | {ym} | {cite_s} | 是 | {mark(r)} |"


groups = {"E1": [], "E2": [], "E3": []}
for r in results:
    g = r.get("group")
    if g in groups:
        groups[g].append(r)
for g in groups:
    groups[g].sort(key=sort_key)

ub_papers = sorted([r for r in results if r.get("ub_priority")], key=sort_key)

L = []
A = L.append
A("# 超节点硬件体系架构 -- arXiv 检索轻量摘要表")
A("")
A("> **检索日期**：2026-08-31")
A("> **检索范围**：arXiv 预印本，2022-01-01 至今，英文")
A("> **检索方法**：因 `export.arxiv.org`（arXiv 官方 REST API 端点）在本环境 HTTPS 不可达（TCP 握手后 read 超时，已多轮验证），按 academic-search skill 失败降级规则，改用 **OpenAlex REST API**（HTTPS 可达、索引 arXiv 全量预印本、且提供引用数与 OA 状态--arXiv 原生 API 无引用数字段）。所有结果均过滤为**在 arXiv 上有收录的论文**（OpenAlex `locations.source.id == S4306400194`，即 arXiv 源），等价于“在 arXiv 检索”的目标范围。3 个已知 UB-优先 arXiv ID 额外通过 `arxiv.org/abs/<id>`（HTTPS 可达）直拉确认标题/年月/分类。")
A("> **引用数来源**：OpenAlex `cited_by_count`；后续可由另一 Agent 用 Semantic Scholar / Google Scholar 补全对齐。")
A("> **OA PDF**：arXiv 预印本均为开放获取，标“是”，直链 `https://arxiv.org/pdf/{arxiv_id}`。")
A("> **优先级标记**：`[UB-优先]` = 涉及灵衢总线 UnifiedBus/UB、华为超节点体系（CloudMatrix、昇腾 SuperPOD）或显式以“supernode/superpod”硬件体系为主题的论文，按 CLAUDE.md 最高优先级规则入选；`[前次已收]` = 已在前次报告中的已知论文（本次增量检索保留并标注）。")
A("")
A("---")
A("")
A("## 检索方法说明")
A("")
A("**平台**：OpenAlex REST API（`https://api.openalex.org/works`，`search` 关键词检索 + `filter=from_publication_date:2022-01-01,locations.source.id:S4306400194` 限定 arXiv 源）。")
A("")
A("**降级原因**：`export.arxiv.org` HTTPS API 在本环境不可达。诊断：HTTP 80 端口 0.6s 返回 301->HTTPS；HTTPS 443 端口 TCP 可连但 read 操作超时（18s+）；对照 `arxiv.org/abs/*` HTTPS 可达、`api.openalex.org` HTTPS 可达、`api.semanticscholar.org` HTTPS 可达（429 限流），判定为 export 子域端点在该网络路径下不可用。")
A("")
A("**关键词组合（实际执行的子查询，3 组共 34 个子查询，每个 25 条/页 ×2 页，合并去重）**：")
A("")
A("- **E1（超节点本体 + 华为/统一内存/NVL/GB200）**：`CloudMatrix`、`UnifiedBus`、`Ascend SuperPOD`、`unified memory semantics`、`supernode interconnect`、`superpod AI`、`scale-up domain`、`rack-scale LLM`、`pod-scale AI`、`NVL72`、`GB200`、`unified memory GPU`、`rack-scale GPU`")
A("- **E2（设备管理统一性 / 资源解耦 / 可组合基础设施）**：`resource disaggregation GPU`、`disaggregated memory GPU`、`composable infrastructure GPU`、`composable datacenter`、`single system image GPU`、`single-node abstraction`、`unified device abstraction`、`disaggregated LLM`、`disaggregated accelerator`")
A("- **E3（互联互通 / 互连拓扑 / CXL / 集合通信）**：`scale-up fabric`、`scale-up network LLM`、`interconnect topology LLM`、`interconnect topology GPU cluster`、`CXL collective communication`、`CXL LLM`、`CXL training`、`CXL accelerator`、`collective communication LLM`、`collective communication training`、`AI cluster interconnect`、`GPU cluster topology`")
A("")
A("**筛选规则**：")
A(f"- OpenAlex `search` 为相关性排序（非布尔），原始召回 raw_hits = {d.get('raw_hits')} 条；")
A(f"- 对每条结果遍历全部子查询规则施加**精度过滤**：宽泛概念词（scale-up / disaggregation / composable / topology / fabric 等）要求主词出现在**标题**且带上下文（如 topology+cluster/gpu、fabric+scale/network），罕见专有词（CloudMatrix/UnifiedBus/NVL72/GB200/CXL/SuperPOD/supernode/superpod/unified memory）允许标题或摘要；叠加 **CS 系统类 concept 门槛**与**噪声领域排除**（图神经网络/天文学/区块链/分子物理/神经科学/量子/机器人/医学/CFD 等同名或无关方向）；过滤后 221 条；")
A(f"- 去重（arXiv ID 优先，无 ID 则 title+year）后 {d.get('strict_filtered')} 条；")
A(f"- 按匹配子查询重分配组（E1 优先，避免宽松 query 锚定到错误组）；组内按 UB-优先 -> 前次已收 -> 引用降序 -> 年月降序排序，每组 cap 30 条；")
A(f"- 最终 E1={d['E1']}、E2={d['E2']}、E3={d['E3']}，合计 **{d['final_total']}** 条；其中 `[UB-优先]` **{d['ub_priority']}** 条。")
A("")
A("**局限**：")
A("- 本次未直接调用 `export.arxiv.org` API（环境网络不通），改走 OpenAlex 同源（arXiv 源过滤）等价检索并补充引用数；arXiv 原生 category 字段未取全（仅 3 个已知 ID 经 `arxiv.org/abs` 解析了 primary category），其余论文的 arXiv 分类待后续深拉元数据时补；")
A("- 引用数取自 OpenAlex（与 Semantic Scholar / Google Scholar 数值会不一致，属正常）；")
A("- Semantic Scholar 未使用（无 API Key，避免 429）；Google Scholar / 知网未使用（CDP 未开启，且本任务为 arXiv 英文检索，知网为另一并行任务的范围）；")
A("- 本表为第一遍轻量摘要，未在正文中展开完整摘要（完整摘要保存于中间 JSON，供第二遍深拉调用）。")
A("")
A("---")
A("")
A("## 一、[UB-优先] 论文清单（灵衢/华为超节点体系，固定首组）")
A("")
A("| # | 标题 | arXiv ID | 年月 | 引用数 | OA PDF | 优先级标记 |")
A("|---|------|----------|------|--------|--------|------------|")
for i, r in enumerate(ub_papers, 1):
    A(table_row(i, r))
A("")
for g, title in [
    ("E1", "二、E1 检索结果（超节点本体 + 华为/统一内存/NVL/GB200）"),
    ("E2", "三、E2 检索结果（设备管理统一性 / 资源解耦 / 可组合基础设施）"),
    ("E3", "四、E3 检索结果（互联互通 / 互连拓扑 / CXL / 集合通信）"),
]:
    A(f"## {title}")
    A("")
    A("| # | 标题 | arXiv ID | 年月 | 引用数 | OA PDF | 优先级标记 |")
    A("|---|------|----------|------|--------|--------|------------|")
    for i, r in enumerate(groups[g], 1):
        A(table_row(i, r))
    A("")
A("---")
A("")
A("## 中间产物")
A("")
A("- `arxiv_raw.json`：OpenAlex 原始召回（含完整摘要、作者、concepts、query 来源、OA 状态）")
A("- `arxiv_final.json`：严格过滤+去重+分组 cap 30 后的最终 90 条结构化结果（供第二遍深拉）")
A("- `openalex_search.py` / `refine.py` / `verify_ub.py` / `gen_md.py`：检索/重筛/核对/生成脚本（可复现）")
A("")

content = "\n".join(L)
with open(os.path.join(OUT_DIR, "arxiv_results.md"), "w", encoding="utf-8") as f:
    f.write(content)
print("wrote arxiv_results.md chars=", len(content), file=sys.stderr)
print("UB:", len(ub_papers), "E1:", len(groups["E1"]), "E2:", len(groups["E2"]), "E3:", len(groups["E3"]), "total:", sum(len(groups[g]) for g in groups), file=sys.stderr)
