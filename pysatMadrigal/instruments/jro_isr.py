#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-.
"""Supports the Incoherent Scatter Radar at the Jicamarca Radio Observatory.

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
The Incoherent Scatter Radar (ISR) at the Jicamarca Radio Observatory (JRO)
observes ion drifts, line-of-sight neutral winds, electron density and
temperature, ion temperature, and ion composition through three overarching
experiments.

Downloads data from the JRO Madrigal Database.

Please provide name (user) and email (password) when downloading data with this
routine.

"""

import datetime as dt
import functools
import numpy as np

from pysat import logger

from pysatMadrigal.instruments.methods import general
from pysatMadrigal.instruments.methods import jro

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'jro'
name = 'isr'
tags = {'drifts': 'Drifts and wind', 'drifts_ave': 'Averaged drifts',
        'oblique_stan': 'Standard Faraday rotation double-pulse',
        'oblique_rand': 'Randomized Faraday rotation double-pulse',
        'oblique_long': 'Long pulse Faraday rotation'}
inst_ids = {'': list(tags.keys())}

pandas_format = False

# Madrigal tags
madrigal_inst_code = 10
madrigal_tag = {'': {'drifts': "1910", 'drifts_ave': "1911",
                     'oblique_stan': "1800", 'oblique_rand': "1801",
                     'oblique_long': "1802"}, }

# Local attributes
jro_fname = general.madrigal_file_format_str(madrigal_inst_code, verbose=False)
supported_tags = {ss: {'drifts': jro_fname.replace("*", "drifts"),
                       'drifts_ave': jro_fname.replace("*", "drifts_avg"),
                       'oblique_stan': jro_fname.replace("*", ""),
                       'oblique_rand': jro_fname.replace("*", "?"),
                       'oblique_long': jro_fname.replace("*", "?")}
                  for ss in inst_ids.keys()}
remote_tags = {ss: {kk: supported_tags[ss][kk].format(file_type='hdf5')
                    for kk in inst_ids[ss]} for ss in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {'': {'drifts': dt.datetime(2010, 1, 19),
                    'drifts_ave': dt.datetime(2010, 1, 19),
                    'oblique_stan': dt.datetime(2010, 4, 19),
                    'oblique_rand': dt.datetime(2000, 11, 9),
                    'oblique_long': dt.datetime(2010, 4, 12)}}


# ----------------------------------------------------------------------------
# Instrument methods

def init(self):
    """Initialize the Instrument object with values specific to JRO ISR."""
    ackn_str = '\n'.join([jro.acknowledgements(), general.cedar_rules()])

    logger.info(ackn_str)
    self.acknowledgements = ackn_str
    self.references = jro.references()

    return


def clean(self):
    """Clean the JRO ISR data cleaned to the specified level.

    Note
    ----
    Supports 'clean'
    'clean' is unknown for oblique modes, over 200 km for drifts
    'dusty' is the same as clean
    'Dirty' is the same as clean

    When called by pysat, a clean level of None will skip this routine.

    """
    # Default to selecting all of the data
    iclean = {'gdalt': [i for i in range(self.data.indexes['gdalt'].shape[0])]}

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

            idalt, = np.where((self.data.indexes['gdalt'] > 200.0))
            iclean['gdalt'] = np.unique(idalt)

    # Downselect data based upon cleaning conditions above
    self.data = self[iclean]

    return


def preprocess(self):
    """Preprocess data to default loaded data to a single day."""
    # Madrigal will sometimes include multiple days within a file
    # labeled with a single date. This routine filters out this extra data
    # using the pysat nanokernel processing queue.
    general.filter_data_single_date(self)

    # Warn the user about low altitude drifts if no cleaning is being performed
    if self.clean_level == 'none' or self.clean_level is None:
        logger.warning(' '.join(["interpretation of drifts below 200 km",
                                 "should always be done in partnership",
                                 "with the contact people"]))
    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal and pysat methods

# Support listing the local files
list_files = functools.partial(general.list_files,
                               supported_tags=supported_tags)

# Set list_remote_files routine
list_remote_files = functools.partial(general.list_remote_files,
                                      supported_tags=remote_tags,
                                      inst_code=madrigal_inst_code,
                                      kindats=madrigal_tag)


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
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : str
        Password for data download. (default=None)
    file_type : str
        File format for Madrigal data. (default='hdf5')

    Notes
    -----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as "Ruby Payne-Scott"

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    general.download(date_array, inst_code=str(madrigal_inst_code),
                     kindat=madrigal_tag[inst_id][tag], data_path=data_path,
                     user=user, password=password, file_type=file_type)
    return


def load(fnames, tag='', inst_id=''):
    """Load the JRO ISR data.

    Parameters
    -----------
    fnames : list
        List of filenames
    tag : str
        tag name used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself. (default='')

    Returns
    --------
    data : xarray.Dataset
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    """
    # Define the xarray coordinate dimensions (apart from time)
    xcoords = {'drifts': {('time', 'gdalt', 'gdlatr', 'gdlonr', 'kindat',
                           'kinst'): ['nwlos', 'range', 'vipn', 'dvipn', 'vipe',
                                      'dvipe', 'vipn2', 'dvipn2',
                                      'vipe1', 'dvipe1', 'vi72', 'dvi72',
                                      'vi82', 'dvi82', 'vi7', 'dvi7', 'vi8',
                                      'dvi8', 'paiwl', 'pacwl', 'pbiwl',
                                      'pbcwl', 'pciel', 'pccel',
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
    data, meta = general.load(fnames, tag, inst_id, xarray_coords=xcoords[tag])

    # Squeeze the kindat and kinst 'coordinates', but keep them as floats
    data = data.squeeze(dim=['kindat', 'kinst', 'gdlatr', 'gdlonr'])

    return data, meta
