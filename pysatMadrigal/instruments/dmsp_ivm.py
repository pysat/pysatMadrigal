#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Supports the Defense Meteorological Satellite Program (DMSP) IVM instruments.

The Ion Velocity Meter (IVM) is comprised of the Retarding Potential Analyzer
(RPA) and Drift Meter (DM). The RPA measures the energy of plasma along the
direction of satellite motion. By fitting these measurements to a theoretical
description of plasma the number density, plasma composition, plasma
temperature, and plasma motion may be determined. The DM directly measures the
arrival angle of plasma. Using the reported motion of the satellite the angle is
converted into ion motion along two orthogonal directions, perpendicular to the
satellite track. The IVM is part of the Special Sensor for Ions, Electrons, and
Scintillations (SSIES) instrument suite on DMSP.

Downloads data from the National Science Foundation Madrigal Database. The
routine is configured to utilize data files with instrument performance flags
generated at the Center for Space Sciences at the University of Texas at Dallas.

Properties
----------
platform
    'dmsp'
name
    'ivm'
tag
    'utd', ''
inst_id
    ['f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18']

Example
-------
::

    import pysat
    dmsp = pysat.Instrument('dmsp', 'ivm', 'utd', 'f15', clean_level='clean')
    dmsp.download(dt.datetime(2017, 12, 30), dt.datetime(2017, 12, 31),
                  user='Firstname+Lastname', password='email@address.com')
    dmsp.load(2017, 363)

Note
----
Please provide name and email when downloading data with this routine.

Code development supported by NSF grant 1259508

"""

import datetime as dt
import functools
import numpy as np

from pysat import logger

from pysatMadrigal.instruments.methods import dmsp
from pysatMadrigal.instruments.methods import general

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'dmsp'
name = 'ivm'
tags = {'utd': 'UTDallas DMSP data processing', '': 'Level 2 data processing'}
inst_ids = {'f11': ['utd', ''], 'f12': ['utd', ''], 'f13': ['utd', ''],
            'f14': ['utd', ''], 'f15': ['utd', ''], 'f16': [''], 'f17': [''],
            'f18': ['']}

pandas_format = True

# Local attributes
dmsp_fname1 = {'utd': 'dms_ut_{{year:4d}}{{month:02d}}{{day:02d}}_',
               '': 'dms_{{year:4d}}{{month:02d}}{{day:02d}}_'}
dmsp_fname2 = {'utd': '.{{version:03d}}.{file_type}',
               '': 's?.{{version:03d}}.{file_type}'}
supported_tags = {ss: {kk: dmsp_fname1[kk] + ss[1:] + dmsp_fname2[kk]
                       for kk in inst_ids[ss]} for ss in inst_ids.keys()}
remote_tags = {ss: {kk: supported_tags[ss][kk].format(file_type='hdf5')
                    for kk in inst_ids[ss]} for ss in inst_ids.keys()}

# Madrigal tags
madrigal_inst_code = 8100
madrigal_tag = {'f11': {'utd': '10241', '': '10111'},
                'f12': {'utd': '10242', '': '10112'},
                'f13': {'utd': '10243', '': '10113'},
                'f14': {'utd': '10244', '': '10114'},
                'f15': {'utd': '10245', '': '10115'},
                'f16': {'': '10116'},
                'f17': {'': '10117'},
                'f18': {'': '10118'}, }

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {
    'f11': {tag: dt.datetime(1998, 1, 2) for tag in inst_ids['f11']},
    'f12': {tag: dt.datetime(1998, 1, 2) for tag in inst_ids['f12']},
    'f13': {tag: dt.datetime(1998, 1, 2) for tag in inst_ids['f13']},
    'f14': {tag: dt.datetime(1998, 1, 2) for tag in inst_ids['f14']},
    'f15': {tag: dt.datetime(2017, 12, 30) for tag in inst_ids['f15']},
    'f16': {tag: dt.datetime(2009, 1, 1) for tag in inst_ids['f16']},
    'f17': {tag: dt.datetime(2009, 1, 1) for tag in inst_ids['f17']},
    'f18': {tag: dt.datetime(2017, 12, 30) for tag in inst_ids['f18']}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with values specific to DMSP IVM."""
    logger.info(general.cedar_rules())
    self.acknowledgements = general.cedar_rules()
    self.references = dmsp.references(self.name)
    return


def clean(self):
    """Clean DMSP IVM data to the specified level.

    Note
    ----
    Supports 'clean', 'dusty', 'dirty'

    'clean' enforces that both RPA and DM flags are <= 1
    'dusty' <= 2
    'dirty' <= 3

    When called directly by pysat, a clean level of 'none' causes pysat to skip
    this routine.

    """
    if self.tag == 'utd':
        if self.clean_level == 'clean':
            iclean, = np.where((self['rpa_flag_ut'] <= 1)
                               & (self['idm_flag_ut'] <= 1))
        elif self.clean_level == 'dusty':
            iclean, = np.where((self['rpa_flag_ut'] <= 2)
                               & (self['idm_flag_ut'] <= 2))
        elif self.clean_level == 'dirty':
            iclean, = np.where((self['rpa_flag_ut'] <= 3)
                               & (self['idm_flag_ut'] <= 3))
    else:
        logger.warning('this level 1 data has no quality flags')
        iclean = slice(0, self.index.shape[0])

    # Downselect data based upon cleaning conditions above
    self.data = self[iclean]

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal and pysat methods

# Support listing the local files
list_files = functools.partial(general.list_files,
                               supported_tags=supported_tags)

# Set the list_remote_files routine
list_remote_files = functools.partial(general.list_remote_files,
                                      inst_code=madrigal_inst_code,
                                      kindats=madrigal_tag,
                                      supported_tags=remote_tags)

# Set the load routine
load = general.load


def download(date_array, tag='', inst_id='', data_path=None, user=None,
             password=None, file_type='hdf5'):
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
        Satellite ID string identifier used for particular dataset. This input
        is provided by pysat. (default='')
    data_path : str
        Path to directory to download data to. (default=None)
    user : str
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for downloads this routine here must
        error if user not supplied. (default=None)
    password : str
        Password for data download. (default=None)
    file_type : str
        File format for Madrigal data. (default='hdf5')

    Note
    ----
    The user's names should be provided in field user. Ritu Karidhal should
    be entered as Ritu+Karidhal

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    general.download(date_array, inst_code=str(madrigal_inst_code),
                     kindat=madrigal_tag[inst_id][tag], data_path=data_path,
                     user=user, password=password, file_type=file_type)
    return
