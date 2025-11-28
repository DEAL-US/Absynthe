# CAISE - Graph and Motif Composition Generator

Python project for generating and manipulating graphs using motifs and composition engines.

## Overview
- Reusable graph and motif generators.
- Composition and perturbation engines to test structural properties.

## Requirements
- Python 3.8 or newer
- (Optional) Create a virtual environment: `python -m venv venv`

## Quick Setup
On Linux / macOS (bash):

```bash
python -m venv venv
source venv/bin/activate
pip install -U pip
pip install pytest
```

There is no `requirements.txt` in the repository by default; add dependencies to your environment as needed.

## Running Tests
To run the full test suite:

```bash
pytest -q
```

To run a specific test file, for example:

```bash
pytest test_graph.py -q
```

## Project Structure
- `graph/`: generators and composition/perturbation engines.
- `motifs/`: motif generators.
- `utils/`: helper utilities such as `graph_utils.py`.
- Root scripts: `graph_generator.py`, `motif_generator.py`, `label_assigner.py`, `node_remover.py`, plus tests.


## License
This repository is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the `GPL-3.0 license` file in the project root for the full text.
