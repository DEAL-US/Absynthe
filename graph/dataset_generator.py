import os
import json
from typing import List, Tuple, Dict, Any, Optional
import networkx as nx
from graph_generator import GraphGenerator
from labeling_function import LabelingFunction
from perturbation import Perturbation
from graph.perturbation_engine import PerturbationPipeline


class GraphDatasetGenerator:
    """Orchestrator for generating datasets of graphs.

    Receives pluggable components:
    - A GraphGenerator instance for creating graphs
    - A list of LabelingFunction instances for computing labels
    - A list of (Perturbation, count) pairs for perturbing graphs
    - Output configuration

    Changing the components (generator, labeling functions, perturbations)
    changes the behavior without modifying this class.
    """

    def __init__(
        self,
        graph_generator: GraphGenerator,
        labeling_functions: Optional[List[LabelingFunction]] = None,
        perturbations: Optional[List[Tuple[Perturbation, int]]] = None,
        output_dir: str = "output",
        max_perturbation_iterations: int = 10,
    ):
        """
        Args:
            graph_generator: Instance of a GraphGenerator implementation.
            labeling_functions: List of LabelingFunction implementations.
                If None, no labeling is performed.
            perturbations: List of (Perturbation, desired_count) pairs.
                Each perturbation is applied up to desired_count times,
                only accepting applications that cause label changes.
                If None, no perturbations are applied.
            output_dir: Directory where the dataset will be saved.
            max_perturbation_iterations: Maximum total attempts per
                perturbation to find label-changing applications.
        """
        self.graph_generator = graph_generator
        self.labeling_functions = labeling_functions or []
        self.perturbations = perturbations or []
        self.output_dir = output_dir
        self.max_perturbation_iterations = max_perturbation_iterations

        os.makedirs(self.output_dir, exist_ok=True)
        self.graph_dir = os.path.join(self.output_dir, "graphs")
        os.makedirs(self.graph_dir, exist_ok=True)

    def _compute_and_store_labels(self, graph: nx.Graph, attribute_name: str) -> None:
        """Compute labels using all labeling functions and store them as node attributes.

        Args:
            graph: The graph to label (modified in place).
            attribute_name: Node attribute name to store labels under
                            (e.g., 'expected_ground_truth', 'observed_ground_truth').
        """
        for lf in self.labeling_functions:
            labels = lf.compute_labels(graph)
            for node, label in labels.items():
                graph.nodes[node][attribute_name] = label
                graph.nodes[node]['label'] = label

    def generate_dataset(self, num_graphs: int, **graph_kwargs) -> List[Dict[str, Any]]:
        """Generate a dataset of graphs.

        For each graph:
        1. Generate the graph using graph_generator
        2. Compute and store expected labels (pre-perturbation)
        3. Apply perturbations (only accepting those that change labels)
        4. Compute and store observed labels (post-perturbation)
        5. Save to disk

        Args:
            num_graphs: Number of graphs to generate.
            **graph_kwargs: Extra keyword arguments passed to
                graph_generator.generate_graph().

        Returns:
            Metadata list with one entry per graph.
        """
        metadata = []

        for i in range(num_graphs):
            # 1. Generate graph
            graph = self.graph_generator.generate_graph(**graph_kwargs)

            # 2. Compute and store expected labels (before perturbation)
            if self.labeling_functions:
                self._compute_and_store_labels(graph, 'expected_ground_truth')

            # 3. Apply perturbations (if any)
            perturbation_info = None
            if self.perturbations and self.labeling_functions:
                pipeline = PerturbationPipeline(
                    perturbations=self.perturbations,
                    labeling_functions=self.labeling_functions,
                    max_iterations=self.max_perturbation_iterations,
                )
                graph, perturbation_info = pipeline.apply_and_check(graph)

                # 4. Compute and store observed labels (after perturbation)
                self._compute_and_store_labels(graph, 'observed_ground_truth')

            # 5. Save
            graph_path = os.path.join(self.graph_dir, f"graph_{i}.graphml")
            self.save_graph(graph, graph_path)

            metadata.append({
                "graph_id": i,
                "graph_path": graph_path,
                "perturbation_info": perturbation_info,
            })

        metadata_path = os.path.join(self.output_dir, "metadata.json")
        self.save_metadata(metadata, metadata_path)
        return metadata

    def save_graph(self, graph, path):
        """Save a graph to GraphML format."""
        nx.write_graphml(graph, path)

    def save_metadata(self, metadata, path):
        """Save metadata to a JSON file."""
        with open(path, "w") as f:
            json.dump(metadata, f, indent=4, default=str)
