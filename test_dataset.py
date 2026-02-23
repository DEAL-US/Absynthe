import os
from graph.dataset_generator import GraphDatasetGenerator
from graph.composite_graph_generator import MotifComposite
from graph.labeling_functions import MotifLabelingFunction
from graph.perturbations import RemoveNodesPerturbation, EdgePerturbation


def test_graph_dataset_generator():
    """
    Test the GraphDatasetGenerator with the new pluggable architecture.
    """
    output_dir = "test_output"

    # Clean up previous test output if it exists
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(output_dir)

    # 1. Create pluggable components
    graph_gen = MotifComposite(motifs=[["cycle", 4], ["house"], ["cycle", 3]])

    labeling = [MotifLabelingFunction(motif_order=["cycle_4", "house", "cycle_3"])]

    perturbations = [
        (RemoveNodesPerturbation(num_nodes=2, strategy="motif"), 2),
        (EdgePerturbation(p_remove=0.1), 1),
    ]

    # 2. Create orchestrator with all components
    generator = GraphDatasetGenerator(
        graph_generator=graph_gen,
        labeling_functions=labeling,
        perturbations=perturbations,
        output_dir=output_dir,
        max_perturbation_iterations=5,
    )

    # 3. Generate the dataset
    metadata = generator.generate_dataset(num_graphs=3)

    # 4. Assertions
    assert os.path.exists(output_dir), "Output directory was not created."
    assert os.path.exists(os.path.join(output_dir, "graphs")), "Graphs directory was not created."
    assert os.path.exists(os.path.join(output_dir, "metadata.json")), "Metadata file was not created."

    # Print metadata for verification
    print("Generated Metadata:")
    for entry in metadata:
        print(entry)

    # Check we have originals and variants
    originals = [m for m in metadata if m["is_original"]]
    variants = [m for m in metadata if not m["is_original"]]
    print(f"\nOriginal graphs: {len(originals)}")
    print(f"Perturbed variants: {len(variants)}")


if __name__ == "__main__":
    test_graph_dataset_generator()
