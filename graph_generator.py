import abc
import networkx as nx
from typing import List


class GraphGenerator(abc.ABC):
    """Abstract base class for generating graphs composed of motifs.

    A graph generator takes a list of motif descriptions and generates
    a complete graph by combining them.
    """

    @abc.abstractmethod
    def generate_graph(self, **kwargs) -> nx.Graph:
        """Generate a graph.

        Args:
            **kwargs: Keyword arguments specific to the graph generation.

        Returns:
            nx.Graph: The generated graph.
        """
        pass