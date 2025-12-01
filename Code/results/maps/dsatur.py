# world_dsatur_map.py
# Requires: geopandas, networkx, matplotlib, descartes (sometimes), pyproj
# pip install geopandas networkx matplotlib

import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
import random

# ---------- DSatur implementation (from earlier) ----------
def dsatur_from_graphnx(G, tie_break='degree'):
    color = {v: None for v in G.nodes()}
    sat_colors = {v: set() for v in G.nodes()}
    degree = dict(G.degree())

    # start with highest degree vertex
    v0 = max(G.nodes(), key=lambda v: degree[v])
    color[v0] = 0
    for nb in G.neighbors(v0):
        sat_colors[nb].add(0)

    uncolored = set(G.nodes()) - {v0}
    coloring_order = [v0]

    while uncolored:
        def key(u):
            if tie_break == 'degree':
                return (len(sat_colors[u]), degree[u])
            elif tie_break == 'random':
                return (len(sat_colors[u]), random.random())
            else:
                return (len(sat_colors[u]), degree[u])
        u = max(uncolored, key=key)

        used = { color[w] for w in G.neighbors(u) if color[w] is not None }
        c = 0
        while c in used:
            c += 1
        color[u] = c

        for nb in G.neighbors(u):
            if color[nb] is None:
                sat_colors[nb].add(c)

        uncolored.remove(u)
        coloring_order.append(u)

    num_colors = max(color.values()) + 1
    return color, num_colors, coloring_order

# ---------- Load country polygons ----------
# Replace this with your path to a GeoJSON or shapefile of countries
# e.g., naturalearth_lowres provided by geopandas (coarse)
url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
gdf = gpd.read_file(url)

# Optional: remove Antarctica by name
if 'NAME' in gdf.columns:
    gdf = gdf[gdf['NAME'] != 'Antarctica'].copy()

gdf = gdf.reset_index(drop=True)


# Ensure valid geometries & consistent CRS (use an equal-area or plate-carree for plotting)
gdf['geometry'] = gdf['geometry'].buffer(0)  # fix invalids
gdf = gdf.to_crs(epsg=4326)

# If some countries are MultiPolygons (overseas territories cause many parts),
# you might want to split them into separate rows for coloring separate pieces:
gdf = gdf.explode(index_parts=False).reset_index(drop=True)

# ---------- Build adjacency graph ----------
# Use spatial index for speed
sindex = gdf.sindex
G = nx.Graph()

# Add nodes with an identifier (index).  Use ISO code or name if available.
for idx, row in gdf.iterrows():
    node_id = idx  # or row['iso_a3'] if unique
    G.add_node(node_id, name=row.get('name', str(idx)))

# Efficient adjacency: for each polygon, query bounding-box candidates
for idx, geom in enumerate(gdf.geometry):
    possible = list(sindex.intersection(geom.bounds))
    for j in possible:
        if j <= idx:
            continue
        other = gdf.geometry.iloc[j]
        # adjacency test: prefer 'touches' (shared boundary)
        try:
            touches = geom.touches(other)
            # Some boundaries can be represented with tiny overlaps — consider intersects with nonzero length
            intersects = geom.intersects(other) and geom.boundary.intersection(other.boundary).length > 0
            adjacent = touches or intersects
        except Exception:
            adjacent = geom.intersects(other)
        if adjacent:
            G.add_edge(idx, j)

print(f"Built adjacency graph: nodes={G.number_of_nodes()}, edges={G.number_of_edges()}")

# ---------- Run DSatur ----------
coloring, k_used, order = dsatur_from_graphnx(G, tie_break='degree')
print("Colors used:", k_used)

# Map colors back to GeoDataFrame
gdf['dsatur_color'] = gdf.index.map(coloring)
# For plotting, map colors to a colormap (repeat if k_used > palette)
cmap = plt.colormaps.get_cmap('tab20')  # larger palette
gdf['plot_color'] = [cmap((int(c) % cmap.N)/cmap.N) if c is not None else (0.9,0.9,0.9,1.0)
                     for c in gdf['dsatur_color']]

# ---------- Plot static result ----------
fig, ax = plt.subplots(1, 1, figsize=(18, 9))
gdf.plot(color=gdf['plot_color'], linewidth=0.3, edgecolor='black', ax=ax)
ax.set_title(f"World map colored by DSatur (k={k_used})", fontsize=16)
ax.axis('off')

# Optional: annotate with color IDs or country names for a small region
# For example annotate a few countries:
sample = gdf.sample(10, random_state=1)
for idx, row in sample.iterrows():
    x, y = row.geometry.representative_point().x, row.geometry.representative_point().y
    ax.text(x, y, str(int(row['dsatur_color'])), fontsize=7, ha='center')

plt.show()

# ---------- Optional: save to GeoJSON with colors ----------
# gdf.to_file("dsatur_colored_world.geojson", driver="GeoJSON")