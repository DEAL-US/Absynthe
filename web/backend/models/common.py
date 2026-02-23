"""Shared Pydantic models and Cytoscape serialisation helpers."""
from typing import Any, Dict, List

from pydantic import BaseModel


class NodeData(BaseModel):
    id: str
    label: str = "unknown"
    motif: str = ""
    motif_id: str = ""
    expected_ground_truth: str = ""
    observed_ground_truth: str = ""


class EdgeData(BaseModel):
    id: str
    source: str
    target: str


class CytoscapeElement(BaseModel):
    group: str  # "nodes" or "edges"
    data: Dict[str, Any]
    classes: str = ""


class CytoscapeGraph(BaseModel):
    elements: List[CytoscapeElement]
