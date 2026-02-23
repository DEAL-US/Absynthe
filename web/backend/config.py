"""Application-level settings."""
import os

# CORS origins allowed in development
DEV_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:4173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Output directory for generated datasets (relative to project root)
DEFAULT_DATASET_OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "datasets",
)
