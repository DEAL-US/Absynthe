import networkx as nx
import random

def add_random_edges(graph: nx.Graph, p: float = None, num_edges: int = None, rng: random.Random = None) -> nx.Graph:
    """Add random edges to the graph. Can add a percentage p of random edges based on the original number of edges,
    or a specific number of edges. If both p and num_edges are provided, p takes priority.

    Args:
        graph (nx.Graph): The input graph.
        p (float, optional): The percentage of edges to add (e.g., 0.1 for 10%). Takes priority if provided.
        num_edges (int, optional): The exact number of edges to add.

    Returns:
        nx.Graph: A new graph with the additional edges.

    Raises:
        ValueError: If neither p nor num_edges is provided.
    """
    new_graph = graph.copy()
    original_edges = new_graph.number_of_edges()
    if p is not None:
        num_to_add = int(p * original_edges)
    elif num_edges is not None:
        num_to_add = num_edges
    else:
        raise ValueError("Must provide either 'p' or 'num_edges'")
    rnd = rng or random
    nodes = list(new_graph.nodes())
    added = 0
    while added < num_to_add:
        if len(nodes) < 2:
            break
        u, v = rnd.sample(nodes, 2)
        if not new_graph.has_edge(u, v):
            new_graph.add_edge(u, v)
            added += 1
    return new_graph

def add_vertices(graph: nx.Graph, num_vertices: int, rng: random.Random = None) -> nx.Graph:
    """Add a specified number of vertices to the graph, each connected to a random existing node.

    Args:
        graph (nx.Graph): The input graph.
        num_vertices (int): The number of vertices to add.

    Returns:
        nx.Graph: A new graph with the additional vertices connected.
    """
    new_graph = graph.copy()
    current_max = max(new_graph.nodes()) if new_graph.nodes() else -1
    rnd = rng or random
    for i in range(num_vertices):
        new_node = current_max + 1 + i
        new_graph.add_node(new_node)
        # Connect to a random existing node
        existing_nodes = [n for n in new_graph.nodes() if n != new_node]
        if existing_nodes:
            random_node = rnd.choice(existing_nodes)
            new_graph.add_edge(new_node, random_node)
    return new_graph
