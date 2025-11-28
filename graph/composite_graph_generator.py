import networkx as nx
from graph_generator import GraphGenerator
from label_assigner import NodeLabelAssigner
from node_remover import NodeRemover
from motifs import CycleMotifGenerator, HouseMotifGenerator, ChainMotifGenerator, StarMotifGenerator, GateMotifGenerator
from typing import List, Dict, Type, Optional, Tuple
from collections import defaultdict
from graph.perturbation_engine import remove_nodes, perturb_edges
import random
from utils.graph_utils import add_vertices, add_random_edges
from graph.composition_engine import compose_motifs


class CompositeGraphGenerator(GraphGenerator, NodeLabelAssigner, NodeRemover):
    """Generator for composite graphs from a list of motif strings."""

    def __init__(self, motifs: List[List] = None, seed: int = None, rng: Optional[random.Random] = None):
        self.motifs = motifs or []
        self.generators: Dict[str, Type] = {
            "cycle": CycleMotifGenerator,
            "house": HouseMotifGenerator,
            "chain": ChainMotifGenerator,
            "star": StarMotifGenerator,
            "gate": GateMotifGenerator,
        }
        # Default RNG/seed for reproducibility; can be overridden per-call via kwargs
        self.default_seed = 42
        if rng is not None:
            self.rng = rng
        elif seed is not None:
            self.rng = random.Random(seed)
            self.default_seed = seed
        else:
            self.rng = random.Random(self.default_seed)

    def generate_graph(self, num_extra_vertices: int = 0, num_extra_edges: int = 0, **kwargs) -> nx.Graph:
        """Generate a composite graph by combining motifs from the list, then adding extra vertices and edges.

        Args:
            num_extra_vertices (int): Number of additional vertices to add.
            num_extra_edges (int): Number of additional edges to add randomly.
            **kwargs: Additional arguments (e.g., start offset).

        Returns:
            nx.Graph: The combined graph with extra vertices and edges.
        """
        combined_graph = nx.Graph()
        current_start = kwargs.get("start", 0)
        # Track counts per motif type for automatic ID assignment
        motif_counts = defaultdict(int)
        motif_node_sets = []  # To store node sets for connecting motifs

        for motif_list in self.motifs:
            # Parse motif list: [base, param1, param2, ...]
            base = motif_list[0]
            params = motif_list[1:]

            if base not in self.generators:
                raise ValueError(f"Unknown motif type: {base}")

            generator_class = self.generators[base]
            generator = generator_class()

            # Get current ID for this motif type
            current_id = motif_counts[base]

            # Generate motif
            if base == "cycle":
                len_cycle = params[0] if params else 4  # default to 4 if no param
                motif_graph = generator.generate_motif(start=current_start, len_cycle=len_cycle, id=current_id)
            elif base == "house":
                motif_graph = generator.generate_motif(start=current_start, id=current_id)
            else:
                raise ValueError(f"Unsupported motif: {motif_list}")

            # Add to combined graph
            combined_graph.add_nodes_from(motif_graph.nodes(data=True))
            combined_graph.add_edges_from(motif_graph.edges())

            # Store node set for later connection
            motif_node_sets.append(set(motif_graph.nodes()))

            # Update start for next motif (simple offset, adjust as needed)
            current_start += len(motif_graph.nodes())
            # Increment count for this motif type
            motif_counts[base] += 1

        # Compose motifs according to composition pattern
        pattern = kwargs.get('composition', 'sequential')
        comp_params = kwargs.get('composition_params', {}) or {}

        # RNG / seed handling for reproducibility
        rng = kwargs.get('rng')
        seed = kwargs.get('seed')
        if rng is None:
            if seed is not None:
                rng = random.Random(seed)
            else:
                rng = self.rng

        motif_edges = compose_motifs(len(motif_node_sets), pattern, comp_params, rng=rng)
        for i, j in motif_edges:
            if motif_node_sets[i] and motif_node_sets[j]:
                node1 = rng.choice(list(motif_node_sets[i]))
                node2 = rng.choice(list(motif_node_sets[j]))
                combined_graph.add_edge(node1, node2)

        # Add extra vertices, each connected to a random existing node
        combined_graph = add_vertices(combined_graph, num_extra_vertices, rng=rng)

        # Add extra edges randomly
        # utils.add_random_edges expects either p or num_edges; here we pass num_edges
        if num_extra_edges:
            combined_graph = add_random_edges(combined_graph, num_edges=num_extra_edges, rng=rng)

        return combined_graph

    # composition logic moved to `graph.composition_engine.compose_motifs`

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

    def label_assignment(self, graph: nx.Graph, node_list: Optional[List[int]] = None, **kwargs) -> nx.Graph:
        """Compute and store the expected ground-truth labels for the (unperturbed) graph.

        This runs the same labeling logic as `assign_label` and stores the resulting
        label for each node under the attribute `expected_ground_truth`.

        Returns the same graph with attributes written for convenience.
        """
        labels = self.assign_label(graph, node_list=node_list, **kwargs)
        for node, label in labels.items():
            graph.nodes[node]['expected_ground_truth'] = label
            graph.nodes[node]['label'] = label
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

    def remove_important_nodes(self, graph: nx.Graph, n: int) -> Optional[Tuple[nx.Graph, List[int]]]:
        """Remove n random nodes from the graph and reassign labels to the remaining nodes.
        If n >= 2, remove nodes from the same motif (same motif_id).
        If any node's label has changed, return the modified graph and the list of removed nodes.
        Otherwise, return None.

        Args:
            graph (nx.Graph): The input graph.
            n (int): The number of nodes to remove.

        Returns:
            Optional[Tuple[nx.Graph, List[int]]]: The modified graph and list of removed nodes if labels changed, else None.
        """
        # Use the new perturbation engine: default strategy is 'motif' to preserve previous behaviour
        # Use the generator's RNG for reproducibility
        graph_copy, nodes_removed = remove_nodes(graph, n, strategy='motif', params=None, rng=self.rng)

        # Reassign labels to the remaining nodes (persist as observed_ground_truth)
        graph_copy = self.label_reassignment(graph_copy)

        return (graph_copy, nodes_removed)
    
    