"""Label assignment service."""
import web.backend.services  # noqa: F401

from typing import List, Optional, Tuple

from web.backend.services import graph_store, serialization


def assign(graph_id: str, motif_order: Optional[List[str]] = None) -> Tuple[str, list, dict]:
    """Assign *expected* ground-truth labels. Mutates stored graph in-place.

    Returns (graph_id, updated_elements, label_distribution).
    """
    from graph.label_engine import LabelEngine

    graph = graph_store.get(graph_id)
    engine = LabelEngine()
    engine.label_assignment(graph, motif_order=motif_order)
    graph_store.update(graph_id, graph)

    elements = serialization.graph_to_elements(graph)
    dist = serialization.label_distribution(graph, attr="expected_ground_truth")
    return graph_id, elements, dist


def reassign(graph_id: str, motif_order: Optional[List[str]] = None) -> Tuple[str, list, dict]:
    """Assign *observed* ground-truth labels after perturbation.

    Returns (graph_id, updated_elements, label_distribution).
    """
    from graph.label_engine import LabelEngine

    graph = graph_store.get(graph_id)
    engine = LabelEngine()
    engine.label_reassignment(graph, motif_order=motif_order)
    graph_store.update(graph_id, graph)

    elements = serialization.graph_to_elements(graph)
    dist = serialization.label_distribution(graph, attr="observed_ground_truth")
    return graph_id, elements, dist
