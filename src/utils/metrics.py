"""
Advanced Metrics Module

Comprehensive metrics for algorithm analysis and comparison.
Includes performance metrics, quality metrics, and graph property analysis.
"""

from typing import Dict, List, Tuple, Optional
import networkx as nx
from collections import Counter
import math


class ColoringMetrics:
    """Compute comprehensive metrics for graph coloring solutions."""
    
    @staticmethod
    def color_imbalance(coloring: Dict[int, int]) -> float:
        """
        Measure how evenly distributed colors are used.
        
        Color Imbalance = (max_color_freq - min_color_freq) / avg_color_freq
        
        Lower is better (perfectly balanced = 0)
        
        Args:
            coloring: Vertex to color assignment
        
        Returns:
            float: Imbalance score (0 = perfectly balanced)
        
        Example:
            >>> coloring = {1: 0, 2: 0, 3: 1, 4: 1}  # Balanced
            >>> ColoringMetrics.color_imbalance(coloring)
            0.0
        """
        if not coloring:
            return 0.0
        
        color_counts = Counter(coloring.values())
        counts = list(color_counts.values())
        
        if len(counts) <= 1:
            return 0.0
        
        max_count = max(counts)
        min_count = min(counts)
        avg_count = sum(counts) / len(counts)
        
        return (max_count - min_count) / avg_count if avg_count > 0 else 0.0
    
    
    @staticmethod
    def color_utilization(G: nx.Graph, coloring: Dict[int, int]) -> float:
        """
        Percentage of colors actually used vs. available colors.
        
        For algorithms that specify a color palette, shows efficiency.
        
        Args:
            G: The graph
            coloring: Vertex to color assignment
        
        Returns:
            float: Utilization percentage (0-100)
        """
        if not coloring:
            return 0.0
        
        num_colors_used = len(set(coloring.values()))
        num_vertices = G.number_of_nodes()
        
        # Maximum possible colors needed = number of vertices (worst case)
        # Minimum = 1 (best case, empty graph)
        return (num_colors_used / num_vertices) * 100
    
    
    @staticmethod
    def conflict_density(G: nx.Graph, coloring: Dict[int, int]) -> float:
        """
        Percentage of edges that form conflicts (both endpoints same color).
        
        Valid coloring has conflict_density = 0
        
        Args:
            G: The graph
            coloring: Vertex to color assignment
        
        Returns:
            float: Conflict percentage (0-100)
        """
        if G.number_of_edges() == 0:
            return 0.0
        
        conflicts = 0
        for u, v in G.edges():
            if coloring.get(u) == coloring.get(v):
                conflicts += 1
        
        return (conflicts / G.number_of_edges()) * 100
    
    
    @staticmethod
    def color_class_sizes(coloring: Dict[int, int]) -> Dict[int, int]:
        """
        Get size of each color class (independent set).
        
        Args:
            coloring: Vertex to color assignment
        
        Returns:
            Dict: {color: number_of_vertices}
        """
        return dict(Counter(coloring.values()))
    
    
    @staticmethod
    def largest_color_class(coloring: Dict[int, int]) -> int:
        """
        Size of the largest color class (largest independent set in coloring).
        
        Args:
            coloring: Vertex to color assignment
        
        Returns:
            int: Size of largest color class
        """
        if not coloring:
            return 0
        
        color_counts = Counter(coloring.values())
        return max(color_counts.values()) if color_counts else 0
    
    
    @staticmethod
    def color_class_variance(coloring: Dict[int, int]) -> float:
        """
        Statistical variance of color class sizes.
        
        Measures how uneven color distribution is.
        
        Args:
            coloring: Vertex to color assignment
        
        Returns:
            float: Variance of color class sizes
        """
        if not coloring:
            return 0.0
        
        color_counts = Counter(coloring.values())
        counts = list(color_counts.values())
        
        if len(counts) <= 1:
            return 0.0
        
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        
        return variance
    
    
    @staticmethod
    def degree_of_conflict_vertices(G: nx.Graph, coloring: Dict[int, int]) -> Dict:
        """
        Statistics about vertices involved in conflicts.
        
        Args:
            G: The graph
            coloring: Vertex to color assignment
        
        Returns:
            Dict: Statistics about conflicting vertices
        """
        conflict_vertices = set()
        
        for u, v in G.edges():
            if coloring.get(u) == coloring.get(v):
                conflict_vertices.add(u)
                conflict_vertices.add(v)
        
        if not conflict_vertices:
            return {
                'num_conflict_vertices': 0,
                'percent_conflict': 0.0,
                'avg_degree_conflict': 0.0,
                'max_degree_conflict': 0
            }
        
        degrees = [G.degree(v) for v in conflict_vertices]
        
        return {
            'num_conflict_vertices': len(conflict_vertices),
            'percent_conflict': (len(conflict_vertices) / G.number_of_nodes()) * 100,
            'avg_degree_conflict': sum(degrees) / len(degrees) if degrees else 0,
            'max_degree_conflict': max(degrees) if degrees else 0
        }
    
    
    @staticmethod
    def achromatic_power(G: nx.Graph, coloring: Dict[int, int]) -> float:
        """
        Measure of color class independence (how independent each color class is).
        
        Perfect coloring (no conflicts) = maximum achromatic power
        
        Args:
            G: The graph
            coloring: Vertex to color assignment
        
        Returns:
            float: Achromatic power score (0-1, where 1 is perfect)
        """
        conflicts = 0
        for u, v in G.edges():
            if coloring.get(u) == coloring.get(v):
                conflicts += 1
        
        max_possible_conflicts = G.number_of_edges()
        
        if max_possible_conflicts == 0:
            return 1.0
        
        return 1.0 - (conflicts / max_possible_conflicts)
    
    
    @staticmethod
    def chromatic_efficiency(G: nx.Graph, coloring: Dict[int, int], 
                            optimal_chromatic: Optional[int] = None) -> float:
        """
        How close the coloring is to optimal.
        
        If optimal chromatic number is known:
            Efficiency = optimal / used
        
        Otherwise, compare to lower bounds:
            - Clique number
            - Max degree + 1
        
        Args:
            G: The graph
            coloring: Vertex to color assignment
            optimal_chromatic: Known optimal chromatic number (optional)
        
        Returns:
            float: Efficiency ratio (1.0 is optimal)
        """
        num_colors_used = len(set(coloring.values()))
        
        if optimal_chromatic:
            return optimal_chromatic / num_colors_used if num_colors_used > 0 else 0.0
        
        # Use clique number as lower bound
        try:
            cliques = list(nx.find_cliques(G))
            if cliques:
                clique_size = len(max(cliques, key=len))
                return clique_size / num_colors_used if num_colors_used > 0 else 0.0
        except:
            pass
        
        return 1.0
    
    
    @staticmethod
    def color_class_independence(G: nx.Graph, coloring: Dict[int, int]) -> Dict[int, bool]:
        """
        Verify that each color class is an independent set.
        
        Args:
            G: The graph
            coloring: Vertex to color assignment
        
        Returns:
            Dict: {color: is_independent}
        """
        color_classes = {}
        for vertex, color in coloring.items():
            if color not in color_classes:
                color_classes[color] = []
            color_classes[color].append(vertex)
        
        independence = {}
        for color, vertices in color_classes.items():
            # Check if this color class forms an independent set
            is_independent = True
            for i, u in enumerate(vertices):
                for v in vertices[i+1:]:
                    if G.has_edge(u, v):
                        is_independent = False
                        break
                if not is_independent:
                    break
            independence[color] = is_independent
        
        return independence


class GraphMetrics:
    """Metrics about the graph structure itself."""
    
    @staticmethod
    def chromatic_number_lower_bound(G: nx.Graph) -> Tuple[int, str]:
        """
        Compute lower bound on chromatic number.
        
        Uses: max(clique_size, ceil(V / independence_number))
        
        Args:
            G: The graph
        
        Returns:
            Tuple[int, str]: (lower_bound, method_used)
        """
        if G.number_of_nodes() == 0:
            return 0, "empty"
        
        # Method 1: Clique number
        try:
            cliques = list(nx.find_cliques(G))
            if cliques:
                clique_size = len(max(cliques, key=len))
                return clique_size, "clique_number"
        except:
            pass
        
        # Method 2: Max degree + 1
        max_degree = max(dict(G.degree()).values())
        return max_degree + 1, "max_degree_plus_1"
    
    
    @staticmethod
    def chromatic_number_upper_bound(G: nx.Graph) -> Tuple[int, str]:
        """
        Compute upper bound on chromatic number.
        
        Uses: max_degree + 1 (greedy coloring always uses at most this)
        
        Args:
            G: The graph
        
        Returns:
            Tuple[int, str]: (upper_bound, method_used)
        """
        if G.number_of_nodes() == 0:
            return 0, "empty"
        
        max_degree = max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0
        return max_degree + 1, "max_degree_plus_1"
    
    
    @staticmethod
    def fractional_chromatic_number_approximation(G: nx.Graph) -> float:
        """
        Approximate fractional chromatic number using LP relaxation approximation.
        
        Returns a value that is always ≤ chromatic number.
        
        Args:
            G: The graph
        
        Returns:
            float: Fractional chromatic number approximation
        """
        if G.number_of_nodes() == 0:
            return 0.0
        
        # Simple approximation: chi_f(G) >= n / alpha(G)
        # where alpha(G) is independence number
        # We approximate alpha(G) using greedy approach
        
        n = G.number_of_nodes()
        independent_set_size = 1
        
        try:
            # For small graphs, try to find larger independent set
            if n <= 20:
                # Greedy independent set
                remaining = set(G.nodes())
                indep_set = set()
                
                while remaining:
                    v = min(remaining, key=lambda x: len(set(G.neighbors(x)) & remaining))
                    indep_set.add(v)
                    remaining -= {v}
                    remaining -= set(G.neighbors(v))
                
                independent_set_size = len(indep_set)
        except:
            pass
        
        return n / independent_set_size if independent_set_size > 0 else float(n)
    
    
    @staticmethod
    def degeneracy(G: nx.Graph) -> int:
        """
        Compute degeneracy of the graph.
        
        Degeneracy is the smallest k such that every subgraph has a vertex of degree ≤ k.
        
        Coloring algorithms based on degeneracy ordering can use ≤ degeneracy + 1 colors.
        
        Args:
            G: The graph
        
        Returns:
            int: Degeneracy
        """
        if G.number_of_nodes() == 0:
            return 0
        
        # Compute degeneracy by repeatedly removing minimum degree vertex
        G_copy = G.copy()
        max_min_degree = 0
        
        while G_copy.number_of_nodes() > 0:
            min_degree = min(dict(G_copy.degree()).values())
            max_min_degree = max(max_min_degree, min_degree)
            
            # Remove vertex with minimum degree
            min_vertex = min(G_copy.nodes(), key=lambda v: G_copy.degree(v))
            G_copy.remove_node(min_vertex)
        
        return max_min_degree


def compute_all_metrics(G: nx.Graph, coloring: Dict[int, int], 
                       algorithm_name: str = "Unknown",
                       execution_time_ms: float = 0.0,
                       optimal_chromatic: Optional[int] = None) -> Dict:
    """
    Compute comprehensive metrics for a coloring solution.
    
    Args:
        G: The graph
        coloring: Vertex to color assignment
        algorithm_name: Name of algorithm used
        execution_time_ms: Execution time in milliseconds
        optimal_chromatic: Known optimal chromatic number (optional)
    
    Returns:
        Dict: Comprehensive metrics dictionary
    """
    
    num_colors = len(set(coloring.values()))
    conflicts = sum(1 for u, v in G.edges() if coloring.get(u) == coloring.get(v))
    
    return {
        # Basic metrics
        'algorithm': algorithm_name,
        'execution_time_ms': execution_time_ms,
        
        # Solution quality
        'num_colors': num_colors,
        'conflicts': conflicts,
        'is_valid': conflicts == 0,
        'color_imbalance': ColoringMetrics.color_imbalance(coloring),
        'color_utilization_percent': ColoringMetrics.color_utilization(G, coloring),
        'conflict_density_percent': ColoringMetrics.conflict_density(G, coloring),
        'achromatic_power': ColoringMetrics.achromatic_power(G, coloring),
        'chromatic_efficiency': ColoringMetrics.chromatic_efficiency(
            G, coloring, optimal_chromatic
        ),
        'largest_color_class': ColoringMetrics.largest_color_class(coloring),
        'color_class_variance': ColoringMetrics.color_class_variance(coloring),
        
        # Conflict analysis
        'conflict_vertex_stats': ColoringMetrics.degree_of_conflict_vertices(G, coloring),
        
        # Graph properties
        'graph_nodes': G.number_of_nodes(),
        'graph_edges': G.number_of_edges(),
        'graph_density': nx.density(G),
        'max_degree': max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0,
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() 
                      if G.number_of_nodes() > 0 else 0,
        
        # Bounds
        'chromatic_lower_bound': GraphMetrics.chromatic_number_lower_bound(G)[0],
        'chromatic_upper_bound': GraphMetrics.chromatic_number_upper_bound(G)[0],
        'fractional_chromatic_approx': GraphMetrics.fractional_chromatic_number_approximation(G),
        'degeneracy': GraphMetrics.degeneracy(G),
        
        # Color class independence verification
        'color_classes_independent': all(
            ColoringMetrics.color_class_independence(G, coloring).values()
        ),
    }
