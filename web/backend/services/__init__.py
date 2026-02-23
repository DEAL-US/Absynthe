"""Service layer — bridges FastAPI routers to the Absynthe framework.

Adds the project root to sys.path so that all bare framework imports work
(e.g. ``from graph_generator import GraphGenerator``).
"""
import os
import sys

_PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
