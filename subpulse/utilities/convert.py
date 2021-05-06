"""Conversion Utilities."""
from typing import Any


def list_to_dict(data: list, value: Any = {}) -> dict:
    """Convert list to a dictionary.

    Parameters
    ----------
    data: list
        Data type to convert
    value: typing.Any
        Default value for the dict keys

    Returns
    -------
    dictionary : dict
        Dictionary of the input data
    """
    return {item: value for item in data}
