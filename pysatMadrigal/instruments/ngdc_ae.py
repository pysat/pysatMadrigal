#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
#
# DISTRIBUTION STATEMENT A: Approved for public release. Distribution is
# unlimited.
# ----------------------------------------------------------------------------
"""Supports access to taped data of AE from the World Data Center A (Boulder).

Properties
----------
platform
    'ngdc'
name
    'ae'
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
The entire data set (1 Jan 1978 through 31 Dec 1987) is provided in a single
file on Madrigal.

Examples
--------
::


    import datetime as dt
    import pysat
    import pysatMadrigal as py_mad

    # Download AE data from Madrigal
    aei = pysat.Instrument(inst_module=py_mad.instruments.ngdc_ae)
    aei.download(start=py_mad.instruments.ngdc_ae.madrigal_start,
                 user='Firstname+Lastname', password='email@address.com')
    aei.load(date=dt.datetime(1981, 1, 1))

"""

import datetime as dt
import functools
import numpy as np
import pandas as pds

import h5py
import pysat

from pysatMadrigal.instruments.methods import general

# ----------------------------------------------------------------------------
# Instrument attributes

platform = 'ngdc'
name = 'ae'
tags = {'': ''}
inst_ids = {'': list(tags.keys())}
pandas_format = True

# Madrigal tags and limits
madrigal_inst_code = 211
madrigal_tag = {'': {'': "30008"}}
madrigal_start = dt.datetime(1978, 1, 1)
madrigal_end = dt.datetime(1988, 1, 1)

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
_clean_warn = {inst_id: {tag: {'dusty': [('logger', 'WARN',
                                          "'dusty' and 'clean' are the same",
                                          'dusty')]}
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
    self.references = ''.join(['Davis, T. Neil and Masahisa Sugiura. “Auroral',
                               ' electrojet activity index AE and its ',
                               'universal time variations.” Journal of ',
                               'Geophysical Research 71 (1966): 785-801.'])

    # Remind the user of the Rules of the Road
    pysat.logger.info(self.acknowledgements)
    return


def clean(self):
    """Raise warning that cleaning is not possible for general data.

    Note
    ----
    Supports 'clean', 'dusty', 'dirty' in the sense that it prints
    a message noting there is no cleaning.
    'None' is also supported as it signifies no cleaning.

    Routine is called by pysat, and not by the end user directly.

    """

    warned = False
    for dvar in self.variables:
        if self.meta[dvar, self.meta.labels.units].find('nT') >= 0:
            # The 'clean', 'dusty', and 'dirty' levels all replace the missing
            # parameter value of -32766 with NaN
            mask = self[dvar] == self.meta[dvar, self.meta.labels.fill_val]
            self[dvar][mask] == np.nan
            self.meta[dvar] = {self.meta.labels.fill_val: np.nan}

            if self.clean_level in ['clean', 'dusty']:
                if self.clean_level == 'dusty' and not warned:
                    pysat.logger.warning(
                        "The NGDC AE 'dusty' and 'clean' levels are the same.")
                    warned = True

                # The 'clean' and 'dusty' levels replace the parameter error
                # value of -32766 with NaN
                self[dvar][self[dvar] == -32766] = np.nan

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
                             kindat=madrigal_tag[''][''], file_type='hdf5')

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
    """Load the NGDC AE data.

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
        Object containing satellite data
    meta : pysat.Meta
        Object containing metadata such as column names and units

    Raises
    ------
    ValueError
        Unexpected time variable names

    """
    # Initialize the output
    meta = pysat.Meta()
    labels = []
    data = None
    fill_val = -32767
    notes = "".join(["Assumed parameters error values are assigned a value ",
                     "of -32766 for clean levels of 'dirty' or 'none'"])

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
    with h5py.File(fname, 'r') as filed:
        file_data = filed['Data']['Table Layout']
        file_meta = filed['Metadata']['Data Parameters']

        # Load available info into pysat.Meta if this is the first file
        if len(labels) == 0:
            for item in file_meta:
                name_string = item[0].decode('UTF-8')
                unit_string = item[3].decode('UTF-8')
                desc_string = item[1].decode('UTF-8')
                labels.append(name_string)

                # Only update metadata if necessary
                if name_string.lower() not in meta:
                    meta_dict = {meta.labels.name: name_string,
                                 meta.labels.units: unit_string,
                                 meta.labels.desc: desc_string}

                    if unit_string.find('nT') >= 0:
                        # Fill and error values only apply to index values
                        meta_dict[meta.labels.fill_val] = fill_val
                        meta_dict[meta.labels.notes] = notes

                    meta[name_string.lower()] = meta_dict

        # Add additional metadata notes. Custom attributes attached to
        # meta are attached to corresponding Instrument object when
        # pysat receives data and meta from this routine
        for key in filed['Metadata']:
            if key != 'Data Parameters':
                setattr(meta, key.replace(' ', '_'), filed['Metadata'][key][:])

        # Extended processing is the same for simple and HDF5 files
        #
        # Construct datetime index from times
        time_keys = np.array(['year', 'month', 'day', 'hour', 'hm', 'hmi'])
        lower_labels = [ll.lower() for ll in labels]
        time_keys = [key for key in time_keys if key not in lower_labels]
        if len(time_keys) > 0:
            raise ValueError(' '.join(["unable to construct time index, ",
                                       "missing {:}".format(time_keys)]))

        # Get the date information
        year = file_data[:]['year']
        month = file_data[:]['month']
        day = file_data[:]['day']
        fdate = pysat.utils.time.create_datetime_index(year=year, month=month,
                                                       day=day)

        # Get the data mask
        dmask = (fdate >= fstart) & (fdate < fstop)

        # Construct the time index
        hour = file_data[dmask]['hour']
        minute = (file_data[dmask]['hm'] / 100.0 - hour) * 100.0
        uts = 3600.0 * hour + 60.0 * minute + file_data[dmask]['hmi']

        tindex = pysat.utils.time.create_datetime_index(
            year=year[dmask], month=month[dmask], day=day[dmask], uts=uts)

        # Load the data into a pandas DataFrame
        data = pds.DataFrame.from_records(file_data[dmask], columns=labels,
                                          index=tindex)

    # Ensure that data is at least an empty Dataset
    if data is None:
        data = pds.DataFrame(dtype=np.float64)

    return data, meta
