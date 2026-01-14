import networkx as nx
from graph_generator import GraphGenerator
from graph.label_engine import LabelEngine
from node_remover import NodeRemover
from motifs import CycleMotifGenerator, HouseMotifGenerator, ChainMotifGenerator, StarMotifGenerator, GateMotifGenerator
from typing import List, Dict, Type, Optional, Tuple
from collections import defaultdict
from graph.perturbation_engine import remove_nodes, perturb_edges
import random
from utils.graph_utils import add_vertices, add_random_edges
from graph.composition_engine import compose_motifs


class CompositeGraphGenerator(GraphGenerator, LabelEngine, NodeRemover):
    """Generator for composite graphs from a list of motif strings."""

    def __init__(self, motifs: List[List] = None):
        self.motifs = motifs or []
        self.generators: Dict[str, Type] = {
            "cycle": CycleMotifGenerator,
            "house": HouseMotifGenerator,
            "chain": ChainMotifGenerator,
            "star": StarMotifGenerator,
            "gate": GateMotifGenerator,
        }

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

        motif_edges = compose_motifs(len(motif_node_sets), pattern, comp_params)
        for i, j in motif_edges:
            if motif_node_sets[i] and motif_node_sets[j]:
                node1 = random.choice(list(motif_node_sets[i]))
                node2 = random.choice(list(motif_node_sets[j]))
                combined_graph.add_edge(node1, node2)

        # Add extra vertices, each connected to a random existing node
        combined_graph = add_vertices(combined_graph, num_extra_vertices)

        # Add extra edges randomly
        # utils.add_random_edges expects either p or num_edges; here we pass num_edges
        if num_extra_edges:
            combined_graph = add_random_edges(combined_graph, num_edges=num_extra_edges)

        return combined_graph

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
        graph_copy, nodes_removed = remove_nodes(graph, n, strategy='motif', params=None)

        # Reassign labels to the remaining nodes (persist as observed_ground_truth)
        graph_copy = self.label_reassignment(graph_copy)

        return (graph_copy, nodes_removed)

