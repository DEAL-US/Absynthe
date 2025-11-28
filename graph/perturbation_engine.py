import random
from typing import List, Tuple, Dict, Optional
import networkx as nx
from statistics import mean


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

    to_remove: List[int] = []

    if n == 0:
        return (G, to_remove)

    strat = (strategy or 'random').lower()

    if strat == 'random':
        to_remove = rng.sample(nodes, n)

    elif strat == 'motif':
        from collections import defaultdict

        motif_groups = defaultdict(list)
        for node in nodes:
            mid = G.nodes[node].get('motif_id')
            if mid is not None:
                motif_groups[mid].append(node)

        # prefer groups with size >= n
        candidates = [grp for grp in motif_groups.values() if len(grp) >= n]
        if candidates:
            chosen = rng.choice(candidates)
            to_remove = rng.sample(chosen, n)
        else:
            # pick from largest group first
            groups_sorted = sorted(motif_groups.values(), key=lambda g: len(g), reverse=True)
            for grp in groups_sorted:
                take = min(n - len(to_remove), len(grp))
                if take > 0:
                    to_remove += rng.sample(grp, take)
                if len(to_remove) >= n:
                    break
            if len(to_remove) < n:
                remaining = [u for u in nodes if u not in to_remove]
                to_remove += rng.sample(remaining, n - len(to_remove))

    elif strat == 'degree':
        mode = params.get('mode', 'high')
        degs = sorted(G.degree(), key=lambda x: x[1], reverse=(mode == 'high'))
        candidates = [u for u, _ in degs]
        to_remove = candidates[:n]

    elif strat == 'centrality':
        centrality = nx.betweenness_centrality(G)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        to_remove = [u for u, _ in sorted_nodes[:n]]

    elif strat == 'role':
        role = params.get('role')
        if role is None:
            # fallback to random
            to_remove = rng.sample(nodes, n)
        else:
            candidates = [u for u in nodes if G.nodes[u].get('role') == role]
            if len(candidates) >= n:
                to_remove = rng.sample(candidates, n)
            else:
                to_remove = candidates + rng.sample([u for u in nodes if u not in candidates], n - len(candidates))

    elif strat == 'by_attribute':
        attr = params.get('attr')
        value = params.get('value')
        if attr is None:
            to_remove = rng.sample(nodes, n)
        else:
            candidates = [u for u in nodes if G.nodes[u].get(attr) == value]
            if len(candidates) >= n:
                to_remove = rng.sample(candidates, n)
            else:
                to_remove = candidates + rng.sample([u for u in nodes if u not in candidates], n - len(candidates))

    else:
        # unknown strategy: fallback to random
        to_remove = rng.sample(nodes, n)

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
