"""Request / response models for the dataset endpoints."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from web.backend.models.graph_models import MotifConfig
from web.backend.models.perturbation_models import EdgePerturbParams


class DatasetPerturbParams(BaseModel):
    num_nodes_to_remove: int = Field(1, ge=1)
    strategy: str = "random"
    strategy_params: Dict[str, Any] = Field(default_factory=dict)
    max_iterations: int = Field(10, ge=1)
    edge_perturb_params: Optional[EdgePerturbParams] = None
    edge_perturb_position: str = "after"


class DatasetGenerateRequest(BaseModel):
    num_graphs: int = Field(..., ge=1, le=10000)
    motifs: List[MotifConfig] = Field(..., min_length=1)
    num_extra_vertices: int = Field(0, ge=0)
    num_extra_edges: int = Field(0, ge=0)
    perturbation_params: Optional[DatasetPerturbParams] = None
    output_dir: str = "datasets/output"


class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending" | "running" | "completed" | "failed"
    current: int
    total: int
    output_dir: Optional[str] = None
    error: Optional[str] = None


class DatasetGraphRecord(BaseModel):
    graph_id: int
    graph_path: str
    perturbation_info: Optional[Dict[str, Any]]


class DatasetListItem(BaseModel):
    output_dir: str
    num_graphs: int
