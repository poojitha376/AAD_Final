# visualise_sa.py
# Simulated Annealing on world map coloring
# Requires geopandas, networkx, matplotlib, shapely, numpy

import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import math
from shapely.geometry import Polygon, MultiPolygon
from matplotlib.animation import FuncAnimation

# ---------- 1. Load world map ----------
url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
gdf = gpd.read_file(url)
if 'NAME' in gdf.columns:
    gdf = gdf[gdf['NAME'] != 'Antarctica'].copy()
gdf = gdf.reset_index(drop=True)
gdf['geometry'] = gdf['geometry'].buffer(0)

# ---------- 2. Build adjacency graph ----------
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

# ---------- 3. Initialize coloring ----------
num_colors = 5  # fixed palette for simplicity
color = {v: random.randint(0, num_colors - 1) for v in G.nodes()}

def conflict_count(G, color):
    conflicts = 0
    for u, v in G.edges():
        if color[u] == color[v]:
            conflicts += 1
    return conflicts

# ---------- 4. Simulated Annealing core ----------
def simulated_annealing(G, color, num_colors, T0=5.0, alpha=0.995, steps=10000):
    T = T0
    current_color = color.copy()
    current_conflicts = conflict_count(G, current_color)
    best_color = current_color.copy()
    best_conflicts = current_conflicts

    history = [current_conflicts]
    snapshots = []

    for step in range(steps):
        # random change: recolor one node
        node = random.choice(list(G.nodes()))
        old_color = current_color[node]
        new_color = random.choice([c for c in range(num_colors) if c != old_color])
        current_color[node] = new_color

        new_conflicts = conflict_count(G, current_color)
        delta = new_conflicts - current_conflicts

        if delta < 0 or random.random() < math.exp(-delta / T):
            current_conflicts = new_conflicts
            if new_conflicts < best_conflicts:
                best_conflicts = new_conflicts
                best_color = current_color.copy()
        else:
            # revert
            current_color[node] = old_color

        T *= alpha
        history.append(current_conflicts)

        # Save snapshot occasionally for animation
        if step % 200 == 0:
            snapshots.append((step, current_color.copy()))

        if best_conflicts == 0:
            break

    return best_color, best_conflicts, history, snapshots

print("Running Simulated Annealing...")
best_color, best_conflicts, history, snapshots = simulated_annealing(G, color, num_colors)
print(f"Final conflicts: {best_conflicts}")

# ---------- 5. Visualization ----------

# Prepare color mapping for plot
cmap = plt.colormaps.get_cmap('tab10')
def plot_map(ax, color_map, title=""):
    gdf['sa_color'] = gdf.index.map(color_map)
    gdf['plot_color'] = [cmap((int(c) % cmap.N)/cmap.N) for c in gdf['sa_color']]
    gdf.plot(color=gdf['plot_color'], linewidth=0.3, edgecolor='black', ax=ax)
    ax.set_title(title, fontsize=14)
    ax.axis('off')

# ---------- 6. Animation ----------
fig, ax = plt.subplots(figsize=(12, 6))

def update(frame_idx):
    step, color_map = snapshots[frame_idx]
    ax.clear()
    plot_map(ax, color_map, f"Simulated Annealing step {step}")

ani = FuncAnimation(fig, update, frames=len(snapshots), interval=700, repeat=False)
plt.show()

# ---------- 7. Plot conflict history ----------
plt.figure(figsize=(8,4))
plt.plot(history, color='purple')
plt.xlabel("Iteration")
plt.ylabel("Conflicts")
plt.title("Simulated Annealing Conflict Reduction")
plt.grid(True)
plt.show()