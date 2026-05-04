from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .perturbation_hint import PerturbationHint


@dataclass
class LabelingResult:
    """Rich result from a labeling function.

    Attributes:
        labels: Mapping from node ID to its label (node-level labeling).
        graph_labels: Named graph-level labels, keyed by label name.
            Multiple labeling functions can contribute different graph-level
            labels without overwriting each other.
        details: Per-node extra information. Each labeling function
            decides what to include (e.g., motif nodes/edges involved
            in the labeling of each node).
        metadata: Arbitrary global information the labeling function
            wants to communicate (e.g., list of detected motif instances).
        hint: Optional ``PerturbationHint`` the labeling function emits
            for downstream perturbations, signaling which nodes/edges
            are part of the relevant zone. If left as ``None``, the
            perturbation pipeline derives a hint automatically from
            ``details`` (``motif_nodes`` / ``motif_edges``).
    """

    labels: Dict[int, Any]
    graph_labels: Dict[str, Any] = field(default_factory=dict)
    details: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hint: Optional[PerturbationHint] = None
