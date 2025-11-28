import sys
sys.path.insert(0, '.')
from graph.composite_graph_generator import CompositeGraphGenerator
from visualize import visualize_graph
import networkx as nx
import random

# Set seed for reproducibility
random.seed(42)

gen = CompositeGraphGenerator(motifs=[["cycle", 4], ["house"], ["cycle", 3]])
graph = gen.generate_graph(num_extra_vertices=2, num_extra_edges=3, start=0)
# Assign expected ground truth before perturbation
graph = gen.label_assignment(graph)

# Apply perturbation (remove nodes) and get removed nodes
graph, nodes = gen.remove_important_nodes(graph, 2)
print("Nodos eliminados:", nodes)

# Recompute observed ground truth after perturbation
graph = gen.label_reassignment(graph)

print("Nodos:", list(graph.nodes()))
print("Aristas:", list(graph.edges()))
print("Atributos de nodos:")
for node in graph.nodes():
    print(f"Nodo {node}: {graph.nodes[node]}")
print("Componentes conexas:", list(nx.connected_components(graph)))