"""Graph generation service."""
import web.backend.services  # noqa: F401 - side-effect import

from collections import defaultdict
from typing import Tuple

import networkx as nx

from web.backend.models.graph_models import GraphGenerateRequest, GraphStats
from web.backend.services import graph_store, serialization
from web.backend.services.registry import normalize_composition_params


def generate(request: GraphGenerateRequest) -> Tuple[str, list, GraphStats]:
    """Generate a composite graph and store it. Returns (graph_id, elements, stats)."""
    import random

    from graph.composite_graph_generator import MotifComposite

    prev_state = None
    if request.seed is not None:
        prev_state = random.getstate()
        random.seed(request.seed)

    try:
        motif_lists = [m.to_list() for m in request.motifs]
        generator = MotifComposite(motifs=motif_lists)
        graph: nx.Graph = generator.generate_graph(
            num_extra_vertices=request.num_extra_vertices,
            num_extra_edges=request.num_extra_edges,
            composition=request.composition,
            composition_params=normalize_composition_params(request.composition_params),
        )
    finally:
        if prev_state is not None:
            random.setstate(prev_state)

    motif_counts: dict = defaultdict(int)
    for _, data in graph.nodes(data=True):
        motif_name = data.get("motif", "")
        if motif_name:
            motif_counts[motif_name] += 1

    stats = GraphStats(
        num_nodes=graph.number_of_nodes(),
        num_edges=graph.number_of_edges(),
        motif_counts=dict(motif_counts),
    )

    graph_id = graph_store.store(graph)
    elements = serialization.graph_to_elements(graph)
    return graph_id, elements, stats
