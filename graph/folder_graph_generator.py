import logging
import os
import random
from enum import Enum
from typing import List

import networkx as nx

from interfaces import GraphGenerator
from interfaces.exceptions import GraphSourceExhausted

logger = logging.getLogger(__name__)


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

        # Collect .graphml files (non-recursive), sorted alphabetically
        all_files = sorted(
            f for f in os.listdir(folder_path) if f.endswith(".graphml")
        )
        if not all_files:
            raise ValueError(f"No .graphml files found in: {folder_path}")

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
            random.shuffle(self._order)
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

        graph = nx.read_graphml(file_path)
        if isinstance(graph, nx.DiGraph):
            graph = nx.Graph(graph)

        return graph
