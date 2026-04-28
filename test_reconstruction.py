"""Load a perturbed variant from the dataset, reconstruct its original, and visualize both."""

import json
import sys
from pathlib import Path

import networkx as nx

from graph.reconstruction import reconstruct_original
from visualize import visualize_graph


def load_entry(dataset_dir: Path, graph_id: int) -> dict:
    with open(dataset_dir / "metadata.json") as f:
        metadata = json.load(f)
    for entry in metadata:
        if entry["graph_id"] == graph_id:
            return entry
    raise ValueError(f"graph_id {graph_id} not found in {dataset_dir}/metadata.json")


def normalize_changes(changes: dict) -> dict:
    """JSON deserializes dict keys as strings and edge endpoints as strings/ints.
    The perturbed GraphML stores node IDs as strings, so align changes to match.
    """
    def to_str(v):
        return str(v)

    out = {}
    for n in changes.get("removed_nodes", []) or []:
        out.setdefault("removed_nodes", []).append({
            "id": to_str(n["id"]),
            "attrs": n.get("attrs", {}),
            "edges": [
                {"u": to_str(e["u"]), "v": to_str(e["v"]), "attrs": e.get("attrs", {})}
                for e in n.get("edges", [])
            ],
        })
    for e in changes.get("removed_edges", []) or []:
        out.setdefault("removed_edges", []).append({
            "u": to_str(e["u"]), "v": to_str(e["v"]), "attrs": e.get("attrs", {}),
        })
    for e in changes.get("added_edges", []) or []:
        out.setdefault("added_edges", []).append({
            "u": to_str(e["u"]), "v": to_str(e["v"]),
        })
    return out


def main(dataset_dir: str = "datasets/house", graph_id: int = 0) -> None:
    ds = Path(dataset_dir)
    entry = load_entry(ds, graph_id)

    perturbed = nx.read_graphml(entry["graph_path"])
    changes = normalize_changes(entry["perturbation_info"]["changes"])
    reconstructed = reconstruct_original(perturbed, changes)

    print(f"Dataset:      {ds}")
    print(f"Variant id:   {graph_id}  (base_graph_id={entry['base_graph_id']})")
    print(f"Perturbed:    {len(perturbed.nodes())} nodes, {len(perturbed.edges())} edges")
    print(f"Reconstructed:{len(reconstructed.nodes())} nodes, {len(reconstructed.edges())} edges")
    print(f"Changes summary: "
          f"removed_nodes={len(changes.get('removed_nodes', []))}, "
          f"removed_edges={len(changes.get('removed_edges', []))}, "
          f"added_edges={len(changes.get('added_edges', []))}")

    for node in reconstructed.nodes():
        if "expected_ground_truth" in reconstructed.nodes[node]:
            reconstructed.nodes[node]["label"] = reconstructed.nodes[node]["expected_ground_truth"]

    out_dir = Path("pictures/reconstruction")
    visualize_graph(
        perturbed,
        title=f"Perturbed graph_{graph_id}",
        filename=str(out_dir / f"graph_{graph_id}_perturbed.png"),
    )
    visualize_graph(
        reconstructed,
        title=f"Reconstructed original from graph_{graph_id}",
        filename=str(out_dir / f"graph_{graph_id}_reconstructed.png"),
    )
    print(f"Saved visualizations under {out_dir}/")


if __name__ == "__main__":
    ds = sys.argv[1] if len(sys.argv) > 1 else "datasets/house"
    gid = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    main(ds, gid)
