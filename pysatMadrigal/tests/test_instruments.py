#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Unit tests for the Instruments."""

import datetime as dt
import os
import pathlib

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
        self.fake_file = ''
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        if os.path.isfile(self.fake_file):
            os.remove(self.fake_file)

        del self.inst_kwargs, self.load_time, self.fake_file
        return

    def test_bad_los_value(self):
        """Test ValueError when the `los_value` is omitted."""
        inst = pysat.Instrument(**self.inst_kwargs[0])

        # Ensure a file is available
        if self.load_time not in inst.files.files.keys():
            self.fake_file = os.path.join(
                inst.files.data_path,
                self.inst_kwargs[0]['inst_module'].supported_tags[inst.inst_id][
                    inst.tag].format(file_type='hdf5').format(
                        year=self.load_time.year, month=self.load_time.month,
                        day=self.load_time.day, version=1))
            pysat.utils.files.check_and_make_path(inst.files.data_path)
            pathlib.Path(self.fake_file).touch()
            inst = pysat.Instrument(**self.inst_kwargs[0])

        eval_bad_input(inst.load, ValueError, "must specify a valid",
                       input_kwargs={'date': self.load_time})
        return
