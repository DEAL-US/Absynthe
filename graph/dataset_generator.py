import os
import json
import warnings
from typing import List, Tuple, Dict, Any, Optional

import networkx as nx

from interfaces import GraphGenerator, LabelingFunction, Perturbation
from interfaces.exceptions import GraphSourceExhausted
from interfaces.labeling_result import LabelingResult
from graph.perturbation_engine import PerturbationPipeline


class GraphDatasetGenerator:
    """Orchestrator for generating datasets of graphs.

    Receives pluggable components:
    - A GraphGenerator instance for creating graphs
    - A list of LabelingFunction instances for computing labels
    - A list of (Perturbation, count) pairs for perturbing graphs
    - Output configuration

    For each original graph, the pipeline generates multiple perturbed
    variants (one per successful perturbation application). Each variant
    is saved as a separate graph in the dataset.
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
                Each perturbation is applied to the ORIGINAL graph up to
                desired_count times, only accepting applications that
                cause label changes.
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
        self.originals_dir = os.path.join(self.output_dir, "originals")
        os.makedirs(self.originals_dir, exist_ok=True)

        self._perturbation_dirs: Dict[str, str] = {}
        for perturbation, _ in self.perturbations:
            folder = perturbation.folder_name
            if folder in self._perturbation_dirs:
                raise ValueError(
                    f"Duplicate perturbation folder_name '{folder}': "
                    "use distinct names per perturbation instance."
                )
            pert_dir = os.path.join(self.output_dir, folder)
            os.makedirs(pert_dir, exist_ok=True)
            self._perturbation_dirs[folder] = pert_dir

    def _compute_and_store_labels(self, graph: nx.Graph, attribute_name: str) -> LabelingResult:
        """Compute labels using all labeling functions and store them as node/graph attributes.

        Args:
            graph: The graph to label (modified in place).
            attribute_name: Node attribute name to store labels under
                            (e.g., 'expected_ground_truth', 'observed_ground_truth').

        Returns:
            The merged ``LabelingResult`` from all labeling functions.
        """
        merged = LabelingResult(labels={})
        for lf in self.labeling_functions:
            result = lf.compute_labels(graph)
            for node, label in result.labels.items():
                graph.nodes[node][attribute_name] = label
                graph.nodes[node]['label'] = label
            merged.labels.update(result.labels)
            merged.graph_labels.update(result.graph_labels)
            for node, det in result.details.items():
                merged.details.setdefault(node, {}).update(det)
            merged.metadata.update(result.metadata)
        # Store graph-level labels as graph attributes
        for key, value in merged.graph_labels.items():
            graph.graph[key] = value
        return merged

    def generate_dataset(self, num_graphs: int, **graph_kwargs) -> List[Dict[str, Any]]:
        """Generate a dataset of perturbed graph variants.

        For each base graph:
        1. Generate the graph using graph_generator
        2. Compute expected labels (pre-perturbation) so the pipeline can
           detect label changes and surviving nodes inherit the labels
        3. Apply perturbations to the ORIGINAL graph, each producing an
           independent perturbed variant
        4. For each variant, compute observed labels and save it

        The base (unperturbed) graph is written to ``originals/graph_<i>.graphml``
        for every base graph. Each perturbed variant is written to a per-perturbation
        subfolder named after the perturbation's ``folder_name``. Each variant's
        metadata entry references the original via ``original_graph_path`` and
        carries a reversible ``perturbation_info.changes`` dict — see
        ``graph.reconstruction.reconstruct_original``.

        Args:
            num_graphs: Number of base graphs to generate.
            **graph_kwargs: Extra keyword arguments passed to
                graph_generator.generate_graph().

        Returns:
            Metadata list with one entry per saved perturbed variant.
        """
        metadata = []
        graph_counter = 0

        for i in range(num_graphs):
            try:
                graph = self.graph_generator.generate_graph(**graph_kwargs)
            except GraphSourceExhausted as e:
                warnings.warn(
                    f"Graph source exhausted after {e.loaded} graphs "
                    f"(requested {e.requested}). Stopping generation early."
                )
                break

            labeling_result = None
            if self.labeling_functions:
                labeling_result = self._compute_and_store_labels(graph, 'expected_ground_truth')

            base_graph_labels = None
            base_motif_instances = None
            if labeling_result:
                if labeling_result.graph_labels:
                    base_graph_labels = dict(labeling_result.graph_labels)
                instances = labeling_result.metadata.get("instances")
                if instances:
                    base_motif_instances = [
                        {
                            "motif_name": inst["motif_name"],
                            "nodes": sorted(inst["nodes"]),
                            "edges": sorted([list(e) for e in inst["edges"]]),
                        }
                        for inst in instances
                    ]

            original_path = os.path.join(self.originals_dir, f"graph_{i}.graphml")
            self.save_graph(graph, original_path)

            if not (self.perturbations and self.labeling_functions):
                continue

            pipeline = PerturbationPipeline(
                perturbations=self.perturbations,
                labeling_functions=self.labeling_functions,
                max_iterations=self.max_perturbation_iterations,
            )
            results = pipeline.apply_and_check(graph)

            for result in results:
                perturbed = result["perturbed_graph"]
                self._compute_and_store_labels(perturbed, 'observed_ground_truth')

                pert_folder = result["perturbation_folder"]
                pert_dir = self._perturbation_dirs[pert_folder]
                variant_path = os.path.join(
                    pert_dir, f"graph_{graph_counter}.graphml"
                )
                self.save_graph(perturbed, variant_path)
                entry: Dict[str, Any] = {
                    "graph_id": graph_counter,
                    "base_graph_id": i,
                    "graph_path": variant_path,
                    "original_graph_path": original_path,
                    "perturbation_name": pert_folder,
                    "perturbation_info": {
                        "changes": result["changes"],
                        "changed_nodes": result["changed_nodes"],
                    },
                }
                if base_graph_labels:
                    entry["graph_labels"] = base_graph_labels
                if base_motif_instances:
                    entry["motif_instances"] = base_motif_instances
                metadata.append(entry)
                graph_counter += 1

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
