#!/usr/bin/env python3
"""
Run Hybrid Algorithms on Your Actual Datasets

Tests all hybrid algorithms on:
1. DIMACS graphs (queen5_5.col, myciel3.col)
2. Real-world data (karate.edgelist, small.csv)
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

import networkx as nx
from src.algorithms import (
    # Base algorithms
    welsh_powell,
    dsatur,
    simulated_annealing,
    find_chromatic_number,
    find_chromatic_number_with_bounds,
    # Hybrid algorithms
    hybrid_dsatur_sa,
    hybrid_wp_sa,
    hybrid_tabu,
    adaptive_hybrid
)

def load_dimacs_graph(filepath):
    """Load DIMACS format graph (.col file)"""
    G = nx.Graph()
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('p edge'):
                parts = line.split()
                n_vertices = int(parts[2])
                for i in range(1, n_vertices + 1):
                    G.add_node(i)
            elif line.startswith('e'):
                parts = line.split()
                u, v = int(parts[1]), int(parts[2])
                G.add_edge(u, v)
    return G

def load_karate_graph(filepath):
    """Load karate club edgelist"""
    return nx.read_edgelist(filepath, nodetype=int)

def load_exam_scheduling_graph(filepath):
    """Load exam scheduling graph from CSV"""
    import csv
    G = nx.Graph()
    courses = {}
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            course = row['course_id']
            student = row['student_id']
            
            if course not in courses:
                courses[course] = set()
            courses[course].add(student)
    
    # Create edges between courses with common students
    course_list = list(courses.keys())
    for i, c1 in enumerate(course_list):
        G.add_node(c1)
        for c2 in course_list[i+1:]:
            if courses[c1] & courses[c2]:  # Common students
                G.add_edge(c1, c2)
    
    return G

def run_algorithm(name, func, G, seed=42):
    """Run a single algorithm and return results"""
    start = time.perf_counter()
    try:
        # Handle different algorithm return signatures
        if name in ['Welsh-Powell', 'DSatur']:
            coloring, colors = func(G)
            stats = {}
        elif name == 'Simulated Annealing':
            # SA needs initial number of colors - use DSatur's result
            _, initial_colors = dsatur(G)
            coloring, colors, conflict_history, comp_time = func(G, initial_num_colors=initial_colors, seed=seed)
            stats = {'initial_colors': initial_colors, 'final_conflicts': conflict_history[-1] if conflict_history else 0}
        elif name in ['Dynamic Programming', 'Dynamic Programming (Bounded)']:
            # DP returns (chromatic_number, coloring) tuple
            if name == 'Dynamic Programming (Bounded)':
                result_tuple = func(G, upper_bound=10)  # Set reasonable bound
            else:
                result_tuple = func(G)
            
            if result_tuple[0] is not None:
                colors = result_tuple[0]
                coloring = result_tuple[1]
                stats = {'exact_chromatic_number': colors, 'method': 'backtracking'}
            else:
                # Fallback if DP couldn't find solution
                coloring, colors = dsatur(G)
                stats = {'method': 'fallback_dsatur'}
        else:
            # Hybrid algorithms
            coloring, colors, stats = func(G, seed=seed)
        
        elapsed = time.perf_counter() - start
        
        # Validate
        valid = True
        for u, v in G.edges():
            if coloring[u] == coloring[v]:
                valid = False
                break
        
        return {
            'algorithm': name,
            'colors': colors,
            'time': elapsed,
            'valid': valid,
            'stats': stats
        }
    except Exception as e:
        import traceback
        return {
            'algorithm': name,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'time': time.perf_counter() - start
        }

def print_results(dataset_name, G, results):
    """Print formatted results"""
    print(f"\n{'='*100}")
    print(f"DATASET: {dataset_name}")
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}, Density: {nx.density(G):.4f}")
    print(f"{'='*100}")
    print(f"{'Algorithm':<30} {'Colors':<10} {'Time (s)':<12} {'Valid':<8} {'Details'}")
    print(f"{'-'*100}")
    
    for r in results:
        if 'error' in r:
            print(f"{r['algorithm']:<30} {'ERROR':<10} {r['time']:>10.4f}   {'✗':<8} {r['error'][:60]}")
        else:
            details = []
            if 'dsatur_colors' in r['stats']:
                details.append(f"DSatur init:{r['stats']['dsatur_colors']}")
            if 'wp_colors' in r['stats']:
                details.append(f"WP init:{r['stats']['wp_colors']}")
            if 'initial_colors' in r['stats']:
                details.append(f"Init:{r['stats']['initial_colors']}")
            if 'reduction' in r['stats']:
                details.append(f"Saved:{r['stats']['reduction']}")
            if 'selected_algorithm' in r['stats']:
                details.append(f"Selected:{r['stats']['selected_algorithm']}")
            
            valid_mark = '✓' if r['valid'] else '✗'
            print(f"{r['algorithm']:<30} {r['colors']:<10} {r['time']:>10.4f}   {valid_mark:<8} {', '.join(details)}")

def main():
    print("\n╔" + "═"*98 + "╗")
    print("║" + " "*20 + "ALL GRAPH COLORING ALGORITHMS - YOUR DATASETS" + " "*33 + "║")
    print("╚" + "═"*98 + "╝\n")
    
    algorithms = [
        # Base Greedy Algorithms
        ('Welsh-Powell', welsh_powell),
        ('DSatur', dsatur),
        
        # Metaheuristic Algorithms
        ('Simulated Annealing', simulated_annealing),
        
        # Exact Algorithms (for small graphs)
        ('Dynamic Programming', find_chromatic_number),
        # ('Dynamic Programming (Bounded)', find_chromatic_number_with_bounds),  # Skip for speed
        
        # Hybrid Algorithms
        ('Hybrid DSatur+SA', hybrid_dsatur_sa),
        ('Hybrid WP+SA', hybrid_wp_sa),
        ('Hybrid Tabu', hybrid_tabu),
        ('Adaptive Hybrid', adaptive_hybrid),
    ]
    
    all_results = []
    
    # 1. DIMACS Graphs
    print("\n" + "="*100)
    print("SECTION 1: DIMACS BENCHMARK GRAPHS")
    print("="*100)
    
    dimacs_files = [
        ('data/dimacs/myciel3.col', 'Myciel3 (Triangle-free)'),
        ('data/dimacs/queen5_5.col', 'Queen 5 (5-colorable)'),
    ]
    
    for filepath, name in dimacs_files:
        if not os.path.exists(filepath):
            print(f"\n✗ {filepath} not found, skipping...")
            continue
        
        print(f"\nLoading {name}...")
        G = load_dimacs_graph(filepath)
        
        results = []
        for algo_name, algo_func in algorithms:
            result = run_algorithm(algo_name, algo_func, G)
            result['dataset'] = name
            results.append(result)
            all_results.append(result)
        
        print_results(name, G, results)
    
    # 2. Real-world Graphs
    print("\n\n" + "="*100)
    print("SECTION 2: REAL-WORLD GRAPHS")
    print("="*100)
    
    # Karate Club
    karate_path = 'data/real-world/karate.edgelist'
    if os.path.exists(karate_path):
        print(f"\nLoading Karate Club Network...")
        G = load_karate_graph(karate_path)
        
        results = []
        for algo_name, algo_func in algorithms:
            result = run_algorithm(algo_name, algo_func, G)
            result['dataset'] = 'Karate Club'
            results.append(result)
            all_results.append(result)
        
        print_results('Karate Club Network', G, results)
    
    # Exam Scheduling
    exam_path = 'data/real-world/small.csv'
    if os.path.exists(exam_path):
        print(f"\nLoading Exam Scheduling Graph...")
        G = load_exam_scheduling_graph(exam_path)
        
        results = []
        for algo_name, algo_func in algorithms:
            result = run_algorithm(algo_name, algo_func, G)
            result['dataset'] = 'Exam Scheduling'
            results.append(result)
            all_results.append(result)
        
        print_results('Exam Scheduling (Course Conflicts)', G, results)
    
    # Summary
    print("\n\n" + "="*100)
    print("SUMMARY - ALGORITHM COMPARISON")
    print("="*100)
    
    algo_stats = {}
    for r in all_results:
        if 'error' in r:
            continue
        algo = r['algorithm']
        if algo not in algo_stats:
            algo_stats[algo] = {'colors': [], 'times': [], 'datasets': []}
        algo_stats[algo]['colors'].append(r['colors'])
        algo_stats[algo]['times'].append(r['time'])
        algo_stats[algo]['datasets'].append(r['dataset'])
    
    print(f"\n{'Algorithm':<30} {'Avg Colors':<15} {'Avg Time (s)':<15} {'Datasets Tested'}")
    print("-"*100)
    
    # Order by category
    algo_order = [
        'Welsh-Powell', 'DSatur',  # Base greedy
        'Simulated Annealing',  # Metaheuristic
        'Dynamic Programming', 'Dynamic Programming (Bounded)',  # Exact
        'Hybrid DSatur+SA', 'Hybrid WP+SA', 'Hybrid Tabu', 'Adaptive Hybrid'  # Hybrid
    ]
    
    for algo in algo_order:
        if algo in algo_stats:
            stats = algo_stats[algo]
            avg_colors = sum(stats['colors']) / len(stats['colors'])
            avg_time = sum(stats['times']) / len(stats['times'])
            n_datasets = len(stats['datasets'])
            print(f"{algo:<30} {avg_colors:>13.2f}   {avg_time:>13.4f}   {n_datasets}")
    
    # Save results
    print("\n" + "="*100)
    print("SAVING RESULTS")
    print("="*100)
    
    os.makedirs('results/data', exist_ok=True)
    
    import json
    with open('results/data/your_datasets_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print("✓ Saved to: results/data/your_datasets_results.json")
    
    import csv
    with open('results/data/your_datasets_results.csv', 'w', newline='') as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=['dataset', 'algorithm', 'colors', 'time', 'valid'])
            writer.writeheader()
            for r in all_results:
                if 'error' not in r:
                    writer.writerow({
                        'dataset': r.get('dataset', 'unknown'),
                        'algorithm': r['algorithm'],
                        'colors': r['colors'],
                        'time': r['time'],
                        'valid': r['valid']
                    })
    print("✓ Saved to: results/data/your_datasets_results.csv")
    
    print("\n" + "="*100)
    print("✅ BENCHMARK COMPLETE!")
    print("="*100)
    print("\nResults saved in results/data/")
    print("  - your_datasets_results.json")
    print("  - your_datasets_results.csv")

if __name__ == '__main__':
    main()
