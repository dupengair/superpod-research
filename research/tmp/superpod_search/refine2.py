#!/usr/bin/env python3
"""refine2：从 arxiv_raw.json 重筛（精度优先）。
- 宽泛概念词：要求主词出现在【标题】中；
- 罕见专有词（CloudMatrix/UnifiedBus/NVL72/GB200/CXL/SuperPOD 等）：标题或摘要均可；
- 全局 CS 系统类 concept 门槛 + 扩展噪声排除。"""
import json, os, re, sys

OUT_DIR = "/home/dupengair/shared/work/superpod/research/tmp/superpod_search"
data = json.load(open(os.path.join(OUT_DIR, "arxiv_raw.json"), encoding="utf-8"))
results = data["results"]

# mode: "title"=要求主词组在标题；"any"=标题或摘要
# 结构：外层 list = OR（任一 group 命中即保留）；内层 group = AND（组内 term 全部出现）
# keep() 会遍历【全部】规则，任一命中即保留（避免单 query 锚定误杀）
REQ = {
    # E1
    "CloudMatrix": ("any", [["cloudmatrix"]]),
    "UnifiedBus": ("any", [["unifiedbus"], ["unified bus"]]),
    "Ascend SuperPOD": ("any", [["superpod"], ["super pod"], ["super-pod"], ["ascend", "superpod"], ["ascend", "super pod"]]),
    "unified memory semantics": ("any", [["unified memory"]]),
    "supernode interconnect": ("any", [["supernode"], ["super node"], ["super-node"]]),
    "superpod AI": ("any", [["superpod"], ["super pod"], ["super-pod"]]),
    "scale-up domain": ("title", [["scale-up"], ["scale up"], ["scaleup"]]),
    "rack-scale LLM": ("title", [["rack-scale"], ["rack scale"], ["rackscale"]]),
    "pod-scale AI": ("title", [["pod-scale"], ["pod scale"], ["podscale"]]),
    "NVL72": ("any", [["nvl72"], ["nvl-72"], ["nvl 72"]]),
    "GB200": ("any", [["gb200"], ["gb-200"]]),
    "unified memory GPU": ("any", [["unified memory"]]),
    "rack-scale GPU": ("title", [["rack-scale"], ["rack scale"], ["rackscale"]]),
    # E2
    "resource disaggregation GPU": ("any", [["disaggregat"]]),
    "disaggregated memory GPU": ("any", [["disaggregat"]]),
    "composable infrastructure GPU": ("any", [["composab"]]),
    "composable datacenter": ("any", [["composab"]]),
    "single system image GPU": ("any", [["single system image"], ["single-system image"]]),
    "single-node abstraction": ("any", [["single-node abstraction"], ["single node abstraction"], ["single system image"], ["single-system image"]]),
    "unified device abstraction": ("any", [["device abstraction"]]),
    "disaggregated LLM": ("any", [["disaggregat"]]),
    "disaggregated accelerator": ("any", [["disaggregat"]]),
    # E3
    "scale-up fabric": ("title", [["fabric", "scale"], ["fabric", "up"], ["fabric", "interconnect"],
                                    ["fabric", "network"], ["fabric", "compute"], ["scale-up"], ["scale up"], ["scaleup"]]),
    "scale-up network LLM": ("title", [["scale-up"], ["scale up"], ["scaleup"]]),
    "interconnect topology LLM": ("title", [["interconnect"], ["topology", "cluster"], ["topology", "gpu"],
                                             ["network topology"], ["topology", "supercomputer"]]),
    "interconnect topology GPU cluster": ("title", [["interconnect"], ["topology", "cluster"], ["topology", "gpu"],
                                                     ["network topology"], ["topology", "supercomputer"]]),
    "CXL collective communication": ("any", [["cxl"]]),
    "CXL LLM": ("any", [["cxl"]]),
    "CXL training": ("any", [["cxl"]]),
    "CXL accelerator": ("any", [["cxl"]]),
    "collective communication LLM": ("title", [["collective communication"]]),
    "collective communication training": ("title", [["collective communication"]]),
    "AI cluster interconnect": ("title", [["interconnect"], ["ai cluster"], ["ai-cluster"], ["gpu cluster"]]),
    "GPU cluster topology": ("title", [["topology", "cluster"], ["topology", "gpu"], ["network topology"], ["interconnect"]]),
    "KNOWN_ID": ("any", [[]]),
}

# 扩展噪声领域（标题/concept 命中即剔除）
NOISE_TITLE = [
    "graph neural", "molecular", "astronom", "galaxy", "supernova", "blockchain",
    "ledger", "cryptography", "phylogen", "protein", "drug", "crystal", "molecule",
    "neuroscienc", "brain", "quantum", "qubit", "entangle", "robot", "gripper",
    "soft robot", "haptic", "dyslexia", "teacher", "school", "student",
    "crowdsourc", "fairness", "hegemonic", "race", "gender", "social support",
    "social fabric", "soft fabric", "palm-shape", "metafiber", "lasing",
    "speech", "audio", "pose estimation", "vision transformer", "vitpose",
    "medical", "clinical", "patient", "disease", "medmcqa", "meditron",
    "wireless", "6g", "ran", "open ran", "federated", "mojfl", "quantum network",
    "soft computing", "material", "chemistry", "optics", "photon",
    "non-hermitian", "skin effect", "differential equation", "pinns",
    "deformable object", "gripper", "modular soft", "spawning",
    "entanglement", "sensory edge", "slate bandit", "program synthesis",
    "library learning", "e-graphs", "anti-unification", "fortran", "mlir",
    "quantum hamiltonian", "simuq", "diffskill", "causal abstraction",
    "neural race", "representative datasets",
    "cfd", "fluid dynamics", "finite difference", "finite element",
    "weather prediction", "wind turbine", "climate", "ocean",
    "image segmentation", "object manipulation", "ecosystem",
    "try-on", "inpainting", "fashion", "virtual try",
    "satisfiability", "boolean sat", "diffusion decoding",
    "pixel diffusion", "self-speculation", "autoregressive, diffusion",
]
NOISE_CONCEPTS = [
    "astronomy", "astrophysics", "graph neural network", "blockchain",
    "molecular", "chemistry", "combinatorics", "geology", "ecology",
    "epidemiology", "neuroscience", "quantum mechanics", "robotics",
    "materials science", "optics", "photonics", "social science",
    "sociology", "education", "medicine", "health care",
]

# CS 系统类 concept 门槛（命中任一即视为相关领域）
CS_OK = [
    "computer science", "artificial intelligence", "distributed computing",
    "operating system", "computer architecture", "parallel computing",
    "supercomputer", "cloud computing", "graphics processing unit",
    "computer data storage", "memory management", "computer network",
    "telecommunication", "data center", "datacenter", "embedded system",
    "very large scale integration", "computer hardware", "microarchitecture",
    "instruction set architecture", "cache", "bus", "interconnect",
    "computer security", "software engineering", "machine learning",
    "deep learning", "natural language processing", "artificial neural network",
    "accelerator", "field-programmable gate array",
]


def match(text, term_groups):
    t = text.lower()
    return any(all(term in t for term in grp) for grp in term_groups)


def title_match(r, term_groups):
    return match((r.get("title") or ""), term_groups)


def any_match(r, term_groups):
    blob = ((r.get("title") or "") + " " + (r.get("abstract") or "")).lower()
    return any(all(term in blob for term in grp) for grp in term_groups)


def is_noise(r):
    title_l = (r.get("title") or "").lower()
    conc = " ".join(r.get("concepts", []))
    for h in NOISE_TITLE:
        if h in title_l:
            return True
    for c in NOISE_CONCEPTS:
        if c in conc:
            return True
    return False


def cs_gate(r):
    conc = " ".join(r.get("concepts", [])).lower()
    title_l = (r.get("title") or "").lower()
    for c in CS_OK:
        if c in conc:
            return True
    # 标题含强系统信号也算
    sys_hints = ["gpu", "npu", "accelerator", "interconnect", "fabric", "cxl",
                 "disaggregat", "composab", "cluster", "supernode", "superpod",
                 "cloudmatrix", "unifiedbus", "unified memory", "rack-scale",
                 "scale-up", "memory pool", "kv cache", "llm serving",
                 "training", "inference", "collective", "topology", "datacenter",
                 "data center"]
    return any(h in title_l for h in sys_hints)


def keep(r):
    """遍历全部规则，任一命中即保留（避免单 query 锚定误杀）。
    KNOWN_ID 规则（空 term）视为无条件保留。"""
    matched = []
    for q, (mode, groups) in REQ.items():
        if groups == [[]]:
            continue
        if mode == "title":
            ok = title_match(r, groups)
        else:
            ok = any_match(r, groups)
        if ok:
            matched.append(q)
    if not matched:
        return False
    if is_noise(r):
        return False
    if not cs_gate(r):
        return False
    r["matched_queries"] = matched
    return True


kept = [r for r in results if keep(r)]
print("after strict title/any + cs-gate + noise:", len(kept), "of", len(results), file=sys.stderr)

# 去重
by_id = {}
by_title = {}
no_id = []
for r in kept:
    aid = (r.get("arxiv_id") or "").strip()
    ty = ((r.get("title") or "").lower().strip(), r.get("year"))
    if aid:
        if aid in by_id:
            by_id[aid].setdefault("queries", set()).add(r.get("query", ""))
            if (r.get("cited_by_count") or 0) > (by_id[aid].get("cited_by_count") or 0):
                r2 = dict(r); r2["queries"] = by_id[aid].get("queries", set()); by_id[aid] = r2
        else:
            r2 = dict(r); r2["queries"] = {r.get("query", "")}; by_id[aid] = r2; by_title[ty] = r2
    else:
        no_id.append(r)
final_no = []
seen = set()
for r in no_id:
    ty = ((r.get("title") or "").lower().strip(), r.get("year"))
    if ty in by_title:
        by_title[ty].setdefault("queries", set()).add(r.get("query", "")); continue
    if ty in seen:
        continue
    seen.add(ty); final_no.append(r)
merged = list(by_id.values()) + final_no
print("after dedup:", len(merged), file=sys.stderr)

# UB 标记
UB_MARKERS = ["unifiedbus", "unified bus", "cloudmatrix", "ascend superpod", "superpod",
              "huawei", "lingqu", "unified memory semantic", "supernode", "super node"]
for r in merged:
    blob = ((r.get("title") or "") + " " + " ".join(r.get("concepts", [])) + " " + (r.get("abstract") or "")[:600]).lower()
    r["ub_priority"] = any(m in blob for m in UB_MARKERS)

# 分组 + 排序 + cap 30
# 按匹配到的子查询重分配组（E1 优先，避免被宽松 query 锚定到错误组）
GROUP_OF = {}
for q in ["CloudMatrix", "UnifiedBus", "Ascend SuperPOD", "unified memory semantics",
          "supernode interconnect", "superpod AI", "scale-up domain", "rack-scale LLM",
          "pod-scale AI", "NVL72", "GB200", "unified memory GPU", "rack-scale GPU"]:
    GROUP_OF[q] = "E1"
for q in ["resource disaggregation GPU", "disaggregated memory GPU", "composable infrastructure GPU",
          "composable datacenter", "single system image GPU", "single-node abstraction",
          "unified device abstraction", "disaggregated LLM", "disaggregated accelerator"]:
    GROUP_OF[q] = "E2"
for q in ["scale-up fabric", "scale-up network LLM", "interconnect topology LLM",
          "interconnect topology GPU cluster", "CXL collective communication", "CXL LLM",
          "CXL training", "CXL accelerator", "collective communication LLM",
          "collective communication training", "AI cluster interconnect", "GPU cluster topology"]:
    GROUP_OF[q] = "E3"

groups = {"E1": [], "E2": [], "E3": []}
for r in merged:
    mq = r.get("matched_queries") or [r.get("query", "")]
    assigned = None
    for q in mq:
        if GROUP_OF.get(q) == "E1":
            assigned = "E1"; break
    if assigned is None:
        for q in mq:
            if GROUP_OF.get(q) == "E2":
                assigned = "E2"; break
    if assigned is None:
        for q in mq:
            if GROUP_OF.get(q) == "E3":
                assigned = "E3"; break
    if assigned is None:
        assigned = (r.get("group") or "E3")
        if assigned not in groups:
            assigned = "E3"
    r["group"] = assigned
    groups[assigned].append(r)

def sk(r):
    ub = 0 if r.get("ub_priority") else 1
    known = 0 if r.get("arxiv_id") in ["2506.12708", "2508.02520", "2607.20145"] else 1
    cite = -(r.get("cited_by_count") or 0)
    try:
        y = -int((r.get("arxiv_id") or "")[:4])
    except Exception:
        y = 0
    return (ub, known, cite, y)

for g in groups:
    groups[g].sort(key=sk)
    groups[g] = groups[g][:30]

# 已知 ID 兜底注入
final = groups["E1"] + groups["E2"] + groups["E3"]
for kid in ["2506.12708", "2508.02520", "2607.20145"]:
    if not any(r.get("arxiv_id") == kid for r in final):
        for r in results:
            if r.get("arxiv_id") == kid:
                r2 = dict(r); r2["ub_priority"] = True; r2["group"] = "E1"; r2["known_prior"] = True
                if isinstance(r2.get("queries"), set):
                    r2["queries"] = sorted(r2["queries"])
                groups["E1"].insert(0, r2); final.append(r2); break
# set->list
for r in final:
    if isinstance(r.get("queries"), set):
        r["queries"] = sorted([q for q in r["queries"] if q])

ub = [r for r in final if r.get("ub_priority")]
print("final E1=%d E2=%d E3=%d total=%d UB=%d" % (len(groups["E1"]), len(groups["E2"]), len(groups["E3"]), len(final), len(ub)), file=sys.stderr)
print("group sizes before cap: E1=%d E2=%d E3=%d" % (
    sum(1 for r in merged if r.get("group") == "E1"),
    sum(1 for r in merged if r.get("group") == "E2"),
    sum(1 for r in merged if r.get("group") == "E3")), file=sys.stderr)
for r in ub:
    print("  UB:", r.get("arxiv_id"), r.get("year"), r.get("cited_by_count"), repr((r.get("title") or "")[:70]), file=sys.stderr)

# 列出每组前几条以抽查质量
for g in ["E1", "E2", "E3"]:
    print(f"--- {g} sample ---", file=sys.stderr)
    for r in groups[g][:8]:
        print("  ", r.get("arxiv_id"), r.get("year"), r.get("cited_by_count"), repr((r.get("title") or "")[:65]), "|q=", r.get("query"), file=sys.stderr)

out = {
    "query_log": data.get("query_log", []),
    "known_ids": data.get("known_ids", []),
    "raw_hits": data.get("raw_hits"),
    "strict_filtered": len(merged),
    "final_total": len(final),
    "E1": len(groups["E1"]), "E2": len(groups["E2"]), "E3": len(groups["E3"]),
    "ub_priority": len(ub),
    "results": final,
}
json.dump(out, open(os.path.join(OUT_DIR, "arxiv_final.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("wrote arxiv_final.json", file=sys.stderr)
