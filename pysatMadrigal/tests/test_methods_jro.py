#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Test methods for `pysatMadrigal.instruments.methods.jro`."""

import logging
import numpy as np
import pytest

import pysat

from pysatMadrigal.instruments.methods import jro


class TestJRORefs(object):
    """Test the acknowledgements and references for the JRO instruments."""

    def setup(self):
        """Run before every method to create a clean testing setup."""
        self.out = None
        return

    def teardown(self):
        """Run after every method to clean up previous testing."""
        del self.out
        return

    @pytest.mark.parametrize("func, comp_str", [
        ('acknowledgements', 'Jicamarca Radio Observatory'),
        ('references', 'contact PI')])
    def test_ref_output(self, func, comp_str):
        """Test the JRO acknowledgements and references."""
        self.out = getattr(jro, func)()
        assert self.out.find(comp_str) >= 0
        return


class TestJROCalcLoc(object):
    """Test the JRO support function `calc_measurement_loc`."""

    def setup(self):
        """Run before every method to create a clean testing setup."""
        self.inst = pysat.Instrument('pysat', 'testing_xarray', num_samples=100)
        self.stime = pysat.instruments.pysat_testing_xarray._test_dates['']['']

        # Set the hard-coded values
        self.az = 206.0
        self.el = 87.0
        self.lat_min = -12.3232
        self.lat_max = -11.9931
        self.lon_min = -77.04998
        self.lon_max = -76.89074
        self.tol = 1.0e-4
        return

    def teardown(self):
        """Run after every method to clean up previous testing."""
        del self.inst, self.stime, self.az, self.el
        del self.lat_min, self.lat_max, self.lon_min, self.lon_max, self.tol
        return

    def transform_testing_to_jro(self, azel_type=''):
        """Alter `testing_xarray` to mirror the JRO-ISR data."""
        # Load the data
        self.inst.load(date=self.stime)

        # Alter the coordinates
        self.inst.data = self.inst.data.assign_coords(
            {'gdalt': np.arange(100.0, 1000.0, 15.0), 'gdlatr': -11.95,
             'gdlonr': -76.87})

        # Alter the data, if requested
        if azel_type in ['m', 'both', 'both_norange']:
            self.inst.data = self.inst.data.assign(
                {'azm': (("time"), np.full(shape=self.inst.index.shape,
                                           fill_value=self.az)),
                 'elm': (("time"), np.full(shape=self.inst.index.shape,
                                           fill_value=self.el)),
                 'rgate': (("time"), np.full(shape=self.inst.index.shape,
                                             fill_value=15.0))})

        if azel_type in ['dir', 'both']:
            self.inst.data = self.inst.data.assign(
                {'azdir7': (("time"), np.full(shape=self.inst.index.shape,
                                              fill_value=self.az)),
                 'eldir7': (("time"), np.full(shape=self.inst.index.shape,
                                              fill_value=self.el)),
                 'range': (("time", "gdalt"),
                           np.full(shape=(self.inst.index.shape[0],
                                          self.inst['gdalt'].shape[0]),
                                   fill_value=self.inst['gdalt']))})

        if azel_type in ['dir_norange', 'both_norange']:
            self.inst.data = self.inst.data.assign(
                {'azdir7': (("time"), np.full(shape=self.inst.index.shape,
                                              fill_value=self.az)),
                 'eldir7': (("time"), np.full(shape=self.inst.index.shape,
                                              fill_value=self.el))})

        if azel_type == 'baddir':
            self.inst.data = self.inst.data.assign(
                {'azdirX': (("time"), np.full(shape=self.inst.index.shape,
                                              fill_value=self.az)),
                 'eldirX': (("time"), np.full(shape=self.inst.index.shape,
                                              fill_value=self.el)),
                 'range': (("time", "gdalt"),
                           np.full(shape=(self.inst.index.shape[0],
                                          self.inst['gdalt'].shape[0]),
                                   fill_value=self.inst['gdalt']))})

        return

    def eval_calc_lat_range(self, out_lat):
        """Evaluate the calculated latitude output."""
        # Test the minimum
        assert abs(out_lat.min() - self.lat_min) < self.tol, \
            "Beam latitudes below the expected minimum: |{:}| < |{:}|.".format(
                out_lat.min(), self.lat_min)

        # Test the maximum
        assert abs(out_lat.max() - self.lat_max) < self.tol, \
            "Beam latitudes above the expected maximum: |{:}| < |{:}|.".format(
                out_lat.max(), self.lat_max)
        return

    def eval_calc_lon_range(self, out_lon):
        """Evaluate the calculated longitude output."""
        # Test the minimum
        assert abs(out_lon.min() - self.lon_min) < self.tol, \
            "Beam longitudes below the expected minimum: |{:}| < |{:}|.".format(
                out_lon.min(), self.lon_min)

        # Test the maximum
        assert abs(out_lon.max() - self.lon_max) < self.tol, \
            "Beam longitudes above the expected maximum: |{:}| < |{:}|.".format(
                out_lon.max(), self.lon_max)
        return

    @pytest.mark.parametrize("azel_type, err_msg", [
        ('', 'No matching azimuth and elevation data'),
        ('both', 'Multiple range variables'),
        ('dir_norange', 'No range variable found')])
    def test_bad_input_data(self, azel_type, err_msg):
        """Test raises ValueError with bad input data."""

        # Format the test Instrument
        self.transform_testing_to_jro(azel_type=azel_type)

        # Capture the expected error message
        with pytest.raises(ValueError) as verr:
            jro.calc_measurement_loc(self.inst)

        # Test the error message
        assert str(verr).find(err_msg) >= 0
        return

    def test_bad_dirnumber(self, caplog):
        """Test log warning raised for badly formated direction number."""

        # Format the test Instrument
        self.transform_testing_to_jro(azel_type='baddir')

        # Capture the expected log message
        with pytest.raises(ValueError) as verr:
            with caplog.at_level(logging.WARN, logger='pysat'):
                jro.calc_measurement_loc(self.inst)

        # Test the log output
        captured = caplog.text
        assert captured.find('Unknown direction number') >= 0

        # Test the ValueError message
        assert str(verr).find("No matching azimuth") >= 0
        return

    @pytest.mark.parametrize("azel_type, new_vals", [
        ("dir", ["gdlat7", "gdlon7"]),
        ("m", ["gdlat_bm", "gdlon_bm"]),
        ("both_norange", ["gdlat7", "gdlon7", "gdlat_bm", "gdlon_bm"])])
    def test_success(self, azel_type, new_vals):
        """Test the successful calculation of JRO ISR beam locations."""

        # Format the test Instrument
        self.transform_testing_to_jro(azel_type=azel_type)

        # Update the instrument with geographic locations
        jro.calc_measurement_loc(self.inst)

        # Ensure the new values are present
        pysat.utils.testing.assert_list_contains(new_vals, self.inst.variables)

        # Test the calculated outputs
        for val in new_vals:
            # Test the dimensions
            pysat.utils.testing.assert_lists_equal(
                ['gdalt', 'time'], list(self.inst[val].dims))

            # Test the value ranges
            if val.find("lat") > 0:
                self.eval_calc_lat_range(self.inst[val].values)
            else:
                self.eval_calc_lon_range(self.inst[val].values)

        return
