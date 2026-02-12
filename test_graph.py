import sys
sys.path.insert(0, '.')
from graph.composite_graph_generator import CompositeGraphGenerator
from visualize import visualize_graph
import networkx as nx
import random

# Global seed: set once here to control all randomness in the framework
SEED = 42
random.seed(SEED)


gen = CompositeGraphGenerator(motifs=[["cycle", 4], ["house"], ["cycle", 3]])
graph = gen.generate_graph(num_extra_vertices=2, num_extra_edges=3, start=0)
# Define motif order for labeling (example: ["cycle", "house"])
motif_order = ["house", "cycle_4", "cycle_3"] # Adjust based on actual motif names used in generation
# Assign expected ground truth before perturbation
graph = gen.label_assignment(graph, motif_order=motif_order)
for node in graph.nodes():
    print(f"Node {node}: {graph.nodes[node]}")

# Apply perturbation (remove nodes) and get removed nodes
graph, nodes = gen.remove_important_nodes(graph, 2)
print("Removed nodes:", nodes)

# Recompute observed ground truth after perturbation
graph = gen.label_reassignment(graph, motif_order=motif_order)

print("Nodes:", list(graph.nodes()))
print("Edges:", list(graph.edges()))
print("Node attributes:")
for node in graph.nodes():
    print(f"Node {node}: {graph.nodes[node]}")
print("Connected components:", list(nx.connected_components(graph)))

# Visualize the graph
visualize_graph(graph, title="Generated Graph with Motifs")