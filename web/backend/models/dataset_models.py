"""Request / response models for dataset endpoints."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from web.backend.models.graph_models import LabelingFunctionConfig, MotifConfig
from web.backend.models.perturbation_models import PerturbationConfig


class FolderSourceConfig(BaseModel):
    folder_path: str
    iteration_order: str = "sequential"
    exhaustion_policy: str = "stop"


class DatasetGenerateRequest(BaseModel):
    num_graphs: int = Field(..., ge=1, le=10000)
    motifs: Optional[List[MotifConfig]] = None
    folder_source: Optional[FolderSourceConfig] = None
    composition: str = "sequential"
    composition_params: Dict[str, Any] = Field(default_factory=dict)
    num_extra_vertices: int = Field(0, ge=0)
    num_extra_edges: int = Field(0, ge=0)
    labeling_functions: List[LabelingFunctionConfig] = Field(default_factory=list)
    perturbations: List[PerturbationConfig] = Field(default_factory=list)
    max_perturbation_iterations: int = Field(10, ge=1, le=200)
    output_dir: str = "datasets/output"
    seed: Optional[int] = None

    @model_validator(mode="after")
    def validate_graph_source(self):
        if self.motifs and self.folder_source:
            raise ValueError("Specify either 'motifs' or 'folder_source', not both.")
        if not self.motifs and not self.folder_source:
            raise ValueError("Must specify either 'motifs' or 'folder_source'.")
        return self


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
