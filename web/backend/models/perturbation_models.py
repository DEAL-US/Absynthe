"""Request / response models for perturbation endpoints."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from web.backend.models.common import CytoscapeElement
from web.backend.models.graph_models import LabelingFunctionConfig


class PerturbationConfig(BaseModel):
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)
    count: int = Field(1, ge=1)


class PerturbationRequest(BaseModel):
    graph_id: str
    labeling_functions: List[LabelingFunctionConfig] = Field(default_factory=list)
    perturbations: List[PerturbationConfig] = Field(..., min_length=1)
    max_iterations: int = Field(10, ge=1, le=200)
    seed: Optional[int] = None


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


class PerturbationPreview(BaseModel):
    config_index: int
    perturbation_type: str
    desired_count: int
    success: bool
    message: str = ""
    original_elements: List[CytoscapeElement]
    perturbed_elements: List[CytoscapeElement]
    removed_nodes: List[str]
    changed_nodes: List[ChangedNode]
    edge_perturb_info: Dict[str, EdgePerturbInfo] = Field(default_factory=dict)


class PerturbationResponse(BaseModel):
    original_graph_id: str
    perturbed_graph_id: str
    original_elements: List[CytoscapeElement]
    perturbed_elements: List[CytoscapeElement]
    removed_nodes: List[str]
    changed_nodes: List[ChangedNode]
    edge_perturb_info: Dict[str, EdgePerturbInfo] = Field(default_factory=dict)
    previews: List[PerturbationPreview] = Field(default_factory=list)
    success: bool
    message: str = ""
