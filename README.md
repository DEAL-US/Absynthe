# CAISE - Graph and Motif Composition Generator

Python project for generating and manipulating graphs using motifs and composition engines.

## Overview
- Reusable graph and motif generators.
- Composition and perturbation engines to test structural properties.

## Requirements
- Python 3.8 or newer
- A virtual environment is recommended (example below).

This repository includes a `requirements.txt` with the minimal dependencies used by the examples (`networkx`, `numpy`, `matplotlib`). Install them into your venv with:

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

```bash
# macOS / Linux (bash)
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running Examples
After activating the venv and installing `requirements.txt`, run the example runner or tests:

```powershell
# run example
python .\test_graph.py

```

Note: the framework now uses a single global seed defined in `test_graph.py` (variable `SEED`) to control all randomness. Change that value to reproduce different random instances.

## Project Structure
- `graph/`: generators and composition/perturbation engines.
- `motifs/`: motif generators.
- `utils/`: helper utilities such as `graph_utils.py`.
- Root scripts: `graph_generator.py`, `motif_generator.py`, `label_assigner.py`, `node_remover.py`, plus tests.


## License
This repository is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the `GPL-3.0 license` file in the project root for the full text.
