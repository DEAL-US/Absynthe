import networkx as nx

def assign_labels_to_motif(graph: nx.Graph, motif: nx.Graph, motif_name: str):
    """
    Detect monomorphic subgraphs matching the motif within the main graph and label the corresponding nodes. Additional edges not present in the motif are allowed.

    Args:
        graph (nx.Graph): Reference graph.
        motif (nx.Graph): Structural motif.
        motif_name (str): Label applied to detected nodes.

    Returns:
        None: Modify the main graph directly.
    """
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        graph, motif,
        node_match=None,
        edge_match=None
    )

    seen_node_sets = set()

    for subgraph in matcher.subgraph_monomorphisms_iter():

        node_set = frozenset(subgraph.keys())

        # Avoid labeling the same group multiple times (automorphisms)
        if node_set in seen_node_sets:
            continue
        seen_node_sets.add(node_set)

        for node in node_set:
            graph.nodes[node]['label'] = motif_name