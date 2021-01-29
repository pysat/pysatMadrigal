#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Methods supporting the Defense Meteorological Satellite Program (DMSP)
platform

Functions
---------
add_drift_unit_vectors
    Add unit vectors for the satellite velocity
add_drifts_polar_cap_x_y
    Add polar cap drifts in cartesian coordinates
smooth_ram_drifts
    Smooth the ram drifts using a rolling mean
update_DMSP_ephemeris
    Updates DMSP instrument data with DMSP ephemeris

"""

import numpy as np
import pandas as pds

from pysat import logger


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

    inst[rpa_idx, rpa_vel_key] = inst[rpa_idx,
                                      rpa_vel_key].rolling(15, 5).mean()
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

    Note
    ----
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
