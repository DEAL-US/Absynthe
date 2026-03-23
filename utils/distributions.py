"""Generic integer distribution sampling.

Reusable module for sampling integers from configurable distributions.
Uses only ``random.Random`` — no numpy dependency.

Usage::

    from utils.distributions import IntDistribution, sample_int
    from utils.rng import get_rng

    dist = IntDistribution(type="normal", params={"mean": 4, "std": 1})
    value = sample_int(dist, get_rng())          # integer >= 1
    value = sample_int(dist, get_rng(), min_value=0)  # integer >= 0
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, Union


@dataclass
class IntDistribution:
    """Configuration for sampling integer values from a distribution.

    Supported types and their params:

    * ``"uniform"``  — ``{"min": a, "max": b}``
    * ``"normal"``   — ``{"mean": mu, "std": sigma}``
    * ``"poisson"``  — ``{"lambda": lam}``
    """

    type: str
    params: Dict[str, float] = field(default_factory=dict)


def _sample_poisson(lam: float, rng: Union[random.Random, "module"]) -> int:
    """Knuth's algorithm for Poisson sampling using only ``rng.random()``."""
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= rng.random()
    return k - 1


def sample_int(
    dist: IntDistribution,
    rng: Union[random.Random, "module"],
    min_value: int = 1,
) -> int:
    """Sample a single integer from *dist*, clamped to ``>= min_value``.

    Parameters
    ----------
    dist:
        Distribution configuration.
    rng:
        A ``random.Random`` instance or the ``random`` module itself.
    min_value:
        Lower bound for the returned value (default ``1``).
    """
    t = dist.type

    if t == "uniform":
        lo = int(dist.params.get("min", 1))
        hi = int(dist.params.get("max", 5))
        value = rng.randint(lo, hi)

    elif t == "normal":
        mu = dist.params.get("mean", 3.0)
        sigma = dist.params.get("std", 1.0)
        value = round(rng.gauss(mu, sigma))

    elif t == "poisson":
        lam = dist.params.get("lambda", 3.0)
        value = _sample_poisson(lam, rng)

    else:
        raise ValueError(f"Unknown distribution type: {t!r}")

    return max(min_value, value)
