import tempfile
import pytest

import pysat
from pysat.utils import generate_instrument_list
from pysat.tests.instrument_test_class import InstTestClass

import pysatMadrigal

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
    def setup_class(self):
        """Runs once before the tests to initialize the testing setup
        """
        # Make sure to use a temporary directory so that the user's setup is
        # not altered
        self.tempdir = tempfile.TemporaryDirectory()
        self.saved_path = pysat.data_dir
        pysat.utils.set_data_dir(self.tempdir.name, store=False)

        # Developers for instrument libraries should update the following line
        # to point to their own subpackage location, e.g.,
        # self.inst_loc = mypackage.instruments
        self.inst_loc = pysatMadrigal.instruments

    def teardown_class(self):
        """Runs after every method to clean up previous testing
        """
        pysat.utils.set_data_dir(self.saved_path, store=False)
        self.tempdir.cleanup()
        del self.inst_loc, self.saved_path, self.tempdir
