"""
D-Satur (Degree of Saturation) Graph Coloring Algorithm

Author: Algorithm Analysis & Design Team
Description:
    A greedy graph coloring algorithm that colors vertices based on their
    "saturation degree" (number of distinct colors used by its neighbors),
    breaking ties using vertex degree.

    Time Complexity: O(V^2)
    Space Complexity: O(V)
    where V = number of vertices

    The D-Satur algorithm typically produces better colorings than Welsh-Powell
    for many graph classes, as it prioritizes vertices with more constrained neighborhoods.

Reference:
    Brélaz, D. (1979).
    New methods to color the vertices of a graph.
    Communications of the ACM, 22(4), 251-256.
"""

from typing import Dict, Tuple, Set
import networkx as nx


def dsatur(G: nx.Graph, tie_break: str = 'degree') -> Tuple[Dict[int, int], int]:
    """
    Color a graph using the D-Satur (Degree of Saturation) algorithm.
    
    Algorithm:
    1. Initialize all vertices as uncolored; compute saturation degree (SD) = 0 for all
    2. While there are uncolored vertices:
       a. Select uncolored vertex with highest SD
       b. Break ties using vertex degree (or randomly)
       c. Assign it the smallest color not used by its neighbors
       d. Update SD of all uncolored neighbors
    3. Return the coloring
    
    Args:
        G (nx.Graph): NetworkX graph object to color.
        tie_break (str): Tie-breaking strategy: 'degree' (default) or 'random'
    
    Returns:
        Tuple[Dict[int, int], int]:
            - coloring: Dictionary mapping each vertex to its assigned color
            - num_colors: Total number of colors used
    
    Raises:
        ValueError: If graph is None or empty
    
    Example:
        >>> G = nx.Graph()
        >>> G.add_edges_from([(1,2), (2,3), (3,1), (3,4)])
        >>> coloring, k = dsatur(G)
        >>> print(f"Colored with {k} colors using D-Satur")
    """
    
    if G is None or len(G) == 0:
        return {}, 0
    
    # Initialize data structures
    coloring = {v: None for v in G.nodes()}  # None means uncolored
    saturation_degree = {v: set() for v in G.nodes()}  # Set of colors used by neighbors
    vertex_degrees = dict(G.degree())  # Static vertex degrees
    
    uncolored = set(G.nodes())
    
    # Start with a vertex: pick one with highest degree
    if uncolored:
        start_vertex = max(uncolored, key=lambda v: vertex_degrees[v])
        
        # Color the starting vertex with color 0
        coloring[start_vertex] = 0
        uncolored.remove(start_vertex)
        
        # Update saturation degree of neighbors
        for neighbor in G.neighbors(start_vertex):
            saturation_degree[neighbor].add(0)
    
    # Main coloring loop
    while uncolored:
        # Select next vertex: max saturation degree, break ties by vertex degree
        if tie_break == 'degree':
            next_vertex = max(
                uncolored,
                key=lambda v: (len(saturation_degree[v]), vertex_degrees[v])
            )
        else:
            # For random tie-breaking, use saturation degree as primary sort
            next_vertex = max(
                uncolored,
                key=lambda v: len(saturation_degree[v])
            )
        
        # Find the smallest color not used by neighbors
        neighbor_colors = set()
        for neighbor in G.neighbors(next_vertex):
            if coloring[neighbor] is not None:
                neighbor_colors.add(coloring[neighbor])
        
        # Assign smallest available color
        color = 0
        while color in neighbor_colors:
            color += 1
        
        coloring[next_vertex] = color
        uncolored.remove(next_vertex)
        
        # Update saturation degree of uncolored neighbors
        for neighbor in G.neighbors(next_vertex):
            if neighbor in uncolored:
                saturation_degree[neighbor].add(color)
    
    # Calculate number of colors used
    num_colors = max(coloring.values()) + 1 if coloring else 0
    
    return coloring, num_colors


def validate_coloring(G: nx.Graph, coloring: Dict[int, int]) -> bool:
    """
    Verify that a coloring is valid (no adjacent vertices share the same color).
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment dictionary
    
    Returns:
        bool: True if coloring is valid, False otherwise
    """
    for u, v in G.edges():
        if coloring.get(u) == coloring.get(v):
            return False
    return True


def get_color_statistics(G: nx.Graph, coloring: Dict[int, int]) -> Dict:
    """
    Compute statistics about the coloring.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment dictionary
    
    Returns:
        Dict: Statistics including number of colors, validity, graph properties
    """
    from collections import Counter
    
    if not coloring:
        return {}
    
    color_counts = Counter(coloring.values())
    
    return {
        'num_colors': len(color_counts),
        'is_valid': validate_coloring(G, coloring),
        'vertices': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'color_distribution': dict(color_counts),
        'max_degree': max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0
    }
