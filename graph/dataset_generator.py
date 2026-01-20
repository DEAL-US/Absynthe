import os
import json
import networkx as nx
from graph.composite_graph_generator import CompositeGraphGenerator
from graph.perturbation_engine import GraphPerturbation

class GraphDatasetGenerator:
    def __init__(self, output_dir: str):
        """
        Initialize the dataset generator.

        :param output_dir: Directory where the dataset will be saved.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.graph_dir = os.path.join(self.output_dir, "graphs")
        os.makedirs(self.graph_dir, exist_ok=True)

    def generate_graph(self, motifs, num_extra_vertices=0, num_extra_edges=0):
        """
        Generate a single graph using CompositeGraphGenerator.

        :param motifs: List of motif configurations.
        :param num_extra_vertices: Number of extra vertices to add.
        :param num_extra_edges: Number of extra edges to add.
        :return: Generated graph.
        """
        generator = CompositeGraphGenerator(motifs)
        return generator.generate_graph(num_extra_vertices=num_extra_vertices, num_extra_edges=num_extra_edges)

    def generate_dataset(self, num_graphs, motifs, perturbation_params=None):
        """
        Generate a dataset of graphs.

        :param num_graphs: Number of graphs to generate.
        :param motifs: List of motif configurations for each graph.
        :param perturbation_params: Parameters for perturbations (optional).
        :return: Metadata about the dataset.
        """
        metadata = []

        for i in range(num_graphs):
            graph = self.generate_graph(motifs)

            if perturbation_params:
                perturbation = GraphPerturbation(
                    graph,
                    perturbation_params.get("num_nodes_to_remove", 1),
                    perturbation_params.get("strategy", "random"),
                    perturbation_params.get("max_iterations", 10),
                )
                graph, perturbation_info = perturbation.perturb_and_check()
            else:
                perturbation_info = None

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
        """
        Save a graph to a file.

        :param graph: The graph to save.
        :param path: Path to save the graph.
        """
        nx.write_graphml(graph, path)

    def save_metadata(self, metadata, path):
        """
        Save metadata to a JSON file.

        :param metadata: Metadata to save.
        :param path: Path to save the metadata.
        """
        with open(path, "w") as f:
            json.dump(metadata, f, indent=4)

# Example usage
if __name__ == "__main__":
    generator = GraphDatasetGenerator(output_dir="output")
    motifs = [["cycle", 4], ["house"]]
    perturbation_params = {
        "num_nodes_to_remove": 2,
        "strategy": "motif",
        "max_iterations": 5,
    }
    generator.generate_dataset(num_graphs=5, motifs=motifs, perturbation_params=perturbation_params)