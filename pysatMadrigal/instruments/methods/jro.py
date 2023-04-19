#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Methods supporting the Jicamarca Radio Observatory (JRO) platform."""

import numpy as np

from pysat import logger

from pysatMadrigal.utils import coords


def acknowledgements():
    """Provide acknowlegements for the JRO instruments and experiments.

    Returns
    -------
    ackn : str
        String providing acknowledgement text for studies using JRO data

    """
    ackn = ' '.join(["The Jicamarca Radio Observatory is a facility of the",
                     "Instituto Geofisico del Peru operated with support from",
                     "the NSF AGS-1433968 through Cornell University."])

    return ackn


def references():
    """Provide references for the JRO instruments and experiments.

    Returns
    -------
    refs : str
        String providing reference guidenance for the JRO experiments

    """
    refs = "Depends on the radar experiment; contact PI"
    return refs


def calc_measurement_loc(inst):
    """Calculate the instrument measurement location in geographic coordinates.

    Parameters
    ----------
    inst : pysat.Instrument
        JRO ISR Instrument object

    Raises
    ------
    ValueError
        If no appropriate azimuth and elevation angles are found, if no range
        variable is found, or if multiple range variables are found.


    Note
    ----
    Adds 'gdlat#', 'gdlon#' to the instrument, for all directions that
    have azimuth and elevation keys that match the format 'eldir#' and 'azdir#'
    or 'azm' and 'elm' (in this case # will be replaced with '_bm')

    """
    good_dir = list()
    good_pre = list()

    # Assume the 'dir#' format is used
    az_keys = [kk[5:] for kk in inst.variables if kk.find('azdir') == 0]
    el_keys = [kk[5:] for kk in inst.variables if kk.find('eldir') == 0]

    for i, kk in enumerate(az_keys):
        if kk in el_keys:
            try:
                good_dir.append("{:d}".format(int(kk)))
                good_pre.append('dir{:s}'.format(kk))
            except ValueError:
                logger.warning("Unknown direction number [{:}]".format(kk))

    # Assume the 'm' format is used
    if 'azm' in inst.variables and 'elm' in inst.variables:
        good_dir.append('_bm')
        good_pre.append('m')

    # Test the success of finding the azimuths and elevations
    if len(good_dir) == 0:
        raise ValueError("No matching azimuth and elevation data included")

    # Set common meta data variables. Includes determining the longitude range,
    # which is only possible because JRO is in the western hemisphere.
    lon_min = 0.0 if inst['gdlonr'] > 0.0 else -180.0
    lon_max = 360.0 + lon_min
    notes = 'Calculated using {:s}'.format(__name__)

    # Get the range key
    range_data = None
    for rkey in ['range', 'rgate']:
        if rkey in inst.variables:
            if range_data is None:
                if rkey == 'rgate':
                    range_data = inst['gdalt']
                else:
                    range_data = inst[rkey]
            else:
                raise ValueError('Multiple range variables found')

    if range_data is None:
        raise ValueError('No range variable found')

    # Calculate the geodetic latitude and longitude for each direction
    for i, dd in enumerate(good_dir):
        # Format the direction location keys
        az_key = 'az{:s}'.format(good_pre[i])
        el_key = 'el{:s}'.format(good_pre[i])
        lat_key = 'gdlat{:s}'.format(dd)
        lon_key = 'gdlon{:s}'.format(dd)

        # JRO is located 520 m above sea level (jro.igp.gob.pe./english/)
        # Also, altitude has already been calculated
        gdaltr = np.ones(shape=inst['gdlonr'].shape) * 0.52
        gdlat, gdlon, _ = coords.local_horizontal_to_global_geo(inst[az_key],
                                                                inst[el_key],
                                                                range_data,
                                                                inst['gdlatr'],
                                                                inst['gdlonr'],
                                                                gdaltr,
                                                                geodetic=True)

        # Assigning as data, to ensure that the number of coordinates match
        # the number of data dimensions
        inst.data = inst.data.assign({lat_key: gdlat, lon_key: gdlon})

        # Add metadata for the new data values
        bm_label = "Beam" if dd[0] == "_" else "Beam {:s} ".format(dd)
        inst.meta[lat_key] = {inst.meta.labels.units: 'degrees',
                              inst.meta.labels.name: bm_label + 'latitude',
                              inst.meta.labels.notes: notes,
                              inst.meta.labels.desc: bm_label + 'latitude',
                              inst.meta.labels.min_val: -90.0,
                              inst.meta.labels.max_val: 90.0,
                              inst.meta.labels.fill_val: np.nan}
        inst.meta[lon_key] = {inst.meta.labels.units: 'degrees',
                              inst.meta.labels.notes: notes,
                              inst.meta.labels.name: bm_label + 'longitude',
                              inst.meta.labels.desc: bm_label + 'longitude',
                              inst.meta.labels.min_val: lon_min,
                              inst.meta.labels.max_val: lon_max,
                              inst.meta.labels.fill_val: np.nan}

    return
