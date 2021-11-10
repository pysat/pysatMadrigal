#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Unit tests for the general instrument methods."""

import gzip
import tempfile
import os
import pysat
import pytest

from pysatMadrigal.instruments.methods import general


class TestLocal(object):
    """Unit tests for general methods that run locally."""

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        self.out = None
        return

    def teardown(self):
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

    def teardown(self):
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

    @pytest.mark.parametrize("in_key, in_val, test_verr", [
        ("kindat", None, "Must supply Madrigal experiment code"),
        ("file_type", "not a file", "Unknown file format")])
    def test_download_valueerror(self, in_key, in_val, test_verr):
        """Test raises ValueError if `kindat` or `file_type` is unknown.

        Parameters
        ----------
        in_key : str
            Input key
        in_val : str, int, float, NoneType, bool
            Input value
        test_verr : str
            Expected ValueError message

        """
        del self.kwargs['supported_tags'], self.kwargs['kindats']
        self.kwargs[in_key] = in_val

        with pytest.raises(ValueError) as verr:
            general.download([], **self.kwargs)

        assert str(verr).find(test_verr) >= 0
        return

    def test_get_remote_filenames_bad_date_array(self):
        """Test raises ValueError for unexpected date_array input."""

        del self.kwargs['supported_tags'], self.kwargs['kindats']
        self.kwargs['date_array'] = []

        with pytest.raises(ValueError) as verr:
            general.get_remote_filenames(**self.kwargs)

        assert str(verr).find("unknown date_array supplied") >= 0
        return


class TestSimpleFiles(object):
    """Tests for general methods with simple files."""

    def setup(self):
        """Create a clean testing setup."""

        # Create testing directory
        self.data_path = tempfile.TemporaryDirectory()

        # Initialize a test file name
        self.temp_file = os.path.join(self.data_path.name, "temp.simple")
        self.datalines = "\n".join(["year month day hour min sec data1",
                                    "2009 1 1 0 0 0 -4.7"])

        return

    def teardown(self):
        """Clean up previous testing."""

        # Remove the temporary directory and file
        os.remove(self.temp_file)
        self.data_path.cleanup()

        del self.data_path, self.temp_file, self.datalines
        return

    def write_temp_file(self, use_gzip=True):
        """Write data to a temporary file, zipping if desired.

        Parameters
        ----------
        use_gzip : bool
            GZip the data and update the temporary filename if True, leave it
            alone if False (default=True)

        """

        local_open = open

        if use_gzip:
            local_open = gzip.open
            self.temp_file = ".".join([self.temp_file, 'gz'])

        with local_open(self.temp_file, 'w') as fout:
            fout.write(bytes(self.datalines, 'utf-8'))

        return

    def test_load_bad_times(self):
        """Test load raises ValueError with bad time data."""
        # Update the data lines, removing some time inputs
        self.datalines = "\n".join(["year month day hour min data1",
                                    "2009 1 1 0 0 -4.7"])
        self.write_temp_file()

        # Retrieve error message
        with pytest.raises(ValueError) as verr:
            general.load([self.temp_file])

        assert str(verr).find("unable to construct time index") >= 0
        return

    def test_load_bad_coords(self):
        """Test load raises ValueError with bad time xarray coordinates."""
        # Write a temporary file
        self.write_temp_file()

        # Retrieve error message
        with pytest.raises(ValueError) as verr:
            general.load([self.temp_file], xarray_coords=['lat'])

        assert str(verr).find("unknown coordinate key") >= 0
        return

    def test_load(self):
        """Test successsful loading of data and metadata."""

        # Write a temporary file
        self.write_temp_file()

        # Get the data and metadata
        data, meta = general.load([self.temp_file])

        # Test the loaded data
        tst_lines = self.datalines.split('\n')
        header = tst_lines[0].split()
        values = tst_lines[1].split()

        # Assert the data columns and number of values are the same
        assert len(header) == len(data.columns)
        assert len(data.index) == len(tst_lines) - 1

        # Test the values for the meta data name and the first data value
        for i, col in enumerate(header):
            assert str(data[col][0]).find(values[i]) == 0
            assert meta[col, meta.labels.name] == col

        return


class TestListFiles(object):
    """Tests for general methods function `list_files`."""

    def setup(self):
        """Create a clean testing setup."""

        # Initalize a pysat Instrument
        self.inst = pysat.Instrument('pysat', 'testing')

        # Initialize a test file name and supported tags
        self.temp_files = []
        self.supported_tags = {self.inst.inst_id: {
            self.inst.tag: '{{year:4d}}-{{month:02d}}-{{day:02d}}.{file_type}'}}

        return

    def teardown(self):
        """Clean up previous testing."""

        # Remove the temporary directory and file
        for tfile in self.temp_files:
            os.remove(tfile)

        del self.inst, self.temp_files, self.supported_tags
        return

    def write_temp_files(self, same_time=False):
        """Create empty temporary files.

        Parameters
        ----------
        same_time : bool
            Use the same base filename for the temporary files with different
            extension if True, use different base filenames if False.
            (default=False)

        """

        for i, ext in enumerate(general.file_types.values()):
            # Get the desired base file name
            j = 0 if same_time else i
            base_filename = os.path.splitext(self.inst.files.files[j])[0]
            temp_file = os.path.join(self.inst.files.data_path,
                                     "{:s}.{:s}".format(base_filename, ext))

            # Create and save the temporary file to the file list
            self.temp_files.append(temp_file)
            with open(temp_file, 'w'):
                pass  # Create an empty file

        return

    @pytest.mark.parametrize("same_time", [True, False])
    def test_list_files_mult_type(self, same_time):
        """Test `list_files` with multiple file types.

        Parameters
        ----------
        same_time : bool
            Use the same base filename for the temporary files with different
            extension if True, use different base filenames if False.

        """

        #  Write the temporary files
        self.write_temp_files(same_time=same_time)

        # List the temporary files
        out_files = general.list_files(self.inst.tag, self.inst.inst_id,
                                       data_path=self.inst.files.data_path,
                                       supported_tags=self.supported_tags)

        # Prepare the testing data
        out_list = [os.path.join(self.inst.files.data_path, ofile)
                    for ofile in out_files]
        ntimes = 1 if same_time else len(self.temp_files)

        # Test the listed file names and time indexes
        pysat.utils.testing.assert_lists_equal(out_list, self.temp_files)
        assert len(out_files.index.unique()) == ntimes
        return

    @pytest.mark.parametrize("same_time", [True, False])
    @pytest.mark.parametrize("file_type", [
        ftype for ftype in general.file_types.keys()])
    def test_list_files_single_type(self, same_time, file_type):
        """Test `list_files` with multiple file types.

        Parameters
        ----------
        same_time : bool
            Use the same base filename for the temporary files with different
            extension if True, use different base filenames if False.
        file_type : str
            File type to list.

        """

        #  Write the temporary files
        self.write_temp_files(same_time=same_time)

        # List the temporary files
        out_files = general.list_files(self.inst.tag, self.inst.inst_id,
                                       data_path=self.inst.files.data_path,
                                       supported_tags=self.supported_tags,
                                       file_type=file_type)

        # Prepare the testing data
        out_list = [os.path.join(self.inst.files.data_path, ofile)
                    for ofile in out_files]

        # Test the listed file names and time indexes
        pysat.utils.testing.assert_list_contains(out_list, self.temp_files,
                                                 test_case=True)
        assert len(out_files.index) == 1
        return

    def test_list_no_files(self):
        """Test listing files without creating temporary files."""

        # List the temporary files with
        out_files = general.list_files(self.inst.tag, self.inst.inst_id,
                                       data_path=self.inst.files.data_path,
                                       supported_tags=self.supported_tags)

        # Test the output
        assert len(out_files) == 0
        assert len(out_files.index) == 0
        return
