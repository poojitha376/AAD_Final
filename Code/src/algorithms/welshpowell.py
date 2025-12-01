"""
Welsh-Powell Graph Coloring Algorithm

Author: Algorithm Analysis & Design Team
Description:
    Greedy graph coloring algorithm that orders vertices by degree (descending)
    and colors them sequentially, assigning the smallest available color to each vertex.

    Time Complexity: O(V^2 + E)
    Space Complexity: O(V)
    where V = number of vertices, E = number of edges

Reference:
    Welsh, D. J. W., and Powell, M. B. (1967).
    An upper bound for the chromatic number of a graph and its application to timetabling problems.
"""

from typing import Dict, Tuple
import networkx as nx


def welsh_powell(G: nx.Graph) -> Tuple[Dict[int, int], int]:
    """
    Color a graph using the Welsh-Powell greedy algorithm.
    
    Algorithm:
    1. Sort all vertices in decreasing order of degree (highest degree first)
    2. Initialize empty color assignment dictionary
    3. For each uncolored vertex in order:
       - Assign it the smallest color (starting from 0) that is not used 
         by any of its already-colored neighbors
    
    Args:
        G (nx.Graph): NetworkX graph object to color.
    
    Returns:
        Tuple[Dict[int, int], int]:
            - coloring: Dictionary mapping each vertex to its assigned color (0-indexed)
            - num_colors: Total number of colors used (chromatic number or approximation)
    
    Raises:
        ValueError: If graph is None or empty
    
    Example:
        >>> G = nx.Graph()
        >>> G.add_edges_from([(1,2), (2,3), (3,1), (3,4)])
        >>> coloring, k = welsh_powell(G)
        >>> print(f"Colored with {k} colors: {coloring}")
    """
    
    if G is None or len(G) == 0:
        return {}, 0
    
    # Sort vertices by decreasing degree
    vertices_by_degree = sorted(G.nodes(), key=lambda v: G.degree(v), reverse=True)
    
    # Initialize color assignment
    coloring = {}
    
    # Assign colors to each vertex in order
    for vertex in vertices_by_degree:
        # Find colors used by neighbors
        neighbor_colors = set()
        for neighbor in G.neighbors(vertex):
            if neighbor in coloring:
                neighbor_colors.add(coloring[neighbor])
        
        # Find smallest available color (starting from 0)
        color = 0
        while color in neighbor_colors:
            color += 1
        
        coloring[vertex] = color
    
    # Number of colors used
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
        Dict: Statistics including number of colors, balance, validity
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
        'color_balance': max(color_counts.values()) - min(color_counts.values())
    }
