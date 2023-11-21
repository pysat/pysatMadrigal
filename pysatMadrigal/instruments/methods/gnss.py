#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""Methods supporting the Global Navigation Satellite System platform."""

import datetime as dt
import h5py
import numpy as np
import pandas as pds

import pysat

from pysatMadrigal.instruments.methods import general


def acknowledgements(name):
    """Provide the acknowledgements for different GNSS instruments.

    Parameters
    ----------
    name : str
        Instrument name

    Returns
    -------
    ackn : str
        Acknowledgement information to provide in studies using this data

    """
    ackn = {'tec': ''.join(["GPS TEC data products and access through the ",
                            "Madrigal distributed data system are provided to ",
                            "the community by the Massachusetts Institute of ",
                            "Technology under support from U.S. National ",
                            "Science Foundation grant AGS-1242204. Data for ",
                            "the TEC processing is provided by the following ",
                            "organizations: UNAVCO, Scripps Orbit and ",
                            "Permanent Array Center, Institut Geographique ",
                            "National, France, International GNSS Service, The",
                            " Crustal Dynamics Data Information System ",
                            "(CDDIS), National Geodetic Survey, Instituto ",
                            "Brasileiro de Geografiae Estatística, RAMSAC ",
                            "CORS of Instituto Geográfico Nacional del la ",
                            "República Agentina, Arecibo Observatory, ",
                            "Low-Latitude Ionospheric Sensor Network (LISN), ",
                            "Topcon Positioning Systems, Inc., Canadian High ",
                            "Arctic Ionospheric Network, Institute of Geology",
                            " and Geophysics, Chinese Academy of Sciences, ",
                            "China Meterorology Administration, Centro di ",
                            "Niveau des Eaux Littorales Ricerche Sismogiche, ",
                            "Système d’Observation du  (SONEL), RENAG : ",
                            "REseau NAtional GPS permanent, and GeoNet—the ",
                            "official source of geological hazard information ",
                            "for New Zealand."])}

    return ackn[name]


def references(name):
    """Provide suggested references for the specified data set.

    Parameters
    ----------
    name : str
        Instrument name

    Returns
    -------
    refs : str
        Suggested Instrument reference(s)

    """
    refs = {'tec': "\n".join([
        "Rideout and Coster (2006) doi:10.1007/s10291-006-0029-5",
        "Vierinen et al., (2016) doi:10.5194/amt-9-1303-2016"])}

    return refs[name]


def load_vtec(fnames):
    """Load the GNSS vertical TEC data.

    Parameters
    ----------
    fnames : list
        List of filenames

    Returns
    -------
    data : xarray.Dataset
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units
    lat_key : list
        Latitude key names
    lon_key : list
        Longitude key names

    """
    # Define the xarray coordinate dimensions and lat/lon keys
    xcoords = {('time', 'gdlat', 'glon', 'kindat', 'kinst'):
               ['gdalt', 'tec', 'dtec'],
               ('time', ): ['year', 'month', 'day', 'hour', 'min',
                            'sec', 'ut1_unix', 'ut2_unix', 'recno']}
    lat_keys = ['gdlat']
    lon_keys = ['glon']

    # Load the specified data
    data, meta = general.load(fnames, 'vtec', '', xarray_coords=xcoords)

    # Fix the units for tec and dtec
    meta['tec'] = {meta.labels.units: 'TECU', meta.labels.min_val: 0.0,
                   meta.labels.max_val: np.nan}
    meta['dtec'] = {meta.labels.units: 'TECU', meta.labels.min_val: 0.0,
                    meta.labels.max_val: np.nan}

    # Get the maximum and minimum values for altiutde, along with lat/lon keys
    meta['gdalt'] = {meta.labels.min_val: 0.0, meta.labels.max_val: np.nan}

    return data, meta, lat_keys, lon_keys


def load_site(fnames):
    """Load the GNSS TEC site data.

    Parameters
    ----------
    fnames : list
        List of filenames

    Returns
    -------
    data : xarray.Dataset
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units
    lat_keys : list
        Latitude key names
    lon_keys : list
        Longitude key names

    """
    # Define the xarray coordinate dimensions and lat/lon keys
    xcoords = {('time', 'gps_site'): ['gdlatr', 'gdlonr']}
    lat_keys = ['gdlatr']
    lon_keys = ['gdlonr']

    # Load the specified data
    data, meta = general.load(fnames, 'site', '', xarray_coords=xcoords)

    return data, meta, lat_keys, lon_keys


def load_los(fnames, los_method, los_value, gnss_network='all'):
    """Load the GNSS slant TEC data.

    Parameters
    ----------
    fnames : list
        List of filenames
    los_method : str
        For 'los' tag only, load data for a unique GNSS receiver site ('site')
        or at a unique time ('time')
    los_value : str or dt.datetime
        For 'los' tag only, load data at this unique site or time
    gnss_network : bool
        Limit data by GNSS network, if not 'all'.  Currently supports 'all',
        'gps', and 'glonass' (default='all')

    Returns
    -------
    data : xarray.Dataset
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units
    lat_keys : list
        Latitude key names
    lon_keys : list
        Longitude key names

    """
    # Define the xarray coordinate dimensions and lat/lon keys
    xcoords = {('time', 'gps_site', 'sat_id', 'kindat', 'kinst'):
               ['pierce_alt', 'los_tec', 'dlos_tec', 'tec', 'azm', 'elm',
                'gdlat', 'glon', 'rec_bias', 'drec_bias'],
               ('time', ): ['year', 'month', 'day', 'hour', 'min',
                            'sec', 'ut1_unix', 'ut2_unix', 'recno'],
               ('time', 'sat_id', ): ['gnss_type'],
               ('time', 'gps_site', ): ['gdlatr', 'gdlonr']}
    lat_keys = ['gdlatr', 'gdlat']
    lon_keys = ['gdlonr', 'glon']

    # Sort and test the desired filenames by file format
    load_file_types = general.sort_file_formats(fnames)

    for ftype in load_file_types.keys():
        if ftype != 'hdf5' and len(load_file_types[ftype]) > 0:
            pysat.logger.warning(
                'unable to load non-HDF5 slant TEC files: {:}'.format(
                    load_file_types[ftype]))

    # Initalize the meta data
    meta = pysat.Meta()

    # Load the data using the desired method
    if los_method.lower() == 'site':
        sel_key = 'gps_site'

        # Convert the site to bytes
        los_value = np.bytes_(los_value)
    elif los_method.lower() == 'time':
        sel_key = 'ut1_unix'

        # Convert the input datetime to UNIX seconds
        los_value = (los_value - dt.datetime(1970, 1, 1)).total_seconds()
    else:
        raise ValueError('unsupported selection type: {:}'.format(los_method))

    # Load the data by desired method
    data = list()
    labels = list()
    for fname in load_file_types['hdf5']:
        with h5py.File(fname, 'r') as fin:
            sel_arr = fin['Data']['Table Layout'][sel_key]
            sel_mask = sel_arr == los_value

            if gnss_network.lower() != 'all':
                # Redefine the selection mask to include network as well
                gnss_val = '{:8s}'.format(gnss_network.upper())
                try:
                    net_arr = fin['Data']['Table Layout']['gnss_type'][sel_mask]
                    sel_mask[sel_mask] = net_arr.astype(str) == gnss_val
                except ValueError:
                    # If the 'gnss_type' is not available, all data is GPS
                    if gnss_network.lower() != 'gps':
                        sel_mask[sel_mask] = False

            # Save the output for the desired slice
            if sel_mask.any():
                data.extend(list(fin['Data']['Table Layout'][sel_mask]))

                # Save the meta data
                labels = general.update_meta_with_hdf5(fin, meta)

        # If this is time selection, only need to load from one file
        if len(data) > 0:
            break

    # Load data into frame, with labels from metadata
    data = pds.DataFrame.from_records(data, columns=labels)

    if not data.empty:
        # Enforce lowercase variable names
        data.columns = [item.lower() for item in data.columns]

        # Convert the data to an xarray Dataset
        time_ind = general.build_madrigal_datetime_index(data)
    else:
        time_ind = None

        # Convert the output to xarray
        data = general.convert_pandas_to_xarray(xcoords, data, time_ind)

    return data, meta, lat_keys, lon_keys


def get_los_receiver_sites(los_fnames):
    """Retrieve an array of unique receiver names for the desired LoS files.

    Parameters
    ----------
    los_fnames : list
        List of filenames

    Returns
    -------
    sites : np.array
        Array of strings containing GNSS receiver names with data in the files

    """
    los_fnames = pysat.utils.listify(los_fnames)
    sites = list()

    # Get all of the potential sites
    for fname in los_fnames:
        with h5py.File(fname, 'r') as fin:
            site_arr = fin['Data']['Table Layout']['gps_site']
            sites.extend(list(site_arr.astype(str)))

    # Find the unique sites
    sites = np.unique(sites)
    return sites


def get_los_times(los_fnames):
    """Retrieve an array of unique times for the desired LoS files.

    Parameters
    ----------
    los_fnames : list
        List of filenames

    Returns
    -------
    all_times : np.array
        Array of datetime objects with data in the files

    """
    los_fnames = pysat.utils.listify(los_fnames)
    all_times = list()

    # Get all of the potential sites
    for fname in los_fnames:
        with h5py.File(fname, 'r') as fin:
            time_arr = fin['Data']['Table Layout']['ut1_unix']

            # Convert from unix time to a datetime object
            all_times.extend([dt.datetime(1970, 1, 1)
                              + dt.timedelta(seconds=int(time_val))
                              for time_val in time_arr])

    return all_times
