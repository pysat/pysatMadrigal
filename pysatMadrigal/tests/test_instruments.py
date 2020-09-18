import pytest

import pysatMadrigal
from pysat.tests.instrument_test_class import generate_instrument_list
from pysat.tests.instrument_test_class import InstTestClass

instruments = generate_instrument_list(inst_loc=pysatMadrigal.instruments)

method_list = [func for func in dir(InstTestClass)
               if callable(getattr(InstTestClass, func))]
# Search tests for iteration via pytestmark, update instrument list
for method in method_list:
    if hasattr(getattr(InstTestClass, method), 'pytestmark'):
        # Get list of names of pytestmarks
        mark_name = [mod_mark.name for mod_mark
                     in getattr(InstTestClass, method).pytestmark]

        # Add instruments from your library
        if 'all_inst' in mark_name:
            mark = pytest.mark.parametrize("inst_name", instruments['names'])
            getattr(InstTestClass, method).pytestmark.append(mark)
        elif 'download' in mark_name:
            mark = pytest.mark.parametrize("inst_dict",
                                           instruments['download'])
            getattr(InstTestClass, method).pytestmark.append(mark)
        elif 'no_download' in mark_name:
            mark = pytest.mark.parametrize("inst_dict",
                                           instruments['no_download'])
            getattr(InstTestClass, method).pytestmark.append(mark)

# remote_file_list not functional in current code.  Disabling for now
if 'test_remote_file_list' in method_list:
    mark = pytest.mark.skip(reason="not currently implemented")
    getattr(InstTestClass, 'test_remote_file_list').pytestmark.append(mark)


class TestInstruments(InstTestClass):

    def setup(self):
        """Runs before every method to create a clean testing setup
        """
        self.inst_loc = pysatMadrigal.instruments

    def teardown(self):
        """Runs after every method to clean up previous testing
        """
        del self.inst_loc
