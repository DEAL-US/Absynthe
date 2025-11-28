import networkx as nx
from motif_generator import MotifGenerator


class StarMotifGenerator(MotifGenerator):
    """Generator for star motifs.

    A star motif is a central node connected to `num_leaves` leaf nodes.
    """

    def generate_motif(self, start: int, num_leaves: int, id: int = 0) -> nx.Graph:
        """Generate a star motif with `num_leaves` leaves starting from `start`.

        Args:
            start (int): Starting index for the nodes (center node will be `start`).
            num_leaves (int): Number of leaves connected to the center. Must be >= 1.
            id (int): Identifier for the motif.

        Returns:
            nx.Graph: The star graph.

        Raises:
            ValueError: If `num_leaves` < 1.
        """
        if num_leaves < 1:
            raise ValueError("num_leaves must be at least 1 for a star motif.")

        graph = nx.Graph()
        center = start
        leaves = list(range(start + 1, start + 1 + num_leaves))
        graph.add_node(center)
        graph.add_nodes_from(leaves)
        for leaf in leaves:
            graph.add_edge(center, leaf)

        # Add motif attributes
        for node in graph.nodes():
            graph.nodes[node]['motif'] = f'star_{num_leaves}'
            graph.nodes[node]['motif_id'] = f'star_{num_leaves}_{id}'

        return graph
