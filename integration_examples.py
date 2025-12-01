"""
Integration Guide: Adding Hybrid Algorithms to Existing Benchmarking

This script shows how to integrate the new hybrid algorithms into
the existing benchmarking framework.
"""

# Example 1: Update run_experiments.py to include hybrid algorithms

def get_updated_algorithms():
    """
    Updated algorithm dictionary including all hybrid algorithms.
    Add this to your benchmarking/run_experiments.py
    """
    
    # Import existing algorithms
    from src.algorithms.welshpowell import welsh_powell
    from src.algorithms.dsatur import dsatur
    from src.algorithms.simulated_annealing import simulated_annealing
    from src.algorithms.dynamic_programming import find_chromatic_number
    
    # Import new hybrid algorithms
    from src.algorithms.hybrid_dsatur_sa import hybrid_dsatur_sa
    from src.algorithms.hybrid_wp_sa import hybrid_wp_sa
    from src.algorithms.hybrid_tabu import hybrid_tabu
    from src.algorithms.adaptive_hybrid import adaptive_hybrid
    
    algorithms = {
        # Base algorithms
        'Welsh-Powell': lambda G: welsh_powell(G),
        'DSatur': lambda G: dsatur(G),
        'Simulated Annealing': lambda G: simulated_annealing(G, initial_num_colors=len(G))[:2],
        
        # Hybrid algorithms (extract coloring and num_colors from tuple)
        'Hybrid DSatur+SA': lambda G: hybrid_dsatur_sa(G, seed=42)[:2],
        'Hybrid WP+SA': lambda G: hybrid_wp_sa(G, seed=42)[:2],
        'Hybrid Tabu': lambda G: hybrid_tabu(G, seed=42)[:2],
        'Adaptive Hybrid': lambda G: adaptive_hybrid(G, seed=42)[:2],
    }
    
    return algorithms


# Example 2: Benchmark with detailed statistics

def benchmark_with_stats(G, graph_name="Test Graph"):
    """
    Run all algorithms and collect detailed statistics.
    """
    from src.algorithms import (
        hybrid_dsatur_sa, hybrid_wp_sa, hybrid_tabu, adaptive_hybrid
    )
    import time
    
    results = []
    
    algorithms = [
        ('Hybrid DSatur+SA', hybrid_dsatur_sa),
        ('Hybrid WP+SA', hybrid_wp_sa),
        ('Hybrid Tabu', hybrid_tabu),
        ('Adaptive Hybrid', adaptive_hybrid),
    ]
    
    for name, algo_func in algorithms:
        start_time = time.time()
        coloring, num_colors, stats = algo_func(G, seed=42)
        elapsed = time.time() - start_time
        
        result = {
            'algorithm': name,
            'graph': graph_name,
            'num_colors': num_colors,
            'time': elapsed,
            'stats': stats
        }
        results.append(result)
        
        print(f"{name:25} {num_colors:3} colors in {elapsed:.4f}s")
    
    return results


# Example 3: Compare hybrid vs base algorithms

def compare_hybrid_improvement():
    """
    Compare hybrid algorithms against their base algorithms.
    """
    import networkx as nx
    from src.algorithms import (
        dsatur, welsh_powell,
        hybrid_dsatur_sa, hybrid_wp_sa
    )
    
    # Test on various graphs
    test_graphs = [
        ("Petersen", nx.petersen_graph()),
        ("Karate Club", nx.karate_club_graph()),
        ("Random Dense", nx.erdos_renyi_graph(50, 0.5, seed=42)),
        ("Random Sparse", nx.erdos_renyi_graph(50, 0.1, seed=42)),
    ]
    
    print("\nHybrid vs Base Algorithm Comparison")
    print("=" * 80)
    
    for graph_name, G in test_graphs:
        print(f"\n{graph_name} (n={G.number_of_nodes()}, m={G.number_of_edges()}):")
        print("-" * 80)
        
        # Base DSatur
        _, dsatur_colors = dsatur(G)
        print(f"  DSatur (base):        {dsatur_colors} colors")
        
        # Hybrid DSatur+SA
        _, hybrid_ds_colors, stats_ds = hybrid_dsatur_sa(G, seed=42)
        improvement_ds = dsatur_colors - hybrid_ds_colors
        print(f"  Hybrid DSatur+SA:     {hybrid_ds_colors} colors (saved {improvement_ds})")
        
        # Base Welsh-Powell
        _, wp_colors = welsh_powell(G)
        print(f"  Welsh-Powell (base):  {wp_colors} colors")
        
        # Hybrid WP+SA
        _, hybrid_wp_colors, stats_wp = hybrid_wp_sa(G, seed=42)
        improvement_wp = wp_colors - hybrid_wp_colors
        print(f"  Hybrid WP+SA:         {hybrid_wp_colors} colors (saved {improvement_wp})")


# Example 4: Add to metrics analysis

def compute_hybrid_metrics(G, coloring, num_colors, stats):
    """
    Compute additional metrics for hybrid algorithms.
    Can be added to your metrics.py
    """
    metrics = {
        'num_colors': num_colors,
        'vertices': G.number_of_nodes(),
        'edges': G.number_of_edges(),
    }
    
    # Add hybrid-specific metrics
    if 'reduction' in stats:
        metrics['color_reduction'] = stats['reduction']
        metrics['reduction_percent'] = (stats['reduction'] / stats.get('dsatur_colors', stats.get('wp_colors', stats.get('initial_colors', 1)))) * 100
    
    if 'sa_iterations' in stats:
        metrics['sa_iterations'] = stats['sa_iterations']
        metrics['sa_runs'] = stats.get('total_sa_runs', 0)
    
    if 'tabu_iterations' in stats:
        metrics['tabu_iterations'] = stats['tabu_iterations']
    
    if 'selected_algorithm' in stats:
        metrics['selected_algorithm'] = stats['selected_algorithm']
        metrics['graph_size_category'] = stats['graph_characteristics']['size_category']
        metrics['graph_density'] = stats['graph_characteristics']['density']
    
    return metrics


# Example 5: Performance profiling

def profile_algorithms(G, graph_name="Test", runs=5):
    """
    Profile algorithm performance over multiple runs.
    """
    import time
    import statistics
    from src.algorithms import (
        hybrid_dsatur_sa, hybrid_wp_sa, hybrid_tabu, adaptive_hybrid
    )
    
    algorithms = {
        'DSatur+SA': hybrid_dsatur_sa,
        'WP+SA': hybrid_wp_sa,
        'Tabu': hybrid_tabu,
        'Adaptive': adaptive_hybrid,
    }
    
    print(f"\nProfiling on {graph_name} (n={G.number_of_nodes()}, m={G.number_of_edges()})")
    print("=" * 80)
    print(f"{'Algorithm':<15} {'Avg Colors':<12} {'Min':<5} {'Max':<5} {'Avg Time (s)':<15}")
    print("-" * 80)
    
    for name, algo_func in algorithms.items():
        colors_list = []
        times_list = []
        
        for run in range(runs):
            start = time.time()
            _, num_colors, _ = algo_func(G, seed=42 + run)
            elapsed = time.time() - start
            
            colors_list.append(num_colors)
            times_list.append(elapsed)
        
        avg_colors = statistics.mean(colors_list)
        min_colors = min(colors_list)
        max_colors = max(colors_list)
        avg_time = statistics.mean(times_list)
        
        print(f"{name:<15} {avg_colors:>6.1f}       {min_colors:>3}   {max_colors:>3}   {avg_time:>8.4f}")


# Example 6: Generate comparison table for report

def generate_comparison_table():
    """
    Generate a formatted comparison table for final report.
    """
    import networkx as nx
    from src.algorithms import (
        welsh_powell, dsatur,
        hybrid_dsatur_sa, hybrid_wp_sa, hybrid_tabu, adaptive_hybrid
    )
    
    graphs = [
        ("K5", nx.complete_graph(5)),
        ("C10", nx.cycle_graph(10)),
        ("Petersen", nx.petersen_graph()),
        ("Karate", nx.karate_club_graph()),
    ]
    
    print("\n" + "=" * 100)
    print("ALGORITHM COMPARISON TABLE")
    print("=" * 100)
    print(f"{'Graph':<12} {'WP':<5} {'DSatur':<7} {'H-DS+SA':<9} {'H-WP+SA':<9} {'H-Tabu':<8} {'Adaptive':<9}")
    print("-" * 100)
    
    for graph_name, G in graphs:
        _, wp_c = welsh_powell(G)
        _, ds_c = dsatur(G)
        _, hds_c, _ = hybrid_dsatur_sa(G, seed=42)
        _, hwp_c, _ = hybrid_wp_sa(G, seed=42)
        _, ht_c, _ = hybrid_tabu(G, seed=42)
        _, ad_c, _ = adaptive_hybrid(G, seed=42)
        
        print(f"{graph_name:<12} {wp_c:<5} {ds_c:<7} {hds_c:<9} {hwp_c:<9} {ht_c:<8} {ad_c:<9}")
    
    print("=" * 100)


# Example 7: Export results to CSV

def export_hybrid_results_csv(results, filename='hybrid_results.csv'):
    """
    Export benchmark results to CSV for analysis.
    """
    import csv
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'graph', 'algorithm', 'num_colors', 'time', 
            'reduction', 'iterations', 'selected_algo'
        ])
        writer.writeheader()
        
        for result in results:
            row = {
                'graph': result['graph'],
                'algorithm': result['algorithm'],
                'num_colors': result['num_colors'],
                'time': result['time'],
                'reduction': result['stats'].get('reduction', 0),
                'iterations': result['stats'].get('sa_iterations', 
                              result['stats'].get('tabu_iterations', 0)),
                'selected_algo': result['stats'].get('selected_algorithm', 'N/A')
            }
            writer.writerow(row)
    
    print(f"Results exported to {filename}")


# Example 8: Usage in main benchmarking script

if __name__ == '__main__':
    import networkx as nx
    
    print("HYBRID ALGORITHMS INTEGRATION EXAMPLES")
    print("=" * 80)
    
    # Create test graph
    G = nx.karate_club_graph()
    
    # Example 1: Simple benchmark
    print("\n1. Simple Benchmark:")
    benchmark_with_stats(G, "Karate Club")
    
    # Example 2: Compare improvements
    print("\n2. Hybrid vs Base Comparison:")
    compare_hybrid_improvement()
    
    # Example 3: Profile performance
    print("\n3. Performance Profiling:")
    profile_algorithms(G, "Karate Club", runs=3)
    
    # Example 4: Generate comparison table
    print("\n4. Comparison Table:")
    generate_comparison_table()
    
    print("\n" + "=" * 80)
    print("Integration examples completed!")
    print("Copy relevant functions to your benchmarking scripts.")
    print("=" * 80)
