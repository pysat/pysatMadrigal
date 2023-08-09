#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-.
"""Supports access to Dst data archieved at Madrigal.

Properties
----------
platform
    'madrigal'
name
    'dst'
tag
    None supported
inst_id
    None supported

Note
----
Please provide name (user) and email (password) when downloading data with this
routine.

Warnings
--------
The entire data set (1 Jan 1597 through a period close to the recent day) is
provided in a single file on Madrigal.

Examples
--------
::


    import datetime as dt
    import pysat
    import pysatMadrigal as py_mad

    # Download Dst data from Madrigal
    dst = pysat.Instrument(inst_module=py_mad.instruments.madrigal_dst)
    dst.download(start=py_mad.instruments.madrigal_dst.madrigal_start,
                 user='Firstname+Lastname', password='email@address.com')
    dst.load(date=dt.datetime(1981, 1, 1))

"""

import datetime as dt
import functools

import pysat

from pysatMadrigal.instruments.methods import general

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'madrigal'
name = 'dst'
tags = {'': ''}
inst_ids = {'': list(tags.keys())}
pandas_format = True

# Madrigal tags and limits
madrigal_inst_code = 212
madrigal_tag = {'': {'': "30006"}}
madrigal_start = dt.datetime(1957, 1, 1)
madrigal_end = dt.datetime.utcnow()

# Local attributes
#
# Need a way to get the filename strings for a particular instrument unless
# wildcards start working
supported_tags = {
    inst_id: {tag: general.madrigal_file_format_str(madrigal_inst_code,
                                                    verbose=False)
              for tag in inst_ids[inst_id]} for inst_id in inst_ids.keys()}
remote_tags = {ss: {kk: supported_tags[ss][kk].format(file_type='hdf5')
                    for kk in inst_ids[ss]} for ss in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument test attributes

_test_dates = {inst_id: {tag: madrigal_start for tag in inst_ids[inst_id]}
               for inst_id in inst_ids.keys()}
_test_download = {inst_id: {tag: True for tag in inst_ids[inst_id]}
                  for inst_id in inst_ids.keys()}
_clean_warn = {inst_id: {tag: {clvl: [('logger', 'WARN',
                                       "No cleaning available", clvl)]
                               for clvl in ['clean', 'dusty', 'dirty']}
                         for tag in inst_ids[inst_id]}
               for inst_id in inst_ids.keys()}

# ----------------------------------------------------------------------------
# Instrument methods


def init(self):
    """Initialize the Instrument object in support of Madrigal access.

    Parameters
    ----------
    kindat : str
        Madrigal instrument experiment code(s). (default='')

    """
    # Set the standard pysat attributes
    self.acknowledgements = general.cedar_rules()
    self.references = ''.join(['See referenece list and publication at: ',
                               'Sugiura M. and T. Kamei, http://',
                               'wdc.kugi.kyoto-u.ac.jp/dstdir/dst2/',
                               'onDstindex.html, last updated June 1991, ',
                               'accessed Dec 2020'])

    # Remind the user of the Rules of the Road
    pysat.logger.info(self.acknowledgements)
    return


def clean(self):
    """Raise warning that cleaning is not needed for the OMNI2 data.

    Note
    ----
    Supports 'clean', 'dusty', 'dirty' in the sense that it prints
    a message noting there is no cleaning.
    'None' is also supported as it signifies no cleaning.

    Routine is called by pysat, and not by the end user directly.

    """
    pysat.logger.warning("No cleaning available for the Madrigal Dst")

    return


# ----------------------------------------------------------------------------
# Instrument functions
#
# Use the default Madrigal and pysat methods
file_cadence = madrigal_end - madrigal_start
two_digit_year_break = 50

# Set the download routine
download = functools.partial(general.download,
                             inst_code=str(madrigal_inst_code),
                             kindat=madrigal_tag[''][''])

# Set the list routine
list_files = functools.partial(general.list_files,
                               supported_tags=supported_tags,
                               file_cadence=file_cadence,
                               two_digit_year_break=two_digit_year_break)

# Set list_remote_files routine
list_remote_files = functools.partial(general.list_remote_files,
                                      supported_tags=remote_tags,
                                      inst_code=madrigal_inst_code,
                                      kindats=madrigal_tag,
                                      two_digit_year_break=two_digit_year_break)


def load(fnames, tag='', inst_id=''):
    """Load the Madrigal Dst data.

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
    data : pds.DataFrame
        Object containing IMF data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Raises
    ------
    ValueError
        Unexpected time variable names

    """
    # Cycle through all the filenames, getting the desired start and stop times
    fstart = None
    fstop = None
    for fname_date in fnames:
        # Split the date from the filename
        fname = fname_date[:-11]
        fdate = dt.datetime.strptime(fname_date[-10:], '%Y-%m-%d')
        fstop = fdate

        if fstart is None:
            fstart = fdate

    fstop += dt.timedelta(days=1)

    # There is only one file for this Instrument
    data, meta = general.load([fname], tag=tag, inst_id=inst_id)

    # Select the data for the desired time period
    data = data[fstart:fstop]

    return data, meta
