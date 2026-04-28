import shutil
from pathlib import Path

from utils.rng import set_seed, reset_rng
import networkx as nx
from graph.random_motif_composite import RandomMotifComposite
from graph.dataset_generator import GraphDatasetGenerator
from graph.labeling_functions import MotifLabelingFunction
from graph.perturbations import RemoveNodesPerturbation, RemoveEdgesPerturbation, EdgePerturbation
from utils.distributions import IntDistribution
from visualize import visualize_graph

set_seed(42)

# Normal distribution centered at 3 with std=1 -> mostly 2-4 motifs per graph
count_dist = IntDistribution("normal", {"mean": 3, "std": 1})

NUM_GRAPHS = 300

DATASET_CONFIGS = [
    # Single-motif datasets
    {
        "name": "house",
        "motifs": [
            (["house"], 1, count_dist),
        ],
        "motif_order": ["house"],
    },
    {
        "name": "cycle_5",
        "motifs": [
            (["cycle", 5], 1, count_dist),
        ],
        "motif_order": ["cycle_5"],
    },
    {
        "name": "star_5",
        "motifs": [
            (["star", 5], 1, count_dist),
        ],
        "motif_order": ["star_5"],
    },
    # Multi-motif dataset
    {
        "name": "house_cycle5_star5",
        "motifs": [
            (["house"], 1, IntDistribution("normal", {"mean": 2, "std": 1})),
            (["cycle", 5], 1, IntDistribution("normal", {"mean": 2, "std": 1})),
            (["star", 5], 1, IntDistribution("normal", {"mean": 2, "std": 1})),
        ],
        "motif_order": ["house", "cycle_5", "star_5"],
    },
]

datasets_dir = Path("datasets")
if datasets_dir.exists():
    shutil.rmtree(datasets_dir)
    print("Cleared existing datasets/ folder.")

for config in DATASET_CONFIGS:
    dataset_name = config["name"]
    print(f"Generating dataset: {dataset_name}")

    graph_gen = RandomMotifComposite(motif_configs=config["motifs"])

    labeling = [MotifLabelingFunction(motif_order=config["motif_order"])]

    perturbations = [
        (RemoveNodesPerturbation(num_nodes=1, strategy="motif", folder_name="remove_nodes"), 1),
        (EdgePerturbation(p_remove=0.1, p_add=0.05, folder_name="edge_perturbation"), 1),
        (RemoveEdgesPerturbation(p_remove=0.15, folder_name="remove_edges"), 1),
    ]

    generator = GraphDatasetGenerator(
        graph_generator=graph_gen,
        labeling_functions=labeling,
        perturbations=perturbations,
        output_dir=f"datasets/{dataset_name}",
        max_perturbation_iterations=15,
    )

    metadata = generator.generate_dataset(
        num_graphs=NUM_GRAPHS,
        num_extra_vertices=2,
        num_extra_edges=0,
        composition="sequential",
    )

    print(f"  -> {len(metadata)} perturbed variants from {NUM_GRAPHS} base graphs")

    # print(f"  Saving visualizations...")
    # for entry in metadata:
    #     graph = nx.read_graphml(entry["graph_path"])
    #     title = f"{dataset_name} graph_{entry['graph_id']} (perturbed)"
    #     filename = entry["graph_path"].replace(".graphml", ".png")
    #     visualize_graph(graph, title=title, filename=filename)
    # print()

reset_rng()
print("Done. Datasets saved under datasets/")
