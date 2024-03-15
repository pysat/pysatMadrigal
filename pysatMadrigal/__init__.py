"""Core library for pysatMadrigal.

This is a library of `pysat` instrument modules and methods designed to support
instruments archived at the Madrigal portal.

"""

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata

from pysatMadrigal import instruments  # noqa F401
from pysatMadrigal import utils  # noqa F401

__version__ = metadata.version('pysatMadrigal')
