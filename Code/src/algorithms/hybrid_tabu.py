"""
Tabu Search Graph Coloring Algorithm (Hybrid Approach)

Author: Algorithm Analysis & Design Team
Description:
    Tabu Search is a metaheuristic that uses memory structures to escape
    local optima by maintaining a "tabu list" of recently visited solutions
    or moves that are temporarily forbidden.
    
    This implementation combines greedy initialization with tabu search
    for solution improvement, achieving competitive results on graph coloring.

    Time Complexity: O(max_iterations * E) where E = number of edges
    Space Complexity: O(V + tabu_tenure) where V = number of vertices

Strategy:
    - Start with greedy coloring (DSatur or WP)
    - Iteratively move to best non-tabu neighbor
    - Maintain tabu list to prevent cycling
    - Aspiration criterion: accept tabu moves if they improve best solution

Reference:
    Glover, F., and Laguna, M. (1997).
    Tabu Search. Kluwer Academic Publishers.
    
    Hertz, A., and de Werra, D. (1987).
    Using tabu search techniques for graph coloring.
    Computing, 39(4), 345-351.
"""

import random
from typing import Dict, Tuple, List, Optional, Set, Deque
from collections import deque
import networkx as nx


def greedy_coloring_dsatur(G: nx.Graph) -> Tuple[Dict[int, int], int]:
    """
    Generate initial coloring using DSatur-like greedy approach.
    
    Args:
        G (nx.Graph): NetworkX graph object to color.
    
    Returns:
        Tuple[Dict[int, int], int]:
            - coloring: Dictionary mapping each vertex to its assigned color
            - num_colors: Total number of colors used
    """
    if G is None or len(G) == 0:
        return {}, 0
    
    coloring = {}
    vertices = sorted(G.nodes(), key=lambda v: G.degree(v), reverse=True)
    
    for vertex in vertices:
        neighbor_colors = {coloring.get(n) for n in G.neighbors(vertex) if n in coloring}
        color = 0
        while color in neighbor_colors:
            color += 1
        coloring[vertex] = color
    
    num_colors = max(coloring.values()) + 1 if coloring else 0
    return coloring, num_colors


def count_conflicts(G: nx.Graph, coloring: Dict[int, int]) -> int:
    """
    Count number of edges where both endpoints have the same color.
    
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


def get_conflicting_vertices(G: nx.Graph, coloring: Dict[int, int]) -> List[int]:
    """
    Get list of vertices involved in color conflicts.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
    
    Returns:
        List[int]: List of vertices in conflicts
    """
    conflicting = set()
    for u, v in G.edges():
        if coloring.get(u) == coloring.get(v):
            conflicting.add(u)
            conflicting.add(v)
    return list(conflicting)


def generate_neighborhood(
    G: nx.Graph,
    coloring: Dict[int, int],
    num_colors: int,
    tabu_list: Deque[Tuple[int, int]],
    tabu_tenure: int,
    focus_conflicts: bool = True
) -> List[Tuple[Dict[int, int], Tuple[int, int], int]]:
    """
    Generate neighborhood solutions by changing vertex colors.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Current coloring
        num_colors (int): Number of colors available
        tabu_list (Deque): Recent moves (vertex, color) pairs
        tabu_tenure (int): How long moves stay tabu
        focus_conflicts (bool): Whether to prioritize conflicting vertices
    
    Returns:
        List of tuples: (neighbor_coloring, move, conflicts)
            where move = (vertex, new_color)
    """
    neighbors = []
    
    # Determine which vertices to consider
    if focus_conflicts:
        candidates = get_conflicting_vertices(G, coloring)
        if not candidates:
            candidates = list(G.nodes())
    else:
        candidates = list(G.nodes())
    
    # Limit neighborhood size for efficiency
    if len(candidates) > 50:
        candidates = random.sample(candidates, 50)
    
    for vertex in candidates:
        current_color = coloring[vertex]
        for new_color in range(num_colors):
            if new_color == current_color:
                continue
            
            # Check if move is tabu
            move = (vertex, new_color)
            if move in tabu_list:
                continue
            
            # Generate neighbor
            neighbor_coloring = coloring.copy()
            neighbor_coloring[vertex] = new_color
            neighbor_conflicts = count_conflicts(G, neighbor_coloring)
            
            neighbors.append((neighbor_coloring, move, neighbor_conflicts))
    
    return neighbors


def tabu_search(
    G: nx.Graph,
    initial_coloring: Dict[int, int],
    num_colors: int,
    tabu_tenure: int = 10,
    max_iterations: int = 10000,
    stall_limit: int = 1000,
    seed: Optional[int] = None
) -> Tuple[Dict[int, int], bool, int, Dict]:
    """
    Apply Tabu Search to find valid k-coloring.
    
    Algorithm:
    1. Start from initial solution
    2. While not converged:
       a. Generate non-tabu neighbors (or best tabu if aspiration met)
       b. Move to best neighbor
       c. Add move to tabu list
       d. Update best solution if improved
    3. Return best solution found
    
    Args:
        G (nx.Graph): The graph
        initial_coloring (Dict[int, int]): Starting coloring
        num_colors (int): Target number of colors
        tabu_tenure (int): How long moves stay tabu
        max_iterations (int): Maximum iterations
        stall_limit (int): Stop if no improvement for this many iterations
        seed (int, optional): Random seed
    
    Returns:
        Tuple[Dict[int, int], bool, int, Dict]:
            - best_coloring: Best coloring found
            - is_valid: Whether solution is valid
            - iterations: Number of iterations performed
            - stats: Algorithm statistics
    """
    if seed is not None:
        random.seed(seed)
    
    # Initialize
    current_coloring = {v: c % num_colors for v, c in initial_coloring.items()}
    current_conflicts = count_conflicts(G, current_coloring)
    
    best_coloring = current_coloring.copy()
    best_conflicts = current_conflicts
    
    tabu_list: Deque[Tuple[int, int]] = deque(maxlen=tabu_tenure)
    stall_count = 0
    
    stats = {
        'best_conflicts_history': [current_conflicts],
        'tabu_overrides': 0,
        'neighborhoods_explored': 0
    }
    
    for iteration in range(max_iterations):
        # Early termination
        if current_conflicts == 0:
            stats['iterations'] = iteration
            return current_coloring, True, iteration, stats
        
        # Generate neighborhood
        focus = (iteration % 5 != 0)  # Every 5th iteration, explore broadly
        neighbors = generate_neighborhood(
            G, current_coloring, num_colors, tabu_list, tabu_tenure, focus_conflicts=focus
        )
        
        if not neighbors:
            # No non-tabu neighbors, relax constraint
            tabu_list.clear()
            neighbors = generate_neighborhood(
                G, current_coloring, num_colors, tabu_list, tabu_tenure, focus_conflicts=True
            )
        
        if not neighbors:
            break  # Truly stuck
        
        stats['neighborhoods_explored'] += 1
        
        # Select best neighbor (greedy in neighborhood)
        best_neighbor, best_move, best_neighbor_conflicts = min(
            neighbors, key=lambda x: x[2]
        )
        
        # Aspiration criterion: accept tabu move if it improves global best
        if best_move in tabu_list and best_neighbor_conflicts < best_conflicts:
            stats['tabu_overrides'] += 1
        
        # Make move
        current_coloring = best_neighbor
        current_conflicts = best_neighbor_conflicts
        tabu_list.append(best_move)
        
        # Update best solution
        if current_conflicts < best_conflicts:
            best_coloring = current_coloring.copy()
            best_conflicts = current_conflicts
            stall_count = 0
        else:
            stall_count += 1
        
        stats['best_conflicts_history'].append(best_conflicts)
        
        # Check stall
        if stall_count >= stall_limit:
            break
    
    is_valid = (best_conflicts == 0)
    stats['iterations'] = iteration + 1
    return best_coloring, is_valid, iteration + 1, stats


def hybrid_tabu(
    G: nx.Graph,
    tabu_tenure: int = 15,
    max_iterations: int = 10000,
    stall_limit: int = 1000,
    seed: Optional[int] = None,
    aggressive: bool = True
) -> Tuple[Dict[int, int], int, Dict]:
    """
    Hybrid Tabu Search graph coloring algorithm.
    
    Combines greedy initialization with tabu search optimization.
    
    Algorithm:
    1. Generate initial coloring using greedy DSatur approach
    2. Iteratively reduce colors using tabu search
    3. Return best valid coloring
    
    Args:
        G (nx.Graph): NetworkX graph object to color
        tabu_tenure (int): How long moves stay in tabu list
        max_iterations (int): Max iterations per tabu search run
        stall_limit (int): Stop if no improvement for this many iterations
        seed (int, optional): Random seed for reproducibility
        aggressive (bool): If True, tries to minimize colors
    
    Returns:
        Tuple[Dict[int, int], int, Dict]:
            - coloring: Final vertex-to-color mapping
            - num_colors: Number of colors used
            - stats: Dictionary with algorithm statistics
    
    Example:
        >>> G = nx.petersen_graph()
        >>> coloring, k, stats = hybrid_tabu(G)
        >>> print(f"Colored Petersen graph with {k} colors")
        >>> print(f"Initial: {stats['initial_colors']}, Final: {k}")
    """
    if G is None or len(G) == 0:
        return {}, 0, {'initial_colors': 0, 'final_colors': 0, 'reduction': 0}
    
    # Phase 1: Greedy initialization
    initial_coloring, initial_colors = greedy_coloring_dsatur(G)
    
    stats = {
        'initial_colors': initial_colors,
        'tabu_iterations': 0,
        'total_tabu_runs': 0,
        'detailed_stats': []
    }
    
    if not aggressive:
        stats['final_colors'] = initial_colors
        stats['reduction'] = 0
        return initial_coloring, initial_colors, stats
    
    # Phase 2: Iterative color reduction with tabu search
    best_coloring = initial_coloring
    best_num_colors = initial_colors
    
    for target_colors in range(initial_colors - 1, 0, -1):
        improved_coloring, is_valid, iterations, tabu_stats = tabu_search(
            G, best_coloring, target_colors, tabu_tenure,
            max_iterations, stall_limit, seed
        )
        
        stats['tabu_iterations'] += iterations
        stats['total_tabu_runs'] += 1
        stats['detailed_stats'].append({
            'target_colors': target_colors,
            'success': is_valid,
            'iterations': iterations
        })
        
        if is_valid:
            best_coloring = improved_coloring
            best_num_colors = target_colors
        else:
            # Cannot reduce further
            break
    
    stats['final_colors'] = best_num_colors
    stats['reduction'] = initial_colors - best_num_colors
    
    return best_coloring, best_num_colors, stats


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
