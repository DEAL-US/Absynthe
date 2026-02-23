"""Request / response models for graph and labeling endpoints."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from web.backend.models.common import CytoscapeElement


class MotifConfig(BaseModel):
    type: str = Field(..., description="Motif type, e.g. 'cycle', 'house', 'star'")
    params: List[Any] = Field(
        default_factory=list,
        description="Positional params for the motif generator, e.g. [4] for cycle",
    )

    def to_list(self) -> list:
        return [self.type] + list(self.params)


class GraphGenerateRequest(BaseModel):
    motifs: List[MotifConfig] = Field(..., min_length=1)
    composition: str = "sequential"
    composition_params: Dict[str, Any] = Field(default_factory=dict)
    num_extra_vertices: int = Field(0, ge=0)
    num_extra_edges: int = Field(0, ge=0)
    seed: Optional[int] = None


class GraphStats(BaseModel):
    num_nodes: int
    num_edges: int
    motif_counts: Dict[str, int]


class GraphGenerateResponse(BaseModel):
    graph_id: str
    elements: List[CytoscapeElement]
    stats: GraphStats


class LabelingFunctionConfig(BaseModel):
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)


class LabelAssignRequest(BaseModel):
    graph_id: str
    labeling_functions: List[LabelingFunctionConfig] = Field(default_factory=list)


class LabelDistribution(BaseModel):
    counts: Dict[str, int]


class LabeledGraphResponse(BaseModel):
    graph_id: str
    elements: List[CytoscapeElement]
    label_distribution: LabelDistribution
