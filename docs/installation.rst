Installation
============

The following instructions will allow you to install pysatMadrigal.

Prerequisites
-------------

.. image:: figures/poweredbypysat.png
    :width: 150px
    :align: right
    :alt: powered by pysat Logo, blue planet with orbiting python


pysatMadrigal uses common Python modules, as well as modules developed by
and for the Space Physics community.  This module officially supports
Python 3.6+.

 ============== =================
 Common modules Community modules
 ============== =================
  h5py          madrigalWeb    
  numpy         pysat
  pandas
  xarray
 ============== =================


Installation Options
--------------------

You may either install pysatMadrigal via pip or by cloning the git repository

1. Install from pip
::

   pip install pysatMadrigal
   

2. Clone the git repository and use the ``pyproject.toml`` file to install
::

   
   git clone https://github.com/pysat/pysatMadrigal.git

   # Move into the pysatMadrigal directory. Then build the wheel
   python -m build .

   
   # Install at the user or system level, depending on privledges
   pip install .

   # Install with the intent to develop locally
   pip install -e .
