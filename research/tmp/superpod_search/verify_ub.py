#!/usr/bin/env python3
"""核对 UB-优先论文摘要 + 恢复 no_id 论文的 arXiv ID。"""
import json, os, re, sys, time, urllib.request

OUT_DIR = "/home/dupengair/shared/work/superpod/research/tmp/superpod_search"
d = json.load(open(os.path.join(OUT_DIR, "arxiv_final.json"), encoding="utf-8"))
results = d["results"]

print("=== UB-优先论文核对 ===", file=sys.stderr)
for r in results:
    if r.get("ub_priority"):
        print("---", file=sys.stderr)
        print("arxiv:", r.get("arxiv_id"), "| year:", r.get("year"), "| cited:", r.get("cited_by_count"), file=sys.stderr)
        print("title:", r.get("title"), file=sys.stderr)
        print("authors:", ", ".join(r.get("authors", [])[:4]), file=sys.stderr)
        print("venue:", r.get("venue"), "| oa:", r.get("is_oa"), "| oa_url:", r.get("oa_url"), file=sys.stderr)
        ab = (r.get("abstract") or "")[:500]
        print("abstract[:500]:", ab, file=sys.stderr)
        print("queries:", r.get("queries"), file=sys.stderr)

print("\n=== 无 arxiv_id 的论文 ===", file=sys.stderr)
for r in results:
    if not r.get("arxiv_id"):
        print("---", file=sys.stderr)
        print("title:", r.get("title"), "| year:", r.get("year"), "| cited:", r.get("cited_by_count"), file=sys.stderr)
        print("openalex_id:", r.get("openalex_id"), "| venue:", r.get("venue"), file=sys.stderr)
        print("abstract[:300]:", (r.get("abstract") or "")[:300], file=sys.stderr)

# 尝试为 no_id 论文从 openalex_id 反查 arxiv location
print("\n=== 恢复 no_id arxiv ID ===", file=sys.stderr)
for r in results:
    if r.get("arxiv_id"):
        continue
    oid = (r.get("openalex_id") or "").rsplit("/", 1)[-1]
    if not oid:
        continue
    url = f"https://api.openalex.org/works/{oid}?mailto=research@local"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "academic-search-skill/1.x"})
        w = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        print("  fetch fail", oid, e, file=sys.stderr)
        continue
    aid = ""
    aurl = ""
    for loc in w.get("locations") or []:
        u = loc.get("landing_page_url") or loc.get("url") or ""
        p = loc.get("pdf_url") or ""
        for cand in (u, p):
            if "arxiv.org" in cand:
                m = re.search(r"arxiv\.org/(?:abs|pdf)/([^/?#]+)", cand)
                if m:
                    aid = m.group(1); aurl = cand
                    break
        if aid:
            break
    print("  ", oid, "-> recovered arxiv:", aid or "(none)", "| title:", (w.get("title") or "")[:50], file=sys.stderr)
    if aid:
        r["arxiv_id"] = aid
        r["arxiv_url"] = aurl or f"https://arxiv.org/abs/{aid}"
    time.sleep(0.4)

# 回写
json.dump(d, open(os.path.join(OUT_DIR, "arxiv_final.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\nwrote back arxiv_final.json", file=sys.stderr)
