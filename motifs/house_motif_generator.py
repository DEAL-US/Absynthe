import networkx as nx
from motif_generator import MotifGenerator
from motifs.utils import assign_labels_to_motif


class HouseMotifGenerator(MotifGenerator):
    """Generator for house-shaped motifs.

    Generates a house graph with 5 nodes: union of cycle_4 and cycle_3 with 2 common nodes.
    Nodes: start to start+4
    Cycle_4: start-start+1-start+2-start+3-start
    Cycle_3: start+2-start+3-start+4-start+2
    """

    def generate_motif(self, start: int, id: int = 0) -> nx.Graph:
        """Generate a house motif starting from index start.

        The house is the union of a cycle_4 and a cycle_3 with 2 common nodes.

        Args:
            start (int): Starting index for the nodes.
            id (int): Identifier for the motif.

        Returns:
            nx.Graph: The house graph.
        """
        graph = nx.Graph()
        graph.add_nodes_from(range(start, start + 5))
        # Cycle_4: start - start+1 - start+2 - start+3 - start
        graph.add_edges_from([(start, start + 1), (start + 1, start + 2), (start + 2, start + 3), (start + 3, start)])
        # Cycle_3: start+2 - start+3 - start+4 - start+2
        graph.add_edges_from([(start + 2, start + 3), (start + 3, start + 4), (start + 4, start + 2)])
        # Add motif attribute to each node
        for node in graph.nodes():
            graph.nodes[node]['motif'] = 'house'
            graph.nodes[node]['motif_id'] = f'house_{id}'
        return graph

    @staticmethod
    def assign_labels(graph):
        """
        Busca subgrafos con forma de 'house' y etiqueta sus nodos.
        """
        motif = HouseMotifGenerator().generate_motif(0)
        assign_labels_to_motif(graph, motif, 'house')