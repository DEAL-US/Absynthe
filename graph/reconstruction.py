from typing import Any, Dict

import networkx as nx


def reconstruct_original(perturbed: nx.Graph, changes: Dict[str, Any]) -> nx.Graph:
    """Invert a perturbation to recover the original graph from a perturbed variant.

    Expects the reversible ``changes`` dict produced by the perturbations in
    ``graph.perturbations``:

        {
            "removed_nodes": [{"id", "attrs", "edges": [{"u", "v", "attrs"}]}],
            "removed_edges": [{"u", "v", "attrs"}],
            "added_edges":   [{"u", "v"}],
        }

    Note: attributes reloaded from GraphML arrive as strings; this function
    does not reinterpret their types — it round-trips whatever the variant
    file stores.
    """
    G = perturbed.copy()

    for e in changes.get("added_edges", []):
        if G.has_edge(e["u"], e["v"]):
            G.remove_edge(e["u"], e["v"])

    for e in changes.get("removed_edges", []):
        G.add_edge(e["u"], e["v"], **e.get("attrs", {}))

    for n in changes.get("removed_nodes", []):
        G.add_node(n["id"], **n.get("attrs", {}))
        for e in n.get("edges", []):
            G.add_edge(e["u"], e["v"], **e.get("attrs", {}))

    return G
