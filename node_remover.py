import networkx as nx
from abc import ABC, abstractmethod

class NodeRemover(ABC):
    @abstractmethod
    def remove_important_nodes(self, graph: nx.Graph, n: int) -> nx.Graph:
        """
        Removes n nodes from the graph and returns the modified graph.
        The removal should cause changes in the classes of the remaining nodes or the class of the graph.
        
        Args:
            graph: The input graph object.
            n (int): The number of nodes to remove.
        
        Returns:
            The modified graph with n nodes removed.
        """
        pass
