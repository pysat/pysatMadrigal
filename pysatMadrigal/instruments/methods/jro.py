#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Methods supporting the Jicamarca Radio Observatory (JRO) platform
"""

import numpy as np

from pysat import logger

from pysatMadrigal.utils import coords


def acknowledgements():
    """Provides acknowlegements for the JRO instruments and experiments

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
    """Provides references for the JRO instruments and experiments

    Returns
    -------
    refs : str
        String providing reference guidenance for the JRO experiments

    """

    refs = "Depends on the radar experiment; contact PI"
    return refs


def calc_measurement_loc(inst):
    """ Calculate the instrument measurement location in geographic coordinates

    Parameters
    ----------
    inst : pysat.Instrument
        JRO ISR Instrument object

    Note
    ----
    Adds 'gdlat#', 'gdlon#' to the instrument, for all directions that
    have azimuth and elevation keys that match the format 'eldir#' and 'azdir#'

    """

    az_keys = [kk[5:] for kk in list(inst.data.keys())
               if kk.find('azdir') == 0]
    el_keys = [kk[5:] for kk in list(inst.data.keys())
               if kk.find('eldir') == 0]
    good_dir = list()

    for i, kk in enumerate(az_keys):
        if kk in el_keys:
            try:
                good_dir.append(int(kk))
            except ValueError:
                logger.warning("unknown direction number [{:}]".format(kk))

    # Calculate the geodetic latitude and longitude for each direction
    if len(good_dir) == 0:
        raise ValueError("No matching azimuth and elevation data included")

    for dd in good_dir:
        # Format the direction location keys
        az_key = 'azdir{:d}'.format(dd)
        el_key = 'eldir{:d}'.format(dd)
        lat_key = 'gdlat{:d}'.format(dd)
        lon_key = 'gdlon{:d}'.format(dd)
        # JRO is located 520 m above sea level (jro.igp.gob.pe./english/)
        # Also, altitude has already been calculated
        gdaltr = np.ones(shape=inst['gdlonr'].shape) * 0.52
        gdlat, gdlon, _ = coords.local_horizontal_to_global_geo(inst[az_key],
                                                                inst[el_key],
                                                                inst['range'],
                                                                inst['gdlatr'],
                                                                inst['gdlonr'],
                                                                gdaltr,
                                                                geodetic=True)

        # Assigning as data, to ensure that the number of coordinates match
        # the number of data dimensions
        inst.data = inst.data.assign({lat_key: gdlat, lon_key: gdlon})

        # Add metadata for the new data values
        bm_label = "Beam {:d} ".format(dd)
        inst.meta[lat_key] = {inst.meta.labels.units: 'degrees',
                              inst.meta.labels.name: bm_label + 'latitude',
                              inst.meta.labels.desc: bm_label + 'latitude',
                              inst.meta.labels.min_val: -90.0,
                              inst.meta.labels.max_val: 90.0,
                              inst.meta.labels.fill_val: np.nan}
        inst.meta[lon_key] = {inst.meta.labels.units: 'degrees',
                              inst.meta.labels.name: bm_label + 'longitude',
                              inst.meta.labels.desc: bm_label + 'longitude',
                              inst.meta.labels.fill_val: np.nan}

    return
