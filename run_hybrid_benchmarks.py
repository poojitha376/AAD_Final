#!/usr/bin/env python3
"""
Hybrid Algorithms Benchmarking Script

Runs all hybrid algorithms on the same datasets as base algorithms
and generates comprehensive comparison reports.

Author: Algorithm Analysis & Design Team
Date: December 1, 2025
"""

import sys
import os
import time
import csv
import json
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import networkx as nx

# Import base algorithms
from src.algorithms.welshpowell import welsh_powell
from src.algorithms.dsatur import dsatur
from src.algorithms.simulated_annealing import simulated_annealing

# Import hybrid algorithms
from src.algorithms.hybrid_dsatur_sa import hybrid_dsatur_sa, validate_coloring
from src.algorithms.hybrid_wp_sa import hybrid_wp_sa
from src.algorithms.hybrid_tabu import hybrid_tabu
from src.algorithms.adaptive_hybrid import adaptive_hybrid

# Import utilities
from src.utils.graph_generator import (
    generate_erdos_renyi_graph,
    generate_complete_graph,
    generate_cycle_graph,
    generate_petersen_graph
)
from src.utils.graph_loader import load_karate_graph


def benchmark_single_algorithm(algo_name: str, algo_func, G: nx.Graph, seed: int = 42) -> Dict[str, Any]:
    """
    Benchmark a single algorithm on a graph.
    
    Args:
        algo_name: Name of the algorithm
        algo_func: Algorithm function to call
        G: Graph to color
        seed: Random seed for reproducibility
    
    Returns:
        Dictionary with benchmark results
    """
    start_time = time.perf_counter()
    
    try:
        # Call algorithm based on its type
        if algo_name in ['Welsh-Powell', 'DSatur']:
            coloring, num_colors = algo_func(G)
            stats = {}
        elif algo_name == 'Simulated Annealing':
            initial_colors = max(dict(G.degree()).values()) + 1 if G.number_of_nodes() > 0 else 1
            coloring, num_colors, history, sa_time = algo_func(G, initial_colors, seed=seed)
            stats = {}
        else:  # Hybrid algorithms
            coloring, num_colors, stats = algo_func(G, seed=seed)
        
        elapsed_time = time.perf_counter() - start_time
        
        # Validate coloring
        is_valid = validate_coloring(G, coloring)
        
        # Compute improvement metrics for hybrid algorithms
        improvement = 0
        if 'dsatur_colors' in stats:
            improvement = stats['dsatur_colors'] - num_colors
        elif 'wp_colors' in stats:
            improvement = stats['wp_colors'] - num_colors
        elif 'initial_colors' in stats:
            improvement = stats['initial_colors'] - num_colors
        
        return {
            'algorithm': algo_name,
            'success': True,
            'valid': is_valid,
            'colors': num_colors,
            'time_ms': elapsed_time * 1000,
            'improvement': improvement,
            'reduction_pct': (improvement / num_colors * 100) if num_colors > 0 else 0,
            **stats
        }
        
    except Exception as e:
        elapsed_time = time.perf_counter() - start_time
        return {
            'algorithm': algo_name,
            'success': False,
            'error': str(e),
            'time_ms': elapsed_time * 1000,
            'colors': None,
            'valid': False
        }


def print_results_table(results: List[Dict], graph_name: str):
    """Print formatted results table."""
    print(f"\n{graph_name}")
    print("=" * 100)
    print(f"{'Algorithm':<30} {'Colors':<10} {'Time (ms)':<12} {'Valid':<8} {'Improvement':<12} {'Details'}")
    print("-" * 100)
    
    for result in results:
        if result['success']:
            algo = result['algorithm']
            colors = result['colors']
            time_ms = result['time_ms']
            valid = '✓' if result['valid'] else '✗'
            improvement = result.get('improvement', 0)
            
            # Build details string
            details = []
            if 'dsatur_colors' in result:
                details.append(f"DSatur:{result['dsatur_colors']}")
            if 'wp_colors' in result:
                details.append(f"WP:{result['wp_colors']}")
            if 'initial_colors' in result:
                details.append(f"Init:{result['initial_colors']}")
            if 'selected_algorithm' in result:
                details.append(f"Selected:{result['selected_algorithm']}")
            
            details_str = ", ".join(details) if details else ""
            
            print(f"{algo:<30} {colors:<10} {time_ms:>10.3f}   {valid:<8} {improvement:>+4}         {details_str}")
        else:
            print(f"{result['algorithm']:<30} ERROR: {result.get('error', 'Unknown error')}")


def run_hybrid_benchmarks():
    """Run comprehensive benchmarks on all datasets."""
    
    print("\n" + "╔" + "═" * 98 + "╗")
    print("║" + " " * 30 + "HYBRID ALGORITHMS BENCHMARK" + " " * 41 + "║")
    print("╚" + "═" * 98 + "╝")
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Define algorithms to test
    algorithms = [
        ('Welsh-Powell', welsh_powell),
        ('DSatur', dsatur),
        ('Hybrid DSatur+SA', hybrid_dsatur_sa),
        ('Hybrid WP+SA', hybrid_wp_sa),
        ('Hybrid Tabu', hybrid_tabu),
        ('Adaptive Hybrid', adaptive_hybrid),
    ]
    
    all_results = []
    
    # ========================================================================
    # SECTION 1: Small Known Graphs
    # ========================================================================
    print("\n" + "═" * 100)
    print("SECTION 1: SMALL KNOWN GRAPHS")
    print("═" * 100)
    
    test_graphs = {
        'Triangle (K3)': nx.complete_graph(3),
        'Square (C4)': nx.cycle_graph(4),
        'Pentagon (C5)': nx.cycle_graph(5),
        'Hexagon (C6)': nx.cycle_graph(6),
        'Complete K5': nx.complete_graph(5),
        'Petersen Graph': nx.petersen_graph(),
        'Bipartite K(3,3)': nx.complete_bipartite_graph(3, 3),
        'Bipartite K(4,4)': nx.complete_bipartite_graph(4, 4),
        'Karate Club': load_karate_graph(),
    }
    
    for graph_name, G in test_graphs.items():
        results = []
        print(f"\nTesting: {graph_name} (n={G.number_of_nodes()}, m={G.number_of_edges()})")
        
        for algo_name, algo_func in algorithms:
            result = benchmark_single_algorithm(algo_name, algo_func, G)
            result['graph_name'] = graph_name
            result['graph_nodes'] = G.number_of_nodes()
            result['graph_edges'] = G.number_of_edges()
            result['graph_density'] = nx.density(G)
            results.append(result)
            all_results.append(result)
        
        print_results_table(results, f"{graph_name} - Results")
    
    # ========================================================================
    # SECTION 2: Random Graphs - Varying Size
    # ========================================================================
    print("\n\n" + "═" * 100)
    print("SECTION 2: RANDOM GRAPHS - VARYING SIZE")
    print("═" * 100)
    
    sizes = [10, 20, 30, 50, 75, 100]
    p = 0.3
    
    for n in sizes:
        G = generate_erdos_renyi_graph(n, p, seed=42)
        graph_name = f"Random G({n}, {p})"
        
        results = []
        print(f"\nTesting: {graph_name} (m={G.number_of_edges()})")
        
        for algo_name, algo_func in algorithms:
            result = benchmark_single_algorithm(algo_name, algo_func, G)
            result['graph_name'] = graph_name
            result['graph_nodes'] = G.number_of_nodes()
            result['graph_edges'] = G.number_of_edges()
            result['graph_density'] = nx.density(G)
            result['graph_type'] = 'random_size'
            results.append(result)
            all_results.append(result)
        
        print_results_table(results, f"{graph_name} - Results")
    
    # ========================================================================
    # SECTION 3: Random Graphs - Varying Density
    # ========================================================================
    print("\n\n" + "═" * 100)
    print("SECTION 3: RANDOM GRAPHS - VARYING DENSITY (n=30)")
    print("═" * 100)
    
    densities = [0.1, 0.2, 0.3, 0.5, 0.7]
    n = 30
    
    for p in densities:
        G = generate_erdos_renyi_graph(n, p, seed=42)
        graph_name = f"Random G({n}, {p})"
        
        results = []
        print(f"\nTesting: {graph_name} (m={G.number_of_edges()}, density={nx.density(G):.3f})")
        
        for algo_name, algo_func in algorithms:
            result = benchmark_single_algorithm(algo_name, algo_func, G)
            result['graph_name'] = graph_name
            result['graph_nodes'] = G.number_of_nodes()
            result['graph_edges'] = G.number_of_edges()
            result['graph_density'] = nx.density(G)
            result['graph_type'] = 'random_density'
            results.append(result)
            all_results.append(result)
        
        print_results_table(results, f"{graph_name} - Results")
    
    # ========================================================================
    # SECTION 4: Special Graphs
    # ========================================================================
    print("\n\n" + "═" * 100)
    print("SECTION 4: SPECIAL GRAPH STRUCTURES")
    print("═" * 100)
    
    special_graphs = {
        'Path(20)': nx.path_graph(20),
        'Star(20)': nx.star_graph(20),
        'Wheel(20)': nx.wheel_graph(20),
        'Grid(5x5)': nx.grid_2d_graph(5, 5),
        'Grid(7x7)': nx.grid_2d_graph(7, 7),
    }
    
    for graph_name, G in special_graphs.items():
        results = []
        print(f"\nTesting: {graph_name} (n={G.number_of_nodes()}, m={G.number_of_edges()})")
        
        for algo_name, algo_func in algorithms:
            result = benchmark_single_algorithm(algo_name, algo_func, G)
            result['graph_name'] = graph_name
            result['graph_nodes'] = G.number_of_nodes()
            result['graph_edges'] = G.number_of_edges()
            result['graph_density'] = nx.density(G)
            result['graph_type'] = 'special'
            results.append(result)
            all_results.append(result)
        
        print_results_table(results, f"{graph_name} - Results")
    
    # ========================================================================
    # Save Results
    # ========================================================================
    print("\n\n" + "═" * 100)
    print("SAVING RESULTS")
    print("═" * 100)
    
    os.makedirs('results/data', exist_ok=True)
    
    # Save to CSV
    csv_file = 'results/data/hybrid_benchmark_results.csv'
    if all_results:
        # Get all possible keys
        all_keys = set()
        for result in all_results:
            all_keys.update(result.keys())
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"✓ CSV saved to: {csv_file}")
    
    # Save to JSON
    json_file = 'results/data/hybrid_benchmark_results.json'
    with open(json_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"✓ JSON saved to: {json_file}")
    
    # ========================================================================
    # Generate Summary Statistics
    # ========================================================================
    print("\n\n" + "═" * 100)
    print("SUMMARY STATISTICS")
    print("═" * 100)
    
    # Group by algorithm
    algo_stats = {}
    for result in all_results:
        if not result['success']:
            continue
        
        algo = result['algorithm']
        if algo not in algo_stats:
            algo_stats[algo] = {
                'total_runs': 0,
                'total_colors': 0,
                'total_time': 0,
                'total_improvement': 0,
                'valid_count': 0
            }
        
        stats = algo_stats[algo]
        stats['total_runs'] += 1
        stats['total_colors'] += result['colors']
        stats['total_time'] += result['time_ms']
        stats['total_improvement'] += result.get('improvement', 0)
        if result['valid']:
            stats['valid_count'] += 1
    
    print(f"\n{'Algorithm':<30} {'Avg Colors':<12} {'Avg Time (ms)':<15} {'Avg Improvement':<15} {'Success Rate'}")
    print("-" * 100)
    
    for algo in sorted(algo_stats.keys()):
        stats = algo_stats[algo]
        avg_colors = stats['total_colors'] / stats['total_runs']
        avg_time = stats['total_time'] / stats['total_runs']
        avg_improvement = stats['total_improvement'] / stats['total_runs']
        success_rate = stats['valid_count'] / stats['total_runs'] * 100
        
        print(f"{algo:<30} {avg_colors:>10.2f}   {avg_time:>13.3f}   {avg_improvement:>+13.2f}   {success_rate:>5.1f}%")
    
    # ========================================================================
    # Algorithm Comparison
    # ========================================================================
    print("\n\n" + "═" * 100)
    print("HYBRID VS BASE ALGORITHM COMPARISON")
    print("═" * 100)
    
    # Compare hybrid algorithms against their base algorithms
    comparisons = [
        ('DSatur', 'Hybrid DSatur+SA'),
        ('Welsh-Powell', 'Hybrid WP+SA'),
    ]
    
    for base_algo, hybrid_algo in comparisons:
        base_results = [r for r in all_results if r['algorithm'] == base_algo and r['success']]
        hybrid_results = [r for r in all_results if r['algorithm'] == hybrid_algo and r['success']]
        
        if not base_results or not hybrid_results:
            continue
        
        print(f"\n{hybrid_algo} vs {base_algo}:")
        print("-" * 100)
        
        wins = 0
        ties = 0
        losses = 0
        total_improvement = 0
        
        for base, hybrid in zip(base_results, hybrid_results):
            if base['graph_name'] != hybrid['graph_name']:
                continue
            
            if hybrid['colors'] < base['colors']:
                wins += 1
            elif hybrid['colors'] == base['colors']:
                ties += 1
            else:
                losses += 1
            
            total_improvement += (base['colors'] - hybrid['colors'])
        
        total = wins + ties + losses
        if total > 0:
            print(f"  Wins: {wins}/{total} ({wins/total*100:.1f}%)")
            print(f"  Ties: {ties}/{total} ({ties/total*100:.1f}%)")
            print(f"  Losses: {losses}/{total} ({losses/total*100:.1f}%)")
            print(f"  Average color reduction: {total_improvement/total:.2f}")
    
    # ========================================================================
    # Final Summary
    # ========================================================================
    print("\n\n" + "═" * 100)
    print("BENCHMARK COMPLETE")
    print("═" * 100)
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total graphs tested: {len(test_graphs) + len(sizes) + len(densities) + len(special_graphs)}")
    print(f"Total algorithm runs: {len(all_results)}")
    print(f"Results saved to: results/data/")
    print("\n" + "═" * 100)
    
    return all_results


if __name__ == '__main__':
    print("\nHybrid Algorithms Comprehensive Benchmark")
    print("This will test all hybrid algorithms against base algorithms")
    print("on multiple graph types and sizes.\n")
    
    input("Press Enter to start benchmarking...")
    
    results = run_hybrid_benchmarks()
    
    print("\n✅ Benchmarking complete!")
    print("\nResults available in:")
    print("  - results/data/hybrid_benchmark_results.csv")
    print("  - results/data/hybrid_benchmark_results.json")
