from typing import Dict, Any, List, Optional
import networkx as nx
from interfaces import LabelingFunction
from motifs import motif_generators
from graph.utils import parse_motif_name


class MotifLabelingFunction(LabelingFunction):
    """Labeling function that assigns labels based on motif membership.

    Uses subgraph isomorphism to find motif occurrences and labels
    nodes by the motif they belong to. This is one possible implementation
    of LabelingFunction.
    """

    def __init__(self, motif_order: Optional[List[str]] = None):
        """
        Args:
            motif_order: List of motif names to check, in priority order
                         (last in list = highest priority, since it overwrites
                         earlier labels). If None, uses all registered motif
                         generators.
        """
        self.motif_order = motif_order

    def compute_labels(self, graph: nx.Graph) -> Dict[int, Any]:
        """Compute motif-based labels for all nodes in the graph.

        Iterates through motif types in reverse order so that earlier motifs
        in the list can overwrite later ones. Nodes not matching any motif
        get the label 'unknown'.
        """
        order = self.motif_order or list(motif_generators.keys())
        order = order[::-1]

        work_graph = graph.copy()

        # Clear any pre-existing 'label' attributes so that nodes which
        # no longer match a motif are correctly labeled 'unknown' instead
        # of retaining a stale label from a previous labeling pass.
        for node in work_graph.nodes():
            work_graph.nodes[node].pop('label', None)

        node_labels = {}

        for motif_name in order:
            base_name, args = parse_motif_name(motif_name)
            generator_class = motif_generators.get(base_name)
            if generator_class and hasattr(generator_class, 'assign_labels'):
                generator_class.assign_labels(work_graph, *args)
                for node in work_graph.nodes():
                    node_labels[node] = work_graph.nodes[node].get('label', 'unknown')

        return node_labels
