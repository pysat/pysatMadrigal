#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Test methods for `pysatMadrigal.instruments.methods.gnss`."""

import pytest

from pysatMadrigal.instruments.methods import gnss


class TestGNSSRefs(object):
    """Test the acknowledgements and references for the GNSS instruments."""

    def setup_method(self):
        """Run before every method to create a clean testing setup."""
        self.out = None
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        del self.out
        return

    @pytest.mark.parametrize("func, comp_str, in_args", [
        ('acknowledgements', 'GPS TEC data products', ['tec']),
        ('references', 'Rideout and Coster', ['tec'])])
    def test_ref_output(self, func, comp_str, in_args):
        """Test the GNSS acknowledgements and references."""
        self.out = getattr(gnss, func)(*in_args)
        assert self.out.find(comp_str) >= 0
        return
