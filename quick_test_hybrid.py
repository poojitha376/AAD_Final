#!/usr/bin/env python3
"""
Quick Test Script for Hybrid Algorithms

Tests that all algorithms can be imported and run successfully
on a simple graph before running the full benchmark suite.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("Testing Hybrid Algorithms - Quick Verification")
print("=" * 70)

try:
    import networkx as nx
    print("✓ NetworkX imported successfully")
except ImportError:
    print("✗ NetworkX not found. Please install: pip install networkx")
    sys.exit(1)

try:
    # Test imports
    print("\nTesting imports...")
    from src.algorithms.hybrid_dsatur_sa import hybrid_dsatur_sa
    print("  ✓ hybrid_dsatur_sa")
    
    from src.algorithms.hybrid_wp_sa import hybrid_wp_sa
    print("  ✓ hybrid_wp_sa")
    
    from src.algorithms.hybrid_tabu import hybrid_tabu
    print("  ✓ hybrid_tabu")
    
    from src.algorithms.adaptive_hybrid import adaptive_hybrid
    print("  ✓ adaptive_hybrid")
    
    from src.algorithms import welsh_powell, dsatur
    print("  ✓ Base algorithms (welsh_powell, dsatur)")
    
except ImportError as e:
    print(f"\n✗ Import Error: {e}")
    sys.exit(1)

# Test on a simple graph
print("\nTesting on Petersen Graph (10 nodes)...")
print("-" * 70)

G = nx.petersen_graph()
print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

algorithms = [
    ("Welsh-Powell", welsh_powell),
    ("DSatur", dsatur),
    ("Hybrid DSatur+SA", hybrid_dsatur_sa),
    ("Hybrid WP+SA", hybrid_wp_sa),
    ("Hybrid Tabu", hybrid_tabu),
    ("Adaptive Hybrid", adaptive_hybrid),
]

print(f"\n{'Algorithm':<25} {'Colors':<10} {'Status'}")
print("-" * 70)

all_passed = True

for name, algo in algorithms:
    try:
        if name in ["Welsh-Powell", "DSatur"]:
            coloring, num_colors = algo(G)
        else:
            coloring, num_colors, stats = algo(G, seed=42)
        
        # Verify coloring is valid
        is_valid = True
        for u, v in G.edges():
            if coloring[u] == coloring[v]:
                is_valid = False
                break
        
        status = "✓ PASS" if is_valid else "✗ FAIL (invalid coloring)"
        print(f"{name:<25} {num_colors:<10} {status}")
        
        if not is_valid:
            all_passed = False
            
    except Exception as e:
        print(f"{name:<25} ERROR      ✗ FAIL: {str(e)[:30]}")
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print("✅ All algorithms passed!")
    print("\nYou can now run the full benchmark:")
    print("  python3 run_hybrid_benchmarks.py")
else:
    print("❌ Some algorithms failed. Please check the errors above.")
    sys.exit(1)

print("=" * 70)
