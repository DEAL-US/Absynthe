import random
from typing import List, Dict
import networkx as nx

def random_strategy(graph: nx.Graph, n: int, params: Dict, rng: random.Random) -> List[int]:
    nodes = list(graph.nodes())
    return rng.sample(nodes, n)

def motif_strategy(graph: nx.Graph, n: int, params: Dict, rng: random.Random) -> List[int]:
    from collections import defaultdict

    nodes = list(graph.nodes())
    motif_groups = defaultdict(list)
    for node in nodes:
        mid = graph.nodes[node].get('motif_id')
        if mid is not None:
            motif_groups[mid].append(node)

    candidates = [grp for grp in motif_groups.values() if len(grp) >= n]
    if candidates:
        chosen = rng.choice(candidates)
        return rng.sample(chosen, n)
    else:
        groups_sorted = sorted(motif_groups.values(), key=lambda g: len(g), reverse=True)
        to_remove = []
        for grp in groups_sorted:
            take = min(n - len(to_remove), len(grp))
            if take > 0:
                to_remove += rng.sample(grp, take)
            if len(to_remove) >= n:
                break
        if len(to_remove) < n:
            remaining = [u for u in nodes if u not in to_remove]
            to_remove += rng.sample(remaining, n - len(to_remove))
        return to_remove

def degree_strategy(graph: nx.Graph, n: int, params: Dict, rng: random.Random) -> List[int]:
    mode = params.get('mode', 'high')
    degs = sorted(graph.degree(), key=lambda x: x[1], reverse=(mode == 'high'))
    return [u for u, _ in degs[:n]]

def centrality_strategy(graph: nx.Graph, n: int, params: Dict, rng: random.Random) -> List[int]:
    centrality = nx.betweenness_centrality(graph)
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    return [u for u, _ in sorted_nodes[:n]]

def role_strategy(graph: nx.Graph, n: int, params: Dict, rng: random.Random) -> List[int]:
    role = params.get('role')
    nodes = list(graph.nodes())
    if role is None:
        return rng.sample(nodes, n)
    candidates = [u for u in nodes if graph.nodes[u].get('role') == role]
    if len(candidates) >= n:
        return rng.sample(candidates, n)
    return candidates + rng.sample([u for u in nodes if u not in candidates], n - len(candidates))

def by_attribute_strategy(graph: nx.Graph, n: int, params: Dict, rng: random.Random) -> List[int]:
    attr = params.get('attr')
    value = params.get('value')
    nodes = list(graph.nodes())
    if attr is None:
        return rng.sample(nodes, n)
    candidates = [u for u in nodes if graph.nodes[u].get(attr) == value]
    if len(candidates) >= n:
        return rng.sample(candidates, n)
    return candidates + rng.sample([u for u in nodes if u not in candidates], n - len(candidates))

STRATEGY_MAP = {
    'random': random_strategy,
    'motif': motif_strategy,
    'degree': degree_strategy,
    'centrality': centrality_strategy,
    'role': role_strategy,
    'by_attribute': by_attribute_strategy,
}