"""Perturbation service."""
import web.backend.services  # noqa: F401

from typing import Tuple

from web.backend.models.perturbation_models import (
    ChangedNode,
    EdgeChange,
    EdgePerturbInfo,
    PerturbationRequest,
    PerturbationResponse,
)
from web.backend.services import graph_store, serialization


def apply(request: PerturbationRequest) -> PerturbationResponse:
    """Apply perturbation pipeline. Stores perturbed graph, returns full diff."""
    from graph.perturbation_engine import GraphPerturbation

    original_graph = graph_store.get(request.graph_id)
    original_elements = serialization.graph_to_elements(original_graph)

    edge_params = None
    if request.edge_perturb_params:
        edge_params = {
            "p_remove": request.edge_perturb_params.p_remove,
            "p_add": request.edge_perturb_params.p_add,
            "add_num": request.edge_perturb_params.add_num,
        }

    position = request.edge_perturb_position if edge_params else None

    perturbation = GraphPerturbation(
        original_graph.copy(),
        request.num_nodes_to_remove,
        request.strategy,
        request.max_iterations,
        edge_perturb_params=edge_params,
        edge_perturb_position=position or "after",
    )

    perturbed_graph, result = perturbation.perturb_and_check()

    # Annotate perturbed nodes with classes for the diff view
    changed_raw: dict = result.get("changed_nodes", {})
    removed_raw: list = result.get("removed_nodes", [])

    changed_nodes = [
        ChangedNode(node_id=str(nid), old_label=str(v[0]), new_label=str(v[1]))
        for nid, v in changed_raw.items()
    ]

    # Build edge perturb info
    edge_perturb_info: dict = {}
    for phase, info in result.get("edge_perturb_info", {}).items():
        edge_perturb_info[phase] = EdgePerturbInfo(
            removed_edges=[EdgeChange(source=str(u), target=str(v)) for u, v in info.get("removed_edges", [])],
            added_edges=[EdgeChange(source=str(u), target=str(v)) for u, v in info.get("added_edges", [])],
        )

    perturbed_id = graph_store.store(perturbed_graph)
    perturbed_elements = serialization.graph_to_elements(perturbed_graph)

    success = bool(changed_nodes)
    message = "" if success else result.get("message", "No label changes produced.")

    return PerturbationResponse(
        original_graph_id=request.graph_id,
        perturbed_graph_id=perturbed_id,
        original_elements=original_elements,
        perturbed_elements=perturbed_elements,
        removed_nodes=[str(n) for n in removed_raw],
        changed_nodes=changed_nodes,
        edge_perturb_info=edge_perturb_info,
        success=success,
        message=message,
    )
