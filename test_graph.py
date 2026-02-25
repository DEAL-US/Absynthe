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
result = labeling.compute_labels(graph)
for node, label in result.labels.items():
    graph.nodes[node]['expected_ground_truth'] = label
    graph.nodes[node]['label'] = label

for node in graph.nodes():
    print(f"Node {node}: {graph.nodes[node]}")

# Apply perturbation (remove 2 nodes) checking for label changes
# Each result is an independent perturbed variant of the original graph
perturbations = [(RemoveNodesPerturbation(num_nodes=2, strategy="motif"), 1)]
pipeline = PerturbationPipeline(
    perturbations=perturbations,
    labeling_functions=[labeling],
    max_iterations=10,
)
results = pipeline.apply_and_check(graph)

if results:
    # Take the first successful perturbation
    result = results[0]
    perturbed_graph = result["perturbed_graph"]
    print("\nPerturbation changes:", result["changes"])
    print("Changed nodes:", result["changed_nodes"])

    # Store observed ground truth after perturbation
    result_after = labeling.compute_labels(perturbed_graph)
    for node, label in result_after.labels.items():
        perturbed_graph.nodes[node]['observed_ground_truth'] = label
        perturbed_graph.nodes[node]['label'] = label

    print("\nNodes:", list(perturbed_graph.nodes()))
    print("Edges:", list(perturbed_graph.edges()))
    print("Node attributes:")
    for node in perturbed_graph.nodes():
        print(f"Node {node}: {perturbed_graph.nodes[node]}")
    print("Connected components:", list(nx.connected_components(perturbed_graph)))

    # Visualize the perturbed graph
    visualize_graph(perturbed_graph, title="Perturbed Graph")
else:
    print("No perturbation caused label changes.")
