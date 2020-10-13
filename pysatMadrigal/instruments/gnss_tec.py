# -*- coding: utf-8 -*-.
"""Supports the MIT Haystack GNSS TEC data products

The Global Navigation Satellite System (GNSS) is used in conjunction with a
world-wide receiver network to produce total electron content (TEC) data
products, including vertical and line-of-sight TEC.

Downloads data from the MIT Haystack Madrigal Database.

Properties
----------
platform
    'gnss'
name
    'tec'
tag
    'vtec'

Examples
--------
::

    import datetime
    import pysat
    import pysatMadrigal as pymad

    vtec = pysat.Instrument(inst_module=pymad.instruments.gnss_tec, tag='vtec')
    vtec.download(dt.datetime(2017, 11, 19), dt.datetime(2017, 11, 20),
                  user='Firstname+Lastname', password='email@address.com')
    vtec.load(date=dt.datetime(2017, 11, 19))


Note
----
    Please provide name and email when downloading data with this routine.

"""

import datetime as dt
import functools
import numpy as np

from pysat.instruments.methods import general as ps_gen

from pysatMadrigal.instruments.methods import madrigal as mad_meth

import logging
logger = logging.getLogger(__name__)


platform = 'gnss'
name = 'tec'
tags = {'vtec': 'vertical TEC'}
inst_ids = {'': [tag for tag in tags.keys()]}
_test_dates = {'': {'vtec': dt.datetime(2017, 11, 19)}}
pandas_format = False

# Support for the list files routine
# Use the default pysat method within a local routine that defines the
# file type
dname = '{{year:02d}}{{month:02d}}{{day:02d}}'
vname = '.{{version:03d}}'
supported_tags = {ss: {'vtec': ''.join(['gps', dname, 'g', vname,
                                        ".{file_type}"])}
                  for ss in inst_ids.keys()}

# madrigal tags
madrigal_inst_code = 8000
madrigal_tag = {'': {'vtec': 3500}}  # , 'los': 3505}}

# support listing files currently available on remote server (Madrigal)
list_remote_files = functools.partial(mad_meth.list_remote_files,
                                      supported_tags=supported_tags,
                                      inst_code=madrigal_inst_code)


def init(self):
    """Initializes the Instrument object with values specific to GNSS TEC

    Runs once upon instantiation.

    """

    ackn_str = ''.join(["GPS TEC data products and access through the ",
                        "Madrigal distributed data system are provided to ",
                        "the community by the Massachusetts Institute of ",
                        "Technology under support from U.S. National Science",
                        " Foundation grant AGS-1242204. Data for the TEC ",
                        "processing is provided by the following ",
                        "organizations: UNAVCO, Scripps Orbit and Permanent",
                        " Array Center, Institut Geographique National, ",
                        "France, International GNSS Service, The Crustal ",
                        "Dynamics Data Information System (CDDIS), National ",
                        " Geodetic Survey, Instituto Brasileiro de Geografia",
                        "e Estatística, RAMSAC CORS of Instituto Geográfico",
                        " Nacional del la República Agentina, Arecibo ",
                        "Observatory, Low-Latitude Ionospheric Sensor ",
                        "Network (LISN), Topcon Positioning Systems, Inc., ",
                        "Canadian High Arctic Ionospheric Network, ",
                        "Institute of Geology and Geophysics, Chinese ",
                        "Academy of Sciences, China Meterorology ",
                        "Administration, Centro di Ricerche Sismogiche, ",
                        "Système d’Observation du Niveau des Eaux Littorales",
                        " (SONEL), RENAG : REseau NAtional GPS permanent, ",
                        "and GeoNet—the official source of geological ",
                        "hazard information for New Zealand.\n",
                        mad_meth.cedar_rules()])

    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = "Rideout and Coster (2006) doi:10.1007/s10291-006-0029-5"
    
    return


def list_files(tag=None, inst_id=None, data_path=None, format_str=None,
               supported_tags=supported_tags,
               fake_daily_files_from_monthly=False, two_digit_year_break=99,
               delimiter=None, file_type=''):
    """Return a Pandas Series of every data file for this Instrument

    
    Parameters
    -----------
    tag : string or NoneType
        Denotes type of file to load.  Accepted types are <tag strings>.
        (default=None)
    inst_id : string or NoneType
        Specifies the satellite ID for a constellation.  Not used.
        (default=None)
    data_path : string or NoneType
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)
    format_str : string or NoneType
        User specified file format.  If None is specified, the default
        formats associated with the supplied tags are used. (default=None)
    supported_tags : dict or NoneType
        keys are inst_id, each containing a dict keyed by tag
        where the values file format template strings. (default=None)
    fake_daily_files_from_monthly : bool
        Some CDAWeb instrument data files are stored by month, interfering
        with pysat's functionality of loading by day. This flag, when true,
        appends daily dates to monthly files internally. These dates are
        used by load routine in this module to provide data by day.
    two_digit_year_break : int
        If filenames only store two digits for the year, then
        '1900' will be added for years >= two_digit_year_break
        and '2000' will be added for years < two_digit_year_break.
    delimiter : string
        Delimiter string upon which files will be split (e.g., '.')
    file_type : string
        File format for Madrigal data.  Load routines currently only accepts
        'hdf5' and 'netCDF4', but any of the Madrigal options may be used
        here. (default='netCDF4')

    Returns
    --------
    out : pysat.Files.from_os : pysat._files.Files
        A class containing the verified available files

    """
    supported_tags[inst_id][tag] = supported_tags[inst_id][tag].format(
        file_type=file_type)

    out = ps_gen.list_files(
        tag=tag, inst_id=inst_id, data_path=data_path, format_str=format_str,
        supported_tags=supported_tags,
        fake_daily_files_from_monthly=fake_daily_files_from_monthly,
        two_digit_year_break=two_digit_year_break, delimiter=delimiter)

    return out


def download(date_array, tag='', inst_id='', data_path=None, user=None,
             password=None, url='http://cedar.openmadrigal.org',
             file_type='netCDF4'):
    """Downloads data from Madrigal.

    Parameters
    ----------
    date_array : array-like
        list of datetimes to download data for. The sequence of dates need not
        be contiguous.
    tag : string
        Tag identifier used for particular dataset. This input is provided by
        pysat. (default='')
    inst_id : string
        Satellite ID string identifier used for particular dataset. This input
        is provided by pysat. (default='')
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
        here. (default='netCDF4')

    Note
    ----
    The user's names should be provided in field user. Anthea Coster should
    be entered as Anthea+Coster

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    mad_meth.download(date_array, inst_code=str(madrigal_inst_code),
                      kindat=str(madrigal_tag[inst_id][tag]),
                      data_path=data_path, user=user, password=password,
                      file_type=file_type, url=url)

    return


def load(fnames, tag=None, inst_id=None, file_type='netCDF4'):
    """ Routine to load the GNSS TEC data

    Parameters
    -----------
    fnames : list
        List of filenames
    tag : string or NoneType
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)
    inst_id : string or NoneType
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)
    file_type : string
        File format for Madrigal data. Currently only accepts 'hdf5' and
        'netCDF4', but any of the Madrigal options may be used  here.
        (default='netCDF4')

    Returns
    --------
    data : xarray.Dataset
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    """
    # Define the xarray coordinate dimensions (apart from time)
    # Not needed for netCDF
    xcoords = {'vtec': {('time', 'gdlat', 'glon', 'kindat', 'kinst'):
                        ['gdalt', 'tec', 'dtec'],
                        ('time', ): ['year', 'month', 'day', 'hour', 'min',
                                     'sec', 'ut1_unix', 'ut2_unix', 'recno']}}

    # Load the specified data
    data, meta = mad_meth.load(fnames, tag, inst_id,
                               xarray_coords=xcoords[tag],
                               file_type=file_type)

    # Squeeze the kindat and kinst 'coordinates', but keep them as floats
    squeeze_dims = np.array(['kindat', 'kinst'])
    squeeze_mask = [sdim in data.coords for sdim in squeeze_dims]
    if np.any(squeeze_mask):
        data = data.squeeze(dim=squeeze_dims[squeeze_mask])

    # Fix the units for tec and dtec
    if tag == 'vtec':
        meta['tec'] = {meta.units_label: 'TECU'}
        meta['dtec'] = {meta.units_label: 'TECU'}

    return data, meta


def clean(self):
    """Routine to return GNSS TEC data at a specific level

    Note
    ----
    Supports 'clean', 'dusty', 'dirty', or 'None'.
    Routine is called by pysat, and not by the end user directly.

    """
    if self.tag == "vtec":
        logger.info("".join(["Data provided at a clean level, further ",
                             "cleaning may be performed using the ",
                             "measurement error 'dtec'"]))

    return
