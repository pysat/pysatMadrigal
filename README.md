<div align="left">
        <img height="0" width="0px">
        <img width="20%" src="https://raw.githubusercontent.com/pysat/pysatMadrigal/main/docs/figures/pysatMadrigal.png" alt="pysatMadrigal" title="pysatMadrigal"</img>
</div>

# pysatMadrigal
[![Documentation Status](https://readthedocs.org/projects/pysatmadrigal/badge/?version=latest)](https://pysatmadrigal.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/pysat/pysatMadrigal/badge.svg?branch=main)](https://coveralls.io/github/pysat/pysatMadrigal?branch=main)
[![DOI](https://zenodo.org/badge/258384773.svg)](https://zenodo.org/badge/latestdoi/258384773)
[![PyPI version](https://badge.fury.io/py/pysatMadrigal.svg)](https://badge.fury.io/py/pysatMadrigal)

pysatMadrigal allows users to import data from the Madrigal database into
pysat ([pysat documentation](http://pysat.readthedocs.io/en/latest/)).


# Installation

The following instructions provide a guide for installing pysatMadrigal and
give some examples on how to use the routines.

## Prerequisites

pysatMadrigal uses common Python modules, as well as modules developed by and
for the Space Physics community.  This module officially supports Python 3.7+.

| Common modules | Community modules |
| -------------- | ----------------- |
| h5py           | madrigalWeb>=2.6  |
| numpy          | pysat >= 3.0.3    |
| pandas         |                   |
| xarray         |                   |


## PyPi Installation
```
pip install pysatMadrigal
```

## GitHub Installation
```
git clone https://github.com/pysat/pysatMadrigal.git
```

Change directories into the repository folder and run the setup.py file.  For
a local install use the "--user" flag after "install".

```
cd pysatMadrigal/
python setup.py install
```

# Examples

The instrument modules are portable and designed to be run like any pysat
instrument.

```
import pysat
from pysatMadrigal.instruments import dmsp_ivm
ivm = pysat.Instrument(inst_module=dmsp_ivm, tag='utd', inst_id='f15')
```

Another way to use the instruments in an external repository is to register the
instruments.  This only needs to be done the first time you load an instrument.
Afterward, pysat will identify them using the `platform` and `name` keywords.

```
pysat.utils.registry.register('pysatMadrigal.instruments.dmsp_ivm')
dst = pysat.Instrument('dmsp', 'ivm', tag='utd', inst_id='f15')
```
