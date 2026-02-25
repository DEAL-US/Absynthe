import abc
import networkx as nx
from interfaces.labeling_result import LabelingResult


class LabelingFunction(abc.ABC):
    """Abstract base class for computing labels on a graph.

    A labeling function takes a graph and returns a ``LabelingResult``
    containing node-level labels, optional graph-level labels, per-node
    detail information, and arbitrary metadata.

    Implementations may populate any combination of these fields.  For
    example, a motif-based labeler fills ``labels`` and ``details``
    while a graph-classification labeler fills ``graph_labels``.

    Implementations should NOT mutate the input graph.
    """

    @abc.abstractmethod
    def compute_labels(self, graph: nx.Graph) -> LabelingResult:
        """Compute labels for the graph.

        Args:
            graph: The graph to label.

        Returns:
            A ``LabelingResult`` with node labels, graph labels,
            per-node details, and/or global metadata.
        """
        pass
