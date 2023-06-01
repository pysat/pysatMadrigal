#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Support the DMSP Special Sensor-J (SSJ) instrument and derived products.


The Defense Meteorological Satellite Program (DMSP) SSJ measures precipitating
particles using spectrometery. The Auroral Boundary Index (ABI) is automatically
computed from this data set and marks the midnight equatorward boundary in each
hemisphere.

Further questions can be addressed to:
 Gordon Wilson
 Air Force Research Lab
 RVBXP
 3550 Aberdeen Avenue SE, Bldg 570
 Kirtland Air Force Base, NM 87117-5776
 Phone: 505-853-2027
 e-mail: gordon.wilson@kirtland.af.mil
or
 Ernie Holeman (ernestholeman7408@comcast.net)

Please send a copy of all publications that use the Auroral Boundary Index
(ABI) to Dr. Gordon Wilson at the above address.


Properties
----------
platform
    'dmsp'
name
    'ssj'
tag
    'abi'
inst_id
    'f11'

Example
-------
::

    import pysat
    dmsp = pysat.Instrument('dmsp', 'ssj', 'abi', clean_level='clean')
    dmsp.download(dt.datetime(2017, 12, 30), dt.datetime(2017, 12, 31),
                  user='Firstname+Lastname', password='email@address.com')
    dmsp.load(2017, 363)

Note
----
Please provide name and email when downloading data with this routine.

"""

import datetime as dt
import functools
import numpy as np
import pandas as pds
import warnings

from pysat import logger
from pysat.utils.time import create_date_range

from pysatMadrigal.instruments.methods import dmsp
from pysatMadrigal.instruments.methods import general

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'dmsp'
name = 'ssj'
tags = {'abi': 'Midnight Auroral Boundary Index'}
inst_ids = {'': [tag for tag in tags.keys()]}

pandas_format = True

# Madrigal tags
madrigal_inst_code = 180
madrigal_tag = {'': {'abi': '17110'}}

# Local attributes
dmsp_fname = general.madrigal_file_format_str(madrigal_inst_code)
supported_tags = {inst_id: {tag: dmsp_fname for tag in inst_ids[inst_id]}
                  for inst_id in inst_ids.keys()}
remote_tags = {
    inst_id: {tag: supported_tags[inst_id][tag].format(file_type='hdf5')
              for tag in inst_ids[inst_id]} for inst_id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'abi': dt.datetime(1982, 12, 30)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object with values specific to DMSP IVM."""
    self.acknowledgements = ''.join([
        general.cedar_rules(), '\nThe Air Force Research Laboratory Auroral ',
        'Boundary Index (ABI) was provided by the United States Air Force ',
        'Research Laboratory, Kirtland Air Force Base, New Mexico.'])

    logger.info(self.acknowledgements)
    self.references = dmsp.references(self.name)
    return


def clean(self):
    """Clean DMSP IVM data cleaned to the specified level.

    Note
    ----
    Supports 'clean' and 'dusty'

    'clean' QC == 1
    'dusty' QC <= 2
    'dirty' and 'none' allow all QC flags (QC <= 3)

    When called directly by pysat, a clean level of 'none' causes pysat to skip
    this routine.

    Warnings
    --------
    UserWarning
        If the 'dirty' level is invoked (same as no cleaning)

    """
    if self.clean_level == 'clean':
        iclean, = np.where(self['EQB_QC_FL'] <= 1)
    elif self.clean_level == 'dusty':
        iclean, = np.where(self['EQB_QC_FL'] <= 2)
    else:
        warnings.warn('No quality control level "dirty", using "none"')
        iclean = None

    # Downselect data based upon cleaning conditions above
    if iclean is not None:
        self.data = self[iclean]

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal and pysat methods

# Support listing the local files
list_files = functools.partial(general.list_files,
                               supported_tags=supported_tags,
                               file_cadence=pds.DateOffset(years=1))

# Set the list_remote_files routine
list_remote_files = functools.partial(general.list_remote_files,
                                      inst_code=madrigal_inst_code,
                                      kindats=madrigal_tag,
                                      supported_tags=remote_tags)


# Set the load routine
def load(fnames, tag='', inst_id=''):
    """Load DMSP SSJ4 data from Madrigal after accounting for date tags.

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
    # The ABI data has a yearly cadance, extract the unique filenames to load
    load_fnames = list()
    file_dates = list()
    for fname in fnames:
        file_dates.append(dt.datetime.strptime(fname[-10:], '%Y-%m-%d'))
        if fname[0:-11] not in load_fnames:
            load_fnames.append(fname[0:-11])

    # Load the data and metadata
    data, meta = general.load(load_fnames, tag=tag, inst_id=inst_id)

    # If there is a date range, downselect here
    if len(file_dates) > 0:
        idx, = np.where((data.index >= min(file_dates))
                        & (data.index < max(file_dates) + dt.timedelta(days=1)))
        data = data.iloc[idx, :]

    return data, meta


def download(date_array, tag='', inst_id='', data_path=None, user=None,
             password=None, file_type='hdf5'):
    """Download DMSP SSJ4 data from Madrigal.

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
    # Ensure the date range is correct
    if date_array.freq not in ['AS-JAN', 'YS', 'AS']:
        date_array = create_date_range(
            dt.datetime(date_array[0].year, 1, 1), date_array[-1], freq='YS')

    # Download the remote files
    general.download(date_array, inst_code=str(madrigal_inst_code),
                     kindat=madrigal_tag[inst_id][tag], data_path=data_path,
                     user=user, password=password, file_type=file_type)
    return
