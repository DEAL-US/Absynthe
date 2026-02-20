import abc
from typing import Dict, Any
import networkx as nx


class LabelingFunction(abc.ABC):
    """Abstract base class for computing labels on a graph.

    A labeling function takes a graph and returns a mapping from node IDs
    to labels. The labels can represent structural roles, community membership,
    motif participation, or any other property.

    Implementations should NOT mutate the input graph.
    """

    @abc.abstractmethod
    def compute_labels(self, graph: nx.Graph) -> Dict[int, Any]:
        """Compute labels for nodes in the graph.

        Args:
            graph: The graph to label.

        Returns:
            A dictionary mapping node IDs to their labels.
        """
        pass
