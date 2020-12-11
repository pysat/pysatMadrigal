# -*- coding: utf-8 -*-.
"""Provides default routines for integrating CEDAR Madrigal instruments into
pysat, reducing the amount of user intervention.

 """

import datetime as dt
import logging
import numpy as np
import os
import pandas as pds
import xarray as xr

import h5py
from madrigalWeb import madrigalWeb

import pysat

logger = logging.getLogger(__name__)
file_types = ['hdf5', 'netCDF4', 'simple']


def cedar_rules():
    """ General acknowledgement statement for Madrigal data.

    Returns
    -------
    ackn : string
        String with general acknowledgement for all CEDAR Madrigal data

    """
    ackn = "Contact the PI when using this data, in accordance with the CEDAR"
    ackn += " 'Rules of the Road'"
    return ackn


def load(fnames, tag=None, inst_id=None, xarray_coords=[], file_type='hdf5'):
    """Loads data from Madrigal into Pandas or XArray

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    Parameters
    ----------
    fnames : array-like
        iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : string
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. While
        tag defaults to None here, pysat provides '' as the default
        tag unless specified by user at Instrument instantiation. (default='')
    inst_id : string
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    xarray_coords : list
        List of keywords to use as coordinates if xarray output is desired
        instead of a Pandas DataFrame.  Can build an xarray Dataset
        that have different coordinate dimensions by providing a dict
        inside the list instead of coordinate variable name strings. Each dict
        will have a tuple of coordinates as the key and a list of variable
        strings as the value.  For example,
        xarray_coords=[{('time',): ['year', 'doy'],
                        ('time', 'gdalt'): ['data1', 'data2']}]. (default=[])
    file_type : string
        File format for Madrigal data.  Currently only accept 'netCDF4' and
        'hdf5'. (default='hdf5')

    Returns
    -------
    data : pds.DataFrame or xr.Dataset
        A pandas DataFrame or xarray Dataset holding the data from the HDF5
        file
    metadata : pysat.Meta
        Metadata from the HDF5 file, as well as default values from pysat

    Note
    ----
    Currently HDF5 reading breaks if a different file type was used previously

    """
    # Test the file format
    if file_type not in ['netCDF4', 'hdf5']:
        raise ValueError('unknown file format {:s}'.format(file_type))

    # Initialize the output
    meta = pysat.Meta()
    labels = []

    # Load the file data
    if file_type == "netCDF4":
        # Xarray natively opens netCDF data into a Dataset
        if len(fnames) == 1:
            file_data = xr.open_dataset(fnames[0])
        else:
            file_data = xr.open_mfdataset(fnames, combine='by_coords')

        # Currently not saving file header data, as all metadata is at
        # the data variable level
        if len(labels) == 0:
            for item in file_data.data_vars.keys():
                name_string = item
                unit_string = file_data[item].attrs['units']
                desc_string = file_data[item].attrs['description']
                labels.append(name_string)
                meta[name_string.lower()] = {'long_name': name_string,
                                             'units': unit_string,
                                             'desc': desc_string}
                # remove any metadata from xarray
                file_data[item].attrs = {}

        # Reset UNIX timestamp as datetime and set it as an index
        file_data = file_data.rename({'timestamps': 'time'})
        time_data = pds.to_datetime(file_data['time'].values, unit='s')
        data = file_data.assign_coords({'time': ('time', time_data)})

    elif file_type == "hdf5":
        # Ensure we don't try to create an xarray object with only time as
        # the coordinate
        coord_len = len(xarray_coords)
        if 'time' in xarray_coords:
            coord_len -= 1

        # Cycle through all the filenames
        fdata = []
        for fname in fnames:
            # Open the specified file and get the data and metadata
            filed = h5py.File(fname, 'r')
            file_data = filed['Data']['Table Layout']
            file_meta = filed['Metadata']['Data Parameters']

            # load up what is offered into pysat.Meta if this is the first file
            if len(labels) == 0:
                for item in file_meta:
                    name_string = item[0].decode('UTF-8')
                    unit_string = item[3].decode('UTF-8')
                    desc_string = item[1].decode('UTF-8')
                    labels.append(name_string)
                    meta[name_string.lower()] = {'long_name': name_string,
                                                 'units': unit_string,
                                                 'desc': desc_string}

            # Add additional metadata notes. Custom attributes attached to meta
            # are attached to corresponding Instrument object when pysat
            # receives data and meta from this routine
            for key in filed['Metadata']:
                if key != 'Data Parameters':
                    setattr(meta, key.replace(' ', '_'),
                            filed['Metadata'][key][:])

            # data into frame, with labels from metadata
            data = pds.DataFrame.from_records(file_data, columns=labels)

            # lowercase variable names
            data.columns = [item.lower() for item in data.columns]

            # datetime index from times
            time_keys = np.array(['year', 'month', 'day', 'hour', 'min', 'sec'])
            if not np.all([key in data.columns for key in time_keys]):
                time_keys = [key for key in time_keys
                             if key not in data.columns]
                raise ValueError(' '.join(["unable to construct time index, ",
                                           "missing {:}".format(time_keys)]))

            uts = 3600.0 * data.loc[:, 'hour'] + 60.0 * data.loc[:, 'min'] \
                + data.loc[:, 'sec']
            time = pysat.utils.time.create_datetime_index(
                year=data.loc[:, 'year'], month=data.loc[:, 'month'],
                day=data.loc[:, 'day'], uts=uts)

            # Declare index or recast as xarray
            if coord_len > 0:
                # If a list was provided, recast as a dict and grab the data
                # columns
                if not isinstance(xarray_coords, dict):
                    xarray_coords = {tuple(xarray_coords):
                                     [col for col in data.columns
                                      if col not in xarray_coords]}

                # Determine the order in which the keys should be processed:
                #  Greatest to least number of dimensions
                len_dict = {len(xcoords): xcoords
                            for xcoords in xarray_coords.keys()}
                coord_order = [len_dict[xkey] for xkey in sorted(
                    [lkey for lkey in len_dict.keys()], reverse=True)]

                # Append time to the data frame
                data = data.assign(time=pds.Series(time, index=data.index))

                # Cycle through each of the coordinate dimensions
                xdatasets = list()
                for xcoords in coord_order:
                    if not np.all([xkey.lower() in data.columns
                                   for xkey in xcoords]):
                        raise ValueError(''.join(['unknown coordinate key in ',
                                                  '[{:}], use'.format(xcoords),
                                                  ' only: {:}'.format(
                                                      data.columns)]))
                    if not np.all([xkey.lower() in data.columns
                                   for xkey in xarray_coords[xcoords]]):
                        data_mask = [xkey.lower() in data.columns
                                     for xkey in xarray_coords[xcoords]]
                        if np.all(~np.array(data_mask)):
                            raise ValueError(''.join(['all provided data ',
                                                      'variables [',
                                                      '{:}] are '.format(
                                                          xarray_coords[
                                                              xcoords]),
                                                      'unknown, use only: ',
                                                      '{:}'.format(
                                                          data.columns)]))
                        else:
                            logger.warning(''.join(['unknown data variable in',
                                                    ' [{:}], use only'.format(
                                                        xarray_coords[xcoords]),
                                                    ': {:}'.format(
                                                        data.columns)]))

                            # Remove the coordinates that aren't present
                            temp = np.array(xarray_coords[xcoords])[data_mask]
                            xarray_coords[xcoords] = list(temp)

                    # Select the desired data values
                    sel_data = data[list(xcoords) + xarray_coords[xcoords]]

                    # Remove duplicates before indexing, to ensure data with
                    # the same values at different locations are kept
                    sel_data = sel_data.drop_duplicates()

                    # Set the indices
                    sel_data = sel_data.set_index(list(xcoords))

                    # Recast as an xarray
                    xdatasets.append(sel_data.to_xarray())

                # Get the necessary information to test the data
                lcols = data.columns
                ldata = len(lcols)

                # Merge all of the datasets
                data = xr.merge(xdatasets)
                test_variables = [xkey for xkey in data.variables.keys()]
                ltest = len(test_variables)

                # Test to see that all data was retrieved
                if ltest != ldata:
                    if ltest < ldata:
                        estr = 'missing: {:}'.format(
                            ' '.join([dvar for dvar in lcols
                                      if dvar not in test_variables]))
                    else:
                        estr = 'have extra: {:}'.format(
                            ' '.join([tvar for tvar in test_variables
                                      if tvar not in lcols]))
                        raise ValueError(''.join(['coordinates not supplied ',
                                                  'for all data columns: ',
                                                  '{:d} != '.format(ltest),
                                                  '{:d}; '.format(ldata),
                                                  estr]))
            else:
                # Set the index to time
                data.index = time

                # Raise a logging warning if there are duplicate times. This
                # means the data should be stored as an xarray Dataset
                if np.any(time.duplicated()):
                    logger.warning(''.join(["duplicated time indices, consider",
                                            " specifing additional coordinates",
                                            " and storing the data as an ",
                                            "xarray Dataset"]))

            # Compile a list of the data objects
            fdata.append(data)

        # If multiple files were loaded, merge the data together
        if len(fdata) == 1:
            data = fdata[0]
        else:
            if coord_len > 0:
                data = xr.merge(fdata)
            else:
                data = pds.concat(fdata)

    return data, meta


def download(date_array, inst_code=None, kindat=None, data_path=None,
             user=None, password=None, url="http://cedar.openmadrigal.org",
             file_type='hdf5'):
    """Downloads data from Madrigal.

    Parameters
    ----------
    date_array : array-like
        list of datetimes to download data for. The sequence of dates need not
        be contiguous.
    inst_code : string
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindat : string
        Experiment instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    data_path : string
        Path to directory to download data to. (default=None)
    user : string
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : string
        Password for data download. (default=None)
    url : string
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    file_type : string
        File format for Madrigal data.  Load routines currently only accepts
        'hdf5' and 'netCDF4', but any of the Madrigal options may be used
        here. (default='hdf5')

    Note
    ----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """

    if file_type not in file_types:
        raise ValueError("Unknown file format {:}, accepts {:}".format(
            file_type, file_types))

    if inst_code is None:
        raise ValueError("Must supply Madrigal instrument code")

    if kindat is None:
        raise ValueError("Must supply Madrigal experiment code")

    # Initialize the connection to Madrigal
    web_data = madrigalWeb.MadrigalData(url)

    # Get the list of desired remote files
    start = date_array.min()
    stop = date_array.max()
    if start == stop:
        stop += dt.timedelta(days=1)
    files = get_remote_filenames(inst_code=inst_code, kindat=kindat, user=user,
                                 password=password, web_data=web_data, url=url,
                                 start=start, stop=stop)

    for mad_file in files:
        # Build the local filename
        local_file = os.path.join(data_path, os.path.basename(mad_file.name))
        if local_file.find(file_type) <= 0:
            split_file = local_file.split(".")
            split_file[-1] = file_type
            local_file = ".".join(split_file)

        if not os.path.isfile(local_file):
            web_data.downloadFile(mad_file.name, local_file, user, password,
                                  "pysat", format=file_type)

    return


def get_remote_filenames(inst_code=None, kindat=None, user=None,
                         password=None, web_data=None,
                         url="http://cedar.openmadrigal.org",
                         start=dt.datetime(1900, 1, 1), stop=dt.datetime.now(),
                         date_array=None):
    """Retrieve the remote filenames for a specified Madrigal instrument
    (and experiment)

    Parameters
    ----------
    inst_code : string
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindat : string
        Madrigal experiment code(s), cast as a string.  If multiple are used,
        separate them with commas.  If not supplied, all will be returned.
        (default=None)
    data_path : string
        Path to directory to download data to. (default=None)
    user : string
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : string
        Password for data download. (default=None)
    web_data : MadrigalData
        Open connection to Madrigal database or None (will initiate using url)
        (default=None)
    url : string
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    start : dt.datetime
        Starting time for file list (defaults to 01-01-1900)
    stop : dt.datetime
        Ending time for the file list (defaults to time of run)
    date_array : dt.datetime
        Array of datetimes to download data for. The sequence of dates need not
        be contiguous and will be used instead of start and stop if supplied.
        (default=None)

    Note
    ----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.


    """

    if inst_code is None:
        raise ValueError("Must supply Madrigal instrument code")

    if kindat is None:
        kindat = []
    else:
        kindat = [int(kk) for kk in kindat.split(",")]

    # If date_array supplied, overwrite start and stop
    if date_array is not None:
        if len(date_array) == 0:
            raise ValueError('unknown date_array supplied: {:}'.format(
                date_array))
        start = date_array.min()
        stop = date_array.max()
        if start == stop:
            stop += dt.timedelta(days=1)

    # open connection to Madrigal
    if web_data is None:
        web_data = madrigalWeb.MadrigalData(url)

    # get list of experiments for instrument from 1900 till now
    exp_list = web_data.getExperiments(inst_code, start.year, start.month,
                                       start.day, start.hour, start.minute,
                                       start.second, stop.year, stop.month,
                                       stop.day, stop.hour, stop.minute,
                                       stop.second)

    # iterate over experiments to grab files for each one
    files = list()
    logger.info("Found {:d} Madrigal experiments".format(len(exp_list)))
    for exp in exp_list:
        if good_exp(exp, date_array=date_array):
            file_list = web_data.getExperimentFiles(exp.id)

            if len(kindat) == 0:
                files.extend(file_list)
            else:
                for file_obj in file_list:
                    if file_obj.kindat in kindat:
                        files.append(file_obj)

    return files


def good_exp(exp, date_array=None):
    """ Determine if a Madrigal experiment has good data for specified dates

    Parameters
    ----------
    exp : MadrigalExperimentFile
        MadrigalExperimentFile object
    date_array : array-like
        list of datetimes to download data for. The sequence of dates need not
        be contiguous.

    Returns
    -------
    gflag : boolean
        True if good, False if bad

    """

    gflag = False

    if exp.id != -1:
        if date_array is None:
            gflag = True
        else:
            exp_start = dt.datetime(exp.startyear, exp.startmonth,
                                    exp.startday, exp.starthour,
                                    exp.startmin, exp.startsec)
            exp_end = dt.datetime(exp.endyear, exp.endmonth, exp.endday,
                                  exp.endhour, exp.endmin, exp.endsec)

            for date_val in date_array:
                if date_val >= exp_start and date_val < exp_end:
                    gflag = True
                    break

    return gflag


def list_remote_files(tag, inst_id, inst_code=None, kindat=None, user=None,
                      password=None, supported_tags=None,
                      url="http://cedar.openmadrigal.org",
                      two_digit_year_break=None, start=dt.datetime(1900, 1, 1),
                      stop=dt.datetime.now()):
    """List files available from Madrigal.

    Parameters
    ----------
    tag : string or NoneType
        Denotes type of file to load.  Accepted types are <tag strings>.
        (default=None)
    inst_id : string or NoneType
        Specifies the satellite ID for a constellation.  Not used.
        (default=None)
    inst_code : string
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindat : string
        Madrigal experiment code(s), cast as a string.  If multiple are used,
        separate them with commas.  If not supplied, all will be returned.
        (default=None)
    data_path : string
        Path to directory to download data to. (default=None)
    user : string
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : string
        Password for data download. (default=None)
    supported_tags : dict or NoneType
        keys are inst_id, each containing a dict keyed by tag
        where the values file format template strings. (default=None)
    url : string
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    two_digit_year_break : int
        If filenames only store two digits for the year, then
        '1900' will be added for years >= two_digit_year_break
        and '2000' will be added for years < two_digit_year_break.
    start : dt.datetime
        Starting time for file list (defaults to 01-01-1900)
    stop : dt.datetime
        Ending time for the file list (defaults to time of run)

    Note
    ----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    Examples
    --------
    This method is intended to be set in an instrument support file at the
    top level using functools.partial
    ::

        list_remote_files = functools.partial(mad_meth.list_remote_files,
                                              supported_tags=supported_tags,
                                              inst_code=madrigal_inst_code)

    """
    if inst_code is None:
        raise ValueError("Must supply Madrigal instrument code")

    # Test input
    try:
        format_str = supported_tags[inst_id][tag]
    except KeyError:
        raise ValueError('Problem parsing supported_tags')

    # Retrieve remote file list
    files = get_remote_filenames(inst_code=inst_code, kindat=kindat, user=user,
                                 password=password, url=url, start=start,
                                 stop=stop)

    # parse these filenames to grab out the ones we want
    logger.info("Parsing filenames")
    stored = pysat._files.parse_fixed_width_filenames(files, format_str)

    # process the parsed filenames and return a properly formatted Series
    logger.info("Processing filenames")
    return pysat._files.process_parsed_filenames(stored, two_digit_year_break)


def filter_data_single_date(inst):
    """Filters data to a single date.

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument object to which this routine should be attached

    Note
    ----
    Madrigal serves multiple days within a single JRO file
    to counter this, we will filter each loaded day so that it only
    contains the relevant day of data. This is only applied if loading
    by date. It is not applied when supplying pysat with a specific
    filename to load, nor when data padding is enabled. Note that when
    data padding is enabled the final data available within the instrument
    will be downselected by pysat to only include the date specified.

    This routine is intended to be added to the Instrument
    nanokernel processing queue via
    ::

        inst = pysat.Instrument()
        inst.custom.attach(filter_data_single_date, 'modify')

    This function will then be automatically applied to the
    Instrument object data on every load by the pysat nanokernel.

    Warnings
    --------
    For the best performance, this function should be added first in the queue.
    This may be ensured by setting the default function in a
    pysat instrument file to this one.

    within platform_name.py set
    ::

        default = pysat.instruments.methods.madrigal.filter_data_single_date

    at the top level

    """

    # only do this if loading by date!
    if inst._load_by_date and inst.pad is None:
        # identify times for the loaded date
        idx, = np.where((inst.index >= inst.date)
                        & (inst.index < (inst.date + pds.DateOffset(days=1))))

        # downselect from all data
        inst.data = inst[idx]

    return
