"""
Simulated Annealing for Graph Coloring

Author: Algorithm Analysis & Design Team
Description:
    A metaheuristic algorithm that uses probabilistic acceptance of moves
    to escape local optima and find better (possibly optimal) colorings.
    
    Unlike greedy algorithms (Welsh-Powell, D-Satur), SA can improve
    an initial coloring by strategically recoloring vertices.

    Time Complexity: O(max_iterations * E) where E = number of edges
    Space Complexity: O(V) where V = number of vertices

Reference:
    Kirkpatrick, S., Gelatt Jr, C. D., and Vecchi, M. P. (1983).
    Optimization by simulated annealing.
    Science, 220(4598), 671-680.
"""

import random
import math
from typing import Dict, Tuple, List, Optional
import networkx as nx


def count_conflicts(G: nx.Graph, coloring: Dict[int, int]) -> int:
    """
    Count the number of edges where both endpoints have the same color.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
    
    Returns:
        int: Number of conflicting edges
    """
    conflicts = 0
    for u, v in G.edges():
        if coloring.get(u) == coloring.get(v):
            conflicts += 1
    return conflicts


def get_random_neighbor(G: nx.Graph, coloring: Dict[int, int], 
                       num_colors: int) -> Dict[int, int]:
    """
    Generate a neighbor coloring by recoloring a random vertex.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Current coloring
        num_colors (int): Number of available colors
    
    Returns:
        Dict[int, int]: New coloring (neighbor)
    """
    new_coloring = coloring.copy()
    vertex = random.choice(list(G.nodes()))
    new_color = random.randint(0, num_colors - 1)
    new_coloring[vertex] = new_color
    return new_coloring


def initial_coloring(G: nx.Graph, num_colors: int, seed: Optional[int] = None) -> Dict[int, int]:
    """
    Generate an initial random coloring.
    
    Args:
        G (nx.Graph): The graph
        num_colors (int): Number of colors to use
        seed (int, optional): Random seed for reproducibility
    
    Returns:
        Dict[int, int]: Initial coloring
    """
    if seed is not None:
        random.seed(seed)
    
    coloring = {v: random.randint(0, num_colors - 1) for v in G.nodes()}
    return coloring


def simulated_annealing(
    G: nx.Graph,
    initial_num_colors: int,
    T0: float = 10.0,
    alpha: float = 0.99,
    max_iterations: int = 100000,
    stall_limit: int = 10000,
    seed: Optional[int] = None
) -> Tuple[Dict[int, int], int, List[int], float]:
    """
    Color a graph using Simulated Annealing.
    
    Algorithm:
    1. Start with a random coloring using 'initial_num_colors' colors
    2. Initialize temperature T = T0
    3. While T > epsilon and not stalled:
       a. Generate neighbor by recoloring a random vertex
       b. Calculate change in cost (conflicts)
       c. Accept move if better, or with probability exp(-delta/T)
       d. Cool down: T = T * alpha
    4. Return the best coloring found
    
    Args:
        G (nx.Graph): The graph to color
        initial_num_colors (int): Number of colors in initial coloring
        T0 (float): Initial temperature (default 10.0)
        alpha (float): Cooling rate (0 < alpha < 1, default 0.99)
        max_iterations (int): Maximum iterations (default 100000)
        stall_limit (int): Stop if no improvement for this many iterations
        seed (int, optional): Random seed for reproducibility
    
    Returns:
        Tuple[Dict[int, int], int, List[int], float]:
            - best_coloring: Best coloring found
            - num_colors_used: Number of distinct colors in best coloring
            - conflict_history: Conflicts at each iteration
            - computation_time: Time taken in seconds
    
    Example:
        >>> G = nx.erdos_renyi_graph(20, 0.3, seed=42)
        >>> coloring, k, history, time_s = simulated_annealing(G, initial_num_colors=5)
        >>> print(f"Found coloring with {k} colors and {coloring[-1]} conflicts")
    """
    
    import time
    start_time = time.time()
    
    if seed is not None:
        random.seed(seed)
    
    # Initialize
    current_coloring = initial_coloring(G, initial_num_colors, seed=seed)
    current_conflicts = count_conflicts(G, current_coloring)
    
    best_coloring = current_coloring.copy()
    best_conflicts = current_conflicts
    
    T = T0
    iteration = 0
    stall_count = 0
    conflict_history = [current_conflicts]
    
    # Main SA loop
    while iteration < max_iterations and stall_count < stall_limit:
        # Generate neighbor by recoloring a random vertex
        neighbor_coloring = get_random_neighbor(G, current_coloring, initial_num_colors)
        neighbor_conflicts = count_conflicts(G, neighbor_coloring)
        
        # Acceptance criterion
        delta = neighbor_conflicts - current_conflicts
        
        if delta < 0:  # Better solution
            current_coloring = neighbor_coloring
            current_conflicts = neighbor_conflicts
            stall_count = 0
            
            # Update best if this is better
            if neighbor_conflicts < best_conflicts:
                best_coloring = neighbor_coloring.copy()
                best_conflicts = neighbor_conflicts
        else:
            # Accept worse solution with probability exp(-delta / T)
            acceptance_prob = math.exp(-delta / T) if T > 0 else 0
            if random.random() < acceptance_prob:
                current_coloring = neighbor_coloring
                current_conflicts = neighbor_conflicts
                stall_count = 0
            else:
                stall_count += 1
        
        # Cool down
        T = T0 * (alpha ** (iteration + 1))
        
        conflict_history.append(current_conflicts)
        iteration += 1
    
    end_time = time.time()
    computation_time = end_time - start_time
    
    # Count number of distinct colors in best coloring
    num_colors_used = len(set(best_coloring.values()))
    
    return best_coloring, num_colors_used, conflict_history, computation_time


def validate_coloring(G: nx.Graph, coloring: Dict[int, int]) -> bool:
    """
    Verify if coloring is valid (can improve to valid by reducing conflicts to 0).
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
    
    Returns:
        bool: True if coloring is valid (no conflicts), False otherwise
    """
    return count_conflicts(G, coloring) == 0


def get_color_statistics(G: nx.Graph, coloring: Dict[int, int], conflicts: Optional[int] = None) -> Dict:
    """
    Compute statistics about the coloring.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
        conflicts (int, optional): Pre-computed conflict count
    
    Returns:
        Dict: Statistics about the coloring
    """
    from collections import Counter
    
    if not coloring:
        return {}
    
    if conflicts is None:
        conflicts = count_conflicts(G, coloring)
    
    color_counts = Counter(coloring.values())
    
    return {
        'num_colors': len(color_counts),
        'conflicts': conflicts,
        'is_valid': (conflicts == 0),
        'vertices': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'color_distribution': dict(color_counts),
        'max_degree': max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0
    }
