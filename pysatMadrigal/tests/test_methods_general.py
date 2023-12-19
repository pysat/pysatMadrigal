#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
"""Unit tests for the general instrument methods."""

import datetime as dt
import gzip
import logging
import numpy as np
import os
from packaging import version
import tempfile

from madrigalWeb import madrigalWeb
import netCDF4 as nc
import pandas as pds
import pysat
from pysat.utils.testing import eval_bad_input
import pytest
import xarray as xr

from pysatMadrigal.instruments.methods import general


class TestLocal(object):
    """Unit tests for general methods that run locally."""

    def setup_method(self):
        """Run before every method to create a clean testing setup."""
        self.out = None
        return

    def teardown_method(self):
        """Run after every method to clean up previous testing."""
        del self.out
        return

    def test_acknowledgements(self):
        """Test the Madrigal acknowledgements."""
        self.out = general.cedar_rules()
        assert self.out.find("CEDAR 'Rules of the Road'") >= 0
        return

    def test_sort_file_format(self, caplog):
        """Test successful sorting of file names by extension."""
        # Get the output and raise the logging warning
        with caplog.at_level(logging.WARN, logger='pysat'):
            self.out = general.sort_file_formats(['test.hdf5', 'test.netCDF4',
                                                  'test.simple.gz', 'test.bad'])

        # Evaluate the output
        assert isinstance(self.out, dict)
        pysat.utils.testing.assert_lists_equal(list(self.out.keys()),
                                               ['hdf5', 'netCDF4', 'simple'])

        # Evaluate the logger warning
        assert len(caplog.records) == 1, "unexpected number of warnings"
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message.find(
            "file with unknown file type") >= 0
        return

    @pytest.mark.parametrize("xarray_coords", [None, ["lat"]])
    def test_empty_load(self, xarray_coords):
        """Test the general load function with no data files."""
        # Run the empty load
        self.out = general.load([], xarray_coords=xarray_coords)

        # Test the empty output
        if xarray_coords is None:
            assert isinstance(self.out[0], pds.DataFrame)
        else:
            assert isinstance(self.out[0], xr.Dataset)

        assert self.out[1] == pysat.Meta()
        return

    @pytest.mark.skipif(version.Version(pysat.__version__)
                        < version.Version('3.0.2'),
                        reason="requires newer pysat version.")
    @pytest.mark.parametrize("pad", [None, pds.DateOffset(days=2)])
    def test_filter_data_single_date(self, pad):
        """Test Instrument data filtering success.

        Parameters
        ----------
        pad : dict, pds.DateOffset, or NoneType
            Pad values.  If not None, no filtering will be performed.

        """
        # Initalize the test Instrument
        self.out = pysat.Instrument('pysat', 'testing', pad=pad)

        # Load a mult-day period
        start = self.out.inst_module._test_dates['']['']
        stop = start + dt.timedelta(days=2)
        self.out.load(date=start, end_date=stop)

        # Filter the loaded data
        general.filter_data_single_date(self.out)

        # Ensure the expected data is in the Instrument
        assert self.out.date == start
        assert self.out.index[0] == start
        if pad is None:
            assert self.out.index[-1] == start + dt.timedelta(seconds=86399)
        else:
            assert self.out.index[-1] == stop - dt.timedelta(seconds=1)

        return

    @pytest.mark.parametrize("pandas_format", [None, True, False])
    def test_known_madrigal_inst_codes(self, pandas_format):
        """Test the output that specifies known Madrigal instrument codes.

        Parameters
        ----------
        pandas_format : bool or NoneType
            Separate instrument codes by time-series (True) or multi-dimensional
            data types (False) if a boolean is supplied, or supply all if
            NoneType (default=None)

        """
        self.out = general.known_madrigal_inst_codes(pandas_format)

        assert isinstance(self.out, dict)

        if pandas_format is not False:
            assert '120' in self.out.keys()

        if pandas_format is not True:
            assert '10' in self.out.keys()

        return

    @pytest.mark.parametrize("inst_code", [120, 120.0, "120"])
    def test_madrigal_file_format_str(self, inst_code):
        """Test the file format string for known Madrigal instrument codes.

        Parameters
        ----------
        inst_code : int, float, or str
            Madrigal instrument code for a well-defined file format

        """
        # Get the function output
        self.out = general.madrigal_file_format_str(inst_code)

        # Test the formatted string
        for req_str in ['year', 'month', 'day', 'file_type']:
            assert self.out.find(req_str) > 0, "{:s} not in {:s}".format(
                req_str, self.out)
        return

    @pytest.mark.parametrize("inst_code, msg", [
        (8001, "file format string missing date info"),
        (1, "file format string not available for instrument code"),
        (8000, "file format string has multiple '*'"),
        (8400, "file format string has '*' between formatting constraints")])
    def test_madrigal_file_format_str_with_warnings(self, inst_code, msg,
                                                    caplog):
        """Test poorly constrained file formats for Madrigal instrument codes.

        Parameters
        ----------
        inst_code : int
            Madrigal instrument code for a poorly constrained file format
        msg : str
            Logger warning message

        """
        # Get the output and raise the logging warning
        with caplog.at_level(logging.WARN, logger='pysat'):
            self.out = general.madrigal_file_format_str(inst_code)

        # Test the formatted string
        assert self.out.find("file_type") > 0, \
            "'file_type' missing from {:s}".format(self.out)

        # Test the logger warning
        assert len(caplog.records) == 1, "unexpected number of warnings"
        assert caplog.records[0].levelname == "WARNING"
        assert caplog.records[0].message.find(msg) >= 0
        return

    @pytest.mark.parametrize("inst_code", [8001, 1, 8000, 8400])
    def test_madrigal_file_format_str_quiet_warnings(self, inst_code, caplog):
        """Test quiet, poorly constrained file formats for Madrigal inst codes.

        Parameters
        ----------
        inst_code : int
            Madrigal instrument code for a poorly constrained file format

        """
        # Get the output and raise the logging warning
        with caplog.at_level(logging.WARN, logger='pysat'):
            self.out = general.madrigal_file_format_str(inst_code,
                                                        verbose=False)

        # Test the formatted string
        assert self.out.find("file_type") > 0, \
            "'file_type' missing from {:s}".format(self.out)

        # Test the logger warning
        assert len(caplog.records) == 0, "unexpected number of warnings"
        return

    @pytest.mark.parametrize("inst_code, msg", [
        (8001, "file format string missing date info"),
        (1, "file format string not available for instrument code"),
        (8000, "file format string has multiple '*'"),
        (8400, "file format string has '*' between formatting constraints")])
    def test_madrigal_file_format_str_with_errors(self, inst_code, msg):
        """Test poorly constrained file formats raise ValueErrors.

        Parameters
        ----------
        inst_code : int
            Madrigal instrument code for a poorly constrained file format
        msg : str
            Logger warning message

        """
        # Get the output and raise the logging warning
        with pytest.raises(ValueError) as verr:
            general.madrigal_file_format_str(inst_code, strict=True)

        # Test the logger warning
        assert str(verr).find(msg) >= 0
        return


class TestErrors(object):
    """Tests for errors raised by the general methods."""

    def setup_method(self):
        """Create a clean testing setup."""
        self.kwargs = {'inst_code': '10',
                       'user': 'username',
                       'password': 'password',
                       'kindats': {'testing': {'tag': 1000}},
                       'supported_tags': {'testing': {'tag': 'file%Y%m%d.nc'}}}
        return

    def teardown_method(self):
        """Clean up previous testing."""
        del self.kwargs
        return

    @pytest.mark.parametrize("inst_code", [None, "-47"])
    def test_check_madrigal_params_no_code(self, inst_code):
        """Test that an error is thrown if None is passed through.

        Parameters
        ----------
        inst_code : str or NoneType
            A bad Madrigal instrument code

        """
        # Set up the kwargs for this test
        del self.kwargs['kindats'], self.kwargs['supported_tags']
        self.kwargs['inst_code'] = inst_code

        eval_bad_input(general._check_madrigal_params, ValueError,
                       "Unknown Madrigal instrument code",
                       input_kwargs=self.kwargs)
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
        eval_bad_input(general._check_madrigal_params, ValueError,
                       "The madrigal database requries a username",
                       input_kwargs=self.kwargs)
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
        eval_bad_input(general.list_remote_files, ValueError,
                       "Must supply supported_tags and kindats",
                       input_args=['testing', 'tag'], input_kwargs=self.kwargs)
        return

    def test_list_remote_files_bad_tag_inst_id(self):
        """Test that an error is thrown if None is passed through."""
        # Get the expected error message and evaluate it
        eval_bad_input(general.list_remote_files, KeyError, "not_tag",
                       input_args=['testing', 'not_tag'],
                       input_kwargs=self.kwargs)
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

        # Get the expected error message and evaluate it
        eval_bad_input(general.download, ValueError, test_verr,
                       input_args=[[]], input_kwargs=self.kwargs)
        return

    def test_get_remote_filenames_bad_date_array(self):
        """Test raises ValueError for unexpected date_array input."""
        del self.kwargs['supported_tags'], self.kwargs['kindats']
        self.kwargs['date_array'] = []

        # Get the expected error message and evaluate it
        eval_bad_input(general.get_remote_filenames, ValueError,
                       "unknown date_array supplied", input_kwargs=self.kwargs)
        return

    def test_convert_pandas_to_xarray_bad_data_vars(self):
        """Test raises ValueError for unexpected date_array input."""
        self.kwargs = [{('time', ): ['bad_var']}, pds.DataFrame([0]),
                       pds.DatetimeIndex([dt.datetime(2001, 1, 1)])]

        # Get the expected error message and evaluate it
        eval_bad_input(general.convert_pandas_to_xarray, ValueError,
                       "All data variables", input_args=self.kwargs)
        return


class TestSimpleFiles(object):
    """Tests for general methods with simple files."""

    def setup_method(self):
        """Create a clean testing setup."""
        # Create testing directory
        self.data_path = tempfile.TemporaryDirectory()

        # Initialize a test file name
        self.temp_file = os.path.join(self.data_path.name, "temp.simple")
        self.datalines = "\n".join(["year month day hour min sec data1",
                                    "2009 1 1 0 0 0 -4.7"])

        # Initialize the output
        self.data = None
        self.meta = None

        return

    def teardown_method(self):
        """Clean up previous testing."""
        # Remove the temporary directory and file
        os.remove(self.temp_file)
        self.data_path.cleanup()

        del self.data_path, self.temp_file, self.datalines, self.data, self.meta
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

    def eval_data_and_metadata(self):
        """Evaluate the loaded test data and metadata."""
        # Test the loaded data
        tst_lines = self.datalines.split('\n')
        header = tst_lines[0].split()
        values = tst_lines[1].split()

        # Assert the data columns and number of values are the same
        assert len(header) == len(self.data.columns)
        assert len(self.data.index) == len(tst_lines) - 1

        # Test the values for the meta data name and the first data value
        for i, col in enumerate(header):
            assert str(self.data[col][0]).find(values[i]) == 0
            assert self.meta[col, self.meta.labels.name] == col

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

    @pytest.mark.parametrize('xarray_coords', [None, ['time']])
    def test_load(self, xarray_coords):
        """Test successsful loading of data and metadata.

        Parameters
        ----------
        xarray_coords : NoneType or list
            Possible xarray_coords for a good simple file

        """
        # Write a temporary file
        self.write_temp_file()

        # Get the data and metadata
        self.data, self.meta = general.load([self.temp_file],
                                            xarray_coords=xarray_coords)

        self.eval_data_and_metadata()
        return

    def test_load_duplicate_times(self, caplog):
        """Test successful data and metadata loading with duplicate times."""
        # Add a duplicate line
        self.datalines = '\n'.join([self.datalines,
                                    self.datalines.split('\n')[-1]])

        # Write a temporary file
        self.write_temp_file()

        # Get the data and metadata, catching warnings
        with caplog.at_level(logging.WARN, logger='pysat'):
            self.data, self.meta = general.load([self.temp_file])

        # Test the loaded data
        self.eval_data_and_metadata()

        # Test the logging message
        captured = caplog.text
        assert captured.find("duplicated time indices") >= 0
        return


class TestNetCDFFiles(object):
    """Tests for general methods with NetCDF files."""

    def setup_method(self):
        """Create a clean testing setup."""
        # Create testing directory
        self.data_path = tempfile.TemporaryDirectory()

        # Initialize a test file name
        self.temp_files = []
        self.xarray_coords = [{('time',): ['time'],
                               ('lat',): ['lat'],
                               ('lon',): ['lon'],
                               ('time', 'lat', 'lon'): ['value']}]

        # Initialize the output
        self.data = None
        self.meta = None

        return

    def teardown_method(self):
        """Clean up previous testing."""
        # Remove the temporary directory and file
        for tfile in self.temp_files:
            if os.path.isfile(tfile):
                try:
                    os.remove(tfile)
                except PermissionError:
                    pass  # Windows thinks files are always open

        try:
            self.data_path.cleanup()
        except Exception:
            # TODO(#https://github.com/pysat/pysat/issues/974): Windows fix
            # until `ignore_cleanup_errors=True` can be used (3.10 is lowest)
            pass

        del self.data_path, self.temp_files, self.xarray_coords, self.data
        del self.meta
        return

    def write_temp_files(self, nfiles=0):
        """Write data to a temporary file, zipping if desired.

        Parameters
        ----------
        nfiles : int
            Number of temporary NetCDF files to write (default=0)

        """
        for i in range(nfiles):
            tfile = os.path.join(self.data_path.name,
                                 "temp{:d}.netCDF4".format(i))

            # Write a temporary file with data, based off of example:
            # https://opensourceoptions.com/blog/
            #    create-netcdf-files-with-python/
            with nc.Dataset(tfile, "w", format="NETCDF4") as ds:
                # Write the file attributes
                if nfiles > 1:
                    ds.catalog_text = "catalog text test"

                # Write the file dimensions, using Madrigal defaults
                ds.createDimension('timestamps', None)
                ds.createDimension('lat', 10)
                ds.createDimension('lon', 10)

                # Write the data
                dat_dict = {dkey: ds.createVariable(dkey, 'f4', (dkey,))
                            for dkey in ['timestamps', 'lat', 'lon']}

                dat_dict['value'] = ds.createVariable(
                    'value', 'f4', ('timestamps', 'lat', 'lon',))

                dat_dict['timestamps'][0] = i
                dat_dict['lat'][:] = np.arange(40.0, 50.0, 1.0)
                dat_dict['lon'][:] = np.arange(-110.0, -100.0, 1.0)
                dat_dict['value'][0, :, :] = np.random.uniform(0, 100,
                                                               size=(10, 10))

                # Write the default Madrigal meta data
                for dat_name in ['lat', 'lon', 'value']:
                    dat_dict[dat_name].units = 'deg'
                    dat_dict[dat_name].description = 'test data set'

            self.temp_files.append(tfile)

        return

    def eval_dataset_meta_output(self):
        """Evaluate the dataset and meta output for the temp files."""
        # Evaluate the Instrument data variables and coordinates
        pysat.utils.testing.assert_lists_equal(
            [ckey for ckey in self.data.coords.keys()], ['time', 'lat', 'lon'])
        assert "value" in self.data.data_vars
        assert self.data['time'].shape[0] == len(self.temp_files)

        # Evaluate the meta data
        meta_keys = ['timestamps', 'lat', 'lon', 'value']
        pysat.utils.testing.assert_lists_equal(
            [ckey for ckey in self.meta.keys()], meta_keys)

        for mkey in meta_keys:
            uval = '' if mkey == 'timestamps' else 'deg'
            dval = '' if mkey == 'timestamps' else 'test data set'
            assert self.meta[mkey, self.meta.labels.units] == uval, \
                "unexpected unit metadata for {:}: {:}".format(
                    repr(mkey), repr(self.meta[mkey, self.meta.labels.units]))
            assert self.meta[mkey, self.meta.labels.desc] == dval, \
                "unexpected unit metadata for {:}: {:}".format(
                    repr(mkey), repr(self.meta[mkey, self.meta.labels.desc]))

        return

    @pytest.mark.parametrize("nfiles", [1, 2, 3])
    def test_load_netcdf(self, nfiles):
        """Test the loading of single or multiple NetCDF files.

        Parameters
        ----------
        nfiles : int
            Number of NetCDF files to load

        """
        # Create the temporary files
        self.write_temp_files(nfiles=nfiles)

        # Load the file data
        self.data, self.meta = general.load(self.temp_files, self.xarray_coords)

        # Evaluate the loaded data
        self.eval_dataset_meta_output()

        # Close for Windows OS
        self.data.close()

        return

    def test_load_netcdf_extra_xarray_coord(self):
        """Test the loading of a NetCDF file with extra xarray coordinates."""
        # Create the temporary files
        self.write_temp_files(nfiles=1)

        # Add extra xarray coordinates
        self.xarray_coords[0][('space',)] = ['space']

        # Load the file data
        self.data, self.meta = general.load(self.temp_files, self.xarray_coords)

        # Evaluate the loaded data
        self.eval_dataset_meta_output()

        # Close for Windows OS
        self.data.close()

        return


class TestListFiles(object):
    """Tests for general methods function `list_files`."""

    def setup_method(self):
        """Create a clean testing setup."""
        # Initalize a pysat Instrument
        self.inst = pysat.Instrument('pysat', 'testing')

        # Initialize a test file name and supported tags
        self.temp_files = []
        self.supported_tags = {self.inst.inst_id: {
            self.inst.tag: '{{year:4d}}-{{month:02d}}-{{day:02d}}.{file_type}'}}

        # Create the Instrument data path.
        pysat.utils.files.check_and_make_path(self.inst.files.data_path)

        return

    def teardown_method(self):
        """Clean up previous testing."""
        # Remove the temporary file, if it exists
        for tfile in self.temp_files:
            if os.path.isfile(tfile):
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

        Return
        ------
        bool
            True if the correct number of files were created, False if not

        """
        for i, ext in enumerate(general.file_types.values()):
            # Get the desired base file name
            j = 0 if same_time else i
            base_filename = os.path.splitext(self.inst.files.files[j])[0]
            temp_file = os.path.join(self.inst.files.data_path,
                                     "{:s}.{:s}".format(base_filename, ext))

            # Create and save the temporary file to the file list
            with open(temp_file, 'w'):
                pass  # Create an empty file

            # Add file to list if it exists
            if os.path.isfile(temp_file):
                self.temp_files.append(temp_file)

        return len(self.temp_files) == len(general.file_types.values())

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
        assert self.write_temp_files(same_time=same_time)

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
        assert self.write_temp_files(same_time=same_time)

        # List the temporary files
        out_files = general.list_files(self.inst.tag, self.inst.inst_id,
                                       data_path=self.inst.files.data_path,
                                       supported_tags=self.supported_tags,
                                       file_type=file_type)

        # Prepare the testing data
        out_list = [os.path.join(self.inst.files.data_path, ofile)
                    for ofile in out_files]

        # Test the listed file names and time indexes
        pysat.utils.testing.assert_list_contains(out_list, self.temp_files)
        assert len(out_files.index) == 1
        return

    @pytest.mark.parametrize("file_type", [None, 'hdf5', 'simple', 'netCDF4'])
    def test_list_no_files(self, file_type):
        """Test listing files without creating temporary files.

        Parameters
        ----------
        file_type : str or NoneType
            File format for Madrigal data. If None, will look for all known
            file types.

        """
        # List the temporary files with
        out_files = general.list_files(self.inst.tag, self.inst.inst_id,
                                       data_path=self.inst.files.data_path,
                                       supported_tags=self.supported_tags,
                                       file_type=file_type)

        # Test the output
        assert len(out_files) == 0
        assert len(out_files.index) == 0
        return


class TestMadrigalExp(object):
    """Unit tests for the MadrigalWeb functions that use MadrigalExperiment."""

    def setup_method(self):
        """Create a clean testing environment."""
        self.exp = None
        self.start = dt.datetime(1950, 1, 1)
        self.stop = dt.datetime.utcnow()
        return

    def teardown_method(self):
        """Tear down the existing testing environment."""
        del self.exp, self.start, self.stop
        return

    def set_exp_list(self, exp_id):
        """Set a Madrigal experiment object.

        Parameters
        ----------
        exp_id : int
            Madrigal experiment ID

        """
        self.exp = madrigalWeb.MadrigalExperiment(
            exp_id, "http://cedar.openmadrigal.org", "test experiment",
            1, "test site", 10, "test instrument", self.start.year,
            self.start.month, self.start.day, self.start.hour,
            self.start.minute, self.start.second, self.stop.year,
            self.stop.month, self.stop.day, self.stop.hour, self.stop.minute,
            self.stop.second, True, "http://cedar.openmadrigal.org/fake",
            "pysat test", "pysat.developers@gmail.com", "20010101", True, "1.0")

        return

    @pytest.mark.parametrize("exp_id", [0, 1010001])
    @pytest.mark.parametrize("date_array", [
        None, [dt.datetime(2001, 1, 1)],
        pds.date_range(dt.datetime(2001, 1, 1), dt.datetime(2001, 1, 3)),
        [dt.datetime(1001, 1, 1), dt.datetime(2001, 1, 15)]])
    def test_good_exp_is_good(self, exp_id, date_array):
        """Test the `general.good_exp` function returns True.

        Parameters
        ----------
        exp_id : int
            Madrigal experiment ID
        date_array : list-like or NoneType
            List of datetime download times or None to only test that the
            Madrigal experiment is valid.

        """
        # Set the MadrigalExperiment object using good fake information
        self.set_exp_list(exp_id)

        # Ensure experiment test returns True
        assert general.good_exp(self.exp, date_array)

        return

    @pytest.mark.parametrize("exp_id,date_array", [
        (-1, None), (108000, [dt.datetime(1001, 1, 1)])])
    def test_good_exp_is_bad(self, exp_id, date_array):
        """Test the `general.good_exp` function returns True.

        Parameters
        ----------
        exp_id : int
            Madrigal experiment ID
        date_array : list-like or NoneType
            List of datetime download times or None to only test that the
            Madrigal experiment is valid.

        """
        # Set the MadrigalExperiment object using bad fake information
        self.set_exp_list(exp_id)

        # Ensure the experiment test returns False
        assert not general.good_exp(self.exp, date_array)
        return
