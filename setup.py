#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2020, Authors
# Full license can be found in License.md and AUTHORS.md
# -----------------------------------------------------------------------------

import codecs
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'description.txt'), encoding='utf-8') as f:
    long_description = f.read()
version_filename = os.path.join('pysatMadrigal', 'version.txt')
with codecs.open(os.path.join(here, version_filename)) as version_file:
    version = version_file.read().strip()

# Define requirements
# netCDF support requires netCDF4-Python or scipy installation
install_requires = ['pysat', 'pandas', 'xarray', 'numpy', 'netCDF4-Python']

# packages with Fortran code
fortran_install = ['madrigalWeb', 'h5py']

# flag, True if on readthedocs
on_rtd = os.environ.get('READTHEDOCS') == 'True'

# include Fortran for normal install
# read the docs doesn't do Fortran
if not on_rtd:
    # not on ReadTheDocs, add Fortran
    install_requires.extend(fortran_install)


# Run setup
setup(name='pysatMadrigal',
      version=version,
      url='http://github.com/pysat/pysatMadrigal',
      author='Angeline G. Burrell, Russell Stoneback, Jeff Klenzing',
      author_email='angeline.burrell@nrl.navy.mil',
      description='Madrigal instrument support for the pysat ecosystem',
      long_description=long_description,
      packages=find_packages(),
      classifiers=["Development Status :: 4 - Beta",
                   "Topic :: Scientific/Engineering :: Physics",
                   "Intended Audience :: Science/Research",
                   'License :: OSI Approved :: BSD License',
                   "Natural Language :: English",
                   "Programming Language :: Python :: 3 :: Only",
                   "Programming Language :: Python :: 3.6",
                   "Programming Language :: Python :: 3.7",
                   "Programming Language :: Python :: 3.8",
                   "Operating System :: MacOS :: MacOS X"],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,)
