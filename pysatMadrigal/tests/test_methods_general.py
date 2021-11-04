#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Unit tests for the general instrument methods."""

import pytest

from pysatMadrigal.instruments.methods import general


class TestLocal(object):
    """Unit tests for general methods that run locally."""

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.out = None
        return

    def cleanup(self):
        """Runs after every method to clean up previous testing."""
        del self.out
        return

    def test_acknowledgements(self):
        """Test the Madrigal acknowledgements."""
        self.out = general.cedar_rules()
        assert self.out.find("CEDAR 'Rules of the Road'") >= 0
        return


class TestErrors(object):
    """Tests for errors raised by the general methods."""

    def setup(self):
        """Create a clean testing setup."""
        self.kwargs = {'inst_code': 'inst_code',
                       'user': 'username',
                       'password': 'password',
                       'kindats': {'testing': {'tag': 1000}},
                       'supported_tags': {'testing': {'tag': 'file%Y%m%d.nc'}}}
        return

    def cleanup(self):
        """Clean up previous testing."""
        del self.kwargs
        return

    def test_check_madrigal_params_no_code(self):
        """Test that an error is thrown if None is passed through."""
        # Set up the kwargs for this test
        del self.kwargs['kindats'], self.kwargs['supported_tags']
        self.kwargs['inst_code'] = None

        # Get the expected error message and evaluate it
        with pytest.raises(ValueError) as verr:
            general._check_madrigal_params(**self.kwargs)

        assert str(verr).find("Must supply Madrigal instrument code") >= 0
        return

    @pytest.mark.parametrize("bad_val", [None, 17, False, 12.34])
    @pytest.mark.parametrize("test_key", ['user', 'password'])
    def test_check_madrigal_params_bad_input(self, bad_val, test_key):
        """Test that an error is thrown if non-string is passed through.

        Parameters
        ----------
        bad_val
            Any value that is not a string
        test_key : str
            Key in self.kwargs to reset

        """
        # Set up the kwargs for this test
        del self.kwargs['kindats'], self.kwargs['supported_tags']
        self.kwargs[test_key] = bad_val

        # Get the expected error message and evaluate it
        with pytest.raises(ValueError) as verr:
            general._check_madrigal_params(**self.kwargs)

        assert str(verr).find("The madrigal database requries a username") >= 0
        return

    @pytest.mark.parametrize("del_val", ['kindats', 'supported_tags'])
    def test_list_remote_files_bad_kwargs(self, del_val):
        """Test that an error is thrown if None is passed through.

        Parameters
        ----------
        del_val
            Key to remove from input

        """
        # Set up the kwargs for this test
        del self.kwargs[del_val]

        # Get the expected error message and evaluate it
        with pytest.raises(ValueError) as verr:
            general.list_remote_files('testing', 'tag', **self.kwargs)

        assert str(verr).find("Must supply supported_tags and kindats") >= 0
        return

    def test_list_remote_files_bad_tag_inst_id(self):
        """Test that an error is thrown if None is passed through."""

        # Get the expected error message and evaluate it
        with pytest.raises(KeyError) as kerr:
            general.list_remote_files('testing', 'not_tag', **self.kwargs)

        assert str(kerr).find('not_tag') >= 0
        return

    def test_load_no_time(self):
        """Test raises ValueError if time data is missing from file."""
