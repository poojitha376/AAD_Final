"""
Graph Loader Module

Author: Algorithm Analysis & Design Team
Description:
    Loads graph data from various formats:
    - DIMACS .col files (benchmark graphs)
    - Karate club social network
    - Timetable CSV (conflict graphs)
"""

import csv
import networkx as nx
from typing import Optional
from collections import defaultdict


def load_dimacs_graph(file_path: str) -> nx.Graph:
    """
    Load a DIMACS .col graph file.
    
    Format:
    - Lines starting with 'c': comments
    - Line 'p edge n m': problem line (n vertices, m edges)
    - Lines 'e u v': edges between vertices u and v (1-indexed)
    
    Args:
        file_path (str): Path to .col file
    
    Returns:
        nx.Graph: Loaded graph
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    
    Example:
        >>> G = load_dimacs_graph('data/dimacs/myciel3.col')
        >>> print(f"Loaded {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    """
    G = nx.Graph()
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('c'):
                    continue
                
                # Parse problem line (optional)
                if line.startswith('p'):
                    parts = line.split()
                    # Format: p edge num_nodes num_edges
                    continue
                
                # Parse edge
                if line.startswith('e'):
                    parts = line.split()
                    if len(parts) >= 3:
                        u = int(parts[1])
                        v = int(parts[2])
                        G.add_edge(u, v)
        
        return G
    
    except FileNotFoundError:
        raise FileNotFoundError(f"DIMACS file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error parsing DIMACS file: {e}")


def load_karate_graph() -> nx.Graph:
    """
    Load the Zachary Karate Club social network.
    
    A classic small graph with 34 vertices used for testing algorithms.
    Known chromatic number: 4
    
    Returns:
        nx.Graph: Karate club graph
    
    Example:
        >>> G = load_karate_graph()
        >>> print(f"Karate club: {G.number_of_nodes()} nodes")
    """
    return nx.karate_club_graph()


def load_timetable_graph(file_path: str) -> nx.Graph:
    """
    Load a timetable and create a conflict graph.
    
    Format: CSV file with columns 'course_id' and 'student_id'
    Two courses conflict (edge) if they share at least one student.
    
    Args:
        file_path (str): Path to CSV file
    
    Returns:
        nx.Graph: Conflict graph (vertices = courses, edges = shared students)
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If CSV format is invalid
    
    Example:
        >>> G = load_timetable_graph('data/timetable.csv')
        >>> print(f"Timetable conflict graph: {G.number_of_nodes()} courses")
    """
    G = nx.Graph()
    course_students = defaultdict(set)
    
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            
            if reader.fieldnames is None or 'course_id' not in reader.fieldnames:
                raise ValueError("CSV must have 'course_id' and 'student_id' columns")
            
            for row in reader:
                course = row['course_id'].strip()
                student = row['student_id'].strip()
                course_students[course].add(student)
        
        # Add course nodes
        courses = list(course_students.keys())
        G.add_nodes_from(courses)
        
        # Add conflict edges
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                # Two courses conflict if they share students
                if course_students[courses[i]] & course_students[courses[j]]:
                    G.add_edge(courses[i], courses[j])
        
        return G
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Timetable file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error loading timetable: {e}")


def load_graph(file_path: str, graph_type: str = 'auto') -> nx.Graph:
    """
    Load a graph from file, auto-detecting format or using specified type.
    
    Args:
        file_path (str): Path to graph file
        graph_type (str): 'dimacs', 'timetable', 'auto' (detect from extension)
    
    Returns:
        nx.Graph: Loaded graph
    
    Raises:
        ValueError: If format cannot be determined
    
    Example:
        >>> G = load_graph('data/graph.col')  # Auto-detects DIMACS
        >>> G = load_graph('data/conflicts.csv', graph_type='timetable')
    """
    if graph_type == 'auto':
        if file_path.endswith('.col'):
            graph_type = 'dimacs'
        elif file_path.endswith('.csv'):
            graph_type = 'timetable'
        else:
            raise ValueError(f"Cannot auto-detect format for {file_path}")
    
    if graph_type == 'dimacs':
        return load_dimacs_graph(file_path)
    elif graph_type == 'timetable':
        return load_timetable_graph(file_path)
    else:
        raise ValueError(f"Unknown graph type: {graph_type}")


def graph_info(G: nx.Graph) -> dict:
    """
    Get basic information about a loaded graph.
    
    Args:
        G (nx.Graph): The graph
    
    Returns:
        dict: Graph statistics
    """
    return {
        'vertices': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'max_degree': max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0,
        'min_degree': min(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0,
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0,
        'is_connected': nx.is_connected(G),
        'num_components': nx.number_connected_components(G)
    }
