from dataclasses import dataclass, field
from typing import Set, Tuple


@dataclass
class PerturbationHint:
    """Hint produced by a labeling function about which zone of a graph
    is relevant for perturbation.

    A perturbation can use this hint to focus its action on the nodes and
    edges the labeler considers meaningful (e.g., the nodes/edges that
    belong to a detected motif), instead of touching arbitrary parts of
    the graph.

    Attributes:
        nodes: Set of node IDs in the relevant zone.
        edges: Set of edges in the relevant zone, stored as normalized
            (min, max) tuples for undirected graphs.
    """

    nodes: Set[int] = field(default_factory=set)
    edges: Set[Tuple[int, int]] = field(default_factory=set)

    def is_empty(self) -> bool:
        return not self.nodes and not self.edges

    def merge(self, other: "PerturbationHint") -> "PerturbationHint":
        return PerturbationHint(
            nodes=self.nodes | other.nodes,
            edges=self.edges | other.edges,
        )

    @staticmethod
    def normalize_edge(u: int, v: int) -> Tuple[int, int]:
        return (u, v) if u <= v else (v, u)
