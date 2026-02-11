import abc
import networkx as nx
from typing import Any, Optional, List, Dict


class GraphLabelAssigner(abc.ABC):
    """Abstract base class for assigning labels to a graph.

    A graph label assigner takes a graph and assigns labels or attributes
    to the graph itself, based on some criteria, such as overall structure
    or properties of the graph.
    """

    @abc.abstractmethod
    def assign_label(self, graph: nx.Graph, **kwargs) -> nx.Graph:
        """Assign labels or attributes to the graph.

        Args:
            graph (nx.Graph): The graph to label.
            **kwargs: Additional arguments specific to the labeling strategy.
        """
        pass

class NodeLabelAssigner(abc.ABC):
    """Abstract base class for assigning labels to nodes in a graph.

    A node label assigner takes a graph and assigns labels to its nodes
    based on some criteria, such as motif structures or other properties.
    """

    @abc.abstractmethod
    def assign_labels(self, graph: nx.Graph, node_list: Optional[List[int]] = None, **kwargs) -> Dict[int, int]:
        """Compute labels for nodes in the graph and return a mapping node->label.

        This method should NOT mutate the input graph; use `label_assignment` or
        `label_reassignment` to persist labels into node attributes.
        Args:
            graph (nx.Graph): The graph to analyze.
            node_list (Optional[List[int]], optional): List of node IDs to consider. If None, consider all nodes.
            **kwargs: Additional arguments specific to the labeling strategy.

        Returns:
            Dict[int,int]: Mapping from node id to integer label.
        """
        pass