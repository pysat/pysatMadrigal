#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Methods supporting the Defense Meteorological Satellite Program (DMSP)."""

import numpy as np
import pandas as pds

from pysat import logger


def references(name):
    """Provide references for the DMSP instruments and experiments.

    Parameters
    ----------
    name : str
        Instrument name

    Returns
    -------
    refs : str
        String providing reference guidenance for the DMSP data

    """
    refs = {'ivm': ' '.join(('F. J. Rich, Users Guide for the Topside',
                             'Ionospheric Plasma Monitor (SSIES, SSIES-2 and',
                             'SSIES-3) on Spacecraft of the Defense',
                             'Meteorological Satellite Program (Air Force',
                             'Phillips Laboratory, Hanscom AFB, MA, 1994),',
                             'Vol. 1, p. 25.'))}

    return refs[name]


def smooth_ram_drifts(inst, rpa_flag_key=None, rpa_flag_max=1,
                      rpa_vel_key='ion_v_sat_for', smooth_key=None,
                      roll_window=15, roll_kwargs=None):
    """Smooth the ram drifts using a rolling mean.

    Parameters
    ----------
    inst : pysat.Instrument
        DMSP IVM Instrument object
    rpa_flag_key : str or NoneType
        RPA flag key, if None then no data is selected. The UTD RPA flag key
        is 'rpa_flag_ut' (default=None)
    rpa_flag_max : int
        Maximum allowable RPA flag (default=1)
    rpa_vel_key : str
        RPA velocity data key (default='ion_v_sat_for')
    smooth_key : str or NoneType
        If None will fill old RPA data with smoothed data, otherwise assigns
        the smoothed data to this new variable
    roll_window : int, offset, or BaseIndexer subclass
        Size of the moving window (default=15)
    roll_kwargs : dict or NoneType
        Keyword args for rolling mean window.  If None uses {'min_periods': 5}
        (default=None)

    Raises
    ------
    KeyError
        If unknown values are used for `rpa_flag_key` or `rpa_vel_key`

    See Also
    --------
    pandas.rolling

    """
    # Select the desired data for averaging
    if rpa_flag_key is None:
        rpa_idx = list()
    else:
        rpa_idx, = np.where(inst[rpa_flag_key] <= rpa_flag_max)

    # Smooth the data
    if roll_kwargs is None:
        roll_kwargs = {'min_periods': 5}

    smooth = inst[rpa_idx, rpa_vel_key].rolling(roll_window,
                                                **roll_kwargs).mean()

    # Assign the smoothed data
    if smooth_key is None:
        inst[rpa_idx, rpa_vel_key] = smooth
        smooth_key = rpa_vel_key
    else:
        inst[smooth_key] = smooth
        inst.meta[smooth_key] = inst.meta[rpa_vel_key]

    # Update the metadata
    desc = 'Rolling mean of window {:d} and {:} for {:s}'.format(
        roll_window, roll_kwargs, 'no data selected' if rpa_flag_key is None
        else 'RPA flag data <= {:d}'.format(rpa_flag_max))
    inst.meta[smooth_key] = {inst.meta.labels.desc: desc}

    return


def update_DMSP_ephemeris(inst, ephem=None):
    """Update DMSP instrument data with improved DMSP ephemeris.

    Parameters
    ----------
    inst : pysat.Instrument
       DMSP IVM Instrument object
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

    # Ensure the correct satellite and time have ephemeris data
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
    """Add unit vectors for expressing plasma motion at high latitudes.

    Parameters
    ----------
    inst : pysat.Instrument
        DMSP IVM Instrument object

    Note
    ----
    Assumes that the RAM vector is pointed perfectly forward. Expresses the
    satellite ram and crosstrack directions along x (points along 6 MLT)
    and y (points along 12 MLT) unit vectors. Also expresses the same
    parameters along polar coordinate directions, r (origin at magnetic pole)
    and theta (theta=0 points along x). Adds variables `unit_ram_x`,
    `unit_ram_y`, `unit_cross_x`, `unit_cross_y`, `unit_ram_r`,
    `unit_ram_theta`, `unit_cross_r`, `unit_cross_theta`.

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

    # Add metadata, ram drift, x-y
    desc = ''.join(['Unit vector for the satellite ram direction, polar x',
                    ' component. Origin at magnetic pole, points toward ',
                    '6 MLT.'])
    meta_dict = {inst.meta.labels.units: '',
                 inst.meta.labels.name: ''.join(['Unit Vector - ram - x']),
                 inst.meta.labels.desc: desc, inst.meta.labels.fill_val: np.nan,
                 inst.meta.labels.min_val: -1., inst.meta.labels.max_val: 1.}
    inst.meta['unit_ram_x'] = meta_dict

    desc = ''.join(['Unit vector for the satellite ram direction, polar y ',
                    'component. Origin at magnetic pole, points toward ',
                    '12 MLT.'])
    meta_dict[inst.meta.labels.desc] = desc
    meta_dict[inst.meta.labels.name] = ''.join(['Unit Vector - ram - y']),
    inst.meta['unit_ram_y'] = meta_dict

    # Cross-track metadata, x-y
    desc = ''.join(['Unit vector for the satellite cross-track direction, ',
                    'polar x component. Origin at magnetic pole, ',
                    'points toward 6 MLT.'])
    meta_dict = {inst.meta.labels.units: '',
                 inst.meta.labels.name: ''.join(['Unit Vector - cross - x']),
                 inst.meta.labels.desc: desc, inst.meta.labels.fill_val: np.nan,
                 inst.meta.labels.min_val: -1., inst.meta.labels.max_val: 1.}
    inst.meta['unit_cross_x'] = meta_dict

    desc = ''.join(['Unit vector for the satellite cross-track direction, ',
                    'polar y component. Origin at magnetic pole, ',
                    'points toward 12 MLT.'])
    meta_dict[inst.meta.labels.desc] = desc
    meta_dict[inst.meta.labels.name] = ''.join(['Unit Vector - cross - ',
                                                'y']),
    inst.meta['unit_cross_y'] = meta_dict

    # Ram metadata, polar coords
    desc = ''.join(['Unit vector for the satellite ram direction, polar radial',
                    ' component. Origin at magnetic pole.'])
    meta_dict = {inst.meta.labels.units: '',
                 inst.meta.labels.name: ''.join(['Unit Vector - ram - r']),
                 inst.meta.labels.desc: desc, inst.meta.labels.fill_val: np.nan,
                 inst.meta.labels.min_val: -1., inst.meta.labels.max_val: 1.}
    inst.meta['unit_ram_r'] = meta_dict

    desc = ''.join(['Unit vector for the satellite ram direction, polar theta ',
                    'component. Origin at magnetic pole.'])
    meta_dict[inst.meta.labels.desc] = desc
    meta_dict[inst.meta.labels.name] = ''.join(['Unit Vector - ram - theta']),
    inst.meta['unit_ram_theta'] = meta_dict

    # Cross-track metadata, polar coords
    desc = ''.join(['Unit vector for the satellite cross-track direction, ',
                    'polar radial component. Origin at magnetic pole.'])
    meta_dict = {inst.meta.labels.units: '',
                 inst.meta.labels.name: ''.join(['Unit Vector - cross - r']),
                 inst.meta.labels.desc: desc, inst.meta.labels.fill_val: np.nan,
                 inst.meta.labels.min_val: -1., inst.meta.labels.max_val: 1.}
    inst.meta['unit_cross_r'] = meta_dict

    desc = ''.join(['Unit vector for the satellite cross-track direction, ',
                    'polar theta component. Origin at magnetic pole.'])
    meta_dict[inst.meta.labels.desc] = desc
    meta_dict[inst.meta.labels.name] = ''.join(['Unit Vector - cross - ',
                                                'theta']),
    inst.meta['unit_cross_theta'] = meta_dict

    return


def add_drifts_polar_cap_x_y(inst, rpa_flag_key=None,
                             rpa_vel_key='ion_v_sat_for',
                             cross_vel_key='ion_v_sat_left'):
    """Add polar cap drifts in cartesian coordinates.

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

    Note
    ----
    Polar cap drifts assume there is no vertical component to the X-Y
    velocities.

    x points along same direction as from magnetic pole towards 6 MLT, and
    y points along same direction as from magnetic pole towards 12 MLT.

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

    # Add metadata
    desc = ''.join(['Ion velocity along the polar cap "{}" direction,',
                    'which points from the magnetic pole towards {:02d} MLT.'])
    notes = ''.join(['Generated by combining plasma drift measurements ',
                     'from the RPA and DM along the "x" or "y" polar cap ',
                     'directions, as appropriate.'])
    units = inst.meta[cross_vel_key, inst.meta.labels.units]
    inst.meta['ion_vel_pc_x'] = {inst.meta.labels.units: units,
                                 inst.meta.labels.name: ''.join(['Ion Velocity',
                                                                 '- Polar ',
                                                                 'Cap - x']),
                                 inst.meta.labels.desc: desc.format('x', 6),
                                 inst.meta.labels.fill_val: np.nan,
                                 inst.meta.labels.min_val: -np.inf,
                                 inst.meta.labels.max_val: np.inf,
                                 inst.meta.labels.notes: notes}

    inst.meta['ion_vel_pc_y'] = {inst.meta.labels.units: units,
                                 inst.meta.labels.name: ''.join(['Ion Velocity',
                                                                 '- Polar ',
                                                                 'Cap - y']),
                                 inst.meta.labels.desc: desc.format('y',
                                                                    12),
                                 inst.meta.labels.fill_val: np.nan,
                                 inst.meta.labels.min_val: -np.inf,
                                 inst.meta.labels.max_val: np.inf,
                                 inst.meta.labels.notes: notes}

    # Flag the velocities as full (False) or partial (True)
    inst['partial'] = False
    inst[rpa_idx, 'partial'] = True

    desc = ''.join(['True if reported measurement is incomplete as it only ',
                    'has contributions from either the RPA or DM, not both.'])
    inst.meta['partial'] = {inst.meta.labels.units: '',
                            inst.meta.labels.name: ''.join(['Partial ',
                                                            'Vector ',
                                                            'Flag']),
                            inst.meta.labels.desc: desc,
                            inst.meta.labels.fill_val: np.nan,
                            inst.meta.labels.min_val: False,
                            inst.meta.labels.max_val: True}

    return
