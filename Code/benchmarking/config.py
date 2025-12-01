"""
Configuration Module

Defines parameters for benchmarking experiments.
"""

# Graph generation parameters
GRAPH_SIZES = [10, 15, 20, 25, 30]  # Number of vertices
EDGE_PROBABILITIES = [0.2, 0.3, 0.5, 0.7]  # Erdős-Rényi probabilities

# Simulated Annealing parameters
SA_INITIAL_TEMP = 10.0
SA_COOLING_RATE = 0.99
SA_MAX_ITERATIONS = 100000
SA_STALL_LIMIT = 10000

# Dynamic Programming parameters
DP_MAX_COLORS = 20
DP_MAX_VERTICES = 15  # Warn if graph larger than this

# Number of trials per configuration
NUM_TRIALS = 3

# Random seeds for reproducibility
RANDOM_SEEDS = [42, 123, 456, 789, 999]

# Dataset paths
DATASET_PATH_DIMACS = "data/dimacs/"
DATASET_PATH_REAL_WORLD = "data/real-world/"
RESULTS_PATH = "results/"
RESULTS_DATA_PATH = "results/data/"
RESULTS_PLOTS_PATH = "results/plots/"

# Benchmark datasets
BENCHMARK_DATASETS = {
    'karate_club': ('karate', None),
    'petersen': ('petersen', None),
    'random_20_0.3': ('random', (20, 0.3)),
    'random_30_0.5': ('random', (30, 0.5)),
}
