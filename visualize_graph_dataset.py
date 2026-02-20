import networkx as nx
from visualize import visualize_graph

# Cargar un grafo de test_output/graphs (por ejemplo, el primero)
graph_path = "test_output/graphs/graph_0.graphml"
graph = nx.read_graphml(graph_path)

# Imprimir información de los nodos
def print_node_info(graph):
    print("Información de los nodos:")
    for node in graph.nodes(data=True):
        print(node)

print_node_info(graph)

# Visualizar el grafo usando la función proporcionada
visualize_graph(graph, title="Generated Graph with Motifs", filename="pictures/graph_dataset.png")
