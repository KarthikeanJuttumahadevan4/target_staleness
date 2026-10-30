#!/usr/bin/env python3
"""Generate knowledge graph from mock extractions for testing."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent.parent
EXTRACTIONS_DIR = ROOT / "artifacts" / "tests" / "extractions"
OUT_DIR = ROOT / "artifacts" / "graph_test"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Reuse build_graph logic with different source dir
sys.path.append(str(ROOT / "artifacts"))
# Simple inline version to avoid import issues
import networkx as nx
from collections import defaultdict
from datetime import datetime, timezone

def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def load_extractions():
    index_path = EXTRACTIONS_DIR / "index.json"
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    items = []
    for p in EXTRACTIONS_DIR.glob("*.json"):
        if p.name == "index.json":
            continue
        with open(p) as f:
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

data = load_extractions()
G = nx.DiGraph()
vendor_counts = defaultdict(int)
month_counts = defaultdict(int)

for rec in data:
    file_name = rec.get("file_name", "unknown")
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
    G.add_node(f"file:{file_name}", type="File", name=file_name, path=rec.get("file_path",""), suffix=suffix, mtime=str(mtime) if mtime else "")

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

with open(OUT_DIR / "graph.json", "w") as f:
    json.dump(graph_json, f, indent=2)

print(f"Graph written to {OUT_DIR}")
print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
print("Vendors:", dict(vendor_counts))
print("Months:", dict(month_counts))
