# Import Madrigal instruments
from pysatMadrigal.instruments import dmsp_ivm, gnss_tec, jro_isr

# Import Madrigal methods
from pysatMadrigal.instruments import methods  # noqa F401

# Define variable name with all available instruments
__all__ = ['dmsp_ivm', 'gnss_tec', 'jro_isr']
