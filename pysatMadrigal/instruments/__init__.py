# Import Madrigal instruments
from pysatMadrigal.instruments import dmsp_ivm
from pysatMadrigal.instruments import dmsp_ssj
from pysatMadrigal.instruments import gnss_tec
from pysatMadrigal.instruments import jro_isr
from pysatMadrigal.instruments import madrigal_pandas

# Import Madrigal methods
from pysatMadrigal.instruments import methods  # noqa F401

# Define variable name with all available instruments
__all__ = ['dmsp_ivm', 'dmsp_ssj', 'gnss_tec', 'jro_isr', 'madrigal_pandas']
