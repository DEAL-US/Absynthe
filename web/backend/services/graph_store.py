"""In-memory graph store — maps UUID strings to ``nx.Graph`` objects."""
import threading
import uuid
from typing import Dict, Optional

import networkx as nx

_store: Dict[str, nx.Graph] = {}
_lock = threading.Lock()


def store(graph: nx.Graph) -> str:
    gid = str(uuid.uuid4())
    with _lock:
        _store[gid] = graph
    return gid


def get(graph_id: str) -> nx.Graph:
    with _lock:
        g = _store.get(graph_id)
    if g is None:
        raise KeyError(f"Graph '{graph_id}' not found. Generate or upload a graph first.")
    return g


def update(graph_id: str, graph: nx.Graph) -> None:
    with _lock:
        if graph_id not in _store:
            raise KeyError(f"Graph '{graph_id}' not found.")
        _store[graph_id] = graph


def delete(graph_id: str) -> None:
    with _lock:
        _store.pop(graph_id, None)


def ids() -> list:
    with _lock:
        return list(_store.keys())
