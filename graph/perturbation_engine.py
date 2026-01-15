import random
from typing import List, Tuple, Dict, Optional
import networkx as nx
from statistics import mean
from .perturbation_strategies import (
    random_strategy,
    motif_strategy,
    degree_strategy,
    centrality_strategy,
    role_strategy,
    by_attribute_strategy,
    STRATEGY_MAP
)

def remove_nodes(graph: nx.Graph,
                 n: int,
                 strategy: str = 'motif',
                 params: Optional[Dict] = None,
                 rng: Optional[random.Random] = None) -> Tuple[nx.Graph, List[int]]:
    """Remove n nodes according to the requested strategy and return (new_graph, removed_nodes).

    Strategies:
    - 'random': uniform random sampling
    - 'motif': prefer removing nodes from the same motif_id (like previous behavior)
    - 'degree': remove nodes with highest ('mode'='high') or lowest ('mode'='low') degree
    - 'centrality': remove nodes with highest betweenness centrality
    - 'role': remove nodes matching attribute 'role' == params['role'] (sample among them if > n)
    - 'by_attribute': remove nodes where node[attr]==value (params: attr, value)

    Fallback: if the strategy cannot find enough nodes, it will fill with random nodes.
    """
    params = params or {}
    rng = rng or random

    G = graph.copy()
    nodes = list(G.nodes())
    n = min(n, len(nodes))

    if n == 0:
        return (G, [])

    strat = STRATEGY_MAP.get((strategy or 'random').lower())
    if not strat:
        raise ValueError(f"Unknown strategy: {strategy}")

    to_remove = strat(G, n, params, rng)

    # perform removal
    G.remove_nodes_from(to_remove)
    return (G, to_remove)


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
