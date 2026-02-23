import abc
import networkx as nx
from typing import List


class GraphGenerator(abc.ABC):
    """Abstract base class for generating graphs.

    A graph generator produces a NetworkX graph. Concrete implementations
    may generate graphs from motifs, read them from files, use random
    graph models, or any other method.
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