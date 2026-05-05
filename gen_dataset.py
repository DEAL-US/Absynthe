"""Generate the canonical Absynthe datasets.

Two configuration sources are supported:

  - **Python mode** (default when no CLI argument is given): edit the
    `DATASET_CONFIGS` block below, just like before.
  - **JSON mode**: pass a config file path as a positional argument, or use
    `--json` to load `configs/default.json`. The JSON format mirrors the
    `DatasetGenerateRequest` model used by the web backend, so an experiment
    can be reproduced from a single file.

Examples
    python gen_dataset.py                    # Python mode (DATASET_CONFIGS)
    python gen_dataset.py configs/default.json
    python gen_dataset.py --json             # equivalent to the previous line
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List

from utils.rng import set_seed, reset_rng
from graph.random_motif_composite import RandomMotifComposite
from graph.dataset_generator import GraphDatasetGenerator
from graph.labeling_functions import MotifLabelingFunction
from graph.perturbations import (
    RemoveNodesPerturbation,
    RemoveEdgesPerturbation,
    EdgePerturbation,
)
from utils.distributions import IntDistribution


# ---------------------------------------------------------------------------
# Python-mode configuration (used when no JSON file is provided)
# ---------------------------------------------------------------------------

SEED = 42
NUM_GRAPHS = 300
DATASETS_ROOT = "datasets"
CLEAN_OUTPUT = True

# Normal distribution centered at 3 with std=1 -> mostly 2-4 motifs per graph
count_dist = IntDistribution("normal", {"mean": 3, "std": 1})

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


# ---------------------------------------------------------------------------
# Python-mode adapter: turn DATASET_CONFIGS into the runtime form expected by
# `run_pipeline`.
# ---------------------------------------------------------------------------

def _datasets_from_python_configs() -> List[Dict[str, Any]]:
    datasets: List[Dict[str, Any]] = []
    for config in DATASET_CONFIGS:
        name = config["name"]
        graph_gen = RandomMotifComposite(motif_configs=config["motifs"])
        labeling = [MotifLabelingFunction(motif_order=config["motif_order"])]
        perturbations = [
            (RemoveNodesPerturbation(num_nodes=1, strategy="motif", folder_name="remove_nodes"), 1),
            (EdgePerturbation(p_remove=0.1, p_add=0.05, folder_name="edge_perturbation"), 1),
            (RemoveEdgesPerturbation(p_remove=0.15, folder_name="remove_edges"), 1),
        ]
        datasets.append({
            "name": name,
            "graph_generator": graph_gen,
            "labeling": labeling,
            "perturbations": perturbations,
            "output_dir": f"{DATASETS_ROOT}/{name}",
            "max_perturbation_iterations": 15,
            "gen_kwargs": {
                "num_graphs": NUM_GRAPHS,
                "num_extra_vertices": 2,
                "num_extra_edges": 0,
                "composition": "sequential",
            },
        })
    return datasets


# ---------------------------------------------------------------------------
# JSON-mode adapter: load a JSON suite file and translate each entry to the
# same runtime form via the shared web/backend builders.
# ---------------------------------------------------------------------------

def _datasets_from_json(path: str | Path) -> tuple[List[Dict[str, Any]], int | None, bool]:
    from utils.dataset_config import load_dataset_config
    from web.backend.services.registry import (
        build_graph_generator,
        build_labeling_functions,
        build_perturbations,
        normalize_composition_params,
    )

    suite = load_dataset_config(path)
    datasets: List[Dict[str, Any]] = []
    for name, request in zip(suite.names, suite.datasets):
        datasets.append({
            "name": name,
            "graph_generator": build_graph_generator(request),
            "labeling": build_labeling_functions(request.labeling_functions),
            "perturbations": build_perturbations(request.perturbations),
            "output_dir": request.output_dir,
            "max_perturbation_iterations": request.max_perturbation_iterations,
            "gen_kwargs": {
                "num_graphs": request.num_graphs,
                "num_extra_vertices": request.num_extra_vertices,
                "num_extra_edges": request.num_extra_edges,
                "composition": request.composition,
                "composition_params": normalize_composition_params(request.composition_params),
            },
        })
    return datasets, suite.seed, suite.clean_output


# ---------------------------------------------------------------------------
# Generation pipeline (shared by both modes).
# ---------------------------------------------------------------------------

def run_pipeline(
    datasets: List[Dict[str, Any]],
    *,
    seed: int | None,
    clean_output: bool,
    datasets_root: str,
) -> None:
    if seed is not None:
        set_seed(seed)

    root = Path(datasets_root)
    if clean_output and root.exists():
        shutil.rmtree(root)
        print(f"Cleared existing {root}/ folder.")

    for entry in datasets:
        name = entry["name"]
        print(f"Generating dataset: {name}")

        generator = GraphDatasetGenerator(
            graph_generator=entry["graph_generator"],
            labeling_functions=entry["labeling"],
            perturbations=entry["perturbations"],
            output_dir=entry["output_dir"],
            max_perturbation_iterations=entry["max_perturbation_iterations"],
        )

        metadata = generator.generate_dataset(**entry["gen_kwargs"])
        num_graphs = entry["gen_kwargs"]["num_graphs"]
        print(f"  -> {len(metadata)} perturbed variants from {num_graphs} base graphs")

        # print(f"  Saving visualizations...")
        # for entry in metadata:
        #     graph = nx.read_graphml(entry["graph_path"])
        #     title = f"{dataset_name} graph_{entry['graph_id']} (perturbed)"
        #     filename = entry["graph_path"].replace(".graphml", ".png")
        #     visualize_graph(graph, title=title, filename=filename)
    
        # originals_dir = Path(f"datasets/{dataset_name}/originals")
        # for orig_path in sorted(originals_dir.glob("*.graphml")):
        #     graph = nx.read_graphml(str(orig_path))
        #     title = f"{dataset_name} {orig_path.stem} (original)"
        #     filename = str(orig_path.with_suffix(".png"))
        #     visualize_graph(graph, title=title, filename=filename)
        # print()

    if seed is not None:
        reset_rng()
    print(f"Done. Datasets saved under {datasets_root}/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

DEFAULT_JSON_PATH = "configs/default.json"


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "config",
        nargs="?",
        default=None,
        help="Optional path to a JSON config file. If omitted, uses the in-script DATASET_CONFIGS.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help=f"Use JSON mode with the default config at {DEFAULT_JSON_PATH}.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = _parse_args(argv if argv is not None else sys.argv[1:])

    config_path: str | None = args.config
    if config_path is None and args.json:
        config_path = DEFAULT_JSON_PATH

    if config_path is None:
        datasets = _datasets_from_python_configs()
        run_pipeline(
            datasets,
            seed=SEED,
            clean_output=CLEAN_OUTPUT,
            datasets_root=DATASETS_ROOT,
        )
    else:
        datasets, seed, clean_output = _datasets_from_json(config_path)
        # The JSON's per-dataset output_dirs are absolute or relative paths set
        # by the loader; pick the common parent as the cleanup root if every
        # dataset shares one, otherwise fall back to "datasets".
        roots = {Path(d["output_dir"]).parent.as_posix() for d in datasets}
        datasets_root = roots.pop() if len(roots) == 1 else "datasets"
        run_pipeline(
            datasets,
            seed=seed,
            clean_output=clean_output,
            datasets_root=datasets_root,
        )


if __name__ == "__main__":
    main()
