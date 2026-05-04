import logging
import os
from enum import Enum
from typing import List

import networkx as nx

from interfaces import GraphGenerator
from interfaces.exceptions import GraphSourceExhausted
from utils.rng import get_rng

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (".graphml", ".rdf", ".ttl", ".nt", ".n3", ".owl")

_RDF_FORMAT_BY_EXT = {
    ".rdf": "xml",
    ".owl": "xml",
    ".ttl": "turtle",
    ".nt": "nt",
    ".n3": "n3",
}


def _rdf_to_nx(path: str, rdf_format: str) -> nx.Graph:
    """Load an RDF file and project it onto an undirected nx.Graph.

    IRI/blank-node objects become edges (with the predicate stored on the edge);
    literal objects become attributes on the subject node so the resulting graph
    matches the rest of the pipeline (entities-as-nodes only).
    """
    import rdflib

    rdf_graph = rdflib.Graph()
    rdf_graph.parse(path, format=rdf_format)

    g = nx.Graph()
    for s, p, o in rdf_graph:
        s_id = str(s)
        p_str = str(p)
        if not g.has_node(s_id):
            g.add_node(s_id)
        if isinstance(o, rdflib.Literal):
            g.nodes[s_id][p_str] = str(o)
        else:
            o_id = str(o)
            if not g.has_node(o_id):
                g.add_node(o_id)
            g.add_edge(s_id, o_id, predicate=p_str)
    return g


def load_graph_file(path: str) -> nx.Graph:
    """Load a graph file (GraphML or RDF) and return an undirected nx.Graph."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".graphml":
        graph = nx.read_graphml(path)
        if isinstance(graph, nx.DiGraph):
            graph = nx.Graph(graph)
        return graph
    rdf_format = _RDF_FORMAT_BY_EXT.get(ext)
    if rdf_format is None:
        raise ValueError(f"Unsupported graph file extension: {ext}")
    return _rdf_to_nx(path, rdf_format)


class IterationOrder(Enum):
    SEQUENTIAL = "sequential"
    RANDOM = "random"


class ExhaustionPolicy(Enum):
    STOP = "stop"
    RAISE = "raise"
    CYCLE = "cycle"


class FolderGraphGenerator(GraphGenerator):
    """GraphGenerator that loads pre-existing graphs from a folder of GraphML files."""

    def __init__(
        self,
        folder_path: str,
        iteration_order: IterationOrder = IterationOrder.SEQUENTIAL,
        exhaustion_policy: ExhaustionPolicy = ExhaustionPolicy.STOP,
    ):
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        self.folder_path = folder_path
        self.iteration_order = iteration_order
        self.exhaustion_policy = exhaustion_policy

        # Collect supported graph files (non-recursive), sorted alphabetically
        all_files = sorted(
            f for f in os.listdir(folder_path)
            if f.lower().endswith(SUPPORTED_EXTENSIONS)
        )
        if not all_files:
            raise ValueError(
                f"No supported graph files found in: {folder_path} "
                f"(extensions: {', '.join(SUPPORTED_EXTENSIONS)})"
            )

        self._files: List[str] = [
            os.path.join(folder_path, f) for f in all_files
        ]
        self._total = len(self._files)
        self._order: List[int] = []
        self._index = 0
        self._graphs_served = 0

        self._reset_order()

        logger.info("Loaded %d graphs from folder %s", self._total, folder_path)

    def _reset_order(self) -> None:
        """Initialize or re-shuffle the iteration order."""
        if self.iteration_order == IterationOrder.RANDOM:
            self._order = list(range(self._total))
            get_rng().shuffle(self._order)
        else:
            self._order = list(range(self._total))
        self._index = 0

    def generate_graph(self, **kwargs) -> nx.Graph:
        if self._index >= self._total:
            if self.exhaustion_policy == ExhaustionPolicy.CYCLE:
                self._reset_order()
            else:
                raise GraphSourceExhausted(
                    loaded=self._total,
                    requested=self._graphs_served + 1,
                )

        file_path = self._files[self._order[self._index]]
        self._index += 1
        self._graphs_served += 1

        return load_graph_file(file_path)
