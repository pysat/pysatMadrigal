import os
from pysatMadrigal import instruments  # noqa F401
from pysatMadrigal import utils  # noqa F401

# set version
here = os.path.abspath(os.path.dirname(__file__))
version_filename = os.path.join(here, 'version.txt')
with open(version_filename, 'r') as version_file:
    __version__ = version_file.read().strip()
del here, version_filename, version_file
