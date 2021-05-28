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
import pandas as pds

from pysat.instruments.methods import general as ps_gen
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

# madrigal tags
madrigal_inst_code = 8000
madrigal_tag = {'': {'vtec': '3500'}}  # , 'los': '3505'}}

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

# support listing files currently available on remote server (Madrigal)
list_remote_files = functools.partial(general.list_remote_files,
                                      supported_tags=remote_tags,
                                      inst_code=madrigal_inst_code,
                                      kindats=madrigal_tag)


def list_files(tag=None, inst_id=None, data_path=None, format_str=None,
               supported_tags=supported_tags, two_digit_year_break=99,
               delimiter=None, file_type=None):
    """Return a Pandas Series of every data file for this Instrument

    Parameters
    ----------
    tag : str or NoneType
        Denotes type of file to load.  Accepted types are <tag strings>.
        (default=None)
    inst_id : str or NoneType
        Specifies the satellite ID for a constellation.  Not used.
        (default=None)
    data_path : str or NoneType
        Path to data directory.  If None is specified, the value previously
        set in Instrument.files.data_path is used.  (default=None)
    format_str : str or NoneType
        User specified file format.  If None is specified, the default
        formats associated with the supplied tags are used. (default=None)
    supported_tags : dict or NoneType
        keys are inst_id, each containing a dict keyed by tag
        where the values file format template strings. (default=None)
    two_digit_year_break : int
        If filenames only store two digits for the year, then
        '1900' will be added for years >= two_digit_year_break
        and '2000' will be added for years < two_digit_year_break.
    delimiter : str
        Delimiter string upon which files will be split (e.g., '.')
    file_type : str or NoneType
        File format for Madrigal data.  Load routines currently accepts 'hdf5',
        'simple', and 'netCDF4', but any of the Madrigal options may be used
        here. If None, will look for all known file types. (default=None)

    Returns
    -------
    out : pysat.Files.from_os : pysat._files.Files
        A class containing the verified available files

    """
    file_types = general.file_types.keys() if file_type is None else [file_type]
    sup_tags = {inst_id: {tag: supported_tags[inst_id][tag]}}
    out_series = list()

    for file_type in file_types:
        if supported_tags[inst_id][tag].find('{file_type}') > 0:
            sup_tags[inst_id][tag] = supported_tags[inst_id][tag].format(
                file_type=general.file_types[file_type])

        out_series.append(
            ps_gen.list_files(tag=tag, inst_id=inst_id, data_path=data_path,
                              format_str=format_str, delimiter=delimiter,
                              two_digit_year_break=two_digit_year_break,
                              supported_tags=sup_tags))

    if len(out_series) == 0:
        out = pds.Series(dtype=str)
    elif len(out_series) == 1:
        out = out_series[0]
    else:
        out = pds.concat(out_series).sort_index()

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
        meta['tec'] = {meta.labels.units: 'TECU'}
        meta['dtec'] = {meta.labels.units: 'TECU'}

    return data, meta
