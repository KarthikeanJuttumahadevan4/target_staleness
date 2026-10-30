#!/usr/bin/env python3
"""Build a prototype knowledge graph from extractions.

Creates NetworkX graph with nodes: Invoice, Vendor, File, Month
and exports JSON + PyVis HTML for quick visual prototype.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import networkx as nx

ROOT = Path(__file__).parent
EXTRACTIONS_DIR = ROOT / "artifacts" / "extractions"
OUT_DIR = ROOT / "artifacts" / "graph"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            pass
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def load_extractions():
    index_path = EXTRACTIONS_DIR / "index.json"
    if index_path.exists():
        with index_path.open() as f:
            return json.load(f)
    items = []
    for p in EXTRACTIONS_DIR.glob("*.json"):
        if p.name == "index.json":
            continue
        with p.open() as f:
            items.append(json.load(f))
    return items

def normalize_vendor(v):
    if not v:
        return "Unknown Vendor"
    return str(v).strip().title()

def normalize_total(t):
    try:
        return float(str(t).replace(",", ""))
    except Exception:
        return None

def main():
    data = load_extractions()
    G = nx.DiGraph()
    vendor_counts = defaultdict(int)
    month_counts = defaultdict(int)

    for rec in data:
        file_name = rec.get("file_name", "unknown")
        file_path = rec.get("file_path", "")
        suffix = rec.get("suffix", "")
        mtime = parse_date(rec.get("file_mtime"))
        vendor = normalize_vendor(rec.get("vendor"))
        inv_date = parse_date(rec.get("invoice_date"))
        total = normalize_total(rec.get("total"))

        recency = "unknown"
        if mtime:
            age_days = (datetime.now(timezone.utc) - mtime).days
            if age_days <= 7:
                recency = "last_7d"
            elif age_days <= 30:
                recency = "last_30d"
            else:
                recency = "older"

        month_key = None
        if inv_date:
            month_key = inv_date.strftime("%Y-%m")
        elif mtime:
            month_key = mtime.strftime("%Y-%m")

        invoice_id = f"invoice:{file_name}"
        G.add_node(invoice_id, type="Invoice", vendor=vendor, invoice_date=str(inv_date.date() if inv_date else ""), total=total, recency=recency, file=file_name, suffix=suffix)
        G.add_node(f"vendor:{vendor}", type="Vendor", name=vendor)
        G.add_node(f"file:{file_name}", type="File", name=file_name, path=file_path, suffix=suffix, mtime=str(mtime) if mtime else "")

        if month_key:
            G.add_node(f"month:{month_key}", type="Month", name=month_key)
            G.add_edge(invoice_id, f"month:{month_key}", rel="in_month")

        G.add_edge(invoice_id, f"vendor:{vendor}", rel="from_vendor")
        G.add_edge(invoice_id, f"file:{file_name}", rel="stored_in")

        vendor_counts[vendor] += 1
        if month_key:
            month_counts[month_key] += 1

    graph_json = {
        "nodes": [{"id": n, **G.nodes[n]} for n in G.nodes],
        "edges": [{"source": u, "target": v, **G.edges[u,v]} for u,v in G.edges],
        "stats": {
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "vendors": dict(vendor_counts),
            "months": dict(month_counts),
        }
    }
    with (OUT_DIR / "graph.json").open("w", encoding="utf-8") as f:
        json.dump(graph_json, f, ensure_ascii=False, indent=2)

    try:
        from pyvis.network import Network
        net = Network(height="800px", width="100%", directed=True)
        for n, attr in G.nodes(data=True):
            label = attr.get("name") or n
            color = {"Invoice":"#6baed6","Vendor":"#fd8d3c","File":"#74c476","Month":"#9e9ac8"}.get(attr.get("type"), "#ccc")
            net.add_node(n, label=label, title=json.dumps(attr), color=color)
        for u,v,attr in G.edges(data=True):
            net.add_edge(u, v, title=attr.get("rel",""))
        net.save_graph(str(OUT_DIR / "graph.html"))
    except Exception as e:
        print(f"PyVis export skipped: {e}", file=sys.stderr)

    summary = []
    summary.append("# Knowledge Graph Prototype Summary")
    summary.append(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    summary.append("## Vendors")
    for v,c in sorted(vendor_counts.items(), key=lambda x: -x[1]):
        summary.append(f"- {v}: {c}")
    summary.append("## Months")
    for m,c in sorted(month_counts.items()):
        summary.append(f"- {m}: {c}")
    with (OUT_DIR / "summary.md").open("w", encoding="utf-8") as f:
        f.write("\n".join(summary))

    print(f"Graph written to {OUT_DIR}")

if __name__ == "__main__":
    main()
