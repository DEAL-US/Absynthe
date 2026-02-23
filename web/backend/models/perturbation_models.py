"""Request / response models for the perturbation endpoints."""
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from web.backend.models.common import CytoscapeElement


class EdgePerturbParams(BaseModel):
    p_remove: float = Field(0.0, ge=0.0, le=1.0)
    p_add: float = Field(0.0, ge=0.0, le=1.0)
    add_num: Optional[int] = Field(None, ge=0)


class PerturbationRequest(BaseModel):
    graph_id: str
    num_nodes_to_remove: int = Field(1, ge=1)
    strategy: str = "random"
    strategy_params: Dict[str, Any] = Field(default_factory=dict)
    max_iterations: int = Field(10, ge=1, le=100)
    edge_perturb_params: Optional[EdgePerturbParams] = None
    edge_perturb_position: str = "after"  # "before", "after", or "none"


class ChangedNode(BaseModel):
    node_id: str
    old_label: str
    new_label: str


class EdgeChange(BaseModel):
    source: str
    target: str


class EdgePerturbInfo(BaseModel):
    removed_edges: List[EdgeChange] = Field(default_factory=list)
    added_edges: List[EdgeChange] = Field(default_factory=list)


class PerturbationResponse(BaseModel):
    original_graph_id: str
    perturbed_graph_id: str
    original_elements: List[CytoscapeElement]
    perturbed_elements: List[CytoscapeElement]
    removed_nodes: List[str]
    changed_nodes: List[ChangedNode]
    edge_perturb_info: Dict[str, EdgePerturbInfo] = Field(default_factory=dict)
    success: bool
    message: str = ""


class LabelAssignRequest(BaseModel):
    graph_id: str
    motif_order: Optional[List[str]] = None
