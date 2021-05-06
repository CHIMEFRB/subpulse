"""
Core Analysis Functions.

Note
----
Analysis functions at the top-level are methods core to the repository,
commonly used by multiple routines and required by default. For simpler projects,
all analysis functions could be core.
"""
import uuid
from typing import Union


def get_uuid(flavor: str = "str") -> Union[str, bytes]:
    """Generate a Universally Unique Identifier.

    Parameters
    ----------
    flavor : str, optional
        Type of uuid, can be str, hex or bytes, by default str

    Returns
    -------
    Union[str, bytes]
        uuid

    Raises
    ------
    ValueError
        Raised when uuid flavor misconfigured.
    """
    if flavor == "str":
        return str(uuid.uuid1())
    elif flavor == "hex":
        return uuid.uuid1().hex
    elif flavor == "bytes":
        return uuid.uuid1().bytes
    else:
        raise ValueError("undefined flavor")
