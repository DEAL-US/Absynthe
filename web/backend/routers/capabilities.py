"""Capability endpoints — expose available motifs, strategies and compositions."""
import inspect
from typing import Any, Dict, List

from fastapi import APIRouter

import web.backend.services  # noqa: F401 — ensures sys.path is set

router = APIRouter()

# ── Motif metadata (parameter schemas) ───────────────────────────────────────
# Manually curated so the frontend can render correct forms immediately
# without complex runtime introspection.

_MOTIF_SCHEMAS: List[Dict[str, Any]] = [
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

_STRATEGIES: List[Dict[str, Any]] = [
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

_COMPOSITIONS: List[Dict[str, Any]] = [
    {"id": "sequential", "label": "Sequential", "description": "Linear chain between motifs", "params": []},
    {
        "id": "er",
        "label": "Erdős–Rényi",
        "description": "Random edges between motif pairs with probability p",
        "params": [{"name": "p", "label": "Probability", "type": "float", "default": 0.5, "min": 0.0, "max": 1.0}],
    },
    {
        "id": "ba",
        "label": "Barabási–Albert",
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
        ],
    },
    {
        "id": "star",
        "label": "Star",
        "description": "One central motif connected to all others",
        "params": [],
    },
    {
        "id": "hierarchical",
        "label": "Hierarchical",
        "description": "Motifs grouped into clusters with inter-group connections",
        "params": [{"name": "groups", "label": "Groups", "type": "int", "default": 2, "min": 1}],
    },
]


@router.get("/motifs")
async def get_motifs() -> list:
    return _MOTIF_SCHEMAS


@router.get("/strategies")
async def get_strategies() -> list:
    return _STRATEGIES


@router.get("/compositions")
async def get_compositions() -> list:
    return _COMPOSITIONS
