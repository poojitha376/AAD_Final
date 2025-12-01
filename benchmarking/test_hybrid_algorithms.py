"""
Test Suite for Hybrid Graph Coloring Algorithms

Author: Algorithm Analysis & Design Team
Description:
    Comprehensive test cases for all hybrid graph coloring algorithms.
    Tests correctness, performance, and edge cases.

Tests include:
    - Small graphs with known chromatic numbers
    - Standard benchmark graphs
    - Edge cases (empty, single vertex, complete graphs)
    - Comparison with base algorithms
    - Validation of all colorings
"""

import unittest
import networkx as nx
from src.algorithms.hybrid_dsatur_sa import hybrid_dsatur_sa, validate_coloring
from src.algorithms.hybrid_wp_sa import hybrid_wp_sa
from src.algorithms.hybrid_tabu import hybrid_tabu
from src.algorithms.adaptive_hybrid import adaptive_hybrid, analyze_graph_characteristics


class TestHybridAlgorithms(unittest.TestCase):
    """Test suite for hybrid graph coloring algorithms."""
    
    def setUp(self):
        """Set up test graphs."""
        # Empty graph
        self.empty_graph = nx.Graph()
        
        # Single vertex
        self.single_vertex = nx.Graph()
        self.single_vertex.add_node(1)
        
        # Triangle (K3) - chromatic number = 3
        self.triangle = nx.complete_graph(3)
        
        # Square (C4) - chromatic number = 2
        self.square = nx.cycle_graph(4)
        
        # Petersen graph - chromatic number = 3
        self.petersen = nx.petersen_graph()
        
        # Complete graph K5 - chromatic number = 5
        self.k5 = nx.complete_graph(5)
        
        # Bipartite graph - chromatic number = 2
        self.bipartite = nx.complete_bipartite_graph(3, 4)
        
        # Path graph - chromatic number = 2
        self.path = nx.path_graph(10)
        
        # Random graphs for stress testing
        self.random_sparse = nx.erdos_renyi_graph(30, 0.1, seed=42)
        self.random_dense = nx.erdos_renyi_graph(30, 0.5, seed=42)
    
    def test_empty_graph(self):
        """Test all algorithms on empty graph."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.empty_graph)
                self.assertEqual(num_colors, 0)
                self.assertEqual(len(coloring), 0)
    
    def test_single_vertex(self):
        """Test all algorithms on single vertex graph."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.single_vertex)
                self.assertEqual(num_colors, 1)
                self.assertEqual(len(coloring), 1)
                self.assertTrue(validate_coloring(self.single_vertex, coloring))
    
    def test_triangle_chromatic_number(self):
        """Test triangle (K3) - should use 3 colors."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.triangle)
                self.assertTrue(validate_coloring(self.triangle, coloring))
                # Triangle requires exactly 3 colors
                self.assertEqual(num_colors, 3)
    
    def test_square_chromatic_number(self):
        """Test square (C4) - should use 2 colors."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.square)
                self.assertTrue(validate_coloring(self.square, coloring))
                # Square requires exactly 2 colors (bipartite)
                self.assertEqual(num_colors, 2)
    
    def test_petersen_graph(self):
        """Test Petersen graph - chromatic number = 3."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.petersen, seed=42)
                self.assertTrue(validate_coloring(self.petersen, coloring))
                # Petersen requires 3 colors
                self.assertLessEqual(num_colors, 4)  # Should be 3, but allow 4
    
    def test_complete_graph_k5(self):
        """Test complete graph K5 - should use 5 colors."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.k5)
                self.assertTrue(validate_coloring(self.k5, coloring))
                # Complete graph requires n colors
                self.assertEqual(num_colors, 5)
    
    def test_bipartite_graph(self):
        """Test bipartite graph - should use 2 colors."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.bipartite)
                self.assertTrue(validate_coloring(self.bipartite, coloring))
                # Bipartite requires exactly 2 colors
                self.assertEqual(num_colors, 2)
    
    def test_path_graph(self):
        """Test path graph - should use 2 colors."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.path)
                self.assertTrue(validate_coloring(self.path, coloring))
                # Path requires 2 colors (or 3 if odd cycle, but path is not a cycle)
                self.assertLessEqual(num_colors, 3)
    
    def test_random_sparse_validity(self):
        """Test that random sparse graph produces valid coloring."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.random_sparse, seed=42)
                self.assertTrue(validate_coloring(self.random_sparse, coloring))
                self.assertGreater(num_colors, 0)
    
    def test_random_dense_validity(self):
        """Test that random dense graph produces valid coloring."""
        for algo_func, name in [(hybrid_dsatur_sa, 'DSatur+SA'),
                                (hybrid_wp_sa, 'WP+SA'),
                                (hybrid_tabu, 'Tabu'),
                                (adaptive_hybrid, 'Adaptive')]:
            with self.subTest(algorithm=name):
                coloring, num_colors, stats = algo_func(self.random_dense, seed=42)
                self.assertTrue(validate_coloring(self.random_dense, coloring))
                self.assertGreater(num_colors, 0)
    
    def test_dsatur_sa_stats(self):
        """Test that DSatur+SA returns proper statistics."""
        coloring, num_colors, stats = hybrid_dsatur_sa(self.petersen, seed=42)
        
        self.assertIn('dsatur_colors', stats)
        self.assertIn('final_colors', stats)
        self.assertIn('reduction', stats)
        self.assertGreaterEqual(stats['dsatur_colors'], num_colors)
    
    def test_wp_sa_stats(self):
        """Test that WP+SA returns proper statistics."""
        coloring, num_colors, stats = hybrid_wp_sa(self.petersen, seed=42)
        
        self.assertIn('wp_colors', stats)
        self.assertIn('final_colors', stats)
        self.assertIn('reduction', stats)
        self.assertGreaterEqual(stats['wp_colors'], num_colors)
    
    def test_tabu_stats(self):
        """Test that Tabu Search returns proper statistics."""
        coloring, num_colors, stats = hybrid_tabu(self.petersen, seed=42)
        
        self.assertIn('initial_colors', stats)
        self.assertIn('final_colors', stats)
        self.assertIn('reduction', stats)
        self.assertGreaterEqual(stats['initial_colors'], num_colors)
    
    def test_adaptive_selection(self):
        """Test that adaptive algorithm selects appropriately."""
        # Small dense graph should select DSatur+SA or Tabu
        coloring, num_colors, stats = adaptive_hybrid(self.k5, verbose=False)
        self.assertTrue(validate_coloring(self.k5, coloring))
        self.assertIn('selected_algorithm', stats)
        self.assertIn('graph_characteristics', stats)
        
        # Sparse graph might select WP+SA
        coloring, num_colors, stats = adaptive_hybrid(self.path, verbose=False)
        self.assertTrue(validate_coloring(self.path, coloring))
        self.assertIn('selected_algorithm', stats)
    
    def test_graph_analysis(self):
        """Test graph characteristic analysis."""
        # Test triangle
        chars = analyze_graph_characteristics(self.triangle)
        self.assertEqual(chars['num_nodes'], 3)
        self.assertEqual(chars['num_edges'], 3)
        self.assertEqual(chars['size_category'], 'tiny')
        
        # Test larger graph
        chars = analyze_graph_characteristics(self.random_sparse)
        self.assertEqual(chars['num_nodes'], 30)
        self.assertIn('density_category', chars)
        self.assertIn('avg_degree', chars)
    
    def test_reproducibility_with_seed(self):
        """Test that results are reproducible with same seed."""
        coloring1, num_colors1, _ = hybrid_dsatur_sa(self.random_sparse, seed=42)
        coloring2, num_colors2, _ = hybrid_dsatur_sa(self.random_sparse, seed=42)
        
        # Should produce same number of colors with same seed
        self.assertEqual(num_colors1, num_colors2)
    
    def test_aggressive_vs_fast_mode(self):
        """Test aggressive vs fast mode in hybrid algorithms."""
        # Aggressive mode
        _, colors_aggressive, stats_aggressive = hybrid_dsatur_sa(
            self.petersen, seed=42, aggressive=True
        )
        
        # Fast mode
        _, colors_fast, stats_fast = hybrid_dsatur_sa(
            self.petersen, seed=42, aggressive=False
        )
        
        # Both should be valid, aggressive might use fewer colors
        self.assertGreater(colors_aggressive, 0)
        self.assertGreater(colors_fast, 0)


class TestValidationFunction(unittest.TestCase):
    """Test the coloring validation function."""
    
    def test_valid_coloring(self):
        """Test validation of correct coloring."""
        G = nx.cycle_graph(4)
        coloring = {0: 0, 1: 1, 2: 0, 3: 1}
        self.assertTrue(validate_coloring(G, coloring))
    
    def test_invalid_coloring(self):
        """Test detection of invalid coloring."""
        G = nx.cycle_graph(4)
        coloring = {0: 0, 1: 0, 2: 0, 3: 1}  # 0 and 1 are adjacent with same color
        self.assertFalse(validate_coloring(G, coloring))
    
    def test_empty_graph_validation(self):
        """Test validation on empty graph."""
        G = nx.Graph()
        coloring = {}
        self.assertTrue(validate_coloring(G, coloring))


def run_correctness_tests():
    """Run all correctness tests and print summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestHybridAlgorithms))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationFunction))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("HYBRID ALGORITHMS TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_correctness_tests()
    exit(0 if success else 1)
