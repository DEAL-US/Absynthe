"""Convert between ``nx.Graph`` and Cytoscape elements JSON."""
from typing import Any, Dict, List

import networkx as nx

from web.backend.models.common import CytoscapeElement


def graph_to_elements(graph: nx.Graph) -> List[CytoscapeElement]:
    """Convert a NetworkX graph to a list of Cytoscape element dicts."""
    elements: List[CytoscapeElement] = []

    for node, attrs in graph.nodes(data=True):
        data: Dict[str, Any] = {"id": str(node)}
        # copy all recognised string attributes
        for key in (
            "label",
            "motif",
            "motif_id",
            "expected_ground_truth",
            "observed_ground_truth",
        ):
            val = attrs.get(key, "")
            data[key] = str(val) if val is not None else ""
        elements.append(CytoscapeElement(group="nodes", data=data))

    for u, v in graph.edges():
        elements.append(
            CytoscapeElement(
                group="edges",
                data={"id": f"{u}-{v}", "source": str(u), "target": str(v)},
            )
        )

    return elements


def label_distribution(graph: nx.Graph, attr: str = "label") -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for _, data in graph.nodes(data=True):
        lbl = str(data.get(attr, "unknown"))
        counts[lbl] = counts.get(lbl, 0) + 1
    return counts
