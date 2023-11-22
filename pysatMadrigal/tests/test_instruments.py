#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Unit tests for the Instruments."""

import datetime as dt

# Import the test classes from pysat
import pysat
from pysat.tests.classes import cls_instrument_library as clslib
from pysat.utils.testing import eval_bad_input

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


class TestInstrumentLoadError(object):
    """Class for unit testing errors raised when loading data."""

    def setup_method(self):
        """Run before every method to create a clean testing setup."""
        self.inst_kwargs = [{'inst_module': pysatMadrigal.instruments.gnss_tec,
                             'tag': 'los', 'los_method': 'site'}]
        self.load_time = dt.datetime(2001, 1, 1)
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        del self.inst_kwargs, self.load_time
        return

    def test_bad_los_value(self):
        """Test ValueError when the `los_value` is omitted."""
        inst = pysat.Instrument(**self.inst_kwargs)

        eval_bad_input(inst.load, ValueError, "must specify a valid",
                       input_kwargs={'date': self.load_time})
        return
