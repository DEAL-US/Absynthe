"""Graph generator that samples motif counts per graph from distributions.

Wraps :class:`MotifComposite` so that each call to
:meth:`generate_graph` can produce a graph with a different number of
motif instances, while keeping ``MotifComposite`` and
``GraphDatasetGenerator`` unchanged.
"""

from typing import List, Optional, Tuple

import networkx as nx

from graph.composite_graph_generator import MotifComposite
from interfaces import GraphGenerator
from utils.distributions import IntDistribution, sample_int
from utils.rng import get_rng


class RandomMotifComposite(GraphGenerator):
    """Generator that re-samples motif counts on every call.

    Parameters
    ----------
    motif_configs:
        List of tuples ``(motif_list, count, distribution)`` where:

        * *motif_list* is ``[type, *params]`` (e.g. ``["cycle", 4]``)
        * *count* is the fixed instance count (used when *distribution* is
          ``None``)
        * *distribution* is an optional :class:`IntDistribution`; when
          present it overrides *count* and is sampled on each call.
    """

    def __init__(
        self,
        motif_configs: List[Tuple[list, int, Optional[IntDistribution]]],
    ):
        self.motif_configs = motif_configs

    def generate_graph(self, **kwargs) -> nx.Graph:
        rng = kwargs.get("rng") or get_rng()

        expanded: List[list] = []
        for motif_list, count, dist in self.motif_configs:
            n = sample_int(dist, rng) if dist else count
            expanded.extend([motif_list] * n)

        delegate = MotifComposite(motifs=expanded)
        return delegate.generate_graph(**kwargs)
