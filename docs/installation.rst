Installation
============

The following instructions will allow you to install pysatMadrigal.

Prerequisites
-------------

.. image:: figures/poweredbypysat.png
    :width: 150px
    :align: right
    :alt: powered by pysat Logo, blue planet with orbiting python


pysatSpaceWeather uses common Python modules, as well as modules developed by
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
   

2. Clone the git repository and use the ``setup.py`` file to install
::

   
   git clone https://github.com/pysat/pysatMadrigal.git

   # Install on the system (root privileges required)
   sudo python3 setup.py install
   
   # Install at the user level
   python3 setup.py install --user  

   # Install at the user level with the intent to develop locally
   python3 setup.py develop --user
