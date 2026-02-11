import random
from typing import List, Tuple, Dict, Optional
import networkx as nx
from statistics import mean
from .perturbation_strategies import STRATEGY_MAP
from .label_engine import LabelEngine

def remove_nodes(graph: nx.Graph,
                 n: int,
                 strategy: str = 'motif',
                 params: Optional[Dict] = None,
                 rng: Optional[random.Random] = None,
                 node_list: Optional[List[int]] = None) -> Tuple[nx.Graph, List[int]]:
    """Remove n nodes according to the requested strategy and return (new_graph, removed_nodes).

    Args:
        graph (nx.Graph): The input graph.
        n (int): Number of nodes to remove.
        strategy (str): Strategy for selecting nodes to remove.
        params (Optional[Dict]): Additional parameters for the strategy.
        rng (Optional[random.Random]): Random number generator.
        node_list (Optional[List[int]]): Subset of nodes to consider for removal.

    Returns:
        Tuple[nx.Graph, List[int]]: The perturbed graph and the list of removed nodes.
    """
    params = params or {}
    rng = rng or random

    G = graph.copy()

    # Determine the nodes to consider
    nodes = node_list if node_list is not None else list(G.nodes())

    n = min(n, len(nodes))

    if n == 0:
        return G, []

    strat = STRATEGY_MAP.get((strategy or 'random').lower())
    if not strat:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Apply the strategy to the filtered nodes
    to_remove = strat(G.subgraph(nodes), n, params, rng)

    # Perform removal
    G.remove_nodes_from(to_remove)
    return G, to_remove


def perturb_edges(graph: nx.Graph,
                  p_remove: float = 0.0,
                  p_add: float = 0.0,
                  add_num: Optional[int] = None,
                  add_strategy: str = 'random',
                  params: Optional[Dict] = None,
                  rng: Optional[random.Random] = None) -> nx.Graph:
    """Perturb edges by removing each existing edge with probability `p_remove` and adding edges.

    - p_remove: probability to remove each existing edge
    - p_add: probability for each non-edge to be added (used if add_num is None)
    - add_num: explicit number of edges to add (if provided, p_add ignored)
    - add_strategy: currently only 'random' supported; placeholder for block-aware additions
    """
    params = params or {}
    rng = rng or random

    G = graph.copy()

    # remove edges
    if p_remove > 0:
        for u, v in list(G.edges()):
            if rng.random() < p_remove:
                G.remove_edge(u, v)

    # add edges
    non_edges = list(nx.non_edges(G))
    if add_num is not None:
        add_num = min(add_num, len(non_edges))
        additions = rng.sample(non_edges, add_num) if add_num > 0 else []
        G.add_edges_from(additions)
    else:
        if p_add > 0:
            for u, v in non_edges:
                if rng.random() < p_add:
                    G.add_edge(u, v)

    return G

class GraphPerturbation:
    def __init__(self, graph: nx.Graph, num_nodes_to_remove: int, strategy: str, max_iterations: int):
        """
        Initialize the GraphPerturbation class.

        :param graph: The input graph to perturb.
        :param num_nodes_to_remove: Number of nodes to remove in each perturbation.
        :param strategy: Strategy for selecting nodes to remove.
        :param max_iterations: Maximum number of iterations to find a valid perturbation.
        """
        self.graph = graph
        self.num_nodes_to_remove = num_nodes_to_remove
        self.strategy = strategy
        self.max_iterations = max_iterations

    def perturb_and_check(self):
        """
        Perform perturbations on the graph and check if any node's class changes.

        :return: Tuple containing the perturbed graph and a dictionary with details of the perturbation.
        """
        label_engine = LabelEngine()
        original_labels = label_engine.assign_labels(self.graph)

        for iteration in range(self.max_iterations):
            perturbed_graph, removed_nodes = remove_nodes(
                self.graph, self.num_nodes_to_remove, self.strategy
            )

            perturbed_labels = label_engine.assign_labels(perturbed_graph)

            changed_nodes = {
                node: (original_labels[node], perturbed_labels[node])
                for node in perturbed_labels
                if perturbed_labels[node] != original_labels.get(node)
            }

            if changed_nodes:
                return perturbed_graph, {
                    "removed_nodes": removed_nodes,
                    "changed_nodes": changed_nodes,
                }

        return None, {"message": "No valid perturbation found after maximum iterations."}
