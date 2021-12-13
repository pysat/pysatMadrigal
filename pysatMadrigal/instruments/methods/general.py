# -*- coding: utf-8 -*-.
"""General routines for integrating CEDAR Madrigal instruments into pysat.

"""

import datetime as dt
import gzip
import numpy as np
import os
import pandas as pds
import xarray as xr

import h5py
import pysat

from madrigalWeb import madrigalWeb


logger = pysat.logger
file_types = {'hdf5': 'hdf5', 'netCDF4': 'netCDF4', 'simple': 'simple.gz'}


def cedar_rules():
    """General acknowledgement statement for Madrigal data.

    Returns
    -------
    ackn : str
        String with general acknowledgement for all CEDAR Madrigal data

    """
    ackn = "".join(["Contact the PI when using this data, in accordance ",
                    "with the CEDAR 'Rules of the Road'"])
    return ackn


def load(fnames, tag='', inst_id='', xarray_coords=None):
    """Loads data from Madrigal into Pandas or XArray.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        Tag name used to identify particular data set to be loaded. This input
        is nominally provided by pysat itself and is not used here. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself, and is not used here.
        (default='')
    xarray_coords : list or NoneType
        List of keywords to use as coordinates if xarray output is desired
        instead of a Pandas DataFrame.  Can build an xarray Dataset
        that have different coordinate dimensions by providing a dict
        inside the list instead of coordinate variable name strings. Each dict
        will have a tuple of coordinates as the key and a list of variable
        strings as the value.  Empty list if None. For example,
        xarray_coords=[{('time',): ['year', 'doy'],
        ('time', 'gdalt'): ['data1', 'data2']}]. (default=None)

    Returns
    -------
    data : pds.DataFrame or xr.Dataset
        A pandas DataFrame or xarray Dataset holding the data from the file
    meta : pysat.Meta
        Metadata from the file, as well as default values from pysat

    Raises
    ------
    ValueError
       If data columns expected to create the time index are missing or if
       coordinates are not supplied for all data columns.

    Note
    ----
    Currently HDF5 reading breaks if a different file type was used previously

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    """
    # Test the file formats
    load_file_types = {ftype: [] for ftype in file_types.keys()}
    for fname in fnames:
        for ftype in file_types.keys():
            if fname.find(ftype) > 0:
                load_file_types[ftype].append(fname)
                break

    # Initialize xarray coordinates, if needed
    if xarray_coords is None:
        xarray_coords = []

    # Initialize the output
    meta = pysat.Meta()
    labels = []
    data = None

    # Load the file data for netCDF4 files
    if len(load_file_types["netCDF4"]) == 1:
        # Xarray natively opens netCDF data into a Dataset
        file_data = xr.open_dataset(load_file_types["netCDF4"][0],
                                    engine="netcdf4")
    elif len(load_file_types["netCDF4"]) > 1:
        file_data = xr.open_mfdataset(load_file_types["netCDF4"],
                                      combine='by_coords', engine="netcdf4")

    if len(load_file_types["netCDF4"]) > 0:
        # Currently not saving file header data, as all metadata is at
        # the data variable level. The attributes are only saved if they occur
        # in all of the loaded files.
        if 'catalog_text' in file_data.attrs:
            notes = file_data.attrs['catalog_text']
        else:
            notes = "No catalog text"

        # Get the coordinate and data variable names
        meta_items = [dkey for dkey in file_data.data_vars.keys()]
        meta_items.extend([dkey for dkey in file_data.coords.keys()])

        for item in meta_items:
            # Set the meta values for the expected labels
            meta_dict = {meta.labels.name: item, meta.labels.fill_val: np.nan,
                         meta.labels.notes: notes}

            for key, label in [('units', meta.labels.units),
                               ('description', meta.labels.desc)]:
                if key in file_data[item].attrs.keys():
                    meta_dict[label] = file_data[item].attrs[key]
                else:
                    meta_dict[label] = ''

            meta[item.lower()] = meta_dict

            # Remove any metadata from xarray
            file_data[item].attrs = {}

        # Reset UNIX timestamp as datetime and set it as an index
        file_data = file_data.rename({'timestamps': 'time'})
        time_data = pds.to_datetime(file_data['time'].values, unit='s')
        data = file_data.assign_coords({'time': ('time', time_data)})

    # Load the file data for HDF5 files
    if len(load_file_types["hdf5"]) > 0 or len(load_file_types["simple"]) > 0:
        # Ensure we don't try to create an xarray object with only time as
        # the coordinate
        coord_len = len(xarray_coords)
        if 'time' in xarray_coords:
            coord_len -= 1

        # Cycle through all the filenames
        fdata = []
        fnames = list(load_file_types["hdf5"])
        fnames.extend(load_file_types["simple"])
        for fname in fnames:
            # Open the specified file
            if fname in load_file_types["simple"]:
                # Get the gzipped text data
                with gzip.open(fname, 'rb') as fin:
                    file_data = fin.readlines()

                # Load available info into pysat.Meta if this is the first file
                header = [item.decode('UTF-8')
                          for item in file_data.pop(0).split()]
                if len(labels) == 0:
                    for item in header:
                        labels.append(item)

                        # Only update metadata if necessary
                        if item.lower() not in meta:
                            meta[item.lower()] = {meta.labels.name: item}

                # Construct a dict of the output
                file_dict = {item.lower(): list() for item in header}
                for line in file_data:
                    for i, val in enumerate(line.split()):
                        file_dict[header[i].lower()].append(float(val))

                # Load data into frame, with labels from metadata
                ldata = pds.DataFrame.from_dict(file_dict)
            else:
                # Open the specified file and get the data and metadata
                filed = h5py.File(fname, 'r')
                file_data = filed['Data']['Table Layout']
                file_meta = filed['Metadata']['Data Parameters']

                # Load available info into pysat.Meta if this is the first file
                if len(labels) == 0:
                    for item in file_meta:
                        name_string = item[0].decode('UTF-8')
                        unit_string = item[3].decode('UTF-8')
                        desc_string = item[1].decode('UTF-8')
                        labels.append(name_string)

                        # Only update metadata if necessary
                        if name_string.lower() not in meta:
                            meta[name_string.lower()] = {
                                meta.labels.name: name_string,
                                meta.labels.units: unit_string,
                                meta.labels.desc: desc_string}

                # Add additional metadata notes. Custom attributes attached to
                # meta are attached to corresponding Instrument object when
                # pysat receives data and meta from this routine
                for key in filed['Metadata']:
                    if key != 'Data Parameters':
                        setattr(meta, key.replace(' ', '_'),
                                filed['Metadata'][key][:])

                # Load data into frame, with labels from metadata
                ldata = pds.DataFrame.from_records(file_data, columns=labels)

                # Enforce lowercase variable names
                ldata.columns = [item.lower() for item in ldata.columns]

            # Extended processing is the same for simple and HDF5 files
            #
            # Construct datetime index from times
            time_keys = np.array(['year', 'month', 'day', 'hour', 'min', 'sec'])
            if not np.all([key in ldata.columns for key in time_keys]):
                time_keys = [key for key in time_keys
                             if key not in ldata.columns]
                raise ValueError(' '.join(["unable to construct time index, ",
                                           "missing {:}".format(time_keys)]))

            uts = 3600.0 * ldata.loc[:, 'hour'] + 60.0 * ldata.loc[:, 'min'] \
                + ldata.loc[:, 'sec']
            time = pysat.utils.time.create_datetime_index(
                year=ldata.loc[:, 'year'], month=ldata.loc[:, 'month'],
                day=ldata.loc[:, 'day'], uts=uts)

            # Declare index or recast as xarray
            if coord_len > 0:
                # If a list was provided, recast as a dict and grab the data
                # columns
                if not isinstance(xarray_coords, dict):
                    xarray_coords = {tuple(xarray_coords):
                                     [col for col in ldata.columns
                                      if col not in xarray_coords]}

                # Determine the order in which the keys should be processed:
                #  Greatest to least number of dimensions
                len_dict = {len(xcoords): xcoords
                            for xcoords in xarray_coords.keys()}
                coord_order = [len_dict[xkey] for xkey in sorted(
                    [lkey for lkey in len_dict.keys()], reverse=True)]

                # Append time to the data frame
                ldata = ldata.assign(time=pds.Series(time, index=ldata.index))

                # Cycle through each of the coordinate dimensions
                xdatasets = list()
                for xcoords in coord_order:
                    if not np.all([xkey.lower() in ldata.columns
                                   for xkey in xcoords]):
                        raise ValueError(''.join(['unknown coordinate key ',
                                                  'in [{:}'.format(xcoords),
                                                  '], use only: {:}'.format(
                                                      ldata.columns)]))
                    if not np.all([xkey.lower() in ldata.columns
                                   for xkey in xarray_coords[xcoords]]):
                        good_ind = [
                            i for i, xkey in enumerate(xarray_coords[xcoords])
                            if xkey.lower() in ldata.columns]

                        if len(good_ind) == 0:
                            raise ValueError(''.join([
                                'All data variables {:} are unknown.'.format(
                                    xarray_coords[xcoords])]))
                        elif len(good_ind) < len(xarray_coords[xcoords]):
                            # Remove the coordinates that aren't present.
                            temp = np.array(xarray_coords[xcoords])[good_ind]

                            # Warn user, some of this may be due to a file
                            # format update or change.
                            bad_ind = [i for i in
                                       range(len(xarray_coords[xcoords]))
                                       if i not in good_ind]
                            logger.warning(''.join([
                                'unknown data variable(s) {:}, '.format(
                                    np.array(xarray_coords[xcoords])[bad_ind]),
                                'using only: {:}'.format(temp)]))

                            # Assign good data as a list.
                            xarray_coords[xcoords] = list(temp)

                    # Select the desired data values
                    sel_data = ldata[list(xcoords) + xarray_coords[xcoords]]

                    # Remove duplicates before indexing, to ensure data with
                    # the same values at different locations are kept
                    sel_data = sel_data.drop_duplicates()

                    # Set the indices
                    sel_data = sel_data.set_index(list(xcoords))

                    # Recast as an xarray
                    xdatasets.append(sel_data.to_xarray())

                # Get the necessary information to test the data
                lcols = ldata.columns
                len_data = len(lcols)

                # Merge all of the datasets
                ldata = xr.merge(xdatasets)
                test_variables = [xkey for xkey in ldata.variables.keys()]
                ltest = len(test_variables)

                # Test to see that all data was retrieved
                if ltest != len_data:
                    if ltest < len_data:
                        estr = 'missing: {:}'.format(
                            ' '.join([dvar for dvar in lcols
                                      if dvar not in test_variables]))
                    else:
                        estr = 'have extra: {:}'.format(
                            ' '.join([tvar for tvar in test_variables
                                      if tvar not in lcols]))
                        raise ValueError(''.join([
                            'coordinates not supplied for all data columns',
                            ': {:d} != {:d}; '.format(ltest, len_data), estr]))
            else:
                # Set the index to time
                ldata.index = time

                # Raise a logging warning if there are duplicate times. This
                # means the data should be stored as an xarray Dataset
                if np.any(time.duplicated()):
                    logger.warning(''.join(["duplicated time indices, ",
                                            "consider specifing additional",
                                            " coordinates and storing the ",
                                            "data as an xarray Dataset"]))

            # Compile a list of the data objects
            fdata.append(ldata)

        # Merge the data together, accounting for potential netCDF output
        if data is None and len(fdata) == 1:
            data = fdata[0]
        else:
            if coord_len > 0:
                if data is None:
                    data = xr.merge(fdata)
                else:
                    data = xr.combine_by_coords([data, xr.merge(fdata)])
            else:
                if data is None:
                    data = pds.concat(fdata)
                    data = data.sort_index()
                else:
                    ldata = pds.concat(fdata).sort_index().to_xarray()
                    ldata = ldata.rename({'index': 'time'})
                    data = xr.combine_by_coords([data, ldata]).to_pandas()

    # Ensure that data is at least an empty Dataset
    if data is None:
        if len(xarray_coords) > 0:
            data = xr.Dataset()
        else:
            data = pds.DataFrame(dtype=np.float64)

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
    inst_code : str
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindat : str
        Experiment instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    data_path : str
        Path to directory to download data to. (default=None)
    user : str
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : str
        Password for data download. (default=None)
    url : str
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    file_type : str
        File format for Madrigal data.  Load routines currently only accepts
        'hdf5' and 'netCDF4', but any of the Madrigal options may be used
        here. (default='hdf5')

    Raises
    ------
    ValueError
        If the specified input type or Madrigal experiment codes are unknown

    Note
    ----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """

    if file_type not in file_types.keys():
        raise ValueError("Unknown file format {:}, accepts {:}".format(
            file_type, file_types.keys()))

    _check_madrigal_params(inst_code=inst_code, user=user, password=password)

    if kindat is None:
        raise ValueError("Must supply Madrigal experiment code")

    # Get the list of desired remote files
    start = date_array.min()
    stop = date_array.max()
    if start == stop:
        stop += dt.timedelta(days=1)

    # Initialize the connection to Madrigal
    logger.info('Connecting to Madrigal')
    web_data = madrigalWeb.MadrigalData(url)
    logger.info('Connection established.')

    files = get_remote_filenames(inst_code=inst_code, kindat=kindat,
                                 user=user, password=password,
                                 web_data=web_data, url=url,
                                 start=start, stop=stop)

    for mad_file in files:
        # Build the local filename
        local_file = os.path.join(data_path,
                                  os.path.basename(mad_file.name))
        if local_file.find(file_type) <= 0:
            split_file = local_file.split(".")
            split_file[-1] = file_type
            local_file = ".".join(split_file)

        if not os.path.isfile(local_file):
            fstr = ''.join(('Downloading data for ', local_file))
            logger.info(fstr)
            web_data.downloadFile(mad_file.name, local_file, user, password,
                                  "pysat", format=file_type)
        else:
            estr = ''.join((local_file, ' already exists. Skipping.'))
            logger.info(estr)

    return


def get_remote_filenames(inst_code=None, kindat=None, user=None, password=None,
                         web_data=None, url="http://cedar.openmadrigal.org",
                         start=dt.datetime(1900, 1, 1), stop=dt.datetime.now(),
                         date_array=None):
    """Retrieve the remote filenames for a specified Madrigal experiment

    Parameters
    ----------
    inst_code : str or NoneType
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindat : str or NoneType
        Madrigal experiment code(s), cast as a string.  If multiple are used,
        separate them with commas.  If not supplied, all will be returned.
        (default=None)
    data_path : str or NoneType
        Path to directory to download data to. (default=None)
    user : str or NoneType
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : str or NoneType
        Password for data download. (default=None)
    web_data : MadrigalData or NoneType
        Open connection to Madrigal database or None (will initiate using url)
        (default=None)
    url : str
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    start : dt.datetime
        Starting time for file list (defaults to 01-01-1900)
    stop : dt.datetime
        Ending time for the file list (defaults to time of run)
    date_array : dt.datetime or NoneType
        Array of datetimes to download data for. The sequence of dates need not
        be contiguous and will be used instead of start and stop if supplied.
        (default=None)

    Returns
    -------
    files : madrigalWeb.madrigalWeb.MadrigalExperimentFile
        Madrigal file object that contains remote experiment file data

    Raises
    ------
    ValueError
        If unexpected date_array input is supplied

    Note
    ----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.


    """

    _check_madrigal_params(inst_code=inst_code, user=user, password=password)

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
    # If start and stop are identical, increment
    if start == stop:
        stop += dt.timedelta(days=1)
    # Open connection to Madrigal
    if web_data is None:
        web_data = madrigalWeb.MadrigalData(url)

    # Get list of experiments for instrument from in desired range
    exp_list = web_data.getExperiments(inst_code, start.year, start.month,
                                       start.day, start.hour, start.minute,
                                       start.second, stop.year, stop.month,
                                       stop.day, stop.hour, stop.minute,
                                       stop.second)

    # Iterate over experiments to grab files for each one
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
    """Determine if a Madrigal experiment has good data for specified dates.

    Parameters
    ----------
    exp : MadrigalExperimentFile
        MadrigalExperimentFile object
    date_array : list-like or NoneType
        List of datetimes to download data for. The sequence of dates need not
        be contiguous. If None, then any valid experiment will be assumed
        to be valid. (default=None)

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
            exp_start = dt.date(exp.startyear, exp.startmonth,
                                exp.startday)
            exp_end = (dt.date(exp.endyear, exp.endmonth, exp.endday)
                       + dt.timedelta(days=1))

            for date_val in date_array:
                if date_val.date() >= exp_start and date_val.date() <= exp_end:
                    gflag = True
                    break

    return gflag


def list_remote_files(tag, inst_id, inst_code=None, kindats=None, user=None,
                      password=None, supported_tags=None,
                      url="http://cedar.openmadrigal.org",
                      two_digit_year_break=None, start=dt.datetime(1900, 1, 1),
                      stop=dt.datetime.utcnow()):
    """List files available from Madrigal.

    Parameters
    ----------
    tag : str
        Denotes type of file to load.  Accepts strings corresponding to the
        appropriate Madrigal Instrument `tags`.
    inst_id : str
        Specifies the instrument ID to load. Accepts strings corresponding to
        the appropriate Madrigal Instrument `inst_ids`.
    inst_code : str or NoneType
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindats : dict
        Madrigal experiment codes, in a dict of dicts with inst_ids as top level
        keys and tags as second level keys with Madrigal experiment code(s)
        as values.  These should be strings, with multiple codes separated by
        commas. (default=None)
    data_path : str or NoneType
        Path to directory to download data to. (default=None)
    user : str or NoneType
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : str or NoneType
        Password for data download. (default=None)
    supported_tags : dict or NoneType
        keys are inst_id, each containing a dict keyed by tag
        where the values file format template strings. (default=None)
    url : str
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    two_digit_year_break : int
        If filenames only store two digits for the year, then
        '1900' will be added for years >= two_digit_year_break
        and '2000' will be added for years < two_digit_year_break.
    start : dt.datetime
        Starting time for file list (defaults to 01-01-1900)
    stop : dt.datetime
        Ending time for the file list (defaults to time of run)

    Returns
    -------
    pds.Series
        A series of filenames, see `pysat.utils.files.process_parsed_filenames`
        for more information.

    Raises
    ------
    ValueError
        For missing kwarg input
    KeyError
        For dictionary input missing requested tag/inst_id

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
                                              inst_code=madrigal_inst_code,
                                              kindats=madrigal_tag)

    """

    _check_madrigal_params(inst_code=inst_code, user=user, password=password)

    # Test input
    if supported_tags is None or kindats is None:
        raise ValueError('Must supply supported_tags and kindats dicts')

    # Raise KeyError if input dictionaries don't match the input
    format_str = supported_tags[inst_id][tag]
    kindat = kindats[inst_id][tag]

    # Retrieve remote file experiment list
    files = get_remote_filenames(inst_code=inst_code, kindat=kindat, user=user,
                                 password=password, url=url, start=start,
                                 stop=stop)

    filenames = [os.path.basename(file_exp.name) for file_exp in files]

    # Parse these filenames to grab out the ones we want
    logger.info("Parsing filenames")
    stored = pysat.utils.files.parse_fixed_width_filenames(filenames,
                                                           format_str)

    # Process the parsed filenames and return a properly formatted Series
    logger.info("Processing filenames")
    return pysat.utils.files.process_parsed_filenames(stored,
                                                      two_digit_year_break)


def list_files(tag, inst_id, data_path=None, format_str=None,
               supported_tags=None, file_cadence=dt.timedelta(days=1),
               two_digit_year_break=None, delimiter=None, file_type=None):
    """Return a Pandas Series of every file for chosen Instrument data.

    Parameters
    ----------
    tag : str
        Denotes type of file to load.  Accepts strings corresponding to the
        appropriate Madrigal Instrument `tags`.
    inst_id : str
        Specifies the instrument ID to load. Accepts strings corresponding to
        the appropriate Madrigal Instrument `inst_ids`.
    data_path : str or NoneType
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)
    format_str : str or NoneType
        User specified file format.  If None is specified, the default
        formats associated with the supplied tags are used. (default=None)
    supported_tags : dict or NoneType
        Keys are inst_id, each containing a dict keyed by tag
        where the values file format template strings. (default=None)
    file_cadence : dt.timedelta or pds.DateOffset
        pysat assumes a daily file cadence, but some instrument data file
        contain longer periods of time.  This parameter allows the specification
        of regular file cadences greater than or equal to a day (e.g., weekly,
        monthly, or yearly). (default=dt.timedelta(days=1))
    two_digit_year_break : int or NoneType
        If filenames only store two digits for the year, then '1900' will be
        added for years >= two_digit_year_break and '2000' will be added for
        years < two_digit_year_break. If None, then four-digit years are
        assumed. (default=None)
    delimiter : str or NoneType
        Delimiter string upon which files will be split (e.g., '.'). If None,
        filenames will be parsed presuming a fixed width format. (default=None)
    file_type : str or NoneType
        File format for Madrigal data.  Load routines currently accepts 'hdf5',
        'simple', and 'netCDF4', but any of the Madrigal options may be used
        here. If None, will look for all known file types. (default=None)

    Returns
    -------
    out : pds.Series
        A pandas Series containing the verified available files

    """
    # Initialize the transitional variables
    list_file_types = file_types.keys() if file_type is None else [file_type]
    sup_tags = {inst_id: {tag: supported_tags[inst_id][tag]}}
    out_series = list()

    # Cycle through each requested file type, loading the requested files
    for ftype in list_file_types:
        if supported_tags[inst_id][tag].find('{file_type}') > 0:
            sup_tags[inst_id][tag] = supported_tags[inst_id][tag].format(
                file_type=file_types[ftype])

        out_series.append(pysat.instruments.methods.general.list_files(
            tag=tag, inst_id=inst_id, data_path=data_path,
            format_str=format_str, supported_tags=sup_tags,
            file_cadence=file_cadence,
            two_digit_year_break=two_digit_year_break, delimiter=delimiter))

    # Combine the file lists, ensuring the files are correctly ordered
    if len(out_series) == 1:
        out = out_series[0]
    else:
        out = pds.concat(out_series).sort_index()

    return out


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

    Examples
    --------
    This routine is intended to be added to the Instrument
    nanokernel processing queue via
    ::

        inst = pysat.Instrument()
        inst.custom_attach(filter_data_single_date)

    This function will then be automatically applied to the
    Instrument object data on every load by the pysat nanokernel.

    Warnings
    --------
    For the best performance, this function should be added first in the queue.
    This may be ensured by setting the default function in a  pysat instrument
    file to this one.

    To do this, within platform_name.py set `preprocess` at the top level.
    ::

        preprocess = pysat.instruments.methods.madrigal.filter_data_single_date

    """

    # Only do this if loading by date!
    if inst._load_by_date and inst.pad is None:
        # Identify times for the loaded date
        idx, = np.where((inst.index >= inst.date)
                        & (inst.index < (inst.date + pds.DateOffset(days=1))))

        # Downselect from all data
        inst.data = inst[idx]

    return


def _check_madrigal_params(inst_code, user, password):
    """Checks that parameters requried by Madrigal database are passed through.

    Parameters
    ----------
    inst_code : str or NoneType
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas.
    user : str or NoneType
        The user's names should be provided in field user. Ruby Payne-Scott
        should be entered as Ruby+Payne-Scott
    password : str or NoneType
        The password field should be the user's email address. These parameters
            are passed to Madrigal when downloading.

    Raises
    ------
    ValueError
        Default values of None will raise an error.

    """

    if inst_code is None:
        raise ValueError("Must supply Madrigal instrument code")

    if not (isinstance(user, str) and isinstance(password, str)):
        raise ValueError(' '.join(("The madrigal database requries a username",
                                   "and password.  Please input these as",
                                   "user='firstname+lastname' and",
                                   "password='myname@email.address' in this",
                                   "function.")))

    return
