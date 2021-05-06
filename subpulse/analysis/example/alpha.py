"""Analysis functions for Example."""
from random import randint


def randomized(minimum: int = 0, maximum: int = 100) -> int:
    """Random integer generator.

    Parameters
    ----------
    minimum : int, optional
        Minimum value, by default 0
    maximum : int, optional
        Maximum value, by default 100

    Returns
    -------
    int
        Random integer in range [minimum, maxumim].
    """
    isinstance(minimum, int)
    isinstance(maximum, int)
    return randint(minimum, maximum)
