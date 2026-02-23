import random
from typing import List, Tuple, Dict, Optional, Any
import networkx as nx
from .perturbation_strategies import STRATEGY_MAP
from perturbation import Perturbation
from labeling_function import LabelingFunction


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


class PerturbationPipeline:
    """Applies perturbations to a graph, accepting only those that cause label changes.

    Receives a list of (Perturbation, desired_count) pairs and a list of
    LabelingFunction instances. For each pair, the perturbation is applied
    repeatedly; each application is checked against the labeling functions
    and only accepted if it causes at least one label change. The process
    continues until the desired count of successful (label-changing)
    applications is reached, or max_iterations total attempts are exhausted.
    """

    def __init__(
        self,
        perturbations: List[Tuple[Perturbation, int]],
        labeling_functions: List[LabelingFunction],
        max_iterations: int = 10,
    ):
        """
        Args:
            perturbations: List of (perturbation_instance, desired_count) pairs.
                For each pair, the pipeline will try to apply the perturbation
                desired_count times successfully (i.e., causing label changes).
            labeling_functions: List of labeling functions. Labels from
                later functions overwrite labels from earlier ones for
                the same node.
            max_iterations: Maximum total attempts per perturbation to find
                applications that cause label changes.
        """
        self.perturbations = perturbations
        self.labeling_functions = labeling_functions
        self.max_iterations = max_iterations

    def _compute_labels(self, graph: nx.Graph) -> Dict[int, Any]:
        """Compute labels using all labeling functions.

        Later labeling functions overwrite earlier ones for the same node.
        """
        labels = {}
        for lf in self.labeling_functions:
            labels.update(lf.compute_labels(graph))
        return labels

    def apply_and_check(self, graph: nx.Graph) -> Tuple[nx.Graph, Dict[str, Any]]:
        """Apply perturbations one at a time, only accepting those that change labels.

        For each (perturbation, desired_count) pair:
          - Apply the perturbation to the current graph
          - Check if labels changed compared to before this application
          - If labels changed: accept (keep the perturbed graph), count it
          - If labels didn't change: discard, try again
          - Stop when desired_count successful applications are reached
            or max_iterations total attempts are exhausted for this perturbation

        Args:
            graph: The original graph.

        Returns:
            Tuple of (final_graph, info_dict) where info_dict contains:
            - 'perturbation_results': list of per-perturbation results, each with
              'successful_applications', 'total_attempts', and details of each
              accepted application (changes_dict and changed_nodes).
        """
        current_graph = graph.copy()
        all_results = []

        for perturbation, desired_count in self.perturbations:
            pert_result = {
                "successful_applications": 0,
                "total_attempts": 0,
                "accepted": [],
            }

            successes = 0
            attempts = 0

            while successes < desired_count and attempts < self.max_iterations:
                attempts += 1

                # Labels before this application
                labels_before = self._compute_labels(current_graph)

                # Apply perturbation
                candidate_graph, changes = perturbation.apply(current_graph)

                # Labels after this application
                labels_after = self._compute_labels(candidate_graph)

                # Check for label changes
                changed_nodes = {
                    node: (labels_before.get(node), labels_after[node])
                    for node in labels_after
                    if labels_after[node] != labels_before.get(node)
                }

                if changed_nodes:
                    # Accept: keep the perturbed graph
                    current_graph = candidate_graph
                    successes += 1
                    pert_result["accepted"].append({
                        "changes": changes,
                        "changed_nodes": changed_nodes,
                    })

            pert_result["successful_applications"] = successes
            pert_result["total_attempts"] = attempts
            all_results.append(pert_result)

        return current_graph, {"perturbation_results": all_results}
