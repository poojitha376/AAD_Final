# ============================================
# world_welsh_powell_map.py
# Requires: geopandas, networkx, matplotlib
# ============================================

import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
import random
from shapely.geometry import Polygon, MultiPolygon

# ---------- Load world map ----------
url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
gdf = gpd.read_file(url)
if 'NAME' in gdf.columns:
    gdf = gdf[gdf['NAME'] != 'Antarctica'].copy()
gdf = gdf.reset_index(drop=True)
gdf['geometry'] = gdf['geometry'].buffer(0)

# ---------- Build adjacency graph ----------
sindex = gdf.sindex
G = nx.Graph()

for idx, row in gdf.iterrows():
    G.add_node(idx, name=row.get('NAME', str(idx)))

for idx, geom in enumerate(gdf.geometry):
    possible = list(sindex.intersection(geom.bounds))
    for j in possible:
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

print(f"Built adjacency graph: nodes={G.number_of_nodes()}, edges={G.number_of_edges()}")

# ---------- Welsh–Powell Coloring ----------
def welsh_powell(G):
    # Sort vertices by decreasing degree
    order = sorted(G.nodes(), key=lambda v: G.degree[v], reverse=True)
    color = {}
    current_color = 0

    for v in order:
        if v in color:
            continue
        color[v] = current_color
        for u in order:
            if u not in color:
                # if u not adjacent to any vertex of current color
                if all(color.get(nb) != current_color for nb in G.neighbors(u)):
                    color[u] = current_color
        current_color += 1
    return color, current_color

print("Running Welsh–Powell...")
color_map, k_used = welsh_powell(G)
print(f"Colors used: {k_used}")

# ---------- Plot the result ----------
cmap = plt.colormaps.get_cmap('tab20')
gdf['wp_color'] = gdf.index.map(color_map)
gdf['plot_color'] = [cmap((int(c) % cmap.N)/cmap.N) for c in gdf['wp_color']]

fig, ax = plt.subplots(1, 1, figsize=(18, 9))
gdf.plot(color=gdf['plot_color'], linewidth=0.3, edgecolor='black', ax=ax)
ax.set_title(f"World map colored by Welsh–Powell (k={k_used})", fontsize=16)
ax.axis('off')

# Annotate a few countries for clarity
sample = gdf.sample(10, random_state=1)
for idx, row in sample.iterrows():
    x, y = row.geometry.representative_point().x, row.geometry.representative_point().y
    ax.text(x, y, str(int(row['wp_color'])), fontsize=7, ha='center')

plt.show()