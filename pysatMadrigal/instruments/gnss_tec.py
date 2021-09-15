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

    import datetime as dt
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

from pysat import logger

from pysatMadrigal.instruments.methods import general, gnss

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'gnss'
name = 'tec'
tags = {'vtec': 'vertical TEC'}
inst_ids = {'': [tag for tag in tags.keys()]}

pandas_format = False

# Local attributes
dname = '{{year:02d}}{{month:02d}}{{day:02d}}'
vname = '.{{version:03d}}'
supported_tags = {ss: {'vtec': ''.join(['gps', dname, 'g', vname,
                                        ".{file_type}"])}
                  for ss in inst_ids.keys()}
remote_tags = {ss: {kk: supported_tags[ss][kk].format(file_type='hdf5')
                    for kk in inst_ids[ss]} for ss in inst_ids.keys()}

# Madrigal tags
madrigal_inst_code = 8000
madrigal_tag = {'': {'vtec': '3500'}}  # , 'los': '3505'}} <- Issue #12

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'vtec': dt.datetime(2017, 11, 19)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with values specific to GNSS TEC

    Runs once upon instantiation.

    """

    ackn_str = '\n'.join([gnss.acknowledgements(self.name),
                          general.cedar_rules()])

    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = gnss.references(self.name, self.tag)

    return


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


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal methods

# Support listing the local files
list_files = functools.partial(general.list_files,
                               supported_tags=supported_tags,
                               two_digit_year_break=99)

# Support listing files currently available on remote server (Madrigal)
list_remote_files = functools.partial(general.list_remote_files,
                                      supported_tags=remote_tags,
                                      inst_code=madrigal_inst_code,
                                      kindats=madrigal_tag)


def download(date_array, tag='', inst_id='', data_path=None, user=None,
             password=None, url='http://cedar.openmadrigal.org',
             file_type='netCDF4'):
    """Downloads data from Madrigal.

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
    general.download(date_array, inst_code=str(madrigal_inst_code),
                     kindat=madrigal_tag[inst_id][tag], data_path=data_path,
                     user=user, password=password, file_type=file_type, url=url)

    return


def load(fnames, tag=None, inst_id=None):
    """ Routine to load the GNSS TEC data

    Parameters
    ----------
    fnames : list
        List of filenames
    tag : str or NoneType
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)
    inst_id : str or NoneType
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)

    Returns
    -------
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
    data, meta = general.load(fnames, tag, inst_id, xarray_coords=xcoords[tag])

    # Squeeze the kindat and kinst 'coordinates', but keep them as floats
    squeeze_dims = np.array(['kindat', 'kinst'])
    squeeze_mask = [sdim in data.coords for sdim in squeeze_dims]
    if np.any(squeeze_mask):
        data = data.squeeze(dim=squeeze_dims[squeeze_mask])

    # Fix the units for tec and dtec
    if tag == 'vtec':
        meta['tec'] = {meta.labels.units: 'TECU', meta.labels.min_val: 0.0,
                       meta.labels.max_val: np.nan}
        meta['dtec'] = {meta.labels.units: 'TECU', meta.labels.min_val: 0.0,
                       meta.labels.max_val: np.nan}

    # Get the maximum and minimum values for time, latitude, longitude,
    # and altitude
    ttype = data['time'].values.dtype
    meta['time'] = {meta.labels.notes: data['time'].values.dtype.__doc__,
                    meta.labels.min_val: np.nan, meta.labels.max_val: np.nan}
    meta['gdalt'] = {meta.labels.min_val: 0.0, meta.labels.max_val: np.nan}
    meta['gdlat'] = {meta.labels.min_val: -90.0, meta.labels.max_val: 90.0}
    min_lon =  0.0 if data['glon'].values.min() >= 0.0 else -180.0
    meta['glon'] = {meta.labels.min_val: min_lon,
                    meta.labels.max_val: min_lon + 360.0}

    return data, meta
