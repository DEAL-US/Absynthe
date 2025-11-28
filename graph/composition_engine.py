import random
from typing import List, Tuple, Dict, Optional
import networkx as nx


def compose_motifs(n_motifs: int, pattern: str = 'sequential', params: Dict = None, rng: Optional[random.Random] = None) -> List[Tuple[int, int]]:
    """Create motif-level edges according to the requested composition pattern.

    Returns a list of tuples (i, j) indicating motif indices to connect.
    Supported patterns: sequential, er, ba, sbm, star, hierarchical
    """
    params = params or {}
    rnd = rng or random
    edges: List[Tuple[int, int]] = []
    if n_motifs <= 1:
        return edges

    pattern = (pattern or 'sequential').lower()

    if pattern == 'sequential':
        for i in range(n_motifs - 1):
            edges.append((i, i + 1))

    elif pattern == 'er':
        p = float(params.get('p', 0.1))
        for i in range(n_motifs):
            for j in range(i + 1, n_motifs):
                if rnd.random() < p:
                    edges.append((i, j))

    elif pattern == 'ba':
        m = int(params.get('m', 1))
        m = max(1, min(m, max(1, n_motifs - 1)))
        # networkx accepts a seed; derive one from rnd if provided
        seed_for_nx = None
        try:
            seed_for_nx = rnd.randint(0, 2 ** 32 - 1) if rnd is not random else None
        except Exception:
            seed_for_nx = None
        ba = nx.barabasi_albert_graph(n_motifs, m, seed=seed_for_nx)
        for u, v in ba.edges():
            edges.append((u, v))

    elif pattern == 'sbm':
        blocks = params.get('blocks')
        if not blocks:
            return compose_motifs(n_motifs, 'er', {'p': params.get('p', 0.05)})
        p_in = float(params.get('p_in', 0.6))
        p_out = float(params.get('p_out', 0.01))
        assignment: List[int] = []
        for b_idx, size in enumerate(blocks):
            assignment += [b_idx] * size
        assignment = (assignment + [len(blocks) - 1] * n_motifs)[:n_motifs]
        for i in range(n_motifs):
            for j in range(i + 1, n_motifs):
                prob = p_in if assignment[i] == assignment[j] else p_out
                if rnd.random() < prob:
                    edges.append((i, j))

    elif pattern == 'star':
        center = params.get('center') if params is not None else None
        if center is None:
            center = rnd.randrange(n_motifs)
        for i in range(n_motifs):
            if i != center:
                edges.append((center, i))

    elif pattern == 'hierarchical':
        groups = int(params.get('groups', 2))
        groups = max(1, min(groups, n_motifs))
        group_sizes = [n_motifs // groups] * groups
        for i in range(n_motifs % groups):
            group_sizes[i] += 1
        idx = 0
        group_indices: List[List[int]] = []
        for gsize in group_sizes:
            group = list(range(idx, idx + gsize))
            idx += gsize
            group_indices.append(group)
            for u in group:
                for v in group:
                    if u < v:
                        edges.append((u, v))
        leaders = [g[0] for g in group_indices if g]
        for i in range(len(leaders) - 1):
            edges.append((leaders[i], leaders[i + 1]))

    else:
        for i in range(n_motifs - 1):
            edges.append((i, i + 1))

    return edges
