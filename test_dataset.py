import os
from graph.dataset_generator import GraphDatasetGenerator

def test_graph_dataset_generator():
    """
    Test the GraphDatasetGenerator by generating a small dataset.
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

    # Initialize the generator
    generator = GraphDatasetGenerator(output_dir=output_dir)

    # Define motifs and perturbation parameters
    motifs = [["cycle", 4], ["house"]]
    perturbation_params = {
        "num_nodes_to_remove": 2,
        "strategy": "motif",
        "max_iterations": 5,
    }

    # Generate the dataset
    metadata = generator.generate_dataset(num_graphs=3, motifs=motifs, perturbation_params=perturbation_params)

    # Check if the graphs and metadata were saved
    assert os.path.exists(output_dir), "Output directory was not created."
    assert os.path.exists(os.path.join(output_dir, "graphs")), "Graphs directory was not created."
    assert os.path.exists(os.path.join(output_dir, "metadata.json")), "Metadata file was not created."

    # Print metadata for verification
    print("Generated Metadata:")
    for entry in metadata:
        print(entry)

if __name__ == "__main__":
    test_graph_dataset_generator()