"""Dataset generation service with progress tracking."""
import web.backend.services  # noqa: F401

import os
import threading
import uuid
from typing import Dict, Optional

from web.backend.models.dataset_models import DatasetGenerateRequest, TaskStatus

_tasks: Dict[str, dict] = {}
_lock = threading.Lock()


# ── Task lifecycle ───────────────────────────────────────────────────────────

def create_task(total: int) -> str:
    task_id = str(uuid.uuid4())
    with _lock:
        _tasks[task_id] = {
            "status": "pending",
            "current": 0,
            "total": total,
            "output_dir": None,
            "error": None,
        }
    return task_id


def _update(task_id: str, **kwargs) -> None:
    with _lock:
        if task_id in _tasks:
            _tasks[task_id].update(kwargs)


def get_status(task_id: str) -> Optional[TaskStatus]:
    with _lock:
        raw = _tasks.get(task_id)
    if raw is None:
        return None
    return TaskStatus(
        task_id=task_id,
        status=raw["status"],
        current=raw["current"],
        total=raw["total"],
        output_dir=raw.get("output_dir"),
        error=raw.get("error"),
    )


# ── Generation worker (runs in background thread) ────────────────────────────

def run_generation(task_id: str, request: DatasetGenerateRequest) -> None:
    """Synchronous generation worker — called from FastAPI BackgroundTasks."""
    import networkx as nx
    from graph.composite_graph_generator import CompositeGraphGenerator
    from graph.perturbation_engine import GraphPerturbation

    _update(task_id, status="running")

    try:
        output_dir = os.path.abspath(request.output_dir)
        graph_dir = os.path.join(output_dir, "graphs")
        os.makedirs(graph_dir, exist_ok=True)

        motif_lists = [m.to_list() for m in request.motifs]
        metadata = []

        for i in range(request.num_graphs):
            gen = CompositeGraphGenerator(motifs=motif_lists)
            graph: nx.Graph = gen.generate_graph(
                num_extra_vertices=request.num_extra_vertices,
                num_extra_edges=request.num_extra_edges,
            )

            perturbation_info = None
            if request.perturbation_params:
                pp = request.perturbation_params
                edge_params = None
                if pp.edge_perturb_params:
                    edge_params = {
                        "p_remove": pp.edge_perturb_params.p_remove,
                        "p_add": pp.edge_perturb_params.p_add,
                        "add_num": pp.edge_perturb_params.add_num,
                    }
                perturb = GraphPerturbation(
                    graph,
                    pp.num_nodes_to_remove,
                    pp.strategy,
                    pp.max_iterations,
                    edge_perturb_params=edge_params,
                    edge_perturb_position=pp.edge_perturb_position,
                )
                graph, raw_info = perturb.perturb_and_check()
                # Serialise to JSON-safe format
                perturbation_info = {
                    "removed_nodes": [str(n) for n in raw_info.get("removed_nodes", [])],
                    "changed_nodes": {
                        str(k): [str(v[0]), str(v[1])]
                        for k, v in raw_info.get("changed_nodes", {}).items()
                    },
                    "edge_perturb_info": {
                        phase: {
                            "removed_edges": [[str(u), str(v)] for u, v in info.get("removed_edges", [])],
                            "added_edges": [[str(u), str(v)] for u, v in info.get("added_edges", [])],
                        }
                        for phase, info in raw_info.get("edge_perturb_info", {}).items()
                    },
                }

            graph_path = os.path.join(graph_dir, f"graph_{i}.graphml")
            nx.write_graphml(graph, graph_path)

            metadata.append({
                "graph_id": i,
                "graph_path": graph_path,
                "perturbation_info": perturbation_info,
            })

            _update(task_id, current=i + 1)

        import json
        with open(os.path.join(output_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        _update(task_id, status="completed", output_dir=output_dir)

    except Exception as exc:  # noqa: BLE001
        _update(task_id, status="failed", error=str(exc))
