# -*- coding: utf-8 -*-.
"""Supports the Incoherent Scatter Radar at the Jicamarca Radio Observatory

The Incoherent Scatter Radar (ISR) at the Jicamarca Radio Observatory (JRO)
observes ion drifts, line-of-sight neutral winds, electron density and
temperature, ion temperature, and ion composition through three overarching
experiments.

Downloads data from the JRO Madrigal Database.

Properties
----------
platform
    'jro'
name
    'isr'
tag
    'drifts', 'drifts_ave', 'oblique_stan', 'oblique_rand', 'oblique_long'

Examples
--------
::

    import pysat
    jro = pysat.Instrument('jro', 'isr', 'drifts', clean_level='clean')
    jro.download(pysat.datetime(2017, 12, 30), pysat.datetime(2017, 12, 31),
                 user='Firstname+Lastname', password='email@address.com')
    jro.load(2017, 363)


Note
----
    Please provide name and email when downloading data with this routine.

"""

from __future__ import print_function
from __future__ import absolute_import
import datetime as dt
import functools
import logging
import numpy as np

from pysat.instruments.methods import general as ps_gen

from pysatMadrigal.instruments.methods import madrigal as mad_meth
from pysatMadrigal.utils import coords

logger = logging.getLogger(__name__)


platform = 'jro'
name = 'isr'
tags = {'drifts': 'Drifts and wind', 'drifts_ave': 'Averaged drifts',
        'oblique_stan': 'Standard Faraday rotation double-pulse',
        'oblique_rand': 'Randomized Faraday rotation double-pulse',
        'oblique_long': 'Long pulse Faraday rotation'}
inst_ids = {'': list(tags.keys())}
_test_dates = {'': {'drifts': dt.datetime(2010, 1, 19),
                    'drifts_ave': dt.datetime(2010, 1, 19),
                    'oblique_stan': dt.datetime(2010, 4, 19),
                    'oblique_rand': dt.datetime(2000, 11, 9),
                    'oblique_long': dt.datetime(2010, 4, 12)}}
pandas_format = False

# support list files routine
# use the default CDAWeb method
jro_fname1 = 'jro{{year:4d}}{{month:02d}}{{day:02d}}'
jro_fname2 = '.{{version:03d}}.{file_type}'
supported_tags = {ss: {'drifts': jro_fname1 + "drifts" + jro_fname2,
                       'drifts_ave': jro_fname1 + "drifts_avg" + jro_fname2,
                       'oblique_stan': jro_fname1 + jro_fname2,
                       'oblique_rand': jro_fname1 + "?" + jro_fname2,
                       'oblique_long': jro_fname1 + "?" + jro_fname2}
                  for ss in inst_ids.keys()}

# madrigal tags
madrigal_inst_code = 10
madrigal_tag = {'': {'drifts': 1910, 'drifts_ave': 1911, 'oblique_stan': 1800,
                     'oblique_rand': 1801, 'oblique_long': 1802}, }

# support listing files currently available on remote server (Madrigal)
list_remote_files = functools.partial(mad_meth.list_remote_files,
                                      supported_tags=supported_tags,
                                      inst_code=madrigal_inst_code)

# Madrigal will sometimes include multiple days within a file
# labeled with a single date.
# Filter out this extra data using the pysat nanokernel processing queue.
# To ensure this function is always applied first, we set the filter
# function as the default function for (JRO).
# Default function is run first by the nanokernel on every load call.
default = mad_meth.filter_data_single_date


def init(self):
    """Initializes the Instrument object with values specific to JRO ISR

    Runs once upon instantiation.

    Parameters
    ----------
    self : pysat.Instrument
        This object

    """

    ackn_str = ' '.join(["The Jicamarca Radio Observatory is a facility of",
                         "the Instituto Geofisico del Peru operated",
                         "with support from the NSF AGS-1433968",
                         "through Cornell University.\n",
                         mad_meth.cedar_rules()])

    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = "?"

    return


def list_files(tag=None, inst_id=None, data_path=None, format_str=None,
               supported_tags=supported_tags,
               fake_daily_files_from_monthly=False,
               delimiter=None, file_type=''):
    """Return a Pandas Series of every data file for this Instrument

    
    Parameters
    -----------
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
    --------
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
        File format for Madrigal data.  Currently only accept 'netcdf4' and
        'hdf5'. (default='hdf5')

    Notes
    -----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    mad_meth.download(date_array, inst_code=str(madrigal_inst_code),
                      kindat=str(madrigal_tag[inst_id][tag]),
                      data_path=data_path, user=user, password=password,
                      file_type=file_type)


def load(fnames, tag=None, inst_id=None, file_type='hdf5'):
    """ Routine to load the JRO ISR data

    Parameters
    -----------
    fnames : list
        List of filenames
    tag : string or NoneType
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)
    inst_id : string or NoneType
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default=None)
    file_type : string
        File format for Madrigal data.  Currently only accept 'netcdf4' and
        'hdf5'. (default='hdf5')

    Returns
    --------
    data : xarray.Dataset
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    """
    # Define the xarray coordinate dimensions (apart from time)
    xcoords = {'drifts': {('time', 'gdalt', 'gdlatr', 'gdlonr', 'kindat',
                           'kinst'): ['nwlos', 'range', 'vipn2', 'dvipn2',
                                      'vipe1', 'dvipe1', 'vi72', 'dvi72',
                                      'vi82', 'dvi82', 'paiwl', 'pacwl',
                                      'pbiwl', 'pbcwl', 'pciel', 'pccel',
                                      'pdiel', 'pdcel', 'jro10', 'jro11'],
                          ('time', ): ['year', 'month', 'day', 'hour', 'min',
                                       'sec', 'spcst', 'pl', 'cbadn', 'inttms',
                                       'azdir7', 'eldir7', 'azdir8', 'eldir8',
                                       'jro14', 'jro15', 'jro16', 'ut1_unix',
                                       'ut2_unix', 'recno']},
               'drifts_ave': {('time', 'gdalt', 'gdlatr', 'gdlonr', 'kindat',
                               'kinst'): ['altav', 'range', 'vipn2', 'dvipn2',
                                          'vipe1', 'dvipe1'],
                              ('time', ): ['year', 'month', 'day', 'hour',
                                           'min', 'sec', 'spcst', 'pl',
                                           'cbadn', 'inttms', 'ut1_unix',
                                           'ut2_unix', 'recno']},
               'oblique_stan': {('time', 'gdalt', 'gdlatr', 'gdlonr', 'kindat',
                                 'kinst'): ['rgate', 'ne', 'dne', 'te', 'dte',
                                            'ti', 'dti', 'ph+', 'dph+', 'phe+',
                                            'dphe+'],
                                ('time', ): ['year', 'month', 'day', 'hour',
                                             'min', 'sec', 'azm', 'elm',
                                             'pl', 'inttms', 'tfreq',
                                             'ut1_unix', 'ut2_unix', 'recno']},
               'oblique_rand': {('time', 'gdalt', 'gdlatr', 'gdlonr', 'kindat',
                                 'kinst'): ['rgate', 'pop', 'dpop', 'te', 'dte',
                                            'ti', 'dti', 'ph+', 'dph+', 'phe+',
                                            'dphe+'],
                                ('time', ): ['year', 'month', 'day', 'hour',
                                             'min', 'sec', 'azm', 'elm',
                                             'pl', 'inttms', 'tfreq',
                                             'ut1_unix', 'ut2_unix', 'recno']},
               'oblique_long': {('time', 'gdalt', 'gdlatr', 'gdlonr', 'kindat',
                                 'kinst'): ['rgate', 'pop', 'dpop', 'te', 'dte',
                                            'ti', 'dti', 'ph+', 'dph+', 'phe+',
                                            'dphe+'],
                                ('time', ): ['year', 'month', 'day', 'hour',
                                             'min', 'sec', 'azm', 'elm',
                                             'pl', 'inttms', 'tfreq',
                                             'ut1_unix', 'ut2_unix', 'recno']}}

    # Load the specified data
    data, meta = mad_meth.load(fnames, tag, inst_id,
                               xarray_coords=xcoords[tag],
                               file_type=file_type)

    # Squeeze the kindat and kinst 'coordinates', but keep them as floats
    data = data.squeeze(dim=['kindat', 'kinst', 'gdlatr', 'gdlonr'])

    return data, meta


def clean(self):
    """Routine to return JRO ISR data cleaned to the specified level

    Notes
    --------
    Supports 'clean'
    'clean' is unknown for oblique modes, over 200 km for drifts
    'dusty' is the same as clean
    'Dirty' is the same as clean
    'None' None

    Routine is called by pysat, and not by the end user directly.

    """

    # Default to selecting all of the data
    idx = {'gdalt': [i for i in range(self.data.indexes['gdalt'].shape[0])]}

    if self.tag.find('oblique') == 0:
        # Oblique profile cleaning
        logger.info(' '.join(['The double pulse, coded pulse, and long pulse',
                              'modes implemented at Jicamarca have different',
                              'limitations arising from different degrees of',
                              'precision and accuracy. Users should consult',
                              'with the staff to determine which mode is',
                              'right for their application.']))

        if self.clean_level in ['clean', 'dusty', 'dirty']:
            logger.warning('this level 2 data has no quality flags')
    else:
        # Ion drift cleaning
        if self.clean_level in ['clean', 'dusty', 'dirty']:
            if self.clean_level in ['clean', 'dusty']:
                logger.warning('this level 2 data has no quality flags')

            ida, = np.where((self.data.indexes['gdalt'] > 200.0))
            idx['gdalt'] = np.unique(ida)
        else:
            logger.warning(' '.join(["interpretation of drifts below 200 km",
                                     "should always be done in partnership",
                                     "with the contact people"]))

    # downselect data based upon cleaning conditions above
    self.data = self[idx]

    return


def calc_measurement_loc(self):
    """ Calculate the instrument measurement location in geographic coordinates

    Returns
    -------
    Void : adds 'gdlat#', 'gdlon#' to the instrument, for all directions that
    have azimuth and elevation keys that match the format 'eldir#' and 'azdir#'

    """

    az_keys = [kk[5:] for kk in list(self.data.keys())
               if kk.find('azdir') == 0]
    el_keys = [kk[5:] for kk in list(self.data.keys())
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
        gdaltr = np.ones(shape=self['gdlonr'].shape) * 0.52
        gdlat, gdlon, _ = coords.local_horizontal_to_global_geo(self[az_key],
                                                                self[el_key],
                                                                self['range'],
                                                                self['gdlatr'],
                                                                self['gdlonr'],
                                                                gdaltr,
                                                                geodetic=True)

        # Assigning as data, to ensure that the number of coordinates match
        # the number of data dimensions
        self.data = self.data.assign({lat_key: gdlat, lon_key: gdlon})

        # Add metadata for the new data values
        bm_label = "Beam {:d} ".format(dd)
        self.meta[lat_key] = {self.meta.units_label: 'degrees',
                              self.meta.name_label: bm_label + 'latitude',
                              self.meta.desc_label: bm_label + 'latitude',
                              self.meta.plot_label: bm_label + 'Latitude',
                              self.meta.axis_label: bm_label + 'Latitude',
                              self.meta.scale_label: 'linear',
                              self.meta.min_label: -90.0,
                              self.meta.max_label: 90.0,
                              self.meta.fill_label: np.nan}
        self.meta[lon_key] = {self.meta.units_label: 'degrees',
                              self.meta.name_label: bm_label + 'longitude',
                              self.meta.desc_label: bm_label + 'longitude',
                              self.meta.plot_label: bm_label + 'Longitude',
                              self.meta.axis_label: bm_label + 'Longitude',
                              self.meta.scale_label: 'linear',
                              self.meta.fill_label: np.nan}

    return
