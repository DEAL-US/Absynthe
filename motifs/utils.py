import networkx as nx

def assign_labels_to_motif(graph: nx.Graph, motif: nx.Graph, motif_name: str):
    """
    Identifica subgrafos isomorfos al motivo dado y asigna etiquetas a sus nodos.

    Args:
        graph (nx.Graph): El grafo principal donde buscar.
        motif (nx.Graph): El motivo a buscar.
        motif_name (str): Nombre del motivo para etiquetar los nodos.

    Returns:
        None: Modifica el grafo principal directamente.
    """
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        graph, motif,
        node_match=None,
        edge_match=None
    )
    motif_id = 0
    for subgraph in matcher.subgraph_isomorphisms_iter():
        for node in subgraph:
            graph.nodes[node]['label'] = motif_name
        motif_id += 1