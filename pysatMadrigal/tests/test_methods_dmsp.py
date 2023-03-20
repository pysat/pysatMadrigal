#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Test methods for `pysatMadrigal.instruments.methods.gnss`."""

import logging
import numpy as np
import pytest

import pysat
from pysat.utils.testing import assert_lists_equal, eval_bad_input

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
        self.inst['mlat'] = self.inst['latitude']
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

    def test_no_ephem_logger(self, caplog):
        """Test logger info raised without an ephemeris instrument."""

        # Try to update the ephemeris without providing any ephemeris data
        with caplog.at_level(logging.INFO, logger='pysat'):
            dmsp.update_DMSP_ephemeris(self.inst)

        # Test that there is no data
        assert self.inst.empty, "Updating ephemeris w/o data didn't remove data"

        # Test the logger message
        assert caplog.text.find('No ephemera provided') >= 0
        return

    def test_no_ephem_data_logger(self, caplog):
        """Test logger info raised without ephemeris data."""

        ephem = pysat.Instrument('pysat', 'testing', use_header=True)
        ephem.date = self.inst.date

        # Try to update the ephemeris without providing any ephemeris data
        with caplog.at_level(logging.INFO, logger='pysat'):
            dmsp.update_DMSP_ephemeris(self.inst, ephem)

        # Test that there is no data
        assert self.inst.empty, "Updating ephemeris w/o data didn't remove data"

        # Test the logger message
        assert caplog.text.find('unable to load ephemera for') >= 0
        return

    def test_bad_ephem_inst_id(self):
        """Test that mismatched `inst_id`s raises a ValueError."""

        ephem = pysat.Instrument('pysat', 'testing', use_header=True)
        ephem.inst_id = 'f15'

        eval_bad_input(dmsp.update_DMSP_ephemeris, ValueError,
                       "ephemera provided for the wrong satellite",
                       input_args=[self.inst, ephem])

        return

    def test_good_ephem_local_load(self):
        """Test that `update_DMSP_ephemeris` will load correct data."""

        # Rename the testing instrument variables
        def add_ephem_variables(ephem):
            """Function to add required variables to a test instrument.

            Parameters
            ----------
            ephem : pysat.Instrument
                Instrument to be updated

            """
            ephem['SC_AACGM_LTIME'] = ephem['mlt'] + 1.0
            ephem['SC_AACGM_LAT'] = ephem['latitude'] + 1.0
            return

        ephem = pysat.Instrument('pysat', 'testing', use_header=True)
        ephem.custom_attach(add_ephem_variables)

        # Adjust the Instrument ephemeris
        dmsp.update_DMSP_ephemeris(self.inst, ephem)

        # Test the output
        assert_lists_equal(self.inst['mlt'].values,
                           ephem['SC_AACGM_LTIME'].values)
        assert_lists_equal(self.inst['mlat'].values,
                           ephem['SC_AACGM_LAT'].values)

        return

    def test_add_drift_unit_vectors(self):
        """Test that drift unit vectors are added."""

        dmsp.add_drift_unit_vectors(self.inst)

        # Ensure the variable are present
        for new_var in ['unit_ram_x', 'unit_ram_y', 'unit_cross_x',
                        'unit_cross_y', 'unit_ram_r', 'unit_ram_theta',
                        'unit_cross_r', 'unit_cross_theta']:
            assert new_var in self.inst.variables, "missing {:s}".format(
                new_var)

        # Ensure the variables behave like unit vectors
        for direction in ['ram', 'cross']:
            local_r = np.sqrt(self.inst['unit_{:s}_x'.format(direction)]**2
                              + self.inst['unit_{:s}_y'.format(direction)]**2)
            for unit_r in local_r.values:
                if not np.isnan(unit_r):
                    assert abs(unit_r - 1.0) <= 1.0e-7

        return

    @pytest.mark.parametrize("rpa_flag_key", ['int8_dummy', None])
    def test_add_drifts_polar_cap_x_y(self, rpa_flag_key):
        """Test that polar cap drifts are added.

        Parameters
        ----------
        rpa_flag_key : str
            Key for RPA flag

        """

        dmsp.add_drift_unit_vectors(self.inst)
        dmsp.add_drifts_polar_cap_x_y(self.inst, rpa_flag_key=rpa_flag_key,
                                      rpa_vel_key='dummy1',
                                      cross_vel_key='dummy4')

        # Ensure the variable are present
        for new_var in ['unit_ram_x', 'unit_ram_y', 'unit_cross_x',
                        'unit_cross_y', 'unit_ram_r', 'unit_ram_theta',
                        'unit_cross_r', 'unit_cross_theta', 'ion_vel_pc_x',
                        'ion_vel_pc_y', 'partial']:
            assert new_var in self.inst.variables, "missing {:s}".format(
                new_var)

        return
