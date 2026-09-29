#!/usr/bin/env python3
"""
arXiv 检索脚本：执行多组子查询，解析 Atom XML，输出结构化 JSON。
遵循 academic-search skill 的 arXiv API 用法（REST API，无浏览器）。
速率：每请求间隔 3 秒（arXiv 非官方限制）。
"""
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import json
import time
import sys
import os

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

# 日期范围：2022-01-01 至今（2026-08-31）
DATE_FILTER = 'submittedDate:[202201010000 TO 202608312359]'

# 检索式分组（每组多个子查询以提高召回率，规避超长布尔式解析问题）
QUERIES = {
    # E1：超节点本体 + 华为/统一内存/GB200/NVL 等
    "E1a-CloudMatrix": '(all:"CloudMatrix")',
    "E1b-UnifiedBus": '(all:"UnifiedBus" OR all:"Unified Bus" OR all:"unified bus")',
    "E1c-Ascend-SuperPOD": '(all:"Ascend SuperPOD" OR all:"Ascend Super Pod" OR all:"SuperPod" AND all:"Ascend")',
    "E1d-supernode-superpod": '(all:"supernode" OR all:"superpod" OR all:"scale-up domain" OR all:"rack-scale" OR all:"pod-scale")',
    "E1e-NVL72-GB200": '(all:"NVL72" OR all:"GB200" OR all:"NVL-Link" OR all:"NVLink") AND (all:LLM OR all:inference OR all:training OR all:"unified memory")',
    "E1f-rack-scale-LLM": '(all:"rack-scale" OR all:"rack scale") AND (all:LLM OR all:GPU OR all:"unified memory" OR all:"resource disaggregation" OR all:inference)',
    "E1g-unified-memory-LLM": '(all:"unified memory" OR all:"unified memory semantic") AND (all:LLM OR all:GPU OR all:accelerator OR all:interconnect OR all:supernode OR all:superpod)',
    # E2：设备管理统一性 / 资源解耦 / 可组合基础设施
    "E2a-resource-disaggregation": '(all:"resource disaggregation" OR all:"disaggregated") AND (all:GPU OR all:NPU OR all:accelerator OR all:LLM)',
    "E2b-composable-infra": '(all:"composable infrastructure" OR all:"composable datacenter" OR all:"composable data center") AND (all:GPU OR all:accelerator OR all:LLM)',
    "E2c-single-system-image": '(all:"single system image" OR all:"single-system image" OR all:"single-node abstraction" OR all:"unified device abstraction")',
    "E2d-disaggregation-LLM": '(all:"disaggregated" OR all:"disaggregation") AND (all:LLM OR all:"large language model" OR all:"GPU cluster" OR all:"AI cluster")',
    # E3：互联互通 / 互连拓扑 / CXL / 集合通信
    "E3a-scale-up-fabric": '(all:"scale-up fabric" OR all:"scale up fabric" OR all:"scaleup fabric")',
    "E3b-interconnect-topology": '(all:"interconnect topology" OR all:"network topology") AND (all:LLM OR all:"AI cluster" OR all:training OR all:inference OR all:GPU OR all:collective)',
    "E3c-CXL": '(all:CXL OR all:"Compute Express Link") AND (all:LLM OR all:"collective communication" OR all:training OR all:inference OR all:accelerator OR all:disaggregated)',
    "E3d-collective-comm": '(all:"collective communication" OR all:"collective communications") AND (all:LLM OR all:training OR all:inference OR all:"AI cluster" OR all:GPU)',
    "E3e-ai-cluster-interconnect": '(all:"AI cluster" OR all:"GPU cluster") AND (all:interconnect OR all:topology OR all:fabric OR all:CXL)',
}


def fetch(query_str, max_results=60, start=0):
    """调用 arXiv API，返回 (entries_list, total_results)。"""
    full_query = f'({query_str}) AND {DATE_FILTER}'
    params = {
        "search_query": full_query,
        "start": str(start),
        "max_results": str(max_results),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = ARXIV_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "academic-search-skill/1.x (mailto:research@local)"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"error": str(e), "url": url}, 0
    return parse_atom(data), 0


def parse_atom(xml_text):
    """解析 arXiv Atom XML，返回 entry 列表。"""
    entries = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        return [{"parse_error": str(e)}]
    # totalResults
    total = 0
    tr = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    if tr is not None:
        try:
            total = int(tr.text)
        except ValueError:
            pass
    for entry in root.findall("atom:entry", NS):
        e = {}
        id_el = entry.find("atom:id", NS)
        e["arxiv_id"] = id_el.text.strip().split("/")[-1] if id_el is not None and id_el.text else ""
        title_el = entry.find("atom:title", NS)
        e["title"] = " ".join(title_el.text.split()) if title_el is not None and title_el.text else ""
        pub = entry.find("atom:published", NS)
        e["published"] = pub.text.strip() if pub is not None and pub.text else ""
        upd = entry.find("atom:updated", NS)
        e["updated"] = upd.text.strip() if upd is not None and upd.text else ""
        authors = []
        for a in entry.findall("atom:author", NS):
            name = a.find("atom:name", NS)
            if name is not None and name.text:
                authors.append(name.text.strip())
        e["authors"] = authors
        summary = entry.find("atom:summary", NS)
        e["summary"] = " ".join(summary.text.split()) if summary is not None and summary.text else ""
        # primary category
        pc = entry.find("arxiv:primary_category", NS)
        if pc is not None:
            e["primary_category"] = pc.get("term", "")
        cats = [c.get("term", "") for c in entry.findall("atom:category", NS)]
        e["categories"] = cats
        # journal ref / comments
        comment = entry.find("arxiv:comment", NS)
        e["comment"] = comment.text.strip() if comment is not None and comment.text else ""
        journal = entry.find("arxiv:journal_ref", NS)
        e["journal_ref"] = journal.text.strip() if journal is not None and journal.text else ""
        doi = entry.find("arxiv:doi", NS)
        e["doi"] = doi.text.strip() if doi is not None and doi.text else ""
        # PDF link
        pdf_url = ""
        for link in entry.findall("atom:link", NS):
            if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                pdf_url = link.get("href", "")
                break
        e["pdf_url"] = pdf_url or f"https://arxiv.org/pdf/{e['arxiv_id']}"
        entries.append(e)
    return {"entries": entries, "total": total, "xml_len": len(xml_text)}


def main():
    out_dir = "/home/dupengair/shared/work/superpod/research/tmp/superpod_search"
    os.makedirs(out_dir, exist_ok=True)
    all_results = {}
    query_log = []
    for name, qstr in QUERIES.items():
        print(f"[{name}] querying: {qstr[:80]}...", file=sys.stderr)
        res = fetch(qstr, max_results=60)
        if "error" in res:
            print(f"  ERROR: {res['error']}", file=sys.stderr)
            query_log.append({"query": name, "qstr": qstr, "error": res["error"]})
            all_results[name] = {"entries": [], "total": 0, "error": res["error"]}
            time.sleep(3)
            continue
        entries = res.get("entries", [])
        total = res.get("total", 0)
        print(f"  -> {len(entries)} entries (total {total})", file=sys.stderr)
        all_results[name] = {"entries": entries, "total": total, "qstr": qstr}
        query_log.append({"query": name, "qstr": qstr, "returned": len(entries), "total": total})
        time.sleep(3)  # arXiv 速率限制
    with open(os.path.join(out_dir, "arxiv_raw.json"), "w", encoding="utf-8") as f:
        json.dump({"results": all_results, "query_log": query_log}, f, ensure_ascii=False, indent=2)
    print("done. wrote arxiv_raw.json", file=sys.stderr)


if __name__ == "__main__":
    main()
