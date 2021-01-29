# -*- coding: utf-8 -*-.
"""Supports generalized access to Madrigal Data.

To use this routine, you need to know both the Madrigal Instrument code
as well as the data tag numbers that Madrigal uses to uniquely identify
data sets. Using these codes, the methods.madrigal.py routines will
be used to support downloading and loading of data.

Downloads data from the Madrigal Database.

Warnings
--------
All data downloaded under this general support is placed in the same directory,
pysat_data_dir/madrigal/pandas/. For technical reasons, the file search
algorithm for pysat's Madrigal support is set to permissive defaults. Thus, all
instrument files downloaded via this interface will be picked up by the madrigal
pandas pysat Instrument object unless the file_format keyword is used at
instantiation.

Files can be safely downloaded without knowing the file_format keyword,
or equivalently, how Madrigal names the files. See `Examples` for more.

Properties
----------
platform
    'madrigal'
name
    'pandas'
tag
    madrigal instrument code as an integer
inst_id
    madrigal kindat as a string

Examples
--------
::

    # for isolated use of a madrigal data set
    import pysat
    # download DMSP data from Madrigal
    dmsp = pysat.Instrument('madrigal', 'pandas', inst_code=8100,
                            kindat='10241')
    dmsp.download(dt.datetime(2017, 12, 30), dt.datetime(2017, 12, 31),
                  user='Firstname+Lastname', password='email@address.com')
    dmsp.load(2017, 363)

    # for users that plan on using multiple Madrigal datasets
    # using this general interface then an additional parameter
    # should be supplied upon instrument instantiation (file_format)

    # pysat needs information on how to parse filenames from Madrigal
    # for the particular instrument under study.
    # When starting from scratch (no files), this is a two step process.
    # First, get atleast one file from Madrigal, using the steps above
    # using the file downloaded. Using the filename, convert it to a template
    # string
    # and pass that to pysat when instantiating future Instruments.

    # For example, one of the files downloaded above is
    # dms_ut_19980101_11.002.hdf5
    # pysat needs a template for how to pull out the year, month, day, and,
    # if available, hour, minute, second, etc.
    # the format/template string for this instrument is
    # 'dms_ut_{year:4d}{month:02d}{day:02d}_12.002.hdf5', following
    # python standards for string templates/Formatters
    # https://docs.python.org/2/library/string.html

    # the complete instantiation for this instrument is
    file_fmt = 'dms_ut_{year:4d}{month:02d}{day:02d}_11.002.hdf5'
    dmsp = pysat.Instrument('madrigal', 'pandas', inst_code=8100,
                            kindat='10241', file_format=file_fmt)

Note
----
Please provide name and email when downloading data with this routine.

"""

import functools

from pysat.instruments.methods import general as ps_gen
from pysat import logger

from pysatMadrigal.instruments.methods import general

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'madrigal'
name = 'pandas'
tags = {'': 'General pysat Madrigal data access.'}
inst_ids = {'': list(tags.keys())}

pandas_format = True

# Local attributes
#
# Need a way to get the filename strings for a particular instrument unless
# wildcards start working
fname = '*{year:4d}{month:02d}{day:02d}*.{version:03d}.hdf5'
supported_tags = {ss: {tt: fname for tt in inst_ids[ss]}
                  for ss in inst_ids.keys()}
remote_tags = {ss: {kk: supported_tags[ss][kk].format(file_type='hdf5')
                    for kk in inst_ids[ss]} for ss in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument test attributes

# Need to sort out test day setting for unit testing, maybe through a remote
# function
# _test_dates = {'': {'': dt.datetime(2010, 1, 19)}}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initializes the Instrument object in support of Madrigal access

    Runs once upon instantiation.

    Parameters
    ----------
    self : pysat.Instrument
        This object

    """

    logger.info(general.cedar_rules())
    self.acknowledgements = general.cedar_rules()
    self.references = 'Please remember to cite the instrument articles.'

    self.inst_code = self.kwargs['inst_code']
    self.kindat = self.kwargs['kindat']

    return


def clean(self):
    """Placeholder routine that would normally return cleaned data

    Note
    ----
    Supports 'clean', 'dusty', 'dirty' in the sense that it prints
    a message noting there is no cleaning.
    'None' is also supported as it signifies no cleaning.

    Routine is called by pysat, and not by the end user directly.

    """

    if self.clean_level in ['clean', 'dusty', 'dirty']:
        logger.warning('Generalized Madrigal data support has no cleaning.')

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal and pysat methods

# Set the list_remote_files routine
# Need to fix this
# list_remote_files = functools.partial(general.list_remote_files,
#                                       inst_code=self.kwargs['inst_code'],
#                                       kindats=self.kwargs['kindat'],
#                                       supported_tags=remote_tags)

# Set the load routine
load = general.load

# Set the list routine
list_files = functools.partial(ps_gen.list_files,
                               supported_tags=supported_tags)

# Set up the download routine
# Needs to be fixed
# download = functools.partial(general.download,
#                             inst_code=str(self.kwargs['inst_code']),
#                             kindat=self.kwargs['kindat'])
