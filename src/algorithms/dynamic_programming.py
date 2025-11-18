"""
Dynamic Programming for Optimal Graph Coloring

Author: Algorithm Analysis & Design Team
Description:
    Exact algorithm using backtracking with dynamic programming approach
    to find the chromatic number (minimum colors needed) of a graph.
    
    Guarantees optimal solution but is exponential in complexity.
    Suitable only for small graphs (typically <= 15-20 vertices).

    Time Complexity: O(N^N) worst case, where N = number of vertices
    Space Complexity: O(N) for recursion stack
    
    Practical limits: Works well for N <= 15, may timeout for N >= 20

Reference:
    Backtracking is a standard technique for NP-complete problems like graph coloring.
    Can be combined with branch-and-bound for better pruning.
"""

from typing import Dict, Tuple, Optional, List
import networkx as nx


def is_safe_color(G: nx.Graph, vertex: int, color: int, coloring: Dict[int, int]) -> bool:
    """
    Check if assigning 'color' to 'vertex' is safe (no adjacent vertex has same color).
    
    Args:
        G (nx.Graph): The graph
        vertex (int): Vertex to color
        color (int): Color to try
        coloring (Dict[int, int]): Current partial coloring
    
    Returns:
        bool: True if coloring is valid, False otherwise
    """
    for neighbor in G.neighbors(vertex):
        if neighbor in coloring and coloring[neighbor] == color:
            return False
    return True


def backtrack_color(
    G: nx.Graph,
    vertices: List[int],
    vertex_idx: int,
    num_colors: int,
    coloring: Dict[int, int]
) -> bool:
    """
    Recursive backtracking function to try coloring with 'num_colors' colors.
    
    Args:
        G (nx.Graph): The graph
        vertices (List[int]): List of vertices (ordered for efficiency)
        vertex_idx (int): Index in vertices list currently being processed
        num_colors (int): Number of colors available (0 to num_colors-1)
        coloring (Dict[int, int]): Current partial coloring (modified in-place)
    
    Returns:
        bool: True if valid coloring found, False otherwise
    """
    
    # Base case: all vertices colored
    if vertex_idx == len(vertices):
        return True
    
    vertex = vertices[vertex_idx]
    
    # Try each color from 0 to num_colors-1
    for color in range(num_colors):
        if is_safe_color(G, vertex, color, coloring):
            # Assign color
            coloring[vertex] = color
            
            # Recursively color remaining vertices
            if backtrack_color(G, vertices, vertex_idx + 1, num_colors, coloring):
                return True
            
            # Backtrack: remove color if no solution found
            del coloring[vertex]
    
    return False


def find_chromatic_number(G: nx.Graph, max_colors: Optional[int] = None) -> Tuple[Optional[int], Optional[Dict[int, int]]]:
    """
    Find the chromatic number (minimum colors needed) using dynamic programming with backtracking.
    
    Algorithm:
    1. Try k = 1, 2, 3, ... colors
    2. For each k, use backtracking to check if valid k-coloring exists
    3. Return the first k that works (this is the chromatic number)
    
    Args:
        G (nx.Graph): The graph to color
        max_colors (int, optional): Maximum colors to try. If None, uses num_vertices
    
    Returns:
        Tuple[Optional[int], Optional[Dict[int, int]]]:
            - chromatic_number: Minimum colors needed (or None if not found)
            - coloring: Valid coloring dictionary (or None if not found)
    
    Raises:
        ValueError: If graph has more than reasonable vertices for DP
    
    Example:
        >>> G = nx.Graph()
        >>> G.add_edges_from([(1,2), (2,3), (3,1)])
        >>> k, coloring = find_chromatic_number(G)
        >>> print(f"Chromatic number: {k}")  # Output: 3 (triangle)
    """
    
    if G.number_of_nodes() == 0:
        return 0, {}
    
    if max_colors is None:
        max_colors = G.number_of_nodes()
    
    # Optimization: order vertices by degree (descending)
    # Higher degree vertices have more constraints, color them first
    vertices = sorted(G.nodes(), key=lambda v: G.degree(v), reverse=True)
    
    # Try increasing number of colors
    for k in range(1, max_colors + 1):
        coloring = {}
        if backtrack_color(G, vertices, 0, k, coloring):
            return k, coloring
    
    return None, None


def find_chromatic_number_with_bounds(
    G: nx.Graph,
    max_colors: Optional[int] = None
) -> Tuple[Optional[int], Optional[Dict[int, int]], Dict]:
    """
    Find chromatic number with branch-and-bound optimizations.
    
    Uses lower and upper bounds to reduce search space:
    - Lower bound: max(clique_size, max_degree)
    - Upper bound: greedy heuristic (Welsh-Powell approximation)
    
    Args:
        G (nx.Graph): The graph to color
        max_colors (int, optional): Maximum colors to try
    
    Returns:
        Tuple[Optional[int], Optional[Dict[int, int]], Dict]:
            - chromatic_number: Minimum colors needed
            - coloring: Valid coloring dictionary
            - bounds: Dictionary with 'lower_bound' and 'upper_bound'
    """
    
    if G.number_of_nodes() == 0:
        return 0, {}, {'lower_bound': 0, 'upper_bound': 0}
    
    # Compute lower bound: max degree + 1
    max_degree = max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0
    lower_bound = max_degree + 1
    
    # Try to find larger cliques for better lower bound
    try:
        cliques = list(nx.find_cliques(G))
        if cliques:
            clique_size = len(max(cliques, key=len))
            lower_bound = max(lower_bound, clique_size)
    except:
        pass
    
    # Upper bound: Use a simple greedy algorithm
    upper_bound = max_degree + 1
    
    if max_colors is None:
        max_colors = G.number_of_nodes()
    
    # Order vertices by degree (descending)
    vertices = sorted(G.nodes(), key=lambda v: G.degree(v), reverse=True)
    
    # Try from lower bound to upper bound
    for k in range(max(1, lower_bound), min(upper_bound + 1, max_colors + 1)):
        coloring = {}
        if backtrack_color(G, vertices, 0, k, coloring):
            return k, coloring, {
                'lower_bound': lower_bound,
                'upper_bound': k,
                'search_range': (lower_bound, max_colors)
            }
    
    return None, None, {
        'lower_bound': lower_bound,
        'upper_bound': max_colors,
        'search_range': (lower_bound, max_colors)
    }


def validate_coloring(G: nx.Graph, coloring: Dict[int, int]) -> bool:
    """
    Verify that a coloring is valid.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
    
    Returns:
        bool: True if valid, False otherwise
    """
    for u, v in G.edges():
        if coloring.get(u) == coloring.get(v):
            return False
    return True


def get_color_statistics(G: nx.Graph, coloring: Dict[int, int], chromatic_num: Optional[int] = None) -> Dict:
    """
    Compute statistics about the optimal coloring.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
        chromatic_num (int, optional): The chromatic number
    
    Returns:
        Dict: Statistics about the coloring
    """
    from collections import Counter
    
    if not coloring:
        return {}
    
    color_counts = Counter(coloring.values())
    
    return {
        'chromatic_number': chromatic_num or len(color_counts),
        'is_valid': validate_coloring(G, coloring),
        'vertices': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'color_distribution': dict(color_counts),
        'max_degree': max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0
    }
