#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Unit tests for the Instruments."""

# Import the test classes from pysat
from pysat.tests.classes import cls_instrument_library as clslib

import pysatMadrigal

# Optional code to pass through user and password info to test instruments
# dict, keyed by pysat instrument, with a list of usernames and passwords
# user_info = {'platform_name': {'user': 'pysat_user',
#                                'password': 'None'}}
user_info = {module: {'user': 'pysat+CI_tests',
                      'password': 'pysat.developers@gmail.com'}
             for module in pysatMadrigal.instruments.__all__}

# Tell the standard tests which instruments to run each test on.
# Need to return instrument list for custom tests.
instruments = clslib.InstLibTests.initialize_test_package(
    clslib.InstLibTests, inst_loc=pysatMadrigal.instruments,
    user_info=user_info)


class TestInstruments(clslib.InstLibTests):
    """Main class for instrument tests.

    Note
    ----
    All standard tests, setup, and teardown inherited from the core pysat
    instrument test class.

    """
