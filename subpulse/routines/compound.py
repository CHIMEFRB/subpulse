"""Sample Compound Routine."""
from subpulse.analysis.example import beta
from subpulse.routines import composite, simple


class Compound(composite.Composite, simple.Simple):
    """A compound routine.

    Note
    ----
    This routine is based on two simpler routines and some analysis functions.

    Parameters
    ----------
    composite : composite.Composite
        Composite Analysis Routine
    simple : simple.Simple
        Simple Analysis Routine

    Example
    -------
    >>> from subpulse.routines import compound
    >>> analysis = compound.Compound(maximum=11.0, minimum=3.0, flavor="hex")
    >>> print(analysis.get_alpha())
    >>> print(analysis.get_beta())
    >>> print(analysis.seedling())
    """

    def __init__(self, maximum: float, minimum: float, flavor: str):
        """Initialization.

        Parameters
        ----------
        maximum : float
        minimum : float
        flavor : str
            Flavor of seed, valid values are [str, hex, bytes]
        """
        self.minimum = minimum
        self.maximum = maximum
        self.flavor = flavor

    def get_beta(self):
        """Get random scaled value."""
        return beta.randomized(scale=self.maximum)
