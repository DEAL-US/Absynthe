import random
from typing import Optional, Dict, Any, Tuple, List
import networkx as nx
from interfaces import Perturbation
from .perturbation_strategies import STRATEGY_MAP
from utils.rng import get_rng


# ---------------------------------------------------------------------------
# Utility functions (used internally by the perturbation classes below)
# ---------------------------------------------------------------------------

def remove_nodes(graph: nx.Graph,
                 n: int,
                 strategy: str = 'motif',
                 params: Optional[Dict] = None,
                 rng: Optional[random.Random] = None,
                 node_list: Optional[List[int]] = None) -> Tuple[nx.Graph, List[int]]:
    """Remove n nodes according to the requested strategy and return (new_graph, removed_nodes).

    Args:
        graph: The input graph.
        n: Number of nodes to remove.
        strategy: Strategy for selecting nodes to remove.
        params: Additional parameters for the strategy.
        rng: Random number generator.
        node_list: Subset of nodes to consider for removal.

    Returns:
        Tuple of (perturbed_graph, list_of_removed_nodes).
    """
    params = params or {}
    rng = rng or get_rng()

    G = graph.copy()
    nodes = node_list if node_list is not None else list(G.nodes())
    n = min(n, len(nodes))

    if n == 0:
        return G, []

    strat = STRATEGY_MAP.get((strategy or 'random').lower())
    if not strat:
        raise ValueError(f"Unknown strategy: {strategy}")

    to_remove = strat(G.subgraph(nodes), n, params, rng)
    G.remove_nodes_from(to_remove)
    return G, to_remove


def perturb_edges(graph: nx.Graph,
                  p_remove: float = 0.0,
                  p_add: float = 0.0,
                  add_num: Optional[int] = None,
                  rng: Optional[random.Random] = None) -> nx.Graph:
    """Perturb edges by removing existing edges and/or adding new ones.

    Args:
        graph: The input graph.
        p_remove: Probability to remove each existing edge.
        p_add: Probability for each non-edge to be added (used if add_num is None).
        add_num: Explicit number of edges to add (if provided, p_add is ignored).
        rng: Random number generator.
    """
    rng = rng or get_rng()
    G = graph.copy()

    if p_remove > 0:
        for u, v in list(G.edges()):
            if rng.random() < p_remove:
                G.remove_edge(u, v)

    non_edges = list(nx.non_edges(G))
    if add_num is not None:
        add_num = min(add_num, len(non_edges))
        additions = rng.sample(non_edges, add_num) if add_num > 0 else []
        G.add_edges_from(additions)
    elif p_add > 0:
        for u, v in non_edges:
            if rng.random() < p_add:
                G.add_edge(u, v)

    return G


# ---------------------------------------------------------------------------
# Concrete Perturbation implementations
# ---------------------------------------------------------------------------

class RemoveNodesPerturbation(Perturbation):
    """Remove nodes from a graph using a configurable strategy."""

    def __init__(self, num_nodes: int, strategy: str = 'random',
                 params: Optional[Dict] = None,
                 rng: Optional[random.Random] = None,
                 node_list: Optional[List[int]] = None):
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
        removed_info = []
        for n in removed:
            incident = [
                {"u": n, "v": nb, "attrs": dict(graph.edges[n, nb])}
                for nb in graph.neighbors(n)
            ]
            removed_info.append({
                "id": n,
                "attrs": dict(graph.nodes[n]),
                "edges": incident,
            })
        return new_graph, {"removed_nodes": removed_info}


class RemoveEdgesPerturbation(Perturbation):
    """Remove edges from a graph with a given probability."""

    def __init__(self, p_remove: float = 0.1,
                 rng: Optional[random.Random] = None):
        self.p_remove = p_remove
        self.rng = rng

    def apply(self, graph: nx.Graph) -> Tuple[nx.Graph, Dict[str, Any]]:
        new_graph = perturb_edges(graph, p_remove=self.p_remove, rng=self.rng)
        removed = set(graph.edges()) - set(new_graph.edges())
        removed_info = [
            {"u": u, "v": v, "attrs": dict(graph.edges[u, v])}
            for u, v in removed
        ]
        return new_graph, {"removed_edges": removed_info}


class AddEdgesPerturbation(Perturbation):
    """Add random edges to a graph."""

    def __init__(self, p_add: float = 0.0, add_num: Optional[int] = None,
                 rng: Optional[random.Random] = None):
        self.p_add = p_add
        self.add_num = add_num
        self.rng = rng

    def apply(self, graph: nx.Graph) -> Tuple[nx.Graph, Dict[str, Any]]:
        new_graph = perturb_edges(
            graph, p_add=self.p_add, add_num=self.add_num, rng=self.rng
        )
        added = set(new_graph.edges()) - set(graph.edges())
        added_info = [{"u": u, "v": v} for u, v in added]
        return new_graph, {"added_edges": added_info}


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
        removed_edges = before_edges - after_edges
        added_edges = after_edges - before_edges
        return new_graph, {
            "removed_edges": [
                {"u": u, "v": v, "attrs": dict(graph.edges[u, v])}
                for u, v in removed_edges
            ],
            "added_edges": [
                {"u": u, "v": v} for u, v in added_edges
            ],
        }
