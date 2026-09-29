#!/usr/bin/env python3
"""
arXiv 检索降级脚本：export.arxiv.org HTTPS API 在本环境不可达（hang），
按 academic-search skill 的失败降级规则，改用 OpenAlex REST API（HTTPS 可达，
索引 arXiv 预印本，且提供引用数与 OA 状态——arXiv 原生 API 无引用数字段）。
仅保留在 arXiv 上有收录的论文（locations.source.id == arXiv 源 S4306400194），
等价于“在 arXiv 检索”的目标范围。对 3 个已知 UB-优先 arXiv ID，
通过 arxiv.org/abs/<id>（HTTPS 可达）直拉确认标题/年月/分类。
"""
import urllib.request, urllib.parse, json, time, sys, os, re

OA = "https://api.openalex.org"
ARXIV_SOURCE_ID = "S4306400194"   # arXiv 在 OpenAlex 的 source id
MAILTO = "research@local"
DATE_FROM = "2022-01-01"
OUT_DIR = "/home/dupengair/shared/work/superpod/research/tmp/superpod_search"
os.makedirs(OUT_DIR, exist_ok=True)

# UB-优先关键词（命中即标 [UB-优先]）
UB_MARKERS = ["UnifiedBus", "Unified Bus", "CloudMatrix", "Ascend SuperPOD", "SuperPod",
              "unified memory semantics", "Huawei", "Lingqu", "supernode"]
# 噪声领域（同名 supernode 的无关方向）——命中则剔除
NOISE_CONCEPTS = ["graph neural network", "astronomy", "astrophysics",
                  "blockchain", "molecular", "chemistry", "combinatorics",
                  "geology", "ecology", "epidemiology"]
NOISE_TITLE_HINTS = ["graph neural", "molecular", "astronom", "galaxy", "supernova",
                     "blockchain", "ledger", "cryptography", "graph node",
                     "phylogen", "protein", "drug", "crystal", "molecule"]


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": "academic-search-skill/1.x (mailto:research@local)",
        "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def reconstruct_abstract(inv):
    if not inv:
        return ""
    pos = []
    for w, idxs in inv.items():
        for i in idxs:
            pos.append((i, w))
    pos.sort()
    return " ".join(w for _, w in pos)


def parse_work(w, query):
    arxiv_id = ""
    arxiv_url = ""
    arxiv_cat = ""
    for loc in w.get("locations") or []:
        u = loc.get("landing_page_url") or loc.get("url") or ""
        lic = loc.get("license")
        if "arxiv.org" in u:
            aid = u.rstrip("/").rsplit("/", 1)[-1]
            if aid and not aid.lower().startswith("arxiv"):
                arxiv_id = aid
                arxiv_url = u
            break
    pl = w.get("primary_location") or {}
    src = (pl.get("source") or {})
    venue = src.get("display_name") or ""
    oa = (w.get("open_access") or {})
    concepts = [(c.get("display_name") or "").lower() for c in (w.get("concepts") or [])]
    abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
    return {
        "arxiv_id": arxiv_id,
        "arxiv_url": arxiv_url,
        "title": w.get("title") or "",
        "year": w.get("publication_year"),
        "venue": venue,
        "cited_by_count": w.get("cited_by_count", 0),
        "is_oa": bool(oa.get("is_oa")),
        "oa_url": (pl.get("pdf_url") or ""),
        "authors": [(a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or [])][:8],
        "concepts": concepts[:8],
        "abstract": abstract,
        "query": query,
        "openalex_id": w.get("id", ""),
    }


def oa_search(query, per_page=25, max_pages=2):
    out = []
    for page in range(1, max_pages + 1):
        params = {
            "search": query,
            "filter": f"from_publication_date:{DATE_FROM},locations.source.id:{ARXIV_SOURCE_ID}",
            "per-page": str(per_page),
            "page": str(page),
            "mailto": MAILTO,
        }
        url = OA + "/works?" + urllib.parse.urlencode(params)
        try:
            d = json.loads(http_get(url, 30))
        except Exception as e:
            print(f"  ERROR search {query!r} page {page}: {e}", file=sys.stderr)
            break
        results = d.get("results", [])
        total = d.get("meta", {}).get("count", 0)
        if page == 1:
            print(f"  [{query}] total(arxiv-hosted 2022+): {total}", file=sys.stderr)
        if not results:
            break
        for w in results:
            out.append(parse_work(w, query))
        if len(results) < per_page:
            break
        time.sleep(0.25)
    return out


def is_noise(w):
    title_l = (w["title"] or "").lower()
    conc = " ".join(w["concepts"])
    for h in NOISE_TITLE_HINTS:
        if h in title_l:
            return True
    for c in NOISE_CONCEPTS:
        if c in conc:
            return True
    # GNN + supernode
    if "supernode" in title_l and ("graph" in conc or "neural" in conc) and "infrastructure" not in title_l and "interconnect" not in title_l and "data center" not in title_l and "datacenter" not in title_l:
        return True
    return False


def is_ub_priority(w):
    blob = (w["title"] + " " + " ".join(w["concepts"]) + " " + (w["abstract"][:400] if w["abstract"] else "")).lower()
    for m in ["unifiedbus", "unified bus", "cloudmatrix", "ascend superpod", "superpod", "huawei", "lingqu", "unified memory semantic"]:
        if m in blob:
            return True
    return False


# 分组检索式（每组多个互补子查询，按 OpenAlex search 跑）
GROUPS = {
    "E1": [
        "CloudMatrix",
        "UnifiedBus",
        "Ascend SuperPOD",
        "unified memory semantics",
        "supernode interconnect",
        "superpod AI",
        "scale-up domain",
        "rack-scale LLM",
        "pod-scale AI",
        "NVL72",
        "GB200",
        "unified memory GPU",
        "rack-scale GPU",
    ],
    "E2": [
        "resource disaggregation GPU",
        "disaggregated memory GPU",
        "composable infrastructure GPU",
        "composable datacenter",
        "single system image GPU",
        "single-node abstraction",
        "unified device abstraction",
        "disaggregated LLM",
        "disaggregated accelerator",
    ],
    "E3": [
        "scale-up fabric",
        "scale-up network LLM",
        "interconnect topology LLM",
        "interconnect topology GPU cluster",
        "CXL collective communication",
        "CXL LLM",
        "CXL training",
        "CXL accelerator",
        "collective communication LLM",
        "collective communication training",
        "AI cluster interconnect",
        "GPU cluster topology",
    ],
}

KNOWN_IDS = ["2506.12708", "2508.02520", "2607.20145"]


def fetch_arxiv_abs(arxiv_id):
    """arxiv.org/abs/<id> HTTPS 可达，解析 meta 标签确认标题/年月/分类。"""
    url = f"https://arxiv.org/abs/{arxiv_id}"
    try:
        html = http_get(url, 30)
    except Exception as e:
        return {"arxiv_id": arxiv_id, "error": str(e)}
    def meta(name):
        m = re.search(rf'<meta\s+name="{name}"\s+content="([^"]*)"', html)
        return m.group(1) if m else ""
    title = meta("citation_title") or ""
    if not title:
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        title = (m.group(1).replace("arXiv:", "").strip() if m else "")
    date = meta("citation_date")            # e.g. 2025-06
    authors = re.findall(r'<meta\s+name="citation_author"\s+content="([^"]*)"', html)
    # primary category from the abs page
    cat = ""
    mc = re.search(r'<meta\s+name="citation_arxiv_id"\s+content="([^"]*)"', html)
    aid2 = mc.group(1) if mc else arxiv_id
    # primary category: look for the subjects line
    ms = re.search(r"Subjects?:\s*([^\n<]+)", html)
    if ms:
        cat = ms.group(1).strip()
    return {
        "arxiv_id": arxiv_id,
        "arxiv_url": url,
        "title": title,
        "year": (date[:4] if date else None),
        "date": date,
        "venue": "arXiv preprint",
        "cited_by_count": None,   # 待另一 Agent 从 OpenAlex/S2 补
        "is_oa": True,
        "oa_url": f"https://arxiv.org/pdf/{arxiv_id}",
        "authors": authors[:8],
        "concepts": [],
        "abstract": "",
        "primary_category": cat,
        "query": "KNOWN_ID",
        "openalex_id": "",
    }


def main():
    all_hits = []
    log = []
    for grp, terms in GROUPS.items():
        print(f"=== Group {grp} ===", file=sys.stderr)
        for q in terms:
            hits = oa_search(q)
            print(f"  -> {len(hits)} parsed", file=sys.stderr)
            for h in hits:
                h["group"] = grp
            all_hits.extend(hits)
            log.append({"group": grp, "query": q, "returned": len(hits)})
            time.sleep(0.3)

    # 去重：arxiv_id 优先，无 id 则 title+year
    by_id = {}
    no_id = []
    for h in all_hits:
        aid = (h.get("arxiv_id") or "").strip()
        if aid:
            if aid not in by_id:
                by_id[aid] = h
            else:
                # 合并 query 来源
                prev = by_id[aid]
                qs = set(prev.get("queries", [prev.get("query", "")])) | {h.get("query", "")}
                prev["queries"] = list(qs)
        else:
            no_id.append(h)

    # title+year 去重（对无 arxiv_id 的）
    seen_ty = set()
    no_id_dedup = []
    for h in no_id:
        key = (h["title"].lower().strip(), h.get("year"))
        if key in seen_ty:
            continue
        seen_ty.add(key)
        no_id_dedup.append(h)

    merged = list(by_id.values()) + no_id_dedup

    # 已知 ID 直拉
    known = []
    for kid in KNOWN_IDS:
        print(f"=== known {kid} ===", file=sys.stderr)
        w = fetch_arxiv_abs(kid)
        w["group"] = "E1"
        w["known_prior"] = True
        known.append(w)
        time.sleep(0.5)
    # 把已知 ID 注入 merged（若 OpenAlex 没召回到）
    for k in known:
        if not any(m.get("arxiv_id") == k["arxiv_id"] for m in merged):
            merged.append(k)

    # 噪声剔除
    cleaned = []
    dropped = []
    for h in merged:
        if is_noise(h):
            dropped.append(h)
            continue
        h["ub_priority"] = is_ub_priority(h)
        cleaned.append(h)

    # 排序：UB-优先在前，然后按引用数降序，再按年降序
    cleaned.sort(key=lambda x: (not x.get("ub_priority"), -(x.get("cited_by_count") or 0), -(x.get("year") or 0)))

    out = {
        "query_log": log,
        "known_ids": KNOWN_IDS,
        "raw_hits": len(all_hits),
        "merged": len(merged),
        "cleaned": len(cleaned),
        "dropped_noise": len(dropped),
        "ub_priority_count": sum(1 for h in cleaned if h.get("ub_priority")),
        "results": cleaned,
        "dropped": dropped,
    }
    with open(os.path.join(OUT_DIR, "arxiv_raw.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("done. raw=%d merged=%d cleaned=%d ub=%d dropped=%d"
          % (out["raw_hits"], out["merged"], out["cleaned"], out["ub_priority_count"], out["dropped_noise"]),
          file=sys.stderr)


if __name__ == "__main__":
    main()
