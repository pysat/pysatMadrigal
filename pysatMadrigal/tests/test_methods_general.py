import pytest

from pysatMadrigal.instruments.methods import general


class TestBasic():

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.kwargs = {'inst_code': 'inst_code',
                       'user': 'username',
                       'password': 'password'}

    def cleanup(self):
        """Runs after every method to clean up previous testing."""
        del self.kwargs

    @pytest.mark.parametrize("del_val",
                             ['inst_code', 'user', 'password'])
    def test_check_madrigal_params_no_input(self, del_val):
        """Test that an error is thrown if None is passed through"""
        self.kwargs[del_val] = None

        with pytest.raises(ValueError):
            general._check_madrigal_params(**self.kwargs)

    @pytest.mark.parametrize("del_val",
                             ['user', 'password'])
    def test_check_madrigal_params_bad_input(self, del_val):
        """Test that an error is thrown if non-string is passed through"""
        self.kwargs[del_val] = 17

        with pytest.raises(ValueError):
            general._check_madrigal_params(**self.kwargs)
