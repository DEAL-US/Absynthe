"""Perturbation service."""
from typing import Dict, List

import web.backend.services  # noqa: F401

from interfaces import LabelingFunction
from web.backend.models.perturbation_models import (
    ChangedNode,
    EdgeChange,
    EdgePerturbInfo,
    PerturbationPreview,
    PerturbationRequest,
    PerturbationResponse,
)
from web.backend.services import graph_store, serialization
from web.backend.services.registry import build_labeling_functions, build_perturbation


def _apply_observed_labels(graph, labelers: List[LabelingFunction]) -> None:
    """Compute and store observed labels on the perturbed graph."""
    for labeler in labelers:
        result = labeler.compute_labels(graph)
        for node, label in result.labels.items():
            if node in graph:
                graph.nodes[node]["observed_ground_truth"] = label
                graph.nodes[node]["label"] = label
        for key, value in result.graph_labels.items():
            graph.graph[key] = value


def _map_changed_nodes(changed_raw: dict) -> List[ChangedNode]:
    return [
        ChangedNode(node_id=str(node_id), old_label=str(old), new_label=str(new))
        for node_id, (old, new) in changed_raw.items()
    ]


def _map_edge_info(changes: dict) -> Dict[str, EdgePerturbInfo]:
    removed_edges = [
        EdgeChange(source=str(u), target=str(v))
        for u, v in changes.get("removed_edges", [])
    ]
    added_edges = [
        EdgeChange(source=str(u), target=str(v))
        for u, v in changes.get("added_edges", [])
    ]
    if not removed_edges and not added_edges:
        return {}
    return {
        "applied": EdgePerturbInfo(
            removed_edges=removed_edges,
            added_edges=added_edges,
        )
    }


def apply(request: PerturbationRequest) -> PerturbationResponse:
    """Apply configured perturbations and return preview diff payloads."""
    from graph.perturbation_engine import PerturbationPipeline

    original_graph = graph_store.get(request.graph_id)
    original_elements = serialization.graph_to_elements(original_graph)

    labelers = build_labeling_functions(request.labeling_functions)
    if not request.perturbations:
        raise ValueError("At least one perturbation must be configured.")

    previews: List[PerturbationPreview] = []
    primary_graph = None
    primary_preview = None

    for idx, perturb_config in enumerate(request.perturbations):
        pipeline = PerturbationPipeline(
            perturbations=[(build_perturbation(perturb_config), perturb_config.count)],
            labeling_functions=labelers,
            max_iterations=request.max_iterations,
        )
        results = pipeline.apply_and_check(original_graph)

        if results:
            result = results[0]
            perturbed_graph = result["perturbed_graph"]
            _apply_observed_labels(perturbed_graph, labelers)
            changes = result.get("changes", {})
            changed_nodes = _map_changed_nodes(result.get("changed_nodes", {}))
            success = True
            message = ""
        else:
            perturbed_graph = original_graph.copy()
            _apply_observed_labels(perturbed_graph, labelers)
            changes = {}
            changed_nodes = []
            success = False
            message = (
                f"No label changes produced for perturbation "
                f"'{perturb_config.type}'."
            )

        preview = PerturbationPreview(
            config_index=idx,
            perturbation_type=perturb_config.type,
            desired_count=perturb_config.count,
            success=success,
            message=message,
            original_elements=original_elements,
            perturbed_elements=serialization.graph_to_elements(perturbed_graph),
            removed_nodes=[str(node) for node in changes.get("removed_nodes", [])],
            changed_nodes=changed_nodes,
            edge_perturb_info=_map_edge_info(changes),
        )
        previews.append(preview)

        if primary_preview is None and success:
            primary_preview = preview
            primary_graph = perturbed_graph

    if primary_preview is None:
        primary_preview = previews[0]
        primary_graph = original_graph.copy()
        _apply_observed_labels(primary_graph, labelers)

    perturbed_id = graph_store.store(primary_graph)
    any_success = any(preview.success for preview in previews)

    return PerturbationResponse(
        original_graph_id=request.graph_id,
        perturbed_graph_id=perturbed_id,
        original_elements=primary_preview.original_elements,
        perturbed_elements=primary_preview.perturbed_elements,
        removed_nodes=primary_preview.removed_nodes,
        changed_nodes=primary_preview.changed_nodes,
        edge_perturb_info=primary_preview.edge_perturb_info,
        previews=previews,
        success=any_success,
        message="" if any_success else "No perturbation caused label changes.",
    )
