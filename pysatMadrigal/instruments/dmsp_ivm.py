# -*- coding: utf-8 -*-
"""Supports the Ion Velocity Meter (IVM)
onboard the Defense Meteorological Satellite Program (DMSP).

The IVM is comprised of the Retarding Potential Analyzer (RPA) and
Drift Meter (DM). The RPA measures the energy of plasma along the
direction of satellite motion. By fitting these measurements
to a theoretical description of plasma the number density, plasma
composition, plasma temperature, and plasma motion may be determined.
The DM directly measures the arrival angle of plasma. Using the reported
motion of the satellite the angle is converted into ion motion along
two orthogonal directions, perpendicular to the satellite track. The IVM is
part of the Special Sensor for Ions, Electrons, and Scintillations (SSIES)
instrument suite on DMSP.

Downloads data from the National Science Foundation Madrigal Database.
The routine is configured to utilize data files with instrument
performance flags generated at the Center for Space Sciences at the
University of Texas at Dallas.

Properties
----------
platform
    'dmsp'
name
    'ivm'
tag
    'utd', None
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

Custom Functions
----------------
add_drift_unit_vectors
    Add unit vectors for the satellite velocity
add_drifts_polar_cap_x_y
    Add polar cap drifts in cartesian coordinates
smooth_ram_drifts
    Smooth the ram drifts using a rolling mean
update_DMSP_ephemeris
    Updates DMSP instrument data with DMSP ephemeris

"""

import datetime as dt
import functools
import numpy as np
import pandas as pds

from pysat.instruments.methods import general as ps_gen
from pysat import logger

from pysatMadrigal.instruments.methods import madrigal as mad_meth

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

# madrigal tags
madrigal_inst_code = 8100
madrigal_tag = {'f11': {'utd': 10241, '': 10111},
                'f12': {'utd': 10242, '': 10112},
                'f13': {'utd': 10243, '': 10113},
                'f14': {'utd': 10244, '': 10114},
                'f15': {'utd': 10245, '': 10115},
                'f16': {'': 10116},
                'f17': {'': 10117},
                'f18': {'': 10118}, }

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'f11': {'utd': dt.datetime(1998, 1, 2)},
               'f12': {'utd': dt.datetime(1998, 1, 2)},
               'f13': {'utd': dt.datetime(1998, 1, 2)},
               'f14': {'utd': dt.datetime(1998, 1, 2)},
               'f15': {'utd': dt.datetime(2017, 12, 30)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object with values specific to DMSP IVM

    Runs once upon instantiation.

    Parameters
    ----------
    self : pysat.Instrument
        This object

    """

    logger.info(mad_meth.cedar_rules())
    self.acknowledgements = mad_meth.cedar_rules()
    self.references = ' '.join(('F. J. Rich, Users Guide for the Topside',
                                'Ionospheric Plasma Monitor (SSIES,',
                                'SSIES-2 and SSIES-3) on Spacecraft of',
                                'the Defense Meteorological Satellite',
                                'Program (Air Force Phillips Laboratory,',
                                'Hanscom AFB, MA, 1994), Vol. 1, p. 25.'))
    return


def clean(self):
    """Routine to return DMSP IVM data cleaned to the specified level

    Note
    ----
    Supports 'clean', 'dusty', 'dirty'

    'clean' enforces that both RPA and DM flags are <= 1
    'dusty' <= 2
    'dirty' <= 3
    'none' Causes pysat to skip this routine

    Routine is called by pysat, and not by the end user directly.

    """

    if self.tag == 'utd':
        if self.clean_level == 'clean':
            idx, = np.where((self['rpa_flag_ut'] <= 1)
                            & (self['idm_flag_ut'] <= 1))
        elif self.clean_level == 'dusty':
            idx, = np.where((self['rpa_flag_ut'] <= 2)
                            & (self['idm_flag_ut'] <= 2))
        elif self.clean_level == 'dirty':
            idx, = np.where((self['rpa_flag_ut'] <= 3)
                            & (self['idm_flag_ut'] <= 3))
        else:
            idx = slice(0, self.index.shape[0])
    else:
        if self.clean_level in ['clean', 'dusty', 'dirty']:
            logger.warning('this level 1 data has no quality flags')
        idx = slice(0, self.index.shape[0])

    # downselect data based upon cleaning conditions above
    self.data = self[idx]

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal and pysat methods

# Set the list_remote_files routine
list_remote_files = functools.partial(mad_meth.list_remote_files,
                                      supported_tags=supported_tags,
                                      inst_code=madrigal_inst_code)

# Set the load routine
load = mad_meth.load


def list_files(tag=None, inst_id=None, data_path=None, format_str=None,
               supported_tags=supported_tags,
               fake_daily_files_from_monthly=False, delimiter=None,
               file_type='hdf5'):
    """Return a Pandas Series of every data file for this Instrument

    Parameters
    ----------
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
    delimiter : string
        Delimiter string upon which files will be split (e.g., '.')
    file_type : string
        File format for Madrigal data.  Load routines currently only accepts
        'hdf5' and 'netCDF4', but any of the Madrigal options may be used
        here. (default='netCDF4')

    Returns
    -------
    out : pysat.Files.from_os : pysat._files.Files
        A class containing the verified available files

    """
    if supported_tags[inst_id][tag].find('{file_type}') > 0:
        supported_tags[inst_id][tag] = supported_tags[inst_id][tag].format(
            file_type=file_type)

    out = ps_gen.list_files(
        tag=tag, inst_id=inst_id, data_path=data_path, format_str=format_str,
        supported_tags=supported_tags,
        fake_daily_files_from_monthly=fake_daily_files_from_monthly,
        delimiter=delimiter)

    return out


def download(date_array, tag='', inst_id='', data_path=None, user=None,
             password=None, file_type='hdf5'):
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
    file_type : string
        File format for Madrigal data.  Load routines currently only accepts
        'hdf5' and 'netCDF4', but any of the Madrigal options may be used
        here. (default='hdf5')

    Note
    ----
    The user's names should be provided in field user. Ritu Karidhal should
    be entered as Ritu+Karidhal

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    mad_meth.download(date_array, inst_code=str(madrigal_inst_code),
                      kindat=str(madrigal_tag[inst_id][tag]),
                      data_path=data_path, user=user, password=password)
    return


# ----------------------------------------------------------------------------
# Local functions


def smooth_ram_drifts(inst, rpa_flag_key=None, rpa_vel_key='ion_v_sat_for'):
    """ Smooth the ram drifts using a rolling mean

    Parameters
    ----------
    inst : pysat.Instrument
        DMSP IVM Instrument object
    rpa_flag_key : string or NoneType
        RPA flag key, if None will not select any data. The UTD RPA flag key
        is 'rpa_flag_ut' (default=None)
    rpa_vel_key : string
        RPA velocity data key (default='ion_v_sat_for')

    """

    if rpa_flag_key in list(inst.data.keys()):
        rpa_idx, = np.where(inst[rpa_flag_key] == 1)
    else:
        rpa_idx = list()

    inst[rpa_idx, rpa_vel_key] = \
        inst[rpa_idx, rpa_vel_key].rolling(15, 5).mean()
    return


def update_DMSP_ephemeris(inst, ephem=None):
    """Updates DMSP instrument data with DMSP ephemeris

    Parameters
    ----------
    inst : pysat.Instrument
       DMSP IVM Instrumet object
    ephem : pysat.Instrument or NoneType
        DMSP IVM_EPHEM instrument object

    """

    # Ensure the right ephemera is loaded
    if ephem is None:
        logger.info('No ephemera provided for {:}'.format(inst.date))
        inst.data = pds.DataFrame(None)
        return

    if ephem.inst_id != inst.inst_id:
        raise ValueError('ephemera provided for the wrong satellite')

    if ephem.date != inst.date:
        ephem.load(date=inst.date, verifyPad=True)

        if ephem.data.empty:
            logger.info('unable to load ephemera for {:}'.format(inst.date))
            inst.data = pds.DataFrame(None)
            return

    # Reindex the ephemeris data
    ephem.data = ephem.data.reindex(index=inst.data.index, method='pad')
    ephem.data = ephem.data.interpolate('time')

    # Update the DMSP instrument
    inst['mlt'] = ephem['SC_AACGM_LTIME']
    inst['mlat'] = ephem['SC_AACGM_LAT']

    return


def add_drift_unit_vectors(inst):
    """ Add unit vectors for the satellite velocity

    Parameters
    ----------
    inst : pysat.Instrument
        DMSP IVM Instrument object

    Note
    ----
    Assumes that the RAM vector is pointed perfectly forward

    """
    # Calculate theta and R in radians from MLT and MLat, respectively
    theta = inst['mlt'] * (np.pi / 12.0) - np.pi * 0.5
    r = np.radians(90.0 - inst['mlat'].abs())

    # Determine the positions in cartesian coordinates
    pos_x = r * np.cos(theta)
    pos_y = r * np.sin(theta)
    diff_x = pos_x.diff()
    diff_y = pos_y.diff()
    norm = np.sqrt(diff_x**2 + diff_y**2)

    # Calculate the RAM and cross-track unit vectors in cartesian and polar
    # coordinates.
    # x points along MLT = 6, y points along MLT = 12
    inst['unit_ram_x'] = diff_x / norm
    inst['unit_ram_y'] = diff_y / norm
    inst['unit_cross_x'] = -diff_y / norm
    inst['unit_cross_y'] = diff_x / norm
    idx, = np.where(inst['mlat'] < 0)
    inst.data.loc[inst.index[idx], 'unit_cross_x'] *= -1.0
    inst.data.loc[inst.index[idx], 'unit_cross_y'] *= -1.0

    inst['unit_ram_r'] = (inst['unit_ram_x'] * np.cos(theta)
                          + inst['unit_ram_y'] * np.sin(theta))
    inst['unit_ram_theta'] = (-inst['unit_ram_x'] * np.sin(theta)
                              + inst['unit_ram_y'] * np.cos(theta))

    inst['unit_cross_r'] = (inst['unit_cross_x'] * np.cos(theta)
                            + inst['unit_cross_y'] * np.sin(theta))
    inst['unit_cross_theta'] = (-inst['unit_cross_x'] * np.sin(theta)
                                + inst['unit_cross_y'] * np.cos(theta))
    return


def add_drifts_polar_cap_x_y(inst, rpa_flag_key=None,
                             rpa_vel_key='ion_v_sat_for',
                             cross_vel_key='ion_v_sat_left'):
    """ Add polar cap drifts in cartesian coordinates

    Parameters
    ----------
    inst : pysat.Instrument
        DMSP IVM Instrument object
    rpa_flag_key : string or NoneType
        RPA flag key, if None will not select any data. The UTD RPA flag key
        is 'rpa_flag_ut' (default=None)
    rpa_vel_key : string
        RPA velocity data key (default='ion_v_sat_for')
    cross_vel_key : string
        Cross-track velocity data key (default='ion_v_sat_left')

    Notes
    -------
    Polar cap drifts assume there is no vertical component to the X-Y
    velocities.

    Adds 'ion_vel_pc_x', 'ion_vel_pc_y', and 'partial'.  The last data key
    indicates whether RPA data was available (False) or not (True).

    """

    # Get the good RPA data, if available
    if rpa_flag_key in list(inst.data.keys()):
        rpa_idx, = np.where(inst[rpa_flag_key] != 1)
    else:
        rpa_idx = list()

    # Use the cartesian unit vectors to calculate the desired velocities
    iv_x = inst[rpa_vel_key].copy()
    iv_x[rpa_idx] = 0.0

    # Check to see if unit vectors have been created
    if 'unit_ram_y' not in list(inst.data.keys()):
        add_drift_unit_vectors(inst)

    # Calculate the velocities
    inst['ion_vel_pc_x'] = (iv_x * inst['unit_ram_x']
                            + inst[cross_vel_key] * inst['unit_cross_x'])
    inst['ion_vel_pc_y'] = (iv_x * inst['unit_ram_y']
                            + inst[cross_vel_key] * inst['unit_cross_y'])

    # Flag the velocities as full (False) or partial (True)
    inst['partial'] = False
    inst[rpa_idx, 'partial'] = True

    return
