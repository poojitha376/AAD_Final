"""
Unit Tests for Graph Coloring Algorithms

Tests correctness on small, well-known graphs where optimal solutions are known.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import networkx as nx
from src.algorithms.welshpowell import welsh_powell, validate_coloring as wp_validate
from src.algorithms.dsatur import dsatur, validate_coloring as ds_validate
from src.algorithms.simulated_annealing import simulated_annealing, validate_coloring as sa_validate
from src.algorithms.dynamic_programming import find_chromatic_number, validate_coloring as dp_validate


def test_triangle():
    """Test on triangle graph (K3): chromatic number = 3"""
    print("\n=== Test: Triangle (K3) ===")
    G = nx.complete_graph(3)
    
    # Welsh-Powell
    coloring_wp, k_wp = welsh_powell(G)
    assert wp_validate(G, coloring_wp), "Welsh-Powell produced invalid coloring"
    assert k_wp == 3, f"Welsh-Powell: expected 3 colors, got {k_wp}"
    print(f"✓ Welsh-Powell: {k_wp} colors (correct)")
    
    # D-Satur
    coloring_ds, k_ds = dsatur(G)
    assert ds_validate(G, coloring_ds), "D-Satur produced invalid coloring"
    assert k_ds == 3, f"D-Satur: expected 3 colors, got {k_ds}"
    print(f"✓ D-Satur: {k_ds} colors (correct)")
    
    # Dynamic Programming (optimal)
    k_dp, coloring_dp = find_chromatic_number(G)
    assert dp_validate(G, coloring_dp), "DP produced invalid coloring"
    assert k_dp == 3, f"DP: expected 3 colors, got {k_dp}"
    print(f"✓ Dynamic Programming: {k_dp} colors (optimal)")


def test_bipartite():
    """Test on complete bipartite graph: chromatic number = 2"""
    print("\n=== Test: Complete Bipartite Graph K(3,3) ===")
    G = nx.complete_bipartite_graph(3, 3)
    
    # Welsh-Powell
    coloring_wp, k_wp = welsh_powell(G)
    assert wp_validate(G, coloring_wp), "Welsh-Powell produced invalid coloring"
    assert k_wp == 2, f"Welsh-Powell: expected 2 colors, got {k_wp}"
    print(f"✓ Welsh-Powell: {k_wp} colors (correct)")
    
    # D-Satur
    coloring_ds, k_ds = dsatur(G)
    assert ds_validate(G, coloring_ds), "D-Satur produced invalid coloring"
    assert k_ds == 2, f"D-Satur: expected 2 colors, got {k_ds}"
    print(f"✓ D-Satur: {k_ds} colors (correct)")
    
    # DP
    k_dp, coloring_dp = find_chromatic_number(G)
    assert dp_validate(G, coloring_dp), "DP produced invalid coloring"
    assert k_dp == 2, f"DP: expected 2 colors, got {k_dp}"
    print(f"✓ Dynamic Programming: {k_dp} colors (optimal)")


def test_petersen():
    """Test on Petersen graph: chromatic number = 3"""
    print("\n=== Test: Petersen Graph ===")
    G = nx.petersen_graph()
    
    # Welsh-Powell
    coloring_wp, k_wp = welsh_powell(G)
    assert wp_validate(G, coloring_wp), "Welsh-Powell produced invalid coloring"
    assert k_wp >= 3, f"Welsh-Powell: expected >= 3 colors, got {k_wp}"
    print(f"✓ Welsh-Powell: {k_wp} colors (valid, chromatic number is 3)")
    
    # D-Satur
    coloring_ds, k_ds = dsatur(G)
    assert ds_validate(G, coloring_ds), "D-Satur produced invalid coloring"
    assert k_ds >= 3, f"D-Satur: expected >= 3 colors, got {k_ds}"
    print(f"✓ D-Satur: {k_ds} colors (valid)")
    
    # Simulated Annealing
    coloring_sa, k_sa, history, time_s = simulated_annealing(G, initial_num_colors=5, seed=42)
    assert sa_validate(G, coloring_sa), "SA produced invalid coloring"
    print(f"✓ Simulated Annealing: {k_sa} colors (valid, time={time_s:.3f}s)")


def test_cycle_odd():
    """Test on 5-cycle: chromatic number = 3"""
    print("\n=== Test: Odd Cycle (C5) ===")
    G = nx.cycle_graph(5)
    
    # Welsh-Powell
    coloring_wp, k_wp = welsh_powell(G)
    assert wp_validate(G, coloring_wp), "Welsh-Powell produced invalid coloring"
    assert k_wp == 3, f"Welsh-Powell: expected 3 colors, got {k_wp}"
    print(f"✓ Welsh-Powell: {k_wp} colors (correct)")
    
    # D-Satur
    coloring_ds, k_ds = dsatur(G)
    assert ds_validate(G, coloring_ds), "D-Satur produced invalid coloring"
    assert k_ds == 3, f"D-Satur: expected 3 colors, got {k_ds}"
    print(f"✓ D-Satur: {k_ds} colors (correct)")
    
    # DP
    k_dp, coloring_dp = find_chromatic_number(G)
    assert dp_validate(G, coloring_dp), "DP produced invalid coloring"
    assert k_dp == 3, f"DP: expected 3 colors, got {k_dp}"
    print(f"✓ Dynamic Programming: {k_dp} colors (optimal)")


def test_cycle_even():
    """Test on 6-cycle: chromatic number = 2"""
    print("\n=== Test: Even Cycle (C6) ===")
    G = nx.cycle_graph(6)
    
    # Welsh-Powell
    coloring_wp, k_wp = welsh_powell(G)
    assert wp_validate(G, coloring_wp), "Welsh-Powell produced invalid coloring"
    assert k_wp == 2, f"Welsh-Powell: expected 2 colors, got {k_wp}"
    print(f"✓ Welsh-Powell: {k_wp} colors (correct)")
    
    # D-Satur
    coloring_ds, k_ds = dsatur(G)
    assert ds_validate(G, coloring_ds), "D-Satur produced invalid coloring"
    assert k_ds == 2, f"D-Satur: expected 2 colors, got {k_ds}"
    print(f"✓ D-Satur: {k_ds} colors (correct)")
    
    # DP
    k_dp, coloring_dp = find_chromatic_number(G)
    assert dp_validate(G, coloring_dp), "DP produced invalid coloring"
    assert k_dp == 2, f"DP: expected 2 colors, got {k_dp}"
    print(f"✓ Dynamic Programming: {k_dp} colors (optimal)")


def test_karate_club():
    """Test on Zachary's Karate Club: chromatic number = 4"""
    print("\n=== Test: Zachary's Karate Club ===")
    G = nx.karate_club_graph()
    
    # Welsh-Powell
    coloring_wp, k_wp = welsh_powell(G)
    assert wp_validate(G, coloring_wp), "Welsh-Powell produced invalid coloring"
    print(f"✓ Welsh-Powell: {k_wp} colors (chromatic number is 4)")
    
    # D-Satur
    coloring_ds, k_ds = dsatur(G)
    assert ds_validate(G, coloring_ds), "D-Satur produced invalid coloring"
    print(f"✓ D-Satur: {k_ds} colors")
    
    # Simulated Annealing
    coloring_sa, k_sa, history, time_s = simulated_annealing(G, initial_num_colors=6, seed=42)
    assert sa_validate(G, coloring_sa), "SA produced invalid coloring"
    print(f"✓ Simulated Annealing: {k_sa} colors (time={time_s:.3f}s)")


def run_all_tests():
    """Run all correctness tests."""
    print("="*60)
    print("GRAPH COLORING ALGORITHM CORRECTNESS TESTS")
    print("="*60)
    
    try:
        test_triangle()
        test_bipartite()
        test_cycle_even()
        test_cycle_odd()
        test_petersen()
        test_karate_club()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return True
    
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
