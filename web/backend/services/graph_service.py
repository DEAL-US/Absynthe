"""Graph generation service."""
# Ensure project root is on sys.path
import web.backend.services  # noqa: F401 — side-effect import

from collections import defaultdict
from typing import Tuple

import networkx as nx

from web.backend.models.graph_models import GraphGenerateRequest, GraphStats
from web.backend.services import graph_store, serialization


def generate(request: GraphGenerateRequest) -> Tuple[str, list, GraphStats]:
    """Generate a composite graph and store it. Returns (graph_id, elements, stats)."""
    import random

    from graph.composite_graph_generator import CompositeGraphGenerator

    rng = random.Random(request.seed)

    motif_lists = [m.to_list() for m in request.motifs]
    gen = CompositeGraphGenerator(motifs=motif_lists)

    graph: nx.Graph = gen.generate_graph(
        num_extra_vertices=request.num_extra_vertices,
        num_extra_edges=request.num_extra_edges,
        composition=request.composition,
        composition_params=request.composition_params,
    )

    # Collect stats
    motif_counts: dict = defaultdict(int)
    for _, data in graph.nodes(data=True):
        m = data.get("motif", "")
        if m:
            motif_counts[m] += 1

    stats = GraphStats(
        num_nodes=graph.number_of_nodes(),
        num_edges=graph.number_of_edges(),
        motif_counts=dict(motif_counts),
    )

    graph_id = graph_store.store(graph)
    elements = serialization.graph_to_elements(graph)
    return graph_id, elements, stats
