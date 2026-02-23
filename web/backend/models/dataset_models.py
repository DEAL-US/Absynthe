"""Request / response models for dataset endpoints."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from web.backend.models.graph_models import LabelingFunctionConfig, MotifConfig
from web.backend.models.perturbation_models import PerturbationConfig


class DatasetGenerateRequest(BaseModel):
    num_graphs: int = Field(..., ge=1, le=10000)
    motifs: List[MotifConfig] = Field(..., min_length=1)
    composition: str = "sequential"
    composition_params: Dict[str, Any] = Field(default_factory=dict)
    num_extra_vertices: int = Field(0, ge=0)
    num_extra_edges: int = Field(0, ge=0)
    labeling_functions: List[LabelingFunctionConfig] = Field(default_factory=list)
    perturbations: List[PerturbationConfig] = Field(default_factory=list)
    max_perturbation_iterations: int = Field(10, ge=1, le=200)
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
