import networkx as nx
from typing import Optional, List, Dict
from label_assigner import NodeLabelAssigner

class LabelEngine(NodeLabelAssigner):
    def assign_label(self, graph: nx.Graph, node_list: Optional[List[int]] = None, **kwargs) -> Dict[int, int]:
        """Compute numeric labels for nodes based on detected motif structures in the graph.

        This function is pure: it computes and returns a mapping node->label without
        mutating the input graph. Use `label_assignment` or `label_reassignment`
        to persist the labels into the graph as `expected_ground_truth` or
        `observed_ground_truth` respectively.

        Labels:
        - 0: Nodes in a house structure
        - 1: Nodes in a cycle_3 (not part of a house)
        - 2: Nodes in a cycle_4 (not part of a house)

        Returns:
            Dict[int,int]: mapping node -> label
        """
        # Work on the induced subgraph if node_list provided
        if node_list is not None:
            work_graph = graph.subgraph(node_list).copy()
            nodes_iter = list(work_graph.nodes())
        else:
            work_graph = graph
            nodes_iter = list(graph.nodes())

        # Find all triangles and 4-cycles in the working graph
        cycle_3s = self.find_all_triangles(work_graph)
        cycle_4s = self.find_all_4_cycles(work_graph)

        # Find houses: pairs of cycle_3 and cycle_4 with exactly 2 common nodes
        houses = set()
        for c3 in cycle_3s:
            for c4 in cycle_4s:
                if len(c3 & c4) == 2:
                    houses.add(c3 | c4)

        # Initialize labels to -1
        node_labels: Dict[int, int] = {node: -1 for node in nodes_iter}

        # Assign to houses (0)
        for house in houses:
            for node in house:
                if node in node_labels:
                    node_labels[node] = 0

        # Assign to cycle_4s not in houses (2)
        for c4 in cycle_4s:
            if not any(c4 <= house for house in houses):
                for node in c4:
                    if node in node_labels and node_labels[node] == -1:
                        node_labels[node] = 2

        # Assign to cycle_3s not in houses (1)
        for c3 in cycle_3s:
            if not any(c3 <= house for house in houses):
                for node in c3:
                    if node in node_labels and node_labels[node] == -1:
                        node_labels[node] = 1

        return node_labels

    def find_all_triangles(self, graph: nx.Graph) -> List[frozenset]:
        """Find all triangles (cycles of length 3) in the graph efficiently."""
        triangles = []
        for u in graph.nodes():
            for v in graph.neighbors(u):
                if u < v:  # To avoid duplicates
                    for w in graph.neighbors(v):
                        if w > v and graph.has_edge(u, w):
                            triangles.append(frozenset([u, v, w]))
        return triangles

    def find_all_4_cycles(self, graph: nx.Graph) -> List[frozenset]:
        """Find all 4-cycles in the graph efficiently."""
        cycles = set()
        for u in graph.nodes():
            for v in graph.neighbors(u):
                if u < v:
                    for w in graph.neighbors(v):
                        if w != u and w > v:
                            for x in graph.neighbors(w):
                                if x != v and x > w and graph.has_edge(u, x):
                                    cycles.add(frozenset([u, v, w, x]))
        return list(cycles)

    def label_assignment(self, graph: nx.Graph, node_list: Optional[List[int]] = None, **kwargs) -> nx.Graph:
        """Compute and store the expected ground-truth labels for the (unperturbed) graph.

        This runs the same labeling logic as `assign_label` and stores the resulting
        label for each node under the attribute `expected_ground_truth`.

        Returns the same graph with attributes written for convenience.
        """
        labels = self.assign_label(graph, node_list=node_list, **kwargs)
        for node, label in labels.items():
            graph.nodes[node]['expected_ground_truth'] = label
        return graph

    def label_reassignment(self, graph: nx.Graph, node_list: Optional[List[int]] = None, **kwargs) -> nx.Graph:
        """Compute and store the observed ground-truth labels after perturbations.

        Runs the labeling logic (same as `assign_label`) and stores the resulting
        label for each node under `observed_ground_truth`.

        Returns the same graph with attributes written for convenience.
        """
        labels = self.assign_label(graph, node_list=node_list, **kwargs)
        for node, label in labels.items():
            graph.nodes[node]['observed_ground_truth'] = label
            graph.nodes[node]['label'] = label
        return graph