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
sat_ids = {'': [tag for tag in tags.keys()]}
_test_dates = {'': {'vtec': dt.datetime(2017, 11, 19)}}
pandas_format = False

# support list files routine
# use the default pysat method
dname = '{year:02d}{month:02d}{day:02d}'
vname = '.{version:03d}'
supported_tags = {ss: {'vtec': "gps{:s}g{:s}.hdf5".format(dname, vname)}
                  for ss in sat_ids.keys()}
list_files = functools.partial(ps_gen.list_files,
                               supported_tags=supported_tags,
                               two_digit_year_break=99)

# madrigal tags
madrigal_inst_code = 8000
madrigal_tag = {'': {'vtec': 3500}}  #, 'los': 3505}}

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
                        "Dynamics Data Information System (CDDIS), National",
                        " Geodetic Survey, Instituto Brasileiro de Geografia",
                        " e Estatística, RAMSAC CORS of Instituto Geográfico",
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


def download(date_array, tag='', sat_id='', data_path=None, user=None,
             password=None):
    """Downloads data from Madrigal.

    Parameters
    ----------
    date_array : array-like
        list of datetimes to download data for. The sequence of dates need not
        be contiguous.
    tag : string
        Tag identifier used for particular dataset. This input is provided by
        pysat. (default='')
    sat_id : string
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
                      kindat=str(madrigal_tag[sat_id][tag]),
                      data_path=data_path, user=user, password=password)
    return


def load(fnames, tag=None, sat_id=None):
    """ Routine to load the GNSS TEC data

    Parameters
    -----------
    fnames : list
        List of filenames
    tag : string or NoneType
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)
    sat_id : string or NoneType
        Satellite ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)

    Returns
    --------
    data : xarray.Dataset
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    """
    # Define the xarray coordinate dimensions (apart from time)
    xcoords = {'vtec': {('time', 'gdlat', 'glon', 'gdalt', 'kindat', 'kinst'):
                        ['tec', 'dtec'],
                        ('time',): ['year', 'month', 'day', 'hour', 'min',
                                    'sec', 'ut1_unix', 'ut2_unix', 'recno']},}

    # Load the specified data
    data, meta = mad_meth.load(fnames, tag, sat_id, xarray_coords=xcoords[tag])

    # Squeeze the kindat and kinst 'coordinates', but keep them as floats
    data = data.squeeze(dim=['kindat', 'kinst'])
    
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
