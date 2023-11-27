# -*- coding: utf-8 -*-.
"""Supports the MIT Haystack GNSS TEC data products.

The Global Navigation Satellite System (GNSS) is used in conjunction with a
world-wide receiver network to produce total electron content (TEC) data
products, including vertical and line-of-sight (or slant) TEC.

Downloads data from the MIT Haystack Madrigal Database.

Properties
----------
platform
    'gnss'
name
    'tec'
tag
    'vtec', 'site', 'los'
inst_id
    '' (not used)

Examples
--------
::

    import datetime as dt
    import pysat
    import pysatMadrigal as pymad

    # Get and load all vertical TEC for 19 Nov 2017
    vtec = pysat.Instrument(inst_module=pymad.instruments.gnss_tec, tag='vtec')
    vtec.download(dt.datetime(2017, 11, 19), dt.datetime(2017, 11, 20),
                  user='Firstname+Lastname', password='email@address.com')
    vtec.load(date=dt.datetime(2017, 11, 19))

    # Get and load the GLONASS slant TEC from the zzon site on 1 Jan 2023
    stec = pysat.Instrument(inst_module=pymad.instruments.gnss_tec, tag='los')
    stec.download(start=dt.datetime(2023, 1, 1), user='Firstname+Lastname',
                  password='email@address.com')
    stec.load(2023, 1, los_method='site', los_value='zzon',
              gnss_network='glonass')

Note
----
Please provide name and email when downloading data with this routine.

The line-of-sight data is too large to load an entire file at once. Data may be
loaded by individual receiver site for any number of days (recommended to load
one day) or a given time. To discover the available sites and times (exact times
are required for selection), you may use the
`pysatMadrigal.instruments.methods.gnss.get_los_times` and
`pysatMadrigal.instruments.methods.gnss.get_los_receiver_sites` functions.

"""

import datetime as dt
import numpy as np

import pysat

from pysatMadrigal.instruments.methods import general
from pysatMadrigal.instruments.methods import gnss

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'gnss'
name = 'tec'
tags = {'vtec': 'vertical TEC', 'site': 'Sites used in daily TEC data',
        'los': 'line-of-sight TEC'}
inst_ids = {'': [tag for tag in tags.keys()]}

pandas_format = False

# Madrigal tags
madrigal_inst_code = 8000
madrigal_tag = {'': {'vtec': '3500', 'site': '3506', 'los': '3505'}}

# Local attributes
fname = general.madrigal_file_format_str(madrigal_inst_code,
                                         verbose=False).split("*")
supported_tags = {ss: {'vtec': ''.join(['gps', fname[1], 'g', fname[2]]),
                       'los': ''.join(['los_{{year:04d}}{{month:02d}}',
                                       '{{day:02d}}', fname[2]]),
                       'site': ''.join(['site_{{year:04d}}{{month:02d}}',
                                        '{{day:02d}}', fname[2]])}
                  for ss in inst_ids.keys()}
remote_tags = {ss: {kk: supported_tags[ss][kk].format(file_type='hdf5')
                    for kk in inst_ids[ss]} for ss in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'vtec': dt.datetime(2017, 11, 19),
                    'site': dt.datetime(2001, 1, 1),
                    'los': dt.datetime(2023, 1, 1)}}
_test_load_opt = {'': {'los': [{'los_method': 'site', 'los_value': 'zzon',
                                'gnss_network': 'glonass'},
                               {'los_method': 'time',
                                'los_value': dt.datetime(2023, 1, 1)}]}}
_test_download_ci = {'': {'los': False}}  # Download is too large to test
_password_req = {'': {'los': True}}  # Disable locally, download is too large
_clean_warn = {'': {tag: {clean_level: [('logger', 'INFO',
                                         'Data provided at a clean level'
                                         if tag == 'site' else
                                         'further cleaning may be performed',
                                         clean_level)]
                          for clean_level in ['clean', 'dusty', 'dirty']}
                    for tag in inst_ids['']}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with values specific to GNSS TEC."""
    self.acknowledgements = '\n'.join([gnss.acknowledgements(self.name),
                                       general.cedar_rules()])
    self.references = gnss.references(self.name)
    pysat.logger.info(self.acknowledgements)

    return


def clean(self):
    """Clean GNSS TEC data to a specific level.

    Note
    ----
    Supports 'clean', 'dusty', and 'dirty'.  Not called by pysat if
    `clean_level` is None.

    """
    msg = "Data provided at a clean level"
    if self.tag == "vtec":
        msg = "".join([msg, ", further cleaning may be performed using ",
                       "the measurement error 'dtec'"])
    elif self.tag == "los":
        msg = "".join([msg, ", further cleaning may be performed using ",
                       "the measurement error 'dlos_tec'"])
    pysat.logger.info(msg)

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal methods


def list_files(tag, inst_id, data_path=None, format_str=None,
               file_cadence=dt.timedelta(days=1), delimiter=None,
               file_type=None):
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
    if tag == 'vtec':
        two_digit_year_break = 99
    else:
        two_digit_year_break = None

    out = general.list_files(tag, inst_id, data_path=data_path,
                             format_str=format_str,
                             supported_tags=supported_tags,
                             file_cadence=file_cadence,
                             two_digit_year_break=two_digit_year_break,
                             delimiter=delimiter, file_type=file_type)
    return out


def download(date_array, tag='', inst_id='', data_path=None, user=None,
             password=None, url='http://cedar.openmadrigal.org',
             file_type='netCDF4'):
    """Download data from Madrigal.

    Parameters
    ----------
    date_array : array-like
        list of datetimes to download data for. The sequence of dates need not
        be contiguous.
    tag : str
        Tag identifier used for particular dataset. This input is provided by
        pysat. (default='')
    inst_id : str
        Instrument ID string identifier used for particular dataset. This input
        is provided by pysat. (default='')
    data_path : str
        Path to directory to download data to. (default=None)
    user : str
        User string input used for download. Provided by user and passed via
        pysat. (default=None)
    password : str
        Password for data download. (default=None)
    url : str
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    file_type : str
        File format for Madrigal data. (default='netCDF4')

    Note
    ----
    The user's names should be provided in field user. Anthea Coster should
    be entered as Anthea+Coster

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    if tag == 'los':
        pysat.logger.warning(
            'LoS download is very large and succeptible to failure.')

    general.download(date_array, inst_code=str(madrigal_inst_code),
                     kindat=madrigal_tag[inst_id][tag], data_path=data_path,
                     user=user, password=password, file_type=file_type, url=url)

    return


def load(fnames, tag='', inst_id='', los_method='site', los_value=None,
         gnss_network='all'):
    """Load the GNSS TEC data.

    Parameters
    ----------
    fnames : list
        List of filenames
    tag : str
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    los_method : str
        For 'los' tag only, load data for a unique GNSS receiver site ('site')
        or at a unique time ('time') (default='site')
    los_value : str, dt.datetime, or NoneType
        For 'los' tag only, load data at this unique site or time (default=None)
    gnss_nework : bool
        For 'los' tag only, limit data by GNSS network if not 'all'. Currently
        supports 'all', 'gps', and 'glonass' (default='all')

    Returns
    -------
    data : xarray.Dataset
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Raises
    ------
    ValueError
        If tag is 'los' and no valid 'los_value' is provided or unknown tag

    Note
    ----
    The line-of-sight data is too large to load an entire file at once. Data
    may be loaded by individual receiver site for any number of days
    (recommended to load one day) or a given time. To discover the available
    sites and times (exact times are required for selection), you may use the
    `pysatMadrigal.instruments.methods.gnss.get_los_times` and
    `pysatMadrigal.instruments.methods.gnss.get_los_receiver_sites` functions.

    """
    # Load the specified data
    if tag == 'vtec':
        data, meta, lat_keys, lon_keys = gnss.load_vtec(fnames)
    elif tag == 'site':
        data, meta, lat_keys, lon_keys = gnss.load_site(fnames)
    elif tag == 'los':
        if los_value is None:
            raise ValueError('must specify a valid {:}'.format(los_method))

        data, meta, lat_keys, lon_keys = gnss.load_los(fnames, los_method,
                                                       los_value, gnss_network)

    if len(data.dims.keys()) > 0:
        # Squeeze the kindat and kinst 'coordinates', but keep them as floats
        squeeze_dims = np.array(['kindat', 'kinst'])
        squeeze_mask = [sdim in data.coords for sdim in squeeze_dims]
        if np.any(squeeze_mask):
            data = data.squeeze(dim=squeeze_dims[squeeze_mask])

        # Get the maximum and minimum values for time, latitude, and longitude
        meta['time'] = {meta.labels.notes: data['time'].values.dtype.__doc__,
                        meta.labels.min_val: np.nan,
                        meta.labels.max_val: np.nan}

        for lat_key in lat_keys:
            meta[lat_key] = {meta.labels.min_val: -90.0,
                             meta.labels.max_val: 90.0}

            for lon_key in lon_keys:
                min_lon = 0.0 if data[lon_key].values.min() >= 0.0 else -180.0
                meta[lon_key] = {meta.labels.min_val: min_lon,
                                 meta.labels.max_val: min_lon + 360.0}

    return data, meta


def list_remote_files(tag, inst_id, start=dt.datetime(1998, 10, 15),
                      stop=dt.datetime.utcnow(), user=None, password=None):
    """Create a Pandas Series of every file for chosen remote data.

    Parameters
    ----------
    tag : str
        Denotes type of file to load.  This input is nominally provided
        by pysat itself.
    inst_id : str
        Specifies the satellite or instrument ID. This input is nominally
        provided by pysat itself.
    start : dt.datetime or NoneType
        Starting time for file list. If None, replaced with default.
        (default=10-15-1998)
    stop : dt.datetime or NoneType
        Ending time for the file list. If None, replaced with default.
        (default=time of run)
    user : str or NoneType
        Username to be passed along to resource with relevant data.
        (default=None)
    password : str or NoneType
        User password to be passed along to resource with relevant data.
        (default=None)

    Returns
    -------
    files : pds.Series
        A series of filenames, see `pysat.utils.files.process_parsed_filenames`
        for more information.

    See Also
    --------
    pysatMadrigal.instruments.methods.general.list_remote_files

    """
    if tag == 'vtec':
        two_break = 99
    else:
        two_break = None

    files = general.list_remote_files(
        tag, inst_id, supported_tags=remote_tags,
        inst_code=madrigal_inst_code, kindats=madrigal_tag, start=start,
        stop=stop, user=user, password=password, two_digit_year_break=two_break)

    return files
