<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="/docs/figures/pysatMadrigal.png" alt="pysatMadrigal" title="pysatMadrigal"</img>
</div>

# pysatMadrigal
[![Documentation Status](https://readthedocs.org/projects/pysatMadrigal/badge/?version=latest)](http://pysatMadrigal.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatMadrigal/badge.svg?branch=main)](https://coveralls.io/github/pysat/pysatMadrigal?branch=main)
[![DOI](https://zenodo.org/badge/258384773.svg)](https://zenodo.org/badge/latestdoi/258384773)
[![PyPI version](https://badge.fury.io/py/pysatMadrigal.svg)](https://badge.fury.io/py/pysatMadrigal)

pysatMadrigal allows users to import data from the Madrigal database into
pysat ([pysat documentation](http://pysat.readthedocs.io/en/latest/)).


# Installation

pysatMadrigal may be installed through pip or by cloning the git repository
```
pip install pysatMadrigal
```

```
git clone https://github.com/pysat/pysatMadrigal.git
```

Change directories into the repository folder and run the setup.py file.  For
a local install use the "--user" flag after "install".

```
cd pysatMadrigal/
python setup.py install
```

Note: pre-0.1.0 version
-----------------------
pysatMadrigal is currently provided as an alpha pre-release.  

# Using with pysat

The instrument modules are portable and designed to be run like any pysat
instrument.

```
import pysat
from pysatMadrigal.instruments import dmsp_ivm

ivm = pysat.Instrument(inst_module=dmsp_ivm, tag='utd', inst_id='f15')
```
