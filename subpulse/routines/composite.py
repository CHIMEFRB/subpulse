"""Sample routine, using functions from multiple analysis locations."""
from math import ceil, floor

from subpulse.analysis.example import alpha


class Composite:
    """A composite routine based on two different analysis.

    Example
    -------
    >>> from subpulse.routines import composite
    >>> example = composite.Composite(minimum=1.5, maximum=5.0)
    >>> print(example.get_alpha())
    >>> print(example.get_seed())
    """

    def __init__(self, minimum: float, maximum: float, flavor: str):
        """Intialization.

        Parameters
        ----------
        minimum : float
        maximum : float
        """
        self.minimum = minimum
        self.maximum = maximum

    def get_random_integer(self) -> float:
        """Get random integer.

        Returns
        -------
        float
        """
        return alpha.randomized(floor(self.minimum), ceil(self.maximum))
