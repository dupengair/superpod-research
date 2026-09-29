import json, os
d = json.load(open("/home/dupengair/shared/work/superpod/research/tmp/superpod_search/arxiv_raw.json", encoding="utf-8"))
res = d["results"]
print("total in raw results:", len(res))
hits = [r for r in res if r.get("arxiv_id") == "2602.00748"]
print("2602.00748 occurrences in raw:", len(hits))
for r in hits:
    print("  title:", r.get("title"))
    print("  group:", r.get("group"), "query:", r.get("query"))
    print("  concepts:", r.get("concepts")[:8])
    print("  abstract[:400]:", (r.get("abstract") or "")[:400])
hyp = [r for r in res if "HyperOffload" in (r.get("title") or "")]
print("HyperOffload by title:", len(hyp), [(r.get("arxiv_id"), r.get("query")) for r in hyp])
# replicate refine2 keep logic for this paper
REQ = {
    "supernode interconnect": ("any", [["supernode", "super node", "super-node"]]),
}
def any_match(r, tg):
    blob = ((r.get("title") or "") + " " + (r.get("abstract") or "")).lower()
    return any(all(t in blob for t in g) for g in tg)
for r in hits:
    print("  matches supernode interconnect rule:", any_match(r, REQ["supernode interconnect"][1]))
