#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-.
"""Supports generalized access to Madrigal Data.

Properties
----------
platform
    'madrigal'
name
    'pandas'
tag
    Madrigal instrument code as a string
inst_id
    Madrigal kindat as a string

Note
----
To use this routine, you need to know both the Madrigal Instrument code
as well as the data tag numbers that Madrigal uses to uniquely identify
data sets. You also need to know that the data is a simple time series (e.g.,
satellite in situ observations).

Multiple kindat values are supported, as long as they are separated by commas.

Although you can use this instrument module for any time-series data set, we
highly recommend using the instrument-specific module if it exists.

Please provide name (user) and email (password) when downloading data with this
routine.

Warnings
--------
All data downloaded under this general support is placed in the same directory,
pysat_data_dir/madrigal/pandas/. For technical reasons, the file search
algorithm for pysat's Madrigal support is set to permissive defaults. Thus, all
instrument files downloaded via this interface will be picked up by the madrigal
pandas pysat Instrument object unless the file_format keyword is used at
instantiation.

Files can be safely downloaded without knowing the file_format keyword,
or equivalently, how Madrigal names the files. See `Examples` for more.

Examples
--------
::


    import datetime as dt
    import pysat
    import pysatMadrigal as py_mad

    # Download DMSP data from Madrigal
    dmsp_abi = pysat.Instrument(inst_module=py_mad.instruments.madrigal_pandas,
                                tag='180', kindat='17110')
    dmsp_abi.download(dt.datetime(2015, 1, 1), dt.datetime(2015, 1, 2),
                      user='Firstname+Lastname', password='email@address.com')
    dmsp_abi.load(date=dt.datetime(2015, 1, 1))

"""

import datetime as dt

from pysat import logger

from pysatMadrigal.instruments.methods import general

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'madrigal'
name = 'pandas'
tags = dict()
pandas_format = True
excluded_tags = ['8105']  # Pandas-style data that requires special support

# Assign only tags with pysat-compatible file format strings
pandas_codes = general.known_madrigal_inst_codes(pandas_format=True)
for tag in pandas_codes.keys():
    try:
        general.madrigal_file_format_str(tag, strict=True)
        if tag not in excluded_tags:
            tags[tag] = pandas_codes[tag]
    except ValueError:
        pass

inst_ids = {'': list(tags.keys())}  # There are too many kindat to track here

# Local attributes
#
# Need a way to get the filename strings for a particular instrument unless
# wildcards start working
supported_tags = {ss: {tag: general.madrigal_file_format_str(tag)
                       for tag in inst_ids[ss]} for ss in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument test attributes

# Need to sort out test day setting for unit testing, maybe through a remote
# function
tag_dates = {'120': dt.datetime(1963, 11, 27), '170': dt.datetime(1998, 7, 1),
             '180': dt.datetime(2000, 1, 1), '210': dt.datetime(1950, 1, 1),
             '211': dt.datetime(1978, 1, 1), '212': dt.datetime(1957, 1, 1),
             '7800': dt.datetime(2009, 11, 10)}
_test_dates = {'': {tag: tag_dates[tag] if tag in tag_dates.keys()
                    else tag_dates['7800'] for tag in tags.keys()}}
_test_download = {'': {tag: True for tag in tags.keys()}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self, kindat=''):
    """Initialize the Instrument object in support of Madrigal access.

    Parameters
    ----------
    kindat : str
        Madrigal instrument experiment code(s). (default='')

    """
    # Set the standard pysat attributes
    self.acknowledgements = general.cedar_rules()
    self.references = 'Please remember to cite the instrument articles.'

    # If the kindat (madrigal tag) is not known, advise user
    self.kindat = kindat
    if self.kindat == '':
        logger.warning('`inst_id` did not supply KINDAT, all will be returned.')

    # Remind the user of the Rules of the Road
    logger.info(self.acknowledgements)
    return


def clean(self):
    """Raise warning that cleaning is not possible for general data.

    Note
    ----
    Supports 'clean', 'dusty', 'dirty' in the sense that it prints
    a message noting there is no cleaning.
    'None' is also supported as it signifies no cleaning.

    Routine is called by pysat, and not by the end user directly.

    """
    if self.clean_level in ['clean', 'dusty', 'dirty']:
        logger.warning(''.join(["The generalized Madrigal data Instrument ",
                                "can't support instrument-specific cleaning."]))

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal and pysat methods

# Set the load routine
load = general.load


# Set the list routine
def list_files(tag, inst_id, data_path, kindat='', format_str=None,
               file_cadence=dt.timedelta(days=1), delimiter=None,
               file_type=None):
    """Create a Pandas Series of every file for chosen Instrument data.

    Parameters
    ----------
    tag : str
        Denotes type of file to load.  Accepts strings corresponding to the
        appropriate Madrigal Instrument `tags`.
    inst_id : str
        Specifies the instrument ID to load. Accepts strings corresponding to
        the appropriate Madrigal Instrument `inst_ids`.
    data_path : str
        Path to data directory.
    kindat : str
        Madrigal KINDAT code, specifies an experiment for the specified
        instrument.  May be a single value, blank (all), or a comma-delimited
        list. (defaut='')
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
    if kindat == '':
        kindat = "*"

    # Get the remote file type format
    local_tags = {ss: {kk: supported_tags[ss][kk].replace("{kindat}", kindat)
                       for kk in inst_ids[ss]} for ss in inst_ids.keys()}

    # Determine the two-digit year break value
    if local_tags[inst_id][tag].find("{year:04d}") >= 0:
        two_digit_year_break = None
    else:
        two_digit_year_break = 50

    # Determine if a delimiter is needed
    if delimiter is None and local_tags[inst_id][tag].find('*') >= 0:
        delimiter = '.'

    out = general.list_files(tag, inst_id, data_path, format_str=format_str,
                             supported_tags=local_tags,
                             file_cadence=file_cadence,
                             two_digit_year_break=two_digit_year_break,
                             delimiter=delimiter, file_type=file_type)

    return out


def download(date_array, tag='', inst_id='', data_path=None, user=None,
             password=None, file_type='hdf5', kindat=''):
    """Download data from Madrigal.

    Parameters
    ----------
    date_array : array-like
        list of datetimes to download data for. The sequence of dates need not
        be contiguous.
    tag : str
        Madrigal Instrument code cast as a string. (default='')
    inst_id : str
        Satellite ID string identifier used for particular dataset. (default='')
    data_path : str
        Path to directory to download data to. (default=None)
    user : str
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : str
        Password for data download. (default=None)
    file_type : str
        File format for Madrigal data. (default='hdf5')
    kindat : str
        Madrigal KINDAT code, specifies an experiment for the specified
        instrument.  May be a single value, blank (all), or a comma-delimited
        list. (defaut='')

    Notes
    -----
    The user's names should be provided in field user. Maria Goeppert Mayer
    should be entered as "Maria Goeppert Mayer"

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    general.download(date_array, inst_code=tag, kindat=kindat,
                     data_path=data_path, user=user, password=password,
                     file_type=file_type)
    return


def list_remote_files(tag, inst_id, kindat='', user=None, password=None,
                      url="http://cedar.openmadrigal.org",
                      start=dt.datetime(1900, 1, 1), stop=dt.datetime.utcnow()):
    """List files available from Madrigal.

    Parameters
    ----------
    tag : str
        Denotes type of file to load.  Accepts strings corresponding to the
        appropriate Madrigal Instrument `tags`.
    inst_id : str
        Specifies the instrument ID to load. Accepts strings corresponding to
        the appropriate Madrigal Instrument `inst_ids`.
    kindat : str
        Madrigal KINDAT code, specifies an experiment for the specified
        instrument.  May be a single value, blank (all), or a comma-delimited
        list. (defaut='')
    data_path : str or NoneType
        Path to directory to download data to. (default=None)
    user : str or NoneType
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : str or NoneType
        Password for data download. (default=None)
    url : str
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    start : dt.datetime
        Starting time for file list (default=dt.datetime(1900, 1, 1))
    stop : dt.datetime
        Ending time for the file list (default=dt.datetime.utcnow())

    Returns
    -------
    remote_files : pds.Series
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
    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    if kindat == '':
        kindat = "*"

    # Get the remote file type format
    remote_tags = {ss: {kk: supported_tags[ss][kk].format(file_type='hdf5',
                                                          kindat=kindat)
                        for kk in inst_ids[ss]} for ss in inst_ids.keys()}

    # Determine the two-digit year break value
    if remote_tags[inst_id][tag].find("{year:04d}") >= 0:
        two_digit_year_break = None
    else:
        two_digit_year_break = 50

    # Set the kindat dictionary
    kindats = {ss: {kk: kindat if kk == tag else '' for kk in inst_ids[ss]}
               for ss in inst_ids.keys()}

    # Set the list_remote_files routine
    remote_files = general.list_remote_files(
        tag, inst_id, inst_code=int(tag), kindats=kindats, user=user,
        password=password, supported_tags=remote_tags, url=url,
        two_digit_year_break=two_digit_year_break, start=start, stop=stop)

    return remote_files
