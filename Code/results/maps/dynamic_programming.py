#!/usr/bin/env python3
"""
DP Map Visualization
=====================
Exact (dynamic programming/backtracking) graph coloring applied to geographic regions.
Falls back to Welsh–Powell greedy heuristic for larger maps.

Usage examples:
  python dp_map_visualization.py world --limit 15 --output world_dp.png
  python dp_map_visualization.py sample --sample 20 --output sample_wp.png
  python dp_map_visualization.py india --output india_dp.png   (if India states dataset available)

Flags:
  --limit N      Max nodes for DP attempt (default 18)
  --sample N     Random sample size of countries (world mode only)
  --output FILE  Output image filename (default auto timestamp)
  --no-show      Do not display interactive window
  --json FILE    Save JSON summary

Dependencies: geopandas, networkx, matplotlib, shapely
Install (Linux): pip install geopandas networkx matplotlib shapely
"""
import os
import sys
import json
import time
import random
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import networkx as nx
import matplotlib.pyplot as plt

try:
    import geopandas as gpd
except ImportError:
    print("Error: geopandas not installed. Run: pip install geopandas shapely fiona pyproj")
    sys.exit(1)

# ------------------------------------------------------------
# Adjacency Graph Builder (robust boundary-touch detection)
# ------------------------------------------------------------

def build_region_graph(gdf: 'gpd.GeoDataFrame') -> nx.Graph:
    """Construct adjacency graph where edges indicate shared boundary.
    Uses spatial index for speed and handles geometry robustness.
    """
    gdf = gdf.reset_index(drop=True)
    gdf['geometry'] = gdf['geometry'].buffer(0)
    sindex = gdf.sindex
    G = nx.Graph()
    name_col = 'NAME' if 'NAME' in gdf.columns else ('admin' if 'admin' in gdf.columns else None)
    for idx, row in gdf.iterrows():
        region_name = row.get(name_col, str(idx)) if name_col else str(idx)
        G.add_node(idx, name=region_name)

    for idx, geom in enumerate(gdf.geometry):
        # Candidate neighbors via bbox intersection
        for j in sindex.intersection(geom.bounds):
            if j <= idx:
                continue
            other = gdf.geometry.iloc[j]
            try:
                touches = geom.touches(other)
                intersects = geom.intersects(other) and geom.boundary.intersection(other.boundary).length > 0
                adjacent = touches or intersects
            except Exception:
                adjacent = geom.intersects(other)
            if adjacent:
                G.add_edge(idx, j)
    return G

# ------------------------------------------------------------
# DP Coloring (importing optimized from dynamic_programming_graph_coloring if available)
# ------------------------------------------------------------

def is_valid_color(G: nx.Graph, node, color: int, coloring: Dict) -> bool:
    for neighbor in G.neighbors(node):
        if neighbor in coloring and coloring[neighbor] == color:
            return False
    return True

def backtrack_coloring(G: nx.Graph, nodes: List, index: int, k: int, coloring: Dict) -> bool:
    if index == len(nodes):
        return True
    node = nodes[index]
    for color in range(k):
        if is_valid_color(G, node, color, coloring):
            coloring[node] = color
            if backtrack_coloring(G, nodes, index + 1, k, coloring):
                return True
            del coloring[node]
    return False

def dp_chromatic(G: nx.Graph, max_colors: int = 20) -> Tuple[Optional[int], Optional[Dict]]:
    if G.number_of_nodes() == 0:
        return 0, {}
    nodes = sorted(G.nodes(), key=lambda v: G.degree[v], reverse=True)
    for k in range(1, min(max_colors, G.number_of_nodes()) + 1):
        coloring = {}
        if backtrack_coloring(G, nodes, 0, k, coloring):
            return k, coloring
    return None, None

# Welsh–Powell fallback

def welsh_powell(G: nx.Graph) -> Tuple[Dict, int]:
    order = sorted(G.nodes(), key=lambda v: G.degree(v), reverse=True)
    color = {v: None for v in G.nodes()}
    current = 0
    for i, v in enumerate(order):
        if color[v] is not None:
            continue
        color[v] = current
        for u in order[i+1:]:
            if color[u] is not None:
                continue
            if all(color.get(nb) != current for nb in G.neighbors(u)):
                color[u] = current
        current += 1
    return color, max(color.values()) + 1 if color else 0

# ------------------------------------------------------------
# Map Loading Helpers
# ------------------------------------------------------------

WORLD_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
INDIA_URL = "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson"  # placeholder/state sample


def load_world(sample: Optional[int] = None, continent: Optional[str] = None) -> 'gpd.GeoDataFrame':
    gdf = gpd.read_file(WORLD_URL)
    # Drop Antarctica by name if present
    if 'NAME' in gdf.columns:
        gdf = gdf[gdf['NAME'] != 'Antarctica'].copy()
    # Optional continent filter (handles different casings of column name)
    if continent:
        cont_col = 'CONTINENT' if 'CONTINENT' in gdf.columns else ('continent' if 'continent' in gdf.columns else None)
        if cont_col:
            gdf = gdf[gdf[cont_col].str.lower() == continent.strip().lower()].copy()
        else:
            print("Warning: continent column not found; ignoring --continent filter")
    gdf = gdf.reset_index(drop=True)
    if sample and sample < len(gdf):
        gdf = gdf.sample(sample, random_state=42).reset_index(drop=True)
    return gdf


def load_india() -> 'gpd.GeoDataFrame':
    # NOTE: Replace URL or local path with full India states dataset for richer map
    gdf = gpd.read_file(INDIA_URL)
    return gdf.reset_index(drop=True)

# ------------------------------------------------------------
# Plotting
# ------------------------------------------------------------

def plot_colored_map(gdf, color_map: Dict[int, int], k: int, title: str, output: Optional[str], show: bool):
    cmap = plt.cm.get_cmap('tab20')
    plot_colors = []
    for idx in gdf.index:
        c = color_map.get(idx)
        if c is None:
            plot_colors.append((0.9,0.9,0.9,1.0))
        else:
            plot_colors.append(cmap((int(c) % cmap.N)/cmap.N))
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    gdf.plot(color=plot_colors, linewidth=0.4, edgecolor='black', ax=ax)
    ax.set_title(f"{title} (k={k})", fontsize=16)
    ax.axis('off')
    plt.tight_layout()
    if output:
        plt.savefig(output, dpi=200)
        print(f"Saved map image: {output}")
    if show:
        plt.show()
    plt.close(fig)

# ------------------------------------------------------------
# Summary / JSON persistence
# ------------------------------------------------------------

def save_summary(json_path: str, meta: Dict):
    with open(json_path, 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"Saved JSON summary: {json_path}")

# ------------------------------------------------------------
# Main workflow
# ------------------------------------------------------------

def run_mode(mode: str, args):
    if mode == 'world':
        gdf = load_world(sample=args.sample, continent=args.continent)
        base = f"World"
        if args.continent:
            base += f" - {args.continent.title()}"
        label = f"{base} subset" if args.sample else base
    elif mode == 'sample':
        gdf = load_world(sample=args.sample or 20, continent=args.continent)
        base = f"World sample ({len(gdf)})"
        if args.continent:
            base += f" - {args.continent.title()}"
        label = base
    elif mode == 'india':
        try:
            gdf = load_india()
            label = f"India regions"
        except Exception as e:
            print(f"Failed loading India dataset: {e}")
            return
    else:
        print(f"Unknown mode: {mode}")
        return

    print(f"Loaded {label}: {len(gdf)} regions")
    print("Building adjacency graph...")
    G = build_region_graph(gdf)
    print(f"Graph: nodes={G.number_of_nodes()}, edges={G.number_of_edges()}")

    start = time.perf_counter()
    use_dp = G.number_of_nodes() <= args.limit
    if use_dp:
        print(f"Attempting exact DP coloring (limit {args.limit})...")
        k, coloring = dp_chromatic(G, max_colors=G.number_of_nodes())
        algo = 'dp'
        if k is None:
            print("DP failed within limits; falling back to Welsh–Powell")
            coloring, k = welsh_powell(G)
            algo = 'welsh_powell_fallback'
    else:
        print(f"Map too large for DP (>{args.limit}); using Welsh–Powell heuristic")
        coloring, k = welsh_powell(G)
        algo = 'welsh_powell'
    elapsed = time.perf_counter() - start

    print(f"Coloring complete: k={k}, algorithm={algo}, time={elapsed:.4f}s")

    # Output file naming
    if not args.output:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        cont_tag = (args.continent or 'global').replace(' ', '_').lower()
        args.output = f"map_{mode}_{cont_tag}_{algo}_{len(gdf)}_{ts}.png"

    plot_colored_map(gdf, coloring, k, f"{label} colored", args.output, not args.no_show)

    summary = {
        'mode': mode,
        'regions': len(gdf),
        'edges': G.number_of_edges(),
        'chromatic_number': k,
        'algorithm': algo,
        'time_seconds': elapsed,
        'limit': args.limit,
    }
    if args.json:
        save_summary(args.json, summary)

# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def parse_args(argv):
    p = argparse.ArgumentParser(description="Map graph coloring visualization (DP + fallback)")
    p.add_argument('mode', choices=['world','sample','india'], help='Dataset/mode to run')
    p.add_argument('--limit', type=int, default=18, help='Max node count for DP attempt')
    p.add_argument('--sample', type=int, default=None, help='Sample size for world/subset')
    p.add_argument('--continent', type=str, default=None, help='Filter world by continent (e.g., "South America")')
    p.add_argument('--output', type=str, default=None, help='Output image filename')
    p.add_argument('--json', type=str, default=None, help='Optional JSON summary output path')
    p.add_argument('--no-show', action='store_true', help='Do not display interactive window')
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    run_mode(args.mode, args)

if __name__ == '__main__':
    main()