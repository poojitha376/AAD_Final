"""
Adaptive Hybrid Graph Coloring Algorithm

Author: Algorithm Analysis & Design Team
Description:
    An intelligent meta-algorithm that automatically selects the best
    coloring strategy based on graph characteristics.
    
    Analyzes graph properties (size, density, degree distribution, etc.)
    and chooses the most suitable hybrid approach from:
    - DSatur + SA (for dense graphs, quality-focused)
    - Welsh-Powell + SA (for sparse graphs, speed-focused)
    - Tabu Search (for medium graphs, balanced approach)
    - Pure greedy (for very large graphs where speed is critical)

    Time Complexity: O(analysis + chosen_algorithm)
    Space Complexity: O(V)

Strategy:
    1. Analyze graph properties
    2. Select algorithm based on heuristic rules
    3. Apply selected algorithm with tuned parameters
    4. Optionally try fallback if first choice fails

Reference:
    Adaptive algorithm selection is a key technique in modern combinatorial
    optimization, allowing robust performance across diverse problem instances.
"""

import random
import math
from typing import Dict, Tuple, List, Optional, Any
import networkx as nx


def analyze_graph_characteristics(G: nx.Graph) -> Dict[str, Any]:
    """
    Analyze graph properties to guide algorithm selection.
    
    Args:
        G (nx.Graph): The graph to analyze
    
    Returns:
        Dict[str, Any]: Dictionary of graph characteristics
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()
    
    if n == 0:
        return {
            'num_nodes': 0,
            'num_edges': 0,
            'density': 0,
            'avg_degree': 0,
            'max_degree': 0,
            'size_category': 'empty'
        }
    
    # Basic metrics
    density = (2 * m) / (n * (n - 1)) if n > 1 else 0
    degrees = [d for _, d in G.degree()]
    avg_degree = sum(degrees) / len(degrees) if degrees else 0
    max_degree = max(degrees) if degrees else 0
    
    # Categorize graph size
    if n <= 20:
        size_category = 'tiny'
    elif n <= 50:
        size_category = 'small'
    elif n <= 200:
        size_category = 'medium'
    elif n <= 1000:
        size_category = 'large'
    else:
        size_category = 'very_large'
    
    # Categorize density
    if density < 0.1:
        density_category = 'sparse'
    elif density < 0.3:
        density_category = 'medium'
    else:
        density_category = 'dense'
    
    return {
        'num_nodes': n,
        'num_edges': m,
        'density': density,
        'density_category': density_category,
        'avg_degree': avg_degree,
        'max_degree': max_degree,
        'size_category': size_category
    }


def select_algorithm(characteristics: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Select best algorithm and parameters based on graph characteristics.
    
    Args:
        characteristics (Dict): Graph characteristics from analyze_graph_characteristics
    
    Returns:
        Tuple[str, Dict]: (algorithm_name, parameters)
    """
    size_cat = characteristics['size_category']
    density_cat = characteristics['density_category']
    n = characteristics['num_nodes']
    
    # Decision rules based on empirical performance
    if size_cat == 'tiny':
        # Use exact algorithm for tiny graphs
        return 'dynamic_programming', {}
    
    elif size_cat == 'small':
        if density_cat == 'dense':
            # DSatur + SA works well on small dense graphs
            return 'hybrid_dsatur_sa', {
                'T0': 10.0,
                'alpha': 0.95,
                'max_iterations': 30000,
                'stall_limit': 3000,
                'aggressive': True
            }
        else:
            # Tabu search for small sparse graphs
            return 'hybrid_tabu', {
                'tabu_tenure': 10,
                'max_iterations': 5000,
                'stall_limit': 500,
                'aggressive': True
            }
    
    elif size_cat == 'medium':
        if density_cat == 'dense':
            # DSatur + SA with moderate iterations
            return 'hybrid_dsatur_sa', {
                'T0': 50.0,
                'alpha': 0.96,
                'max_iterations': 50000,
                'stall_limit': 5000,
                'aggressive': True
            }
        elif density_cat == 'sparse':
            # Welsh-Powell + SA for speed
            return 'hybrid_wp_sa', {
                'T0': 50.0,
                'alpha': 0.97,
                'max_iterations': 50000,
                'stall_limit': 5000,
                'aggressive': True
            }
        else:
            # Tabu for balanced cases
            return 'hybrid_tabu', {
                'tabu_tenure': 15,
                'max_iterations': 10000,
                'stall_limit': 1000,
                'aggressive': True
            }
    
    elif size_cat == 'large':
        if density_cat == 'dense':
            # Shorter runs for large dense graphs
            return 'hybrid_dsatur_sa', {
                'T0': 100.0,
                'alpha': 0.98,
                'max_iterations': 100000,
                'stall_limit': 10000,
                'aggressive': False  # Fast mode
            }
        else:
            # WP + light SA for large sparse
            return 'hybrid_wp_sa', {
                'T0': 100.0,
                'alpha': 0.98,
                'max_iterations': 100000,
                'stall_limit': 10000,
                'aggressive': False
            }
    
    else:  # very_large
        # Just use fast greedy for very large graphs
        if density_cat == 'sparse':
            return 'welsh_powell', {}
        else:
            return 'dsatur', {}


def greedy_dsatur(G: nx.Graph) -> Tuple[Dict[int, int], int]:
    """Quick DSatur implementation for fallback."""
    if G is None or len(G) == 0:
        return {}, 0
    
    coloring = {v: None for v in G.nodes()}
    saturation_degree = {v: set() for v in G.nodes()}
    vertex_degrees = dict(G.degree())
    uncolored = set(G.nodes())
    
    if uncolored:
        start_vertex = max(uncolored, key=lambda v: vertex_degrees[v])
        coloring[start_vertex] = 0
        uncolored.remove(start_vertex)
        for neighbor in G.neighbors(start_vertex):
            saturation_degree[neighbor].add(0)
    
    while uncolored:
        next_vertex = max(
            uncolored,
            key=lambda v: (len(saturation_degree[v]), vertex_degrees[v])
        )
        
        neighbor_colors = set()
        for neighbor in G.neighbors(next_vertex):
            if coloring[neighbor] is not None:
                neighbor_colors.add(coloring[neighbor])
        
        color = 0
        while color in neighbor_colors:
            color += 1
        
        coloring[next_vertex] = color
        uncolored.remove(next_vertex)
        
        for neighbor in G.neighbors(next_vertex):
            if coloring[neighbor] is None:
                saturation_degree[neighbor].add(color)
    
    num_colors = max(coloring.values()) + 1 if coloring else 0
    return coloring, num_colors


def greedy_welsh_powell(G: nx.Graph) -> Tuple[Dict[int, int], int]:
    """Quick Welsh-Powell implementation for fallback."""
    if G is None or len(G) == 0:
        return {}, 0
    
    vertices_by_degree = sorted(G.nodes(), key=lambda v: G.degree(v), reverse=True)
    coloring = {}
    
    for vertex in vertices_by_degree:
        neighbor_colors = set()
        for neighbor in G.neighbors(vertex):
            if neighbor in coloring:
                neighbor_colors.add(coloring[neighbor])
        
        color = 0
        while color in neighbor_colors:
            color += 1
        coloring[vertex] = color
    
    num_colors = max(coloring.values()) + 1 if coloring else 0
    return coloring, num_colors


def adaptive_hybrid(
    G: nx.Graph,
    seed: Optional[int] = None,
    verbose: bool = False
) -> Tuple[Dict[int, int], int, Dict]:
    """
    Adaptive hybrid graph coloring algorithm.
    
    Automatically selects and applies the best coloring strategy based on
    graph characteristics.
    
    Algorithm:
    1. Analyze graph properties (size, density, degree distribution)
    2. Select optimal algorithm and parameters
    3. Apply selected algorithm
    4. Return coloring with metadata about selection
    
    Args:
        G (nx.Graph): NetworkX graph object to color
        seed (int, optional): Random seed for reproducibility
        verbose (bool): If True, print algorithm selection info
    
    Returns:
        Tuple[Dict[int, int], int, Dict]:
            - coloring: Final vertex-to-color mapping
            - num_colors: Number of colors used
            - stats: Algorithm statistics including:
                - 'selected_algorithm': Which algorithm was chosen
                - 'graph_characteristics': Analyzed properties
                - 'algorithm_params': Parameters used
                - Additional stats from chosen algorithm
    
    Example:
        >>> G = nx.karate_club_graph()
        >>> coloring, k, stats = adaptive_hybrid(G, verbose=True)
        >>> print(f"Selected: {stats['selected_algorithm']}")
        >>> print(f"Graph size: {stats['graph_characteristics']['size_category']}")
        >>> print(f"Colors used: {k}")
    """
    if G is None or len(G) == 0:
        return {}, 0, {
            'selected_algorithm': 'none',
            'graph_characteristics': {},
            'num_colors': 0
        }
    
    # Phase 1: Analyze graph
    characteristics = analyze_graph_characteristics(G)
    
    # Phase 2: Select algorithm
    algorithm_name, params = select_algorithm(characteristics)
    
    if verbose:
        print(f"Graph Analysis:")
        print(f"  Nodes: {characteristics['num_nodes']}")
        print(f"  Edges: {characteristics['num_edges']}")
        print(f"  Density: {characteristics['density']:.3f} ({characteristics['density_category']})")
        print(f"  Size Category: {characteristics['size_category']}")
        print(f"\nSelected Algorithm: {algorithm_name}")
        if params:
            print(f"Parameters: {params}")
    
    # Phase 3: Execute selected algorithm
    stats = {
        'selected_algorithm': algorithm_name,
        'graph_characteristics': characteristics,
        'algorithm_params': params
    }
    
    try:
        if algorithm_name == 'dynamic_programming':
            # For tiny graphs, use simple greedy (DP is in separate module)
            coloring, num_colors = greedy_dsatur(G)
            stats['method'] = 'greedy_dsatur_fallback'
        
        elif algorithm_name == 'hybrid_dsatur_sa':
            # Import and use DSatur+SA
            from .hybrid_dsatur_sa import hybrid_dsatur_sa
            coloring, num_colors, algo_stats = hybrid_dsatur_sa(G, seed=seed, **params)
            stats.update(algo_stats)
        
        elif algorithm_name == 'hybrid_wp_sa':
            # Import and use WP+SA
            from .hybrid_wp_sa import hybrid_wp_sa
            coloring, num_colors, algo_stats = hybrid_wp_sa(G, seed=seed, **params)
            stats.update(algo_stats)
        
        elif algorithm_name == 'hybrid_tabu':
            # Import and use Tabu Search
            from .hybrid_tabu import hybrid_tabu
            coloring, num_colors, algo_stats = hybrid_tabu(G, seed=seed, **params)
            stats.update(algo_stats)
        
        elif algorithm_name == 'dsatur':
            coloring, num_colors = greedy_dsatur(G)
            stats['method'] = 'pure_dsatur'
        
        elif algorithm_name == 'welsh_powell':
            coloring, num_colors = greedy_welsh_powell(G)
            stats['method'] = 'pure_welsh_powell'
        
        else:
            # Fallback to DSatur
            coloring, num_colors = greedy_dsatur(G)
            stats['method'] = 'fallback_dsatur'
    
    except Exception as e:
        if verbose:
            print(f"Error in {algorithm_name}: {e}")
            print("Falling back to greedy DSatur")
        
        coloring, num_colors = greedy_dsatur(G)
        stats['method'] = 'error_fallback'
        stats['error'] = str(e)
    
    stats['num_colors'] = num_colors
    
    return coloring, num_colors, stats


def validate_coloring(G: nx.Graph, coloring: Dict[int, int]) -> bool:
    """
    Verify that a coloring is valid (no adjacent vertices share the same color).
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
    
    Returns:
        bool: True if coloring is valid, False otherwise
    """
    for u, v in G.edges():
        if coloring.get(u) == coloring.get(v):
            return False
    return True
