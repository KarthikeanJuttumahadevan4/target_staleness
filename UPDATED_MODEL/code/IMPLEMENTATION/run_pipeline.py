#!/usr/bin/env python3
"""Unified pipeline: batch extract -> build graph -> open interactive visual."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

def main():
    print("Step 1/3: Batch extraction")
    from batch_extract import main as batch_main
    batch_main()
    
    print("\nStep 2/3: Build knowledge graph")
    from build_graph import main as graph_main
    graph_main()
    
    graph_html = ROOT / "artifacts" / "graph" / "graph.html"
    print(f"\nStep 3/3: Visual")
    if graph_html.exists():
        print(f"Interactive graph written to {graph_html}")
        print("Open it in a browser to view the knowledge graph.")
        import platform
        import subprocess
        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", str(graph_html)])
            elif platform.system() == "Windows":
                subprocess.run(["start", str(graph_html)], shell=True)
            else:
                subprocess.run(["xdg-open", str(graph_html)])
        except Exception as e:
            print(f"Could not auto-open browser: {e}")
    else:
        print("Graph HTML not found. PyVis may not be installed.")

if __name__ == "__main__":
    main()
