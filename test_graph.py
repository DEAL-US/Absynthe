import sys
sys.path.insert(0, '.')
from graph.composite_graph_generator import MotifComposite
from graph.labeling_functions import MotifLabelingFunction
from graph.perturbations import RemoveNodesPerturbation
from graph.perturbation_engine import PerturbationPipeline
from visualize import visualize_graph
import networkx as nx
import random

# Global seed: set once here to control all randomness in the framework
SEED = 42
random.seed(SEED)

gen = MotifComposite(motifs=[["cycle", 4], ["house"], ["cycle", 3]])
graph = gen.generate_graph(num_extra_vertices=2, num_extra_edges=3, start=0)

# Define labeling function with motif order
motif_order = ["house", "cycle_4", "cycle_3"]
labeling = MotifLabelingFunction(motif_order=motif_order)

# Assign expected ground truth before perturbation
labels = labeling.compute_labels(graph)
for node, label in labels.items():
    graph.nodes[node]['expected_ground_truth'] = label
    graph.nodes[node]['label'] = label

for node in graph.nodes():
    print(f"Node {node}: {graph.nodes[node]}")

# Apply perturbation (remove 2 nodes) checking for label changes
perturbations = [(RemoveNodesPerturbation(num_nodes=2, strategy="motif"), 1)]
pipeline = PerturbationPipeline(
    perturbations=perturbations,
    labeling_functions=[labeling],
    max_iterations=10,
)
graph, info = pipeline.apply_and_check(graph)
print("Perturbation info:", info)

# Store observed ground truth after perturbation
labels_after = labeling.compute_labels(graph)
for node, label in labels_after.items():
    graph.nodes[node]['observed_ground_truth'] = label
    graph.nodes[node]['label'] = label

print("Nodes:", list(graph.nodes()))
print("Edges:", list(graph.edges()))
print("Node attributes:")
for node in graph.nodes():
    print(f"Node {node}: {graph.nodes[node]}")
print("Connected components:", list(nx.connected_components(graph)))

# Visualize the graph
visualize_graph(graph, title="Generated Graph with Motifs")
