import random
from typing import Optional, Dict, Any, Tuple, List
import networkx as nx
from perturbation import Perturbation
from graph.perturbation_engine import remove_nodes, perturb_edges


class RemoveNodesPerturbation(Perturbation):
    """Remove nodes from a graph using a configurable strategy.

    Wraps the existing remove_nodes() function from perturbation_engine.
    """

    def __init__(self, num_nodes: int, strategy: str = 'random',
                 params: Optional[Dict] = None,
                 rng: Optional[random.Random] = None,
                 node_list: Optional[List[int]] = None):
        """
        Args:
            num_nodes: Number of nodes to remove.
            strategy: Node selection strategy (random, motif, degree,
                      centrality, role, by_attribute).
            params: Additional parameters for the strategy.
            rng: Random number generator for reproducibility.
            node_list: Subset of nodes to consider for removal.
        """
        self.num_nodes = num_nodes
        self.strategy = strategy
        self.params = params
        self.rng = rng
        self.node_list = node_list

    def apply(self, graph: nx.Graph) -> Tuple[nx.Graph, Dict[str, Any]]:
        new_graph, removed = remove_nodes(
            graph, self.num_nodes, self.strategy,
            self.params, self.rng, self.node_list
        )
        return new_graph, {"removed_nodes": removed}


class RemoveEdgesPerturbation(Perturbation):
    """Remove edges from a graph with a given probability."""

    def __init__(self, p_remove: float = 0.1,
                 rng: Optional[random.Random] = None):
        self.p_remove = p_remove
        self.rng = rng

    def apply(self, graph: nx.Graph) -> Tuple[nx.Graph, Dict[str, Any]]:
        new_graph = perturb_edges(
            graph, p_remove=self.p_remove, p_add=0.0, rng=self.rng
        )
        removed = set(graph.edges()) - set(new_graph.edges())
        return new_graph, {"removed_edges": list(removed)}


class AddEdgesPerturbation(Perturbation):
    """Add random edges to a graph."""

    def __init__(self, p_add: float = 0.0, add_num: Optional[int] = None,
                 rng: Optional[random.Random] = None):
        self.p_add = p_add
        self.add_num = add_num
        self.rng = rng

    def apply(self, graph: nx.Graph) -> Tuple[nx.Graph, Dict[str, Any]]:
        new_graph = perturb_edges(
            graph, p_remove=0.0, p_add=self.p_add,
            add_num=self.add_num, rng=self.rng
        )
        added = set(new_graph.edges()) - set(graph.edges())
        return new_graph, {"added_edges": list(added)}


class EdgePerturbation(Perturbation):
    """Combined edge perturbation: remove and add edges simultaneously."""

    def __init__(self, p_remove: float = 0.0, p_add: float = 0.0,
                 add_num: Optional[int] = None,
                 rng: Optional[random.Random] = None):
        self.p_remove = p_remove
        self.p_add = p_add
        self.add_num = add_num
        self.rng = rng

    def apply(self, graph: nx.Graph) -> Tuple[nx.Graph, Dict[str, Any]]:
        new_graph = perturb_edges(
            graph, p_remove=self.p_remove, p_add=self.p_add,
            add_num=self.add_num, rng=self.rng
        )
        before_edges = set(graph.edges())
        after_edges = set(new_graph.edges())
        return new_graph, {
            "removed_edges": list(before_edges - after_edges),
            "added_edges": list(after_edges - before_edges),
        }
