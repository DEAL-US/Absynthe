"""Global RNG registry for reproducibility.

Usage::

    from utils.rng import set_seed, get_rng, reset_rng

    set_seed(42)          # all framework randomness becomes reproducible
    rng = get_rng()       # obtain the seeded Random instance
    reset_rng()           # revert to the default (unseeded) random module
"""

import random
from typing import Optional, Union

_rng: Optional[random.Random] = None


def set_seed(seed: int) -> None:
    """Create a seeded ``random.Random`` instance and store it as the framework default."""
    global _rng
    _rng = random.Random(seed)


def get_rng() -> Union[random.Random, "module"]:
    """Return the current default RNG (seeded instance or global ``random`` module)."""
    return _rng if _rng is not None else random


def reset_rng() -> None:
    """Clear the stored RNG, reverting to the unseeded global ``random`` module."""
    global _rng
    _rng = None
