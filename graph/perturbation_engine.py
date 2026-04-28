from typing import List, Tuple, Dict, Any

import networkx as nx

from interfaces import Perturbation, LabelingFunction
from interfaces.labeling_result import LabelingResult


class PerturbationPipeline:
    """Applies perturbations to a graph, accepting only those that cause label changes.

    Receives a list of (Perturbation, desired_count) pairs and a list of
    LabelingFunction instances. For each pair, the perturbation is applied
    repeatedly to the ORIGINAL graph; each application is checked against
    the labeling functions and only accepted if it causes at least one label
    change. The process continues until the desired count of successful
    (label-changing) applications is reached, or max_iterations total
    attempts are exhausted.

    Each successful application produces an independent perturbed graph
    derived from the same original.
    """

    def __init__(
        self,
        perturbations: List[Tuple[Perturbation, int]],
        labeling_functions: List[LabelingFunction],
        max_iterations: int = 10,
    ):
        """
        Args:
            perturbations: List of (perturbation_instance, desired_count) pairs.
                For each pair, the pipeline will try to apply the perturbation
                desired_count times successfully (i.e., causing label changes).
            labeling_functions: List of labeling functions. Labels from
                later functions overwrite labels from earlier ones for
                the same node.
            max_iterations: Maximum total attempts per perturbation to find
                applications that cause label changes.
        """
        self.perturbations = perturbations
        self.labeling_functions = labeling_functions
        self.max_iterations = max_iterations

    def _compute_labels(self, graph: nx.Graph) -> LabelingResult:
        """Compute labels using all labeling functions.

        Later labeling functions overwrite earlier ones for the same node.
        Graph labels and metadata are merged across all functions.
        """
        merged = LabelingResult(labels={})
        for lf in self.labeling_functions:
            result = lf.compute_labels(graph)
            merged.labels.update(result.labels)
            merged.graph_labels.update(result.graph_labels)
            for node, det in result.details.items():
                merged.details.setdefault(node, {}).update(det)
            merged.metadata.update(result.metadata)
        return merged

    def apply_and_check(self, graph: nx.Graph) -> List[Dict[str, Any]]:
        """Apply perturbations to the original graph, only accepting those that change labels.

        For each (perturbation, desired_count) pair:
          - Apply the perturbation to the ORIGINAL graph (not accumulated)
          - Check if labels changed compared to the original
          - If labels changed: accept (store the perturbed graph)
          - If labels didn't change: discard, try again
          - Stop when desired_count successful applications are reached
            or max_iterations total attempts are exhausted

        Args:
            graph: The original graph. All perturbations are applied to this graph.

        Returns:
            A list of result dicts, one per successful perturbation application.
            Each dict contains:
            - 'perturbed_graph': the independently perturbed graph
            - 'changes': what the perturbation changed (from Perturbation.apply)
            - 'changed_nodes': {node: (old_label, new_label)} for nodes whose label changed
            - 'labeling_result': full LabelingResult for the perturbed graph
            - 'original_labeling_result': full LabelingResult for the original graph
            - 'perturbation_folder': folder_name of the perturbation that produced this variant
        """
        original_result = self._compute_labels(graph)
        original_labels = original_result.labels
        results = []

        for perturbation, desired_count in self.perturbations:
            successes = 0
            attempts = 0

            while successes < desired_count and attempts < self.max_iterations:
                attempts += 1

                # Always apply to the original graph
                candidate_graph, changes = perturbation.apply(graph)

                # Check for label changes
                candidate_result = self._compute_labels(candidate_graph)
                candidate_labels = candidate_result.labels
                changed_nodes = {
                    node: (original_labels.get(node), candidate_labels[node])
                    for node in candidate_labels
                    if candidate_labels[node] != original_labels.get(node)
                }

                if changed_nodes:
                    successes += 1
                    results.append({
                        "perturbed_graph": candidate_graph,
                        "changes": changes,
                        "changed_nodes": changed_nodes,
                        "labeling_result": candidate_result,
                        "original_labeling_result": original_result,
                        "perturbation_folder": perturbation.folder_name,
                    })

        return results
