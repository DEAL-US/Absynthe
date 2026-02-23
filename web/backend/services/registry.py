"""Plugin registry and builders for web-configurable modules."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import web.backend.services  # noqa: F401
from interfaces import LabelingFunction, Perturbation
from web.backend.models.graph_models import LabelingFunctionConfig
from web.backend.models.perturbation_models import PerturbationConfig

# UI schemas
MOTIF_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "cycle",
        "label": "Cycle",
        "description": "A ring of n nodes",
        "params": [{"name": "len_cycle", "label": "Length", "type": "int", "default": 4, "min": 3}],
    },
    {
        "type": "house",
        "label": "House",
        "description": "5-node house (square base + triangular roof)",
        "params": [],
    },
    {
        "type": "chain",
        "label": "Chain",
        "description": "A linear path of n nodes",
        "params": [{"name": "length", "label": "Length", "type": "int", "default": 3, "min": 2}],
    },
    {
        "type": "star",
        "label": "Star",
        "description": "Central hub with n leaf nodes",
        "params": [{"name": "num_leaves", "label": "Leaves", "type": "int", "default": 3, "min": 1}],
    },
    {
        "type": "gate",
        "label": "Gate",
        "description": "Entry node, two parallel arms, exit node",
        "params": [{"name": "arm_length", "label": "Arm length", "type": "int", "default": 1, "min": 1}],
    },
]

COMPOSITION_SCHEMAS: List[Dict[str, Any]] = [
    {"id": "sequential", "label": "Sequential", "description": "Linear chain between motifs", "params": []},
    {
        "id": "er",
        "label": "Erdos-Renyi",
        "description": "Random edges between motif pairs with probability p",
        "params": [{"name": "p", "label": "Probability", "type": "float", "default": 0.5, "min": 0.0, "max": 1.0}],
    },
    {
        "id": "ba",
        "label": "Barabasi-Albert",
        "description": "Scale-free preferential attachment",
        "params": [{"name": "m", "label": "Attachments (m)", "type": "int", "default": 1, "min": 1}],
    },
    {
        "id": "sbm",
        "label": "Stochastic Block Model",
        "description": "Community-structured composition",
        "params": [
            {"name": "p_in", "label": "p_in", "type": "float", "default": 0.6},
            {"name": "p_out", "label": "p_out", "type": "float", "default": 0.05},
            {"name": "blocks", "label": "Blocks (comma-separated)", "type": "string", "default": ""},
        ],
    },
    {
        "id": "star",
        "label": "Star",
        "description": "One central motif connected to all others",
        "params": [{"name": "center", "label": "Center motif index", "type": "int", "default": 0, "min": 0}],
    },
    {
        "id": "hierarchical",
        "label": "Hierarchical",
        "description": "Motifs grouped into clusters with inter-group connections",
        "params": [{"name": "groups", "label": "Groups", "type": "int", "default": 2, "min": 1}],
    },
]

STRATEGY_SCHEMAS: List[Dict[str, Any]] = [
    {"id": "random", "label": "Random", "description": "Pick nodes at random", "params": []},
    {"id": "motif", "label": "Motif", "description": "Remove nodes from the same motif instance", "params": []},
    {
        "id": "degree",
        "label": "Degree",
        "description": "Highest or lowest degree nodes",
        "params": [{"name": "mode", "label": "Mode", "type": "select", "options": ["high", "low"], "default": "high"}],
    },
    {"id": "centrality", "label": "Centrality", "description": "Highest betweenness centrality", "params": []},
    {
        "id": "role",
        "label": "Role",
        "description": "Nodes matching a specific role attribute",
        "params": [{"name": "role", "label": "Role value", "type": "string", "default": ""}],
    },
    {
        "id": "by_attribute",
        "label": "By Attribute",
        "description": "Nodes matching a custom attribute value",
        "params": [
            {"name": "attr", "label": "Attribute name", "type": "string", "default": "motif"},
            {"name": "value", "label": "Attribute value", "type": "string", "default": ""},
        ],
    },
]

LABELING_FUNCTION_SCHEMAS: List[Dict[str, Any]] = [
    {
        "id": "motif_labeling",
        "label": "Motif Labeling",
        "description": "Assign labels based on motif subgraph membership.",
        "params": [
            {
                "name": "motif_order",
                "label": "Motif order (comma-separated)",
                "type": "string",
                "default": "",
            }
        ],
    }
]

PERTURBATION_SCHEMAS: List[Dict[str, Any]] = [
    {
        "id": "remove_nodes",
        "label": "Remove Nodes",
        "description": "Remove nodes using a selection strategy.",
        "params": [
            {"name": "num_nodes", "label": "Nodes to remove", "type": "int", "default": 1, "min": 1},
            {
                "name": "strategy",
                "label": "Strategy",
                "type": "select",
                "options": [s["id"] for s in STRATEGY_SCHEMAS],
                "default": "random",
            },
            {"name": "mode", "label": "Degree mode", "type": "select", "options": ["high", "low"], "default": "high"},
            {"name": "role", "label": "Role filter", "type": "string", "default": ""},
            {"name": "attr", "label": "Attribute key", "type": "string", "default": ""},
            {"name": "value", "label": "Attribute value", "type": "string", "default": ""},
        ],
    },
    {
        "id": "remove_edges",
        "label": "Remove Edges",
        "description": "Randomly remove edges with probability p_remove.",
        "params": [{"name": "p_remove", "label": "p_remove", "type": "float", "default": 0.1, "min": 0.0, "max": 1.0}],
    },
    {
        "id": "add_edges",
        "label": "Add Edges",
        "description": "Add edges by probability or explicit count.",
        "params": [
            {"name": "p_add", "label": "p_add", "type": "float", "default": 0.05, "min": 0.0, "max": 1.0},
            {"name": "add_num", "label": "add_num", "type": "int", "default": 0, "min": 0},
        ],
    },
    {
        "id": "edge_perturbation",
        "label": "Edge Perturbation",
        "description": "Combined edge removal and addition.",
        "params": [
            {"name": "p_remove", "label": "p_remove", "type": "float", "default": 0.1, "min": 0.0, "max": 1.0},
            {"name": "p_add", "label": "p_add", "type": "float", "default": 0.05, "min": 0.0, "max": 1.0},
            {"name": "add_num", "label": "add_num", "type": "int", "default": 0, "min": 0},
        ],
    },
]


def _parse_csv_list(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return [chunk.strip() for chunk in str(raw).split(",") if chunk.strip()]


def _to_int(value: Any, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_composition_params(params: Dict[str, Any] | None) -> Dict[str, Any]:
    if not params:
        return {}
    normalized = dict(params)
    blocks = normalized.get("blocks")
    if isinstance(blocks, str):
        values = [chunk.strip() for chunk in blocks.split(",") if chunk.strip()]
        normalized["blocks"] = [int(chunk) for chunk in values if chunk.isdigit()]
    return normalized


def build_labeling_functions(
    configs: List[LabelingFunctionConfig] | None,
) -> List[LabelingFunction]:
    from graph.labeling_functions import MotifLabelingFunction

    if not configs:
        return [MotifLabelingFunction()]

    labeling_functions: List[LabelingFunction] = []
    for cfg in configs:
        cfg_type = (cfg.type or "").lower()
        params = cfg.params or {}
        if cfg_type == "motif_labeling":
            motif_order = _parse_csv_list(params.get("motif_order"))
            labeling_functions.append(
                MotifLabelingFunction(motif_order=motif_order or None)
            )
        else:
            raise ValueError(f"Unknown labeling function: {cfg.type}")
    return labeling_functions


def build_perturbation(config: PerturbationConfig) -> Perturbation:
    from graph.perturbations import (
        AddEdgesPerturbation,
        EdgePerturbation,
        RemoveEdgesPerturbation,
        RemoveNodesPerturbation,
    )

    cfg_type = (config.type or "").lower()
    params = config.params or {}

    if cfg_type == "remove_nodes":
        strategy = str(params.get("strategy", "random"))
        num_nodes = max(1, _to_int(params.get("num_nodes"), 1))
        strategy_params: Dict[str, Any] = {}
        if strategy == "degree":
            strategy_params["mode"] = str(params.get("mode", "high"))
        elif strategy == "role":
            role = str(params.get("role", "")).strip()
            if role:
                strategy_params["role"] = role
        elif strategy == "by_attribute":
            attr = str(params.get("attr", "")).strip()
            value = str(params.get("value", "")).strip()
            if attr:
                strategy_params["attr"] = attr
            if value:
                strategy_params["value"] = value
        return RemoveNodesPerturbation(
            num_nodes=num_nodes,
            strategy=strategy,
            params=strategy_params or None,
        )

    if cfg_type == "remove_edges":
        return RemoveEdgesPerturbation(
            p_remove=_to_float(params.get("p_remove"), 0.1)
        )

    if cfg_type == "add_edges":
        add_num = _to_int(params.get("add_num"), 0)
        return AddEdgesPerturbation(
            p_add=_to_float(params.get("p_add"), 0.05),
            add_num=add_num if add_num > 0 else None,
        )

    if cfg_type == "edge_perturbation":
        add_num = _to_int(params.get("add_num"), 0)
        return EdgePerturbation(
            p_remove=_to_float(params.get("p_remove"), 0.1),
            p_add=_to_float(params.get("p_add"), 0.05),
            add_num=add_num if add_num > 0 else None,
        )

    raise ValueError(f"Unknown perturbation type: {config.type}")


def build_perturbations(
    configs: List[PerturbationConfig] | None,
) -> List[Tuple[Perturbation, int]]:
    if not configs:
        return []
    return [(build_perturbation(cfg), cfg.count) for cfg in configs]
