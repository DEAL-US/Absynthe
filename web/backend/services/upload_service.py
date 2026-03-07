"""Service for uploading and validating GraphML files."""
import web.backend.services  # noqa: F401 - side-effect import

import os
import shutil
import tempfile
import threading
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import networkx as nx
from fastapi import UploadFile

from web.backend.models.graph_models import GraphStats
from web.backend.services import graph_store, serialization

_temp_dirs: Dict[str, str] = {}
_lock = threading.Lock()


def upload(
    files: List[UploadFile],
) -> Tuple[str, list, GraphStats, int, Optional[str], list]:
    """Validate, save, and load uploaded GraphML files.

    Returns (graph_id, elements, stats, file_count, folder_path, warnings).
    """
    if not files:
        raise ValueError("No files provided.")

    temp_dir = tempfile.mkdtemp(prefix="graphtender_upload_")
    valid_paths: List[str] = []
    warnings: List[Dict[str, str]] = []

    try:
        for f in files:
            filename = f.filename or "unknown"

            if not filename.lower().endswith(".graphml"):
                warnings.append({"filename": filename, "error": "File must have a .graphml extension."})
                continue

            dest = os.path.join(temp_dir, filename)
            content = f.file.read()
            with open(dest, "wb") as fh:
                fh.write(content)

            # Validate by parsing
            try:
                nx.read_graphml(dest)
                valid_paths.append(dest)
            except Exception as exc:
                warnings.append({"filename": filename, "error": f"Invalid GraphML: {exc}"})
                os.remove(dest)

        if not valid_paths:
            error_details = "; ".join(f"{w['filename']}: {w['error']}" for w in warnings)
            raise ValueError(f"No valid GraphML files uploaded. {error_details}")

        # Load first graph (alphabetical order) for preview
        valid_paths.sort(key=lambda p: os.path.basename(p))
        first_path = valid_paths[0]
        graph = nx.read_graphml(first_path)
        if isinstance(graph, nx.DiGraph):
            graph = nx.Graph(graph)

        # Compute stats (same pattern as graph_service.py)
        motif_counts: dict = defaultdict(int)
        for _, data in graph.nodes(data=True):
            motif_name = data.get("motif", "")
            if motif_name:
                motif_counts[motif_name] += 1

        stats = GraphStats(
            num_nodes=graph.number_of_nodes(),
            num_edges=graph.number_of_edges(),
            motif_counts=dict(motif_counts),
        )

        graph_id = graph_store.store(graph)
        elements = serialization.graph_to_elements(graph)
        file_count = len(valid_paths)

        if file_count == 1:
            # Single file — temp dir no longer needed
            shutil.rmtree(temp_dir, ignore_errors=True)
            folder_path = None
        else:
            folder_path = temp_dir
            with _lock:
                _temp_dirs[graph_id] = temp_dir

        return graph_id, elements, stats, file_count, folder_path, warnings

    except Exception:
        # On unexpected failure, clean up temp dir if nothing was registered
        with _lock:
            if temp_dir not in _temp_dirs.values():
                shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def cleanup_all() -> None:
    """Remove all registered temp directories (called on shutdown)."""
    with _lock:
        for path in _temp_dirs.values():
            shutil.rmtree(path, ignore_errors=True)
        _temp_dirs.clear()
