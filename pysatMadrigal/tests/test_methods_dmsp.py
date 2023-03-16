#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Test methods for `pysatMadrigal.instruments.methods.gnss`."""

import numpy as np
import pytest

import pysat
from pysat.utils.testing import eval_bad_input

from pysatMadrigal.instruments.methods import dmsp


class TestDMSPRefs(object):
    """Test the acknowledgements and references for the DMSP instruments."""

    def setup_method(self):
        """Run before every method to create a clean testing setup."""
        self.out = None
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        del self.out
        return

    @pytest.mark.parametrize("func, comp_str, in_args", [
        ('references', 'Rich, Users Guide', ['ivm'])])
    def test_ref_output(self, func, comp_str, in_args):
        """Test the DMSP references."""
        self.out = getattr(dmsp, func)(*in_args)
        assert self.out.find(comp_str) >= 0
        return


class TestDMSPCleaning(object):
    """Unit tests for functions that can be used to improve DMSP data."""

    def setup_method(self):
        """Run before every method to create a clean testing setup."""
        # Create an instrument similar to the DMSP IVM UTD instrument
        self.inst = pysat.Instrument('pysat', 'testing', use_header=True)
        self.inst.load(date=pysat.instruments.pysat_testing._test_dates[''][''])
        self.smooth_kwargs = {'rpa_vel_key': 'dummy4'}
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        del self.inst, self.smooth_kwargs
        return

    @pytest.mark.parametrize('bad_key,bad_val', [('rpa_flag_key', 'not_a_key'),
                                                 ('rpa_vel_key', 'not_a_key')])
    def test_bad_keys_smooth_ram_drifts(self, bad_key, bad_val):
        """Test raises KeyError if bad keys are used.

        Parameters
        ----------
        bad_key : str
            Bad kwarg name
        bad_val : str
            Bad input value

        """
        self.smooth_kwargs[bad_key] = bad_val

        eval_bad_input(dmsp.smooth_ram_drifts, KeyError, bad_val,
                       input_args=[self.inst], input_kwargs=self.smooth_kwargs)
        return

    def test_smooth_ram_drifts_none_overwrite(self):
        """Test that the drifts not are overwritten when no data selected."""

        # After averaging, the range should be smaller
        raw_max = self.inst[self.smooth_kwargs['rpa_vel_key']].max()
        raw_min = self.inst[self.smooth_kwargs['rpa_vel_key']].min()

        # Run the smoothed routine
        dmsp.smooth_ram_drifts(self.inst, **self.smooth_kwargs)

        # Evaluate the output
        assert raw_max == self.inst[self.smooth_kwargs['rpa_vel_key']].max()
        assert raw_min == self.inst[self.smooth_kwargs['rpa_vel_key']].min()
        assert self.inst.meta[self.smooth_kwargs['rpa_vel_key'],
                              self.inst.meta.labels.desc].find(
                                  'no data selected') >= 0
        return

    def test_smooth_ram_drifts_none_new_val(self):
        """Test that the drifts remain alongside the smoothed drifts."""

        # After averaging, the range should be smaller
        raw_max = self.inst[self.smooth_kwargs['rpa_vel_key']].max()
        raw_min = self.inst[self.smooth_kwargs['rpa_vel_key']].min()

        # Run the smoothed routine
        self.smooth_kwargs['smooth_key'] = 'smooth'
        dmsp.smooth_ram_drifts(self.inst, **self.smooth_kwargs)

        # Evaluate the output
        assert raw_max == self.inst[self.smooth_kwargs['rpa_vel_key']].max()
        assert raw_min == self.inst[self.smooth_kwargs['rpa_vel_key']].min()
        assert self.inst.meta[self.smooth_kwargs['rpa_vel_key'],
                              self.inst.meta.labels.desc].find(
                                  'Rolling mean') < 0
        assert np.isnan(self.inst[self.smooth_kwargs['smooth_key']].max())
        assert np.isnan(self.inst[self.smooth_kwargs['smooth_key']].min())
        assert self.inst.meta[self.smooth_kwargs['smooth_key'],
                              self.inst.meta.labels.desc].find(
                                  'no data selected') >= 0
        return

    @pytest.mark.parametrize('rpa_flag_max', [0, 1])
    def test_smooth_ram_drift_flag_selection(self, rpa_flag_max):
        """Test the drift selection by RPA flag value."""

        # After averaging, the range should be smaller
        raw_max = self.inst[self.smooth_kwargs['rpa_vel_key']].max()
        raw_min = self.inst[self.smooth_kwargs['rpa_vel_key']].min()

        # Update the input kwargs
        self.smooth_kwargs['rpa_flag_key'] = 'int8_dummy'
        self.smooth_kwargs['rpa_flag_max'] = rpa_flag_max

        # Run the smoothed routine
        dmsp.smooth_ram_drifts(self.inst, **self.smooth_kwargs)

        # Evaluate the output
        nsel = sum(self.inst[self.smooth_kwargs['rpa_flag_key']].values
                   <= rpa_flag_max)

        if nsel > 0:
            assert raw_max > self.inst[self.smooth_kwargs['rpa_vel_key']].max()
            assert raw_min < self.inst[self.smooth_kwargs['rpa_vel_key']].min()
        else:
            assert raw_max == self.inst[self.smooth_kwargs['rpa_vel_key']].max()
            assert raw_min == self.inst[self.smooth_kwargs['rpa_vel_key']].min()
        assert self.inst.meta[self.smooth_kwargs['rpa_vel_key'],
                              self.inst.meta.labels.desc].find(
                                  'RPA flag data <= ') >= 0
        return
