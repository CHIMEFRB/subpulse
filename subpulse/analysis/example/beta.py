"""Example Analysis Functions."""
from random import random


def randomized(scale: float) -> float:
    """Random value.

    Parameters
    ----------
    scale : float
        Scale.

    Returns
    -------
    float
        A random number.
    """
    isinstance(scale, float)
    return scale * random()
