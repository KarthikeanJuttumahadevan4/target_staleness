#!/usr/bin/env python3
"""Visual knowledge graph using NetworkX + Matplotlib, with a tiny PyTorch touch."""
import json
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import torch

ROOT = Path(__file__).parent
GRAPH_PATH = ROOT / "artifacts" / "graph" / "graph.json"

def load_graph():
    with open(GRAPH_PATH) as f:
        data = json.load(f)
    G = nx.DiGraph()
    for n in data["nodes"]:
        G.add_node(n["id"], **{k:v for k,v in n.items() if k!="id"})
    for e in data["edges"]:
        G.add_edge(e["source"], e["target"], **{k:v for k,v in e.items() if k not in ("source","target")})
    return G

def main():
    if not GRAPH_PATH.exists():
        print(f"Graph not found at {GRAPH_PATH}. Run build_graph.py first.")
        return
    G = load_graph()
    # Tiny PyTorch usage: adjacency matrix as torch tensor
    adj = nx.to_scipy_sparse_array(G, format="csr")
    adj_tensor = torch.tensor(adj.toarray(), dtype=torch.float32)
    print(f"Graph adjacency tensor shape: {adj_tensor.shape}, nnz: {int((adj_tensor>0).sum())}")

    # Plot with Matplotlib
    pos = nx.spring_layout(G, seed=42, k=0.5)
    node_colors = []
    for n in G.nodes:
        t = G.nodes[n].get("type","")
        if t=="Invoice": node_colors.append("#6baed6")
        elif t=="Vendor": node_colors.append("#fd8d3c")
        elif t=="File": node_colors.append("#74c476")
        elif t=="Month": node_colors.append("#9e9ac8")
        else: node_colors.append("#cccccc")
    plt.figure(figsize=(12,9))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, alpha=0.9)
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=15, edge_color="#888888", width=1.2)
    labels = {n: G.nodes[n].get("name") or n.split(":")[-1] for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    plt.title("Knowledge Graph Prototype")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
