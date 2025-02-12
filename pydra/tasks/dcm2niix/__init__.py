"""
This is a basic doctest demonstrating that the package and pydra can both be successfully
imported.

>>> import pydra.engine
>>> import pydra.tasks.dcm2niix
"""

from ._version import __version__
from .utils import Dcm2Niix


__all__ = [
    "__version__",
    "Dcm2Niix",
]
