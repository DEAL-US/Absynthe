import networkx as nx
from typing import Optional, List, Dict
from label_assigner import NodeLabelAssigner
from motifs import motif_generators

class LabelEngine(NodeLabelAssigner):
    def assign_labels(self, graph: nx.Graph, motif_order: List[str] = None, node_list: Optional[List[int]] = None) -> Dict[int, str]:
        """
        Assign labels to nodes in the graph or a subgraph based on the specified motif order.

        Args:
            graph (nx.Graph): The graph where labels will be assigned.
            motif_order (list): List of motif names in the desired order. Defaults to all available motifs.
            node_list (Optional[List[int]]): List of nodes to work on a subgraph. If None, the entire graph is used.

        Returns:
            Dict[int, str]: A dictionary mapping nodes to their assigned labels.
        """
        if motif_order is None:
            motif_order = list(motif_generators.keys())

        # Work on an induced subgraph if node_list is provided
        if node_list is not None:
            work_graph = graph.subgraph(node_list).copy()
        else:
            work_graph = graph

        node_labels = {}
        for motif_name in motif_order:
            generator_class = motif_generators.get(motif_name)
            if generator_class:
                generator_class.assign_labels(work_graph)
                for node in work_graph.nodes():
                    node_labels[node] = work_graph.nodes[node].get('motif', 'unknown')
            else:
                print(f"Motif '{motif_name}' not found in motif_generators.")

        # Update the original graph if working on a subgraph
        if node_list is not None:
            for node in work_graph.nodes(data=True):
                graph.nodes[node[0]].update(node[1])

        return node_labels


    def label_assignment(self, graph: nx.Graph, node_list: Optional[List[int]] = None, **kwargs) -> nx.Graph:
        """Compute and store the expected ground-truth labels for the (unperturbed) graph.

        This runs the same labeling logic as `assign_label` and stores the resulting
        label for each node under the attribute `expected_ground_truth`.

        Returns the same graph with attributes written for convenience.
        """
        labels = self.assign_labels(graph, node_list=node_list, **kwargs)
        for node, label in labels.items():
            graph.nodes[node]['expected_ground_truth'] = label
        return graph

    def label_reassignment(self, graph: nx.Graph, node_list: Optional[List[int]] = None, **kwargs) -> nx.Graph:
        """Compute and store the observed ground-truth labels after perturbations.

        Runs the labeling logic (same as `assign_label`) and stores the resulting
        label for each node under `observed_ground_truth`.

        Returns the same graph with attributes written for convenience.
        """
        labels = self.assign_labels(graph, node_list=node_list, **kwargs)
        for node, label in labels.items():
            graph.nodes[node]['observed_ground_truth'] = label
            graph.nodes[node]['label'] = label
        return graph