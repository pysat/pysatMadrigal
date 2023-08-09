#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Import the Instrument sub-modules and methods."""
# Import Madrigal instruments
from pysatMadrigal.instruments import dmsp_ivm
from pysatMadrigal.instruments import dmsp_ssj
from pysatMadrigal.instruments import gnss_tec
from pysatMadrigal.instruments import jro_isr
from pysatMadrigal.instruments import madrigal_dst
from pysatMadrigal.instruments import madrigal_geoind
from pysatMadrigal.instruments import madrigal_pandas
from pysatMadrigal.instruments import ngdc_ae
from pysatMadrigal.instruments import omni2_imf

# Import Madrigal methods
from pysatMadrigal.instruments import methods  # noqa F401

# Define variable name with all available instruments
__all__ = ['dmsp_ivm', 'dmsp_ssj', 'gnss_tec', 'jro_isr', 'madrigal_dst',
           'madrigal_geoind', 'madrigal_pandas', 'ngdc_ae', 'omni2_imf']
