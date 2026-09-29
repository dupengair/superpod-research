#!/usr/bin/env python3
"""从 arxiv_raw.json 重筛：要求原始关键短语在标题或摘要中实际出现，每组 cap ~30。"""
import json, os, re, sys

OUT_DIR = "/home/dupengair/shared/work/superpod/research/tmp/superpod_search"
data = json.load(open(os.path.join(OUT_DIR, "arxiv_raw.json"), encoding="utf-8"))
results = data["results"]

# 每个子查询要求在 title+abstract 中出现的“主词”列表（满足任一即可保留）
# 设计：把宽松 relevance 召回收紧为“确切包含核心术语”
REQ = {
    "CloudMatrix": [["cloudmatrix"]],
    "UnifiedBus": [["unifiedbus", "unified bus"]],
    "Ascend SuperPOD": [["superpod"], ["ascend", "superpod"]],
    "unified memory semantics": [["unified memory"]],
    "supernode interconnect": [["supernode"]],
    "superpod AI": [["superpod"]],
    "scale-up domain": [["scale-up", "scale up", "scaleup"], ["scale", "domain"]],
    "rack-scale LLM": [["rack-scale", "rack scale", "rackscale"]],
    "pod-scale AI": [["pod-scale", "pod scale", "podscale"]],
    "NVL72": [["nvl72", "nvl-72"]],
    "GB200": [["gb200", "gb-200"]],
    "unified memory GPU": [["unified memory"]],
    "rack-scale GPU": [["rack-scale", "rack scale", "rackscale"]],
    # E2
    "resource disaggregation GPU": [["disaggregat"]],
    "disaggregated memory GPU": [["disaggregat"]],
    "composable infrastructure GPU": [["composab"]],
    "composable datacenter": [["composab"]],
    "single system image GPU": [["single system image", "single-system image"]],
    "single-node abstraction": [["abstraction"], ["single", "node"]],
    "unified device abstraction": [["abstraction"]],
    "disaggregated LLM": [["disaggregat"]],
    "disaggregated accelerator": [["disaggregat"]],
    # E3
    "scale-up fabric": [["fabric"], ["scale-up", "scale up"]],
    "scale-up network LLM": [["scale-up", "scale up", "scaleup"]],
    "interconnect topology LLM": [["interconnect", "topology"]],
    "interconnect topology GPU cluster": [["interconnect", "topology"]],
    "CXL collective communication": [["cxl"]],
    "CXL LLM": [["cxl"]],
    "CXL training": [["cxl"]],
    "CXL accelerator": [["cxl"]],
    "collective communication LLM": [["collective"]],
    "collective communication training": [["collective"]],
    "AI cluster interconnect": [["interconnect"], ["ai cluster", "ai-clusters"]],
    "GPU cluster topology": [["topology", "cluster"]],
    "KNOWN_ID": [[]],  # 已知 ID 直拉，无条件保留
}


def match_any(text, term_groups):
    t = text.lower()
    for grp in term_groups:
        if all(term in t for term in grp):
            return True
    return False


def keep(r):
    q = r.get("query", "")
    req = REQ.get(q)
    if req is None:
        return True
    if req == [[]]:
        return True
    blob = ((r.get("title") or "") + " " + (r.get("abstract") or "")).lower()
    return match_any(blob, req)


kept = [r for r in results if keep(r)]
print("after strict term filter:", len(kept), "of", len(results), file=sys.stderr)

# 再次按 arxiv_id 去重（合并 query 来源）
by_id = {}
by_title = {}  # title_lower+year -> record，用于跨 id/no-id 去重
no_id = []
for r in kept:
    aid = (r.get("arxiv_id") or "").strip()
    ty_key = ((r.get("title") or "").lower().strip(), r.get("year"))
    if aid:
        if aid in by_id:
            by_id[aid].setdefault("queries", set()).add(r.get("query", ""))
            if (r.get("cited_by_count") or 0) > (by_id[aid].get("cited_by_count") or 0):
                r2 = dict(r); r2["queries"] = by_id[aid].get("queries", set())
                by_id[aid] = r2
        else:
            r2 = dict(r); r2["queries"] = {r.get("query", "")}
            by_id[aid] = r2
            by_title[ty_key] = r2
    else:
        no_id.append(r)

# 无 id 的：先与有 id 的按 title+year 去重，命中则把 query 合并过去
final_no_id = []
seen_ty = set()
for r in no_id:
    ty_key = ((r.get("title") or "").lower().strip(), r.get("year"))
    if ty_key in by_title:
        by_title[ty_key].setdefault("queries", set()).add(r.get("query", ""))
        continue  # 同一篇，并入有 id 版本
    if ty_key in seen_ty:
        continue
    seen_ty.add(ty_key)
    final_no_id.append(r)
merged = list(by_id.values()) + final_no_id
print("after re-dedup:", len(merged), " no_id_unique:", len(final_no_id), file=sys.stderr)

# 重新标记 ub_priority（基于更严格字段：title+concepts+abstract前600）
UB_MARKERS = ["unifiedbus", "unified bus", "cloudmatrix", "ascend superpod", "superpod",
              "huawei", "lingqu", "unified memory semantic", "supernode"]
for r in merged:
    blob = ((r.get("title") or "") + " " + " ".join(r.get("concepts", [])) + " " + (r.get("abstract") or "")[:600]).lower()
    r["ub_priority"] = any(m in blob for m in UB_MARKERS)

# 分组
groups = {"E1": [], "E2": [], "E3": []}
for r in merged:
    g = r.get("group")
    if g in groups:
        groups[g].append(r)

# 组内排序：UB-优先 -> 引用降序 -> 年降序；cap 30
for g in groups:
    groups[g].sort(key=lambda x: (not x.get("ub_priority"), -(x.get("cited_by_count") or 0), -(x.get("year") or 0)))
    groups[g] = groups[g][:30]

final = groups["E1"] + groups["E2"] + groups["E3"]
# 也确保 3 个 known id 在 final
for kid in ["2506.12708", "2508.02520", "2607.20145"]:
    if not any(r.get("arxiv_id") == kid for r in final):
        # 从原 results 找
        for r in results:
            if r.get("arxiv_id") == kid:
                r2 = dict(r); r2["ub_priority"] = True; r2["group"] = "E1"; r2["known_prior"] = True
                final.append(r2); break

print("final E1=%d E2=%d E3=%d total=%d" % (
    len(groups["E1"]), len(groups["E2"]), len(groups["E3"]), len(final)), file=sys.stderr)
# set -> list 以便 JSON 序列化
for r in final:
    if isinstance(r.get("queries"), set):
        r["queries"] = sorted([q for q in r["queries"] if q])
ub = [r for r in final if r.get("ub_priority")]
print("UB-优先:", len(ub), file=sys.stderr)
for r in ub:
    print("  UB:", r.get("arxiv_id"), r.get("year"), r.get("cited_by_count"), repr((r.get("title") or "")[:70]), file=sys.stderr)

# 保存精简结果
out = {
    "query_log": data.get("query_log", []),
    "known_ids": data.get("known_ids", []),
    "raw_hits": data.get("raw_hits"),
    "merged_all": data.get("merged"),
    "cleaned_all": data.get("cleaned"),
    "dropped_noise": data.get("dropped_noise"),
    "strict_filtered": len(merged),
    "final_total": len(final),
    "E1": len(groups["E1"]), "E2": len(groups["E2"]), "E3": len(groups["E3"]),
    "ub_priority": len(ub),
    "results": final,
}
json.dump(out, open(os.path.join(OUT_DIR, "arxiv_final.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("wrote arxiv_final.json", file=sys.stderr)
