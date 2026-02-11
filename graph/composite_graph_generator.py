import networkx as nx
from graph_generator import GraphGenerator
from graph.label_engine import LabelEngine
from node_remover import NodeRemover
from motifs import motif_generators
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
        self.generators = motif_generators

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

    def remove_important_nodes(self, graph: nx.Graph, n: int, strategy: str = 'motif', max_iterations: int = 10) -> Tuple[nx.Graph, Dict]:
        """
        Remove important nodes using the GraphPerturbation class.

        Args:
            graph (nx.Graph): The input graph.
            n (int): The number of nodes to remove.
            strategy (str): Strategy for selecting nodes to remove.
            max_iterations (int): Maximum number of iterations to find a valid perturbation.

        Returns:
            Tuple[nx.Graph, Dict]: The perturbed graph and details of the perturbation. If unsuccessful, returns the original graph and an empty dictionary.
        """
        from graph.perturbation_engine import GraphPerturbation

        perturbation = GraphPerturbation(graph, n, strategy, max_iterations)
        perturbed_graph, result = perturbation.perturb_and_check()

        if perturbed_graph:
            return perturbed_graph, result

        # Return the original graph and an empty dictionary if perturbation fails
        return graph, {}

