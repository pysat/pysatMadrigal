#!/usr/bin/env python
# Full license can be found in License.md
# Full author list can be found in .zenodo.json file
# DOI:10.5281/zenodo.3824979
# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-.
"""General routines for integrating CEDAR Madrigal instruments into pysat."""

import datetime as dt
import gzip
import numpy as np
import os
import pandas as pds
import xarray as xr

import h5py
import pysat

from madrigalWeb import madrigalWeb


logger = pysat.logger
file_types = {'hdf5': 'hdf5', 'netCDF4': 'netCDF4', 'simple': 'simple.gz'}


def cedar_rules():
    """General acknowledgement statement for Madrigal data.

    Returns
    -------
    ackn : str
        String with general acknowledgement for all CEDAR Madrigal data

    """
    ackn = "".join(["Contact the PI when using this data, in accordance ",
                    "with the CEDAR 'Rules of the Road'"])
    return ackn


def known_madrigal_inst_codes(pandas_format=None):
    """Supply known Madrigal instrument codes with a brief description.

    Parameters
    ----------
    pandas_format : bool or NoneType
       Separate instrument codes by time-series (True) or multi-dimensional
       data types (False) if a boolean is supplied, or supply all if NoneType
       (default=None)

    Returns
    -------
    inst_codes : dict
        Dictionary with string instrument code values as keys and a brief
        description of the corresponding instrument as the value.

    """
    time_series = {'120': 'Interplanetary Mag Field and Solar Wind',
                   '210': 'Geophysical Indicies', '211': 'AE Index',
                   '212': 'DST Index', '170': 'POES Spacecraft Particle Flux',
                   '180': 'DMSP-Auroral Boundary Index',
                   '8100': 'Defense Meteorological Satellite Program',
                   '8105': 'Van Allen Probes', '8400': 'Jason/Topex Ocean TEC',
                   '8250': 'Jicamarca Magnetometer',
                   '8255': 'Piura Magnetometer',
                   '8300': 'Sodankyla Magnetometer',
                   '7800': 'Green Bank Telescope'}
    multi_dim = {'10': 'Jicamarca ISR', '20': 'Arecibo ISR Linefeed',
                 '21': 'Arecibo ISR Gregorian',
                 '22': 'Arecibo ISR Velocity Vector',
                 '25': 'MU ISR', '30': 'Millstone Hill ISR',
                 '31': 'Millstone Hill UHF Steerable Antenna',
                 '32': 'Millstone Hill UHF Zenith Antenna',
                 '40': 'St. Santin ISR', '41': 'St. Santin Nançay Receiver',
                 '42': 'St. Santin Mende Receiver',
                 '43': 'St. Santin Monpazier Receiver',
                 '45': 'Kharkov Ukraine ISR', '50': 'Chatanika ISR',
                 '53': 'ISTP Irkutsk Radar', '57': 'UK Malvern ISR',
                 '61': 'Poker Flat ISR', '70': 'EISCAT combined ISRs',
                 '71': 'EISCAT Kiruna UHF ISR', '72': 'EISCAT Tromsø UHF ISR',
                 '73': 'EISCAT Sodankylä UHF ISR',
                 '74': 'EISCAT Tromsø VHF ISR', '75': 'EISCAT Kiruna VHF ISR',
                 '76': 'EISCAT Sodankylä VHF ISR', '80': 'Sondrestrom ISR',
                 '85': 'ALTAIR ISR', '91': 'Resolute Bay North ISR',
                 '92': 'Resolute Bay Canada ISR',
                 '95': 'EISCAT Svalbard ISR Longyearbyen',
                 '100': 'QuJing ISR', '310': 'TGCM/TIGCM model',
                 '311': 'AMIE Model', '312': 'USU-TDIM Model',
                 '320': 'Solar sd Tides', '321': 'Lunar sd Tides',
                 '322': 'GSWM model', '820': 'Halley HF Radar',
                 '830': 'Syowa Station HF Radar', '845': 'Kapuskasing HF Radar',
                 '861': 'Saskatoon HF Radar', '870': 'Goose Bay HF Radar',
                 '900': 'Hankasalmi HF Radar', '910': 'Stokkseyri HF Radar',
                 '911': 'Pykkvibaer HF Radar', '1040': 'Arecibo MST Radar',
                 '1140': 'Poker Flat MST Radar',
                 '1180': 'SOUSY Svalbard MST Radar Longyearbyen',
                 '1210': 'Scott Base MF Radar',
                 '1215': 'Davis Antarctica MF radar',
                 '1220': 'Mawson MF Radar', '1221': 'Rothera MF radar',
                 '1230': 'Christchurch MF Radar',
                 '1240': 'Adelaide MF Radar', '1245': 'Rarotonga MF radar',
                 '1254': 'Tirunelveli MF radar', '1270': 'Kauai MF radar',
                 '1275': 'Yamagawa MF radar', '1285': 'Platteville MF radar',
                 '1310': 'Wakkanai MF radar', '1320': 'Collm LF Radar',
                 '1340': 'Saskatoon MF Radar',
                 '1375': 'The Poker Flat MF radar', '1390': 'Tromsø MF Radar',
                 '1395': 'Syowa MF Radar', '1400': 'Halley MF Radar',
                 '13': 'JASMET Jicamarca All-Sky Specular Meteor Radar',
                 '1539': 'Ascension Island Meteor Radar',
                 '1540': 'Rothera Meteor Radar',
                 '1560': 'Atlanta meteor Radar', '1620': 'Durham meteor Radar',
                 '1750': 'Obninsk meteor radar', '1775': 'Esrange meteor radar',
                 '1780': 'Wuhan meteor radar', '1781': 'Mohe meteor radar',
                 '1782': 'Beijing meteor radar', '1783': 'Sanya meteor radar',
                 '1784': 'South Pole meteor radar',
                 '1785': 'Southern Argentina Agile Meteor Radar',
                 '1786': 'Cachoeira Paulista Meteor Radar',
                 '1787': 'Buckland Park Meteor Radar',
                 '1788': 'Kingston Meteor Radar', '1790': 'Andes Meteor Radar',
                 '1791': 'Southern Cross Meteor Radar',
                 '1792': 'Las Campanas Meteor Radar',
                 '1793': 'CONDOR multi-static meteor radar system',
                 '2090': 'Christmas Island ST/MEDAC Radar',
                 '2200': 'Platteville ST/MEDAC Radar',
                 '2550': 'ULowell Digisonde MLH Radar',
                 '2890': 'Sondre Stromfjord Digisonde',
                 '2900': 'Sodankylä Ionosonde (SO166)',
                 '2930': 'Qaanaaq Digisonde ST/MEDAC Radars',
                 '2950': 'EISCAT Tromsø Dynasonde',
                 '2951': 'EISCAT Svalbard Dynasonde',
                 '2952': 'IRF Dynasonde at EISCAT site Kiruna',
                 '5000': 'South Pole Fabry-Perot', '5005': 'Palmer Fabry Perot',
                 '5015': 'Arrival Heights Fabry-Perot',
                 '5020': 'Halley Fabry-Perot',
                 '5060': 'Mount John Fabry-Perot',
                 '5140': 'Fabry-Perot Arequipa',
                 '5145': 'Fabry-Perot Jicamarca', '5150': 'Fabry-Perot Mobile',
                 '5160': 'Arecibo Fabry-Perot',
                 '5190': 'Kitt Peak H-alpha Fabry-Perot',
                 '5240': 'Fritz Peak Fabry-Perot',
                 '5292': 'Ann Arbor Fabry-Perot',
                 '5300': 'Peach Mountain Fabry-Perot',
                 '5340': 'Millstone Hill Fabry-Perot',
                 '5360': 'Millstone Hill High-Res Fabry-Perot',
                 '5370': 'Arecibo Imaging Doppler Fabry-Perot',
                 '5380': 'Culebra Fabry-Perot',
                 '5430': 'Watson Lake Fabry-Perot',
                 '5460': 'College Fabry-Perot',
                 '5465': 'Poker Flat all-sky scanning Fabry-Perot',
                 '5470': 'Fort Yukon Fabry-Perot',
                 '5475': 'Poker Flat Fabry-Perot',
                 '5480': 'Sondre Stromfjord Fabry-Perots',
                 '5510': 'Inuvik NWT Fabry-Perot',
                 '5535': 'Resolute Bay Fabry-Perot',
                 '5540': 'Thule Fabry-Perot', '5545': 'Cariri Brazil FPI',
                 '5546': 'Cajazeiras Brazil FPI',
                 '5547': 'Pisgah Astronomical Research FPI',
                 '5548': 'Urbana Atmospheric Observatory FPI',
                 '5549': 'Kirtland Airforce Base FPI',
                 '5550': 'Virginia Tech FPI',
                 '5551': 'Peach Mountain (MiniME) FPI',
                 '5552': 'Merihill Peru FPI', '5553': 'Nazca Peru FPI',
                 '5554': 'Eastern Kentucky FPI',
                 '5600': 'Jang Bogo Station FPI',
                 '5700': 'South Pole Michelson Interferometer',
                 '5720': 'Daytona Beach Michelson Interferometer',
                 '5860': 'Stockholm IR Michelson',
                 '5900': 'Sondrestrom Michelson Interferometer',
                 '5950': 'Resolute Bay Michelson Interferometer',
                 '5980': 'Eureka Michelson Interferometer',
                 '6205': 'Arecibo Potassium [K] lidar',
                 '6206': 'Arecibo Sodium [Na] lidar',
                 '6300': 'CEDAR lidar', '6320': 'Colorado State sodium lidar',
                 '6330': 'Rayleigh lidar at the ALO - USU/CASS',
                 '6340': 'Andes Na T/W Lidar', '6350': 'ALOMAR Sodium Lidar',
                 '6360': 'CU STAR Sodium Lidar', '6370': 'USU Na lidar',
                 '6380': 'Poker Flat lidar', '7190': 'USU CCD Imager',
                 '7192': 'USU Advanced Mesospheric Temperature Mapper',
                 '7200': 'BU Millstone All-Sky Imager',
                 '7201': 'BU Arecibo All-Sky Imager',
                 '7202': 'BU Asiago All-Sky Imager',
                 '7203': 'BU El Leoncito All-Sky Imager',
                 '7204': 'BU McDonald All-Sky Imager',
                 '7205': 'BU Rio Grande All-Sky Imager',
                 '7206': 'BU Jicamarca All-Sky Imager', '7240': 'MIO',
                 '7580': 'All-sky cameras at Qaanaaq',
                 '11': 'Jicamarca Bistatic Radar', '840': 'JULIA',
                 '3000': 'ARL UT TBB Receiver',
                 '7600': 'Chelmsford HS Ozone Radiometer',
                 '7602': 'Lancaster UK Ozone Radiometer',
                 '7603': 'Bridgewater MA Ozone Radiometer',
                 '7604': 'Union College Ozone Radiometer',
                 '7605': 'UNC Greensboro Ozone Radiometer',
                 '7606': 'Lynnfield HS Ozone Radiometer',
                 '7607': 'Alaska Pacific Ozone Radiometer',
                 '7608': 'Hermanus SA Ozone Radiometer',
                 '7609': 'Sanae Antarctic Ozone Radiometer',
                 '7610': 'Sodankylä Ozone Radiometer',
                 '7611': 'Lancaster2 UK Ozone Radiometer',
                 '7612': 'Haystack Ridge Ozone Radiometer',
                 '7613': 'Haystack NUC3 8-channel Ozone Radiometer',
                 '7614': 'Fairbanks Ozone Radiometer',
                 '8001': 'South Pole Scintillation Receiver',
                 '8000': 'World-wide GNSS Receiver Network',
                 '8002': 'McMurdo Scintillation Receiver',
                 '8010': 'GNSS Scintillation Network',
                 '3010': 'Davis Czerny-Turner Scanning Spectrophotometer',
                 '3320': 'Wuppertal (DE) Czerny-Turner OH Grating Spectrometer',
                 '4470': 'Poker Flat 4 Channel Filter Photometer',
                 '4473': 'Fort Yukon 4 Channel Filter Photometer',
                 '4480': 'Arecibo red line photometer',
                 '4481': 'Arecibo green line photometer',
                 '7191': 'USU Mesospheric Temperature Mapper'}

    if pandas_format is None:
        inst_codes = dict(**time_series, **multi_dim)
    elif pandas_format:
        inst_codes = time_series
    else:
        inst_codes = multi_dim

    return inst_codes


def madrigal_file_format_str(inst_code, strict=False, verbose=True):
    """Supply known Madrigal instrument codes with a brief description.

    Parameters
    ----------
    inst_code : int
        Madrigal instrument code as an integer
    strict : bool
        If True, returns only file formats that will definitely not have a
        problem being parsed by pysat.  If False, will return any file format.
        (default=False)
    verbose : bool
        If True raises logging warnings, if False does not log any warnings.
        (default=True)

    Returns
    -------
    fstr : str
        File formatting string that may or may not be parsable by pysat

    Raises
    ------
    ValueError
        If file formats with problems would be returned and `strict` is True.

    Note
    ----
    File strings that have multiple '*' wildcards typically have several
    experiment types and require a full pysat Instrument to properly manage
    these types.

    """
    if not isinstance(inst_code, int):
        inst_code = int(inst_code)

    format_str = {
        120: 'imf{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        210: 'geo{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        211: 'aei{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        212: 'dst{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        170: 'pfx{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        180: 'dmp{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        8100: 'dms*_{{year:04d}}{{month:02d}}{{day:02d}}_*.{{version:03d}}.',
        8105: 'van_allen_{{year:04d}}_{{month:02d}}.{{version:03d}}.',
        8400: '???{{year:04d}}{{month:02d}}{{day:02d}}j*.{{version:03d}}.',
        8250: 'jic{{year:04d}}{{month:02d}}{{day:02d}}_mag.{{version:03d}}.',
        8255: 'pmt*.',
        8300: 'smt*.',
        7800: 'gbt{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        10: 'jro{{year:04d}}{{month:02d}}{{day:02d}}*.{{version:03d}}.',
        20: 'aro*{{year:02d}}{{month:02d}}{{day:02d}}a.{{version:03d}}.',
        21: 'aro*{{year:02d}}{{month:02d}}{{day:02d}}*g.{{version:03d}}.',
        22: 'ar?*{{year:02d}}{{month:02d}}{{day:02d}}*.{{version:03d}}.',
        25: 'mui{{year:02d}}{{month:02d}}{{day:02d}}?.{{version:03d}}.',
        30: 'mlh{{year:02d}}{{month:02d}}{{day:02d}}?.{{version:03d}}.',
        31: 'mlh{{year:02d}}{{month:02d}}{{day:02d}}?.{{version:03d}}.',
        32: 'mlh{{year:02d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        40: 'sts{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        41: 'sts{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        42: 'sts{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        43: 'sts{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        45: 'kha{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        50: 'cht{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        53: 'ist{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        57: 'mlv{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        61: 'pfa{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        70: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*.',
        71: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*@kir.',
        72: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*@uhf.',
        73: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*@sod.',
        74: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*@vhf.',
        75: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*@vkrv*.',
        76: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*@sdv*.',
        80: 'son{{year:02d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        85: 'ALT{{year:02d}}{{month:02d}}{{day:02d}}_*.',
        91: 'ran{{year:02d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        92: 'ras{{year:02d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        95: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*@esr.',
        100: 'MAD????_{year:04d}}-{{month:02d}}-{{day:02d}}_*@quj.',
        310: 'gcm*.',
        311: 'ami*.',
        312: 'tdi*.',
        320: 'sdt*.',
        321: 'sdl*.',
        322: 'gsw*.',
        820: 'hhf*.',
        830: 'syf*.',
        845: 'khf*.',
        861: 'shf*.',
        870: 'gbf*.',
        900: 'fhf*.',
        910: 'whf*.',
        911: 'ehf*.',
        1040: 'arm{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1140: 'pkr{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1180: 'ssr*.',
        1210: 'sbf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1215: 'dav{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1220: 'maf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1221: 'rth{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1230: 'ccf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1240: 'adf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1245: 'rtg{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1254: 'tyr{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1270: 'kau{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1275: 'yam{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1285: 'plr{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1310: 'wak{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1320: 'cof{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1340: 'saf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1375: 'rpk{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1390: 'trf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1395: 'sym_{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        1400: 'hmf_{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        13: 'D{{year:04d}}{{month:02d}}*.',
        1539: 'asc{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1540: 'rmr_{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        1560: 'atm{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1620: 'dum{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        1750: 'obn{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1775: 'emr{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        1780: 'wmr*.',
        1781: 'mmr*.',
        1782: 'bmr*.',
        1783: 'smr*.',
        1784: 'som{{year:02d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        1785: 'amr{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        1786: 'cpr_{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        1787: 'bpr_{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        1788: 'kgr_{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        1790: 'ame*.',
        1791: 'sco*.',
        1792: 'lcm*.',
        1793: 'alo{{year:04d}}{{month:02d}}{{day:02d}}_{{version:03d}}.',
        2090: 'cia{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        2200: 'pla{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        2550: 'uld*.',
        2890: 'ssd{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        2900: 'sdi*.',
        2930: 'qad{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        2950: 'trd*.',
        2951: 'lrd*.',
        2952: 'krd*.',
        5000: 'spf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5005: 'pfi{{year:04d}}{{month:02d}}{{day:02d}}.',
        5015: 'ahf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5020: 'hfp{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5060: 'mjf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5140: 'aqf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5145: 'jfp{{year:04d}}{{month:02d}}{{day:02d}}_*.{{version:03d}}.',
        5150: 'mfp{{year:04d}}{{month:02d}}{{day:02d}}_*.{{version:03d}}.',
        5160: 'afp{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5190: 'kha{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5240: 'fpf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5292: 'aaf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5300: 'pfp{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5340: 'mfp{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.?.',
        5360: 'kfp{{year:02d}}{{month:02d}}{{day:02d}}g*.',
        5370: 'aif{{year:02d}}{{month:02d}}{{day:02d}}g*.',
        5380: 'clf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5430: 'wfp{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5460: 'cfp{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5465: 'pkf{{year:02d}}{{month:02d}}{{day:02d}}*.',
        5470: 'FYU{{year:04d}}{{month:02d}}{{day:02d}}.',
        5475: 'PKZ{{year:04d}}{{month:02d}}{{day:02d}}.',
        5480: 'sfp{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5510: 'ikf{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5535: 'rfp{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5540: 'tfp{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5545: ''.join(['minime01_car_{{year:04d}}{{month:02d}}{{day:02d}}.',
                       'cedar.{{version:03d}}.']),
        5546: ''.join(['minime02_caj_{{year:04d}}{{month:02d}}{{day:02d}}.',
                       'cedar.{{version:03d}}.']),
        5547: ''.join(['minime06_par_{{year:04d}}{{month:02d}}{{day:02d}}.',
                       'cedar.{{version:03d}}.']),
        5548: ''.join(['minime02_uao_{{year:04d}}{{month:02d}}{{day:02d}}.',
                       'cedar.{{version:03d}}.']),
        5549: 'Kirtland Airforce Base FPI',
        5550: ''.join(['minime09_vti_{{year:04d}}{{month:02d}}{{day:02d}}.',
                       'cedar.{{version:03d}}.']),
        5551: ''.join(['minime08_ann_{{year:04d}}{{month:02d}}{{day:02d}}.',
                       'cedar.{{version:03d}}.']),
        5552: 'Merihill Peru FPI',
        5553: 'Nazca Peru FPI',
        5554: ''.join(['minime07_euk_{{year:04d}}{{month:02d}}{{day:02d}}.',
                       'cedar.{{version:03d}}.']),
        5600: 'jbs_{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        5700: 'spm{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5720: 'dbm{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5860: 'stm{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5900: 'sfm{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5950: 'rbm{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        5980: 'eum{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        6205: 'akl{{year:02d}}{{month:02d}}{{day:02d}}g.*.',
        6206: 'asl{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        6300: 'uil{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        6320: 'Colorado State sodium lidar',
        6330: 'usl{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        6340: 'alo*.',
        6350: 'nlo*.',
        6360: 'cul*.',
        6370: 'unl*.',
        6380: 'pfl{{year:04d}}{{month:02d}}{{day:02d}}_{{cycle:03d}}.',
        7190: 'usi*.',
        7192: 'amp{{year:02d}}{{month:02d}}{{day:02d}}?.{{version:03d}}.',
        7200: 'mhi{{year:04d}}{{month:02d}}{{day:02d}}.{kindat}.',
        7201: 'aai{{year:04d}}{{month:02d}}{{day:02d}}.{kindat}.',
        7202: 'abi{{year:04d}}{{month:02d}}{{day:02d}}.{kindat}.',
        7203: 'eai{{year:04d}}{{month:02d}}{{day:02d}}.{kindat}.',
        7204: 'mai{{year:04d}}{{month:02d}}{{day:02d}}.{kindat}.',
        7205: 'rai{{year:04d}}{{month:02d}}{{day:02d}}.{kindat}.',
        7206: 'jci{{year:04d}}{{month:02d}}{{day:02d}}.{kindat}.',
        7240: 'mhi*.',
        7580: 'qac*.',
        11: 'j??*{{year:02d}}{{month:02d}}{{day:02d}}g.{{version:03d}}.',
        840: 'jul{{year:04d}}{{month:02d}}{{day:02d}}_esf.{{version:03d}}.',
        3000: 'utx*.',
        8001: '????_?_??.gps_all.out.',
        8000: '*{{year:02d}}{{month:02d}}{{day:02d}}*.{{version:03d}}.',
        8002: '????_?_??.gps_all.out.',
        8010: 'scin_{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        3010: 'dvs{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        3320: 'wup{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        4470: 'p4p{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        4473: 'y4p{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.',
        4480: 'arp{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        4481: 'agp{{year:04d}}{{month:02d}}{{day:02d}}.{{version:03d}}.',
        7191: 'mtm{{year:02d}}{{month:02d}}{{day:02d}}g.{kindat}.'}

    # Warn if file format not available
    msg = ""
    if inst_code not in format_str.keys():
        msg = "".join(["file format string not available for ",
                       "instrument code {:d}: ".format(inst_code)])
        fstr = "*."
    else:
        fstr = format_str[inst_code]

    # Warn if file format has multiple '*' wildcards
    num_wc = len(fstr.split("*"))
    if num_wc >= 3:
        msg = "".join(["file format string has multiple '*' ",
                       "wildcards, may not be parsable by pysat"])
    elif fstr.find('{{year') < 0 and fstr != "*.":
        msg = "".join(["file format string missing date info, ",
                       "may not be parsable by pysat"])
    elif num_wc > 1:
        nspec_sec = 0
        for fsplit in fstr.split("*"):
            if fsplit.find("}}") > 0 and fsplit.find("{{") >= 0:
                nspec_sec += 1

        if nspec_sec > 1:
            msg = "".join(["file format string has '*' between formatting",
                           " constraints, may not be parsable by pysat"])

    if len(msg) > 0:
        if strict:
            raise ValueError(msg)
        elif verbose:
            logger.warning(msg)

    fstr += "{file_type}"

    return fstr


def load(fnames, tag='', inst_id='', xarray_coords=None):
    """Load data from Madrigal into Pandas or XArray.

    Parameters
    ----------
    fnames : array-like
        Iterable of filename strings, full path, to data files to be loaded.
        This input is nominally provided by pysat itself.
    tag : str
        Tag name used to identify particular data set to be loaded. This input
        is nominally provided by pysat itself and is not used here. (default='')
    inst_id : str
        Instrument ID used to identify particular data set to be loaded.
        This input is nominally provided by pysat itself, and is not used here.
        (default='')
    xarray_coords : list or NoneType
        List of keywords to use as coordinates if xarray output is desired
        instead of a Pandas DataFrame.  Can build an xarray Dataset
        that have different coordinate dimensions by providing a dict
        inside the list instead of coordinate variable name strings. Each dict
        will have a tuple of coordinates as the key and a list of variable
        strings as the value.  Empty list if None. For example,
        xarray_coords=[{('time',): ['year', 'doy'],
        ('time', 'gdalt'): ['data1', 'data2']}]. (default=None)

    Returns
    -------
    data : pds.DataFrame or xr.Dataset
        A pandas DataFrame or xarray Dataset holding the data from the file
    meta : pysat.Meta
        Metadata from the file, as well as default values from pysat

    Raises
    ------
    ValueError
       If data columns expected to create the time index are missing or if
       coordinates are not supplied for all data columns.

    Note
    ----
    Currently HDF5 reading breaks if a different file type was used previously

    This routine is called as needed by pysat. It is not intended
    for direct user interaction.

    """
    # Test the file formats
    load_file_types = {ftype: [] for ftype in file_types.keys()}
    for fname in fnames:
        for ftype in file_types.keys():
            if fname.find(ftype) > 0:
                load_file_types[ftype].append(fname)
                break

    # Initialize xarray coordinates, if needed
    if xarray_coords is None:
        xarray_coords = []

    # Initialize the output
    meta = pysat.Meta()
    labels = []
    data = None

    # Load the file data for netCDF4 files
    if len(load_file_types["netCDF4"]) == 1:
        # Xarray natively opens netCDF data into a Dataset
        file_data = xr.open_dataset(load_file_types["netCDF4"][0],
                                    engine="netcdf4")
    elif len(load_file_types["netCDF4"]) > 1:
        file_data = xr.open_mfdataset(load_file_types["netCDF4"],
                                      combine='by_coords', engine="netcdf4")

    if len(load_file_types["netCDF4"]) > 0:
        # Currently not saving file header data, as all metadata is at
        # the data variable level. The attributes are only saved if they occur
        # in all of the loaded files.
        if 'catalog_text' in file_data.attrs:
            notes = file_data.attrs['catalog_text']
        else:
            notes = "No catalog text"

        # Get the coordinate and data variable names
        meta_items = [dkey for dkey in file_data.data_vars.keys()]
        meta_items.extend([dkey for dkey in file_data.coords.keys()])

        for item in meta_items:
            # Set the meta values for the expected labels
            meta_dict = {meta.labels.name: item, meta.labels.fill_val: np.nan,
                         meta.labels.notes: notes}

            for key, label in [('units', meta.labels.units),
                               ('description', meta.labels.desc)]:
                if key in file_data[item].attrs.keys():
                    meta_dict[label] = file_data[item].attrs[key]
                else:
                    meta_dict[label] = ''

            meta[item.lower()] = meta_dict

            # Remove any metadata from xarray
            file_data[item].attrs = {}

        # Reset UNIX timestamp as datetime and set it as an index
        file_data = file_data.rename({'timestamps': 'time'})
        time_data = pds.to_datetime(file_data['time'].values, unit='s')
        data = file_data.assign_coords({'time': ('time', time_data)})

    # Load the file data for HDF5 files
    if len(load_file_types["hdf5"]) > 0 or len(load_file_types["simple"]) > 0:
        # Ensure we don't try to create an xarray object with only time as
        # the coordinate
        coord_len = len(xarray_coords)
        if 'time' in xarray_coords:
            coord_len -= 1

        # Cycle through all the filenames
        fdata = []
        fnames = list(load_file_types["hdf5"])
        fnames.extend(load_file_types["simple"])
        for fname in fnames:
            # Open the specified file
            if fname in load_file_types["simple"]:
                # Get the gzipped text data
                with gzip.open(fname, 'rb') as fin:
                    file_data = fin.readlines()

                # Load available info into pysat.Meta if this is the first file
                header = [item.decode('UTF-8')
                          for item in file_data.pop(0).split()]
                if len(labels) == 0:
                    for item in header:
                        labels.append(item)

                        # Only update metadata if necessary
                        if item.lower() not in meta:
                            meta[item.lower()] = {meta.labels.name: item}

                # Construct a dict of the output
                file_dict = {item.lower(): list() for item in header}
                for line in file_data:
                    for i, val in enumerate(line.split()):
                        file_dict[header[i].lower()].append(float(val))

                # Load data into frame, with labels from metadata
                ldata = pds.DataFrame.from_dict(file_dict)
            else:
                # Open the specified file and get the data and metadata
                filed = h5py.File(fname, 'r')
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
                            meta[name_string.lower()] = {
                                meta.labels.name: name_string,
                                meta.labels.units: unit_string,
                                meta.labels.desc: desc_string}

                # Add additional metadata notes. Custom attributes attached to
                # meta are attached to corresponding Instrument object when
                # pysat receives data and meta from this routine
                for key in filed['Metadata']:
                    if key != 'Data Parameters':
                        setattr(meta, key.replace(' ', '_'),
                                filed['Metadata'][key][:])

                # Load data into frame, with labels from metadata
                ldata = pds.DataFrame.from_records(file_data, columns=labels)

                # Enforce lowercase variable names
                ldata.columns = [item.lower() for item in ldata.columns]

            # Extended processing is the same for simple and HDF5 files
            #
            # Construct datetime index from times
            time_keys = np.array(['year', 'month', 'day', 'hour', 'min', 'sec'])
            if not np.all([key in ldata.columns for key in time_keys]):
                time_keys = [key for key in time_keys
                             if key not in ldata.columns]
                raise ValueError(' '.join(["unable to construct time index, ",
                                           "missing {:}".format(time_keys)]))

            uts = 3600.0 * ldata.loc[:, 'hour'] + 60.0 * ldata.loc[:, 'min'] \
                + ldata.loc[:, 'sec']
            time = pysat.utils.time.create_datetime_index(
                year=ldata.loc[:, 'year'], month=ldata.loc[:, 'month'],
                day=ldata.loc[:, 'day'], uts=uts)

            # Declare index or recast as xarray
            if coord_len > 0:
                # If a list was provided, recast as a dict and grab the data
                # columns
                if not isinstance(xarray_coords, dict):
                    xarray_coords = {tuple(xarray_coords):
                                     [col for col in ldata.columns
                                      if col not in xarray_coords]}

                # Determine the order in which the keys should be processed:
                #  Greatest to least number of dimensions
                len_dict = {len(xcoords): xcoords
                            for xcoords in xarray_coords.keys()}
                coord_order = [len_dict[xkey] for xkey in sorted(
                    [lkey for lkey in len_dict.keys()], reverse=True)]

                # Append time to the data frame
                ldata = ldata.assign(time=pds.Series(time, index=ldata.index))

                # Cycle through each of the coordinate dimensions
                xdatasets = list()
                for xcoords in coord_order:
                    if not np.all([xkey.lower() in ldata.columns
                                   for xkey in xcoords]):
                        raise ValueError(''.join(['unknown coordinate key ',
                                                  'in [{:}'.format(xcoords),
                                                  '], use only: {:}'.format(
                                                      ldata.columns)]))
                    if not np.all([xkey.lower() in ldata.columns
                                   for xkey in xarray_coords[xcoords]]):
                        good_ind = [
                            i for i, xkey in enumerate(xarray_coords[xcoords])
                            if xkey.lower() in ldata.columns]

                        if len(good_ind) == 0:
                            raise ValueError(''.join([
                                'All data variables {:} are unknown.'.format(
                                    xarray_coords[xcoords])]))
                        elif len(good_ind) < len(xarray_coords[xcoords]):
                            # Remove the coordinates that aren't present.
                            temp = np.array(xarray_coords[xcoords])[good_ind]

                            # Warn user, some of this may be due to a file
                            # format update or change.
                            bad_ind = [i for i in
                                       range(len(xarray_coords[xcoords]))
                                       if i not in good_ind]
                            logger.warning(''.join([
                                'unknown data variable(s) {:}, '.format(
                                    np.array(xarray_coords[xcoords])[bad_ind]),
                                'using only: {:}'.format(temp)]))

                            # Assign good data as a list.
                            xarray_coords[xcoords] = list(temp)

                    # Select the desired data values
                    sel_data = ldata[list(xcoords) + xarray_coords[xcoords]]

                    # Remove duplicates before indexing, to ensure data with
                    # the same values at different locations are kept
                    sel_data = sel_data.drop_duplicates()

                    # Set the indices
                    sel_data = sel_data.set_index(list(xcoords))

                    # Recast as an xarray
                    xdatasets.append(sel_data.to_xarray())

                # Get the necessary information to test the data
                lcols = ldata.columns
                len_data = len(lcols)

                # Merge all of the datasets
                ldata = xr.merge(xdatasets)
                test_variables = [xkey for xkey in ldata.variables.keys()]
                ltest = len(test_variables)

                # Test to see that all data was retrieved
                if ltest != len_data:
                    if ltest < len_data:
                        estr = 'missing: {:}'.format(
                            ' '.join([dvar for dvar in lcols
                                      if dvar not in test_variables]))
                    else:
                        estr = 'have extra: {:}'.format(
                            ' '.join([tvar for tvar in test_variables
                                      if tvar not in lcols]))
                        raise ValueError(''.join([
                            'coordinates not supplied for all data columns',
                            ': {:d} != {:d}; '.format(ltest, len_data), estr]))
            else:
                # Set the index to time
                ldata.index = time

                # Raise a logging warning if there are duplicate times. This
                # means the data should be stored as an xarray Dataset
                if np.any(time.duplicated()):
                    logger.warning(''.join(["duplicated time indices, ",
                                            "consider specifing additional",
                                            " coordinates and storing the ",
                                            "data as an xarray Dataset"]))

            # Compile a list of the data objects
            fdata.append(ldata)

        # Merge the data together, accounting for potential netCDF output
        if data is None and len(fdata) == 1:
            data = fdata[0]
        else:
            if coord_len > 0:
                if data is None:
                    data = xr.merge(fdata)
                else:
                    data = xr.combine_by_coords([data, xr.merge(fdata)])
            else:
                if data is None:
                    data = pds.concat(fdata)
                    data = data.sort_index()
                else:
                    ldata = pds.concat(fdata).sort_index().to_xarray()
                    ldata = ldata.rename({'index': 'time'})
                    data = xr.combine_by_coords([data, ldata]).to_pandas()

    # Ensure that data is at least an empty Dataset
    if data is None:
        if len(xarray_coords) > 0:
            data = xr.Dataset()
        else:
            data = pds.DataFrame(dtype=np.float64)

    return data, meta


def download(date_array, inst_code=None, kindat=None, data_path=None,
             user=None, password=None, url="http://cedar.openmadrigal.org",
             file_type='hdf5'):
    """Download data from Madrigal.

    Parameters
    ----------
    date_array : array-like
        list of datetimes to download data for. The sequence of dates need not
        be contiguous.
    inst_code : str
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindat : str
        Experiment instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    data_path : str
        Path to directory to download data to. (default=None)
    user : str
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : str
        Password for data download. (default=None)
    url : str
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    file_type : str
        File format for Madrigal data.  Load routines currently only accepts
        'hdf5' and 'netCDF4', but any of the Madrigal options may be used
        here. (default='hdf5')

    Raises
    ------
    ValueError
        If the specified input type or Madrigal experiment codes are unknown

    Note
    ----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    """
    if file_type not in file_types.keys():
        raise ValueError("Unknown file format {:}, accepts {:}".format(
            file_type, file_types.keys()))

    _check_madrigal_params(inst_code=inst_code, user=user, password=password)

    if kindat is None:
        raise ValueError("Must supply Madrigal experiment code")

    # Get the list of desired remote files
    start = date_array.min()
    stop = date_array.max()
    if start == stop:
        stop += dt.timedelta(days=1)

    # Initialize the connection to Madrigal
    logger.info('Connecting to Madrigal')
    web_data = madrigalWeb.MadrigalData(url)
    logger.info('Connection established.')

    files = get_remote_filenames(inst_code=inst_code, kindat=kindat,
                                 user=user, password=password,
                                 web_data=web_data, url=url,
                                 start=start, stop=stop)

    for mad_file in files:
        # Build the local filename
        local_file = os.path.join(data_path,
                                  os.path.basename(mad_file.name))

        if local_file.find(file_type) <= 0:
            split_file = local_file.split(".")
            split_file[-1] = file_type
            local_file = ".".join(split_file)

        if not os.path.isfile(local_file):
            fstr = ''.join(('Downloading data for ', local_file))
            logger.info(fstr)
            web_data.downloadFile(mad_file.name, local_file, user, password,
                                  "pysat", format=file_type)
        else:
            estr = ''.join((local_file, ' already exists. Skipping.'))
            logger.info(estr)

    return


def get_remote_filenames(inst_code=None, kindat='', user=None, password=None,
                         web_data=None, url="http://cedar.openmadrigal.org",
                         start=dt.datetime(1900, 1, 1), stop=dt.datetime.now(),
                         date_array=None):
    """Retrieve the remote filenames for a specified Madrigal experiment.

    Parameters
    ----------
    inst_code : str or NoneType
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindat : str
        Madrigal experiment code(s), cast as a string.  If multiple are used,
        separate them with commas.  If not supplied, all will be returned.
        (default='')
    data_path : str or NoneType
        Path to directory to download data to. (default=None)
    user : str or NoneType
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for dowloads this routine here must
        error if user not supplied. (default=None)
    password : str or NoneType
        Password for data download. (default=None)
    web_data : MadrigalData or NoneType
        Open connection to Madrigal database or None (will initiate using url)
        (default=None)
    url : str
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    start : dt.datetime or NoneType
        Starting time for file list, None reverts to default
        (default=dt.datetime(1900, 1, 1))
    stop : dt.datetime or NoneType
        Ending time for the file list, None reverts to default
        (default=dt.datetime.utcnow())
    date_array : dt.datetime or NoneType
        Array of datetimes to download data for. The sequence of dates need not
        be contiguous and will be used instead of start and stop if supplied.
        (default=None)

    Returns
    -------
    files : madrigalWeb.madrigalWeb.MadrigalExperimentFile
        Madrigal file object that contains remote experiment file data

    Raises
    ------
    ValueError
        If unexpected date_array input is supplied

    Note
    ----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.


    """
    _check_madrigal_params(inst_code=inst_code, user=user, password=password)

    if kindat in ['', '*']:
        kindat = []
    else:
        kindat = [int(kk) for kk in kindat.split(",")]

    # If date_array supplied, overwrite start and stop
    if date_array is not None:
        if len(date_array) == 0:
            raise ValueError('unknown date_array supplied: {:}'.format(
                date_array))
        start = date_array.min()
        stop = date_array.max()

    # If NoneType was supplied for start or stop, set to defaults
    if start is None:
        start = dt.datetime(1900, 1, 1)

    if stop is None:
        stop = dt.datetime.utcnow()

    # If start and stop are identical, increment
    if start == stop:
        stop += dt.timedelta(days=1)

    # Open connection to Madrigal
    if web_data is None:
        web_data = madrigalWeb.MadrigalData(url)

    # Get list of experiments for instrument from in desired range
    exp_list = web_data.getExperiments(inst_code, start.year, start.month,
                                       start.day, start.hour, start.minute,
                                       start.second, stop.year, stop.month,
                                       stop.day, stop.hour, stop.minute,
                                       stop.second)

    # Iterate over experiments to grab files for each one
    files = list()
    istr = "Found {:d} Madrigal experiments between {:s} and {:s}".format(
        len(exp_list), start.strftime('%d %B %Y'), stop.strftime('%d %B %Y'))
    logger.info(istr)
    for exp in exp_list:
        if good_exp(exp, date_array=date_array):
            file_list = web_data.getExperimentFiles(exp.id)
            if len(kindat) == 0:
                files.extend(file_list)
            else:
                for file_obj in file_list:
                    if file_obj.kindat in kindat:
                        files.append(file_obj)

    return files


def good_exp(exp, date_array=None):
    """Determine if a Madrigal experiment has good data for specified dates.

    Parameters
    ----------
    exp : MadrigalExperimentFile
        MadrigalExperimentFile object
    date_array : list-like or NoneType
        List of datetimes to download data for. The sequence of dates need not
        be contiguous. If None, then any valid experiment will be assumed
        to be valid. (default=None)

    Returns
    -------
    gflag : boolean
        True if good, False if bad

    """
    gflag = False

    if exp.id != -1:
        if date_array is None:
            gflag = True
        else:
            exp_start = dt.date(exp.startyear, exp.startmonth,
                                exp.startday)
            exp_end = (dt.date(exp.endyear, exp.endmonth, exp.endday)
                       + dt.timedelta(days=1))

            for date_val in date_array:
                if date_val.date() >= exp_start and date_val.date() <= exp_end:
                    gflag = True
                    break

    return gflag


def list_remote_files(tag, inst_id, inst_code=None, kindats=None, user=None,
                      password=None, supported_tags=None,
                      url="http://cedar.openmadrigal.org",
                      two_digit_year_break=None, start=dt.datetime(1900, 1, 1),
                      stop=dt.datetime.utcnow()):
    """List files available from Madrigal.

    Parameters
    ----------
    tag : str
        Denotes type of file to load.  Accepts strings corresponding to the
        appropriate Madrigal Instrument `tags`.
    inst_id : str
        Specifies the instrument ID to load. Accepts strings corresponding to
        the appropriate Madrigal Instrument `inst_ids`.
    inst_code : str or NoneType
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas. (default=None)
    kindats : dict
        Madrigal experiment codes, in a dict of dicts with inst_ids as top level
        keys and tags as second level keys with Madrigal experiment code(s)
        as values.  These should be strings, with multiple codes separated by
        commas. (default=None)
    data_path : str or NoneType
        Path to directory to download data to. (default=None)
    user : str or NoneType
        User string input used for download. Provided by user and passed via
        pysat. If an account is required for downloads this routine here must
        error if user not supplied. (default=None)
    password : str or NoneType
        Password for data download. (default=None)
    supported_tags : dict or NoneType
        keys are inst_id, each containing a dict keyed by tag
        where the values file format template strings. (default=None)
    url : str
        URL for Madrigal site (default='http://cedar.openmadrigal.org')
    two_digit_year_break : int or NoneType
        If filenames only store two digits for the year, then '1900' will be
        added for years >= two_digit_year_break and '2000' will be added for
        years < two_digit_year_break. (default=None)
    start : dt.datetime
        Starting time for file list.  (default=01-01-1900)
    stop : dt.datetime
        Ending time for the file list. (default=time of run)

    Returns
    -------
    pds.Series
        A series of filenames, see `pysat.utils.files.process_parsed_filenames`
        for more information.

    Raises
    ------
    ValueError
        For missing kwarg input
    KeyError
        For dictionary input missing requested tag/inst_id

    Note
    ----
    The user's names should be provided in field user. Ruby Payne-Scott should
    be entered as Ruby+Payne-Scott

    The password field should be the user's email address. These parameters
    are passed to Madrigal when downloading.

    The affiliation field is set to pysat to enable tracking of pysat
    downloads.

    Examples
    --------
    This method is intended to be set in an instrument support file at the
    top level using functools.partial
    ::

        list_remote_files = functools.partial(mad_meth.list_remote_files,
                                              supported_tags=supported_tags,
                                              inst_code=madrigal_inst_code,
                                              kindats=madrigal_tag)

    """
    _check_madrigal_params(inst_code=inst_code, user=user, password=password)

    # Test input
    if supported_tags is None or kindats is None:
        raise ValueError('Must supply supported_tags and kindats dicts')

    # Raise KeyError if input dictionaries don't match the input
    format_str = supported_tags[inst_id][tag]
    kindat = kindats[inst_id][tag]

    # TODO(#1022, pysat) Note default of `pysat.Instrument.remote_file_list`
    #  for start and stop is None. Setting defaults needed for Madrigal.
    if start is None:
        start = dt.datetime(1900, 1, 1)
    if stop is None:
        stop = dt.datetime.utcnow()

    # Retrieve remote file experiment list
    files = get_remote_filenames(inst_code=inst_code, kindat=kindat, user=user,
                                 password=password, url=url, start=start,
                                 stop=stop)

    filenames = [os.path.basename(file_exp.name) for file_exp in files]

    # Madrigal uses 'h5' for some experiments and 'hdf5' for others
    format_ext = os.path.splitext(format_str)[-1]
    if len(filenames) > 0 and format_ext == '.hdf5':
        file_ext = os.path.splitext(filenames[-1])[-1]
        if file_ext == '.h5':
            format_str = format_str.replace('.hdf5', '.h5')

    # Parse these filenames to grab out the ones we want
    logger.info("Parsing filenames")
    if format_str.find('*') < 0:
        stored = pysat.utils.files.parse_fixed_width_filenames(filenames,
                                                               format_str)
    else:
        stored = pysat.utils.files.parse_delimited_filenames(filenames,
                                                             format_str, '.')

    # Process the parsed filenames and return a properly formatted Series
    logger.info("Processing filenames")
    return pysat.utils.files.process_parsed_filenames(stored,
                                                      two_digit_year_break)


def list_files(tag, inst_id, data_path, format_str=None,
               supported_tags=None, file_cadence=dt.timedelta(days=1),
               two_digit_year_break=None, delimiter=None, file_type=None):
    """Create a Pandas Series of every file for chosen Instrument data.

    Parameters
    ----------
    tag : str
        Denotes type of file to load.  Accepts strings corresponding to the
        appropriate Madrigal Instrument `tags`.
    inst_id : str
        Specifies the instrument ID to load. Accepts strings corresponding to
        the appropriate Madrigal Instrument `inst_ids`.
    data_path : str
        Path to data directory.
    format_str : str or NoneType
        User specified file format.  If None is specified, the default
        formats associated with the supplied tags are used. (default=None)
    supported_tags : dict or NoneType
        Keys are inst_id, each containing a dict keyed by tag
        where the values file format template strings. (default=None)
    file_cadence : dt.timedelta or pds.DateOffset
        pysat assumes a daily file cadence, but some instrument data file
        contain longer periods of time.  This parameter allows the specification
        of regular file cadences greater than or equal to a day (e.g., weekly,
        monthly, or yearly). (default=dt.timedelta(days=1))
    two_digit_year_break : int or NoneType
        If filenames only store two digits for the year, then '1900' will be
        added for years >= two_digit_year_break and '2000' will be added for
        years < two_digit_year_break. If None, then four-digit years are
        assumed. (default=None)
    delimiter : str or NoneType
        Delimiter string upon which files will be split (e.g., '.'). If None,
        filenames will be parsed presuming a fixed width format. (default=None)
    file_type : str or NoneType
        File format for Madrigal data.  Load routines currently accepts 'hdf5',
        'simple', and 'netCDF4', but any of the Madrigal options may be used
        here. If None, will look for all known file types. (default=None)

    Returns
    -------
    out : pds.Series
        A pandas Series containing the verified available files

    """
    # Initialize the transitional variables
    list_file_types = file_types.keys() if file_type is None else [file_type]
    sup_tags = {inst_id: {tag: supported_tags[inst_id][tag]}}
    out_series = list()

    # Cycle through each requested file type, loading the requested files
    for ftype in list_file_types:
        if supported_tags[inst_id][tag].find('{file_type}') > 0:
            sup_tags[inst_id][tag] = supported_tags[inst_id][tag].format(
                file_type=file_types[ftype])

        out_series.append(pysat.instruments.methods.general.list_files(
            tag=tag, inst_id=inst_id, data_path=data_path,
            format_str=format_str, supported_tags=sup_tags,
            file_cadence=file_cadence,
            two_digit_year_break=two_digit_year_break, delimiter=delimiter))

    # Combine the file lists, ensuring the files are correctly ordered
    if len(out_series) == 1:
        out = out_series[0]
    else:
        out = pds.concat(out_series).sort_index()

    return out


def filter_data_single_date(inst):
    """Filter data to a single date.

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument object to which this routine should be attached

    Note
    ----
    Madrigal serves multiple days within a single JRO file
    to counter this, we will filter each loaded day so that it only
    contains the relevant day of data. This is only applied if loading
    by date. It is not applied when supplying pysat with a specific
    filename to load, nor when data padding is enabled. Note that when
    data padding is enabled the final data available within the instrument
    will be downselected by pysat to only include the date specified.

    Examples
    --------
    This routine is intended to be added to the Instrument
    nanokernel processing queue via
    ::

        inst = pysat.Instrument()
        inst.custom_attach(filter_data_single_date)

    This function will then be automatically applied to the
    Instrument object data on every load by the pysat nanokernel.

    Warnings
    --------
    For the best performance, this function should be added first in the queue.
    This may be ensured by setting the default function in a  pysat instrument
    file to this one.

    To do this, within platform_name.py set `preprocess` at the top level.
    ::

        preprocess = pysat.instruments.methods.madrigal.filter_data_single_date

    """
    # Only do this if loading by date!
    if inst._load_by_date and inst.pad is None:
        # Identify times for the loaded date
        idx, = np.where((inst.index >= inst.date)
                        & (inst.index < (inst.date + pds.DateOffset(days=1))))

        # Downselect from all data
        inst.data = inst[idx]

    return


def _check_madrigal_params(inst_code, user, password):
    """Check that parameters requried by Madrigal database are passed through.

    Parameters
    ----------
    inst_code : str or NoneType
        Madrigal instrument code(s), cast as a string.  If multiple are used,
        separate them with commas.
    user : str or NoneType
        The user's names should be provided in field user. Ruby Payne-Scott
        should be entered as Ruby+Payne-Scott
    password : str or NoneType
        The password field should be the user's email address. These parameters
            are passed to Madrigal when downloading.

    Raises
    ------
    ValueError
        Default values of None will raise an error.

    """
    inst_codes = known_madrigal_inst_codes(None)

    if str(inst_code) not in inst_codes.keys():
        raise ValueError(''.join(["Unknown Madrigal instrument code: ",
                                  repr(inst_code), ". If this is a valid ",
                                  "Madrigal instrument code, please update ",
                                  "`pysatMadrigal.instruments.methods.general",
                                  ".known_madrigal_inst_codes`."]))

    if not (isinstance(user, str) and isinstance(password, str)):
        raise ValueError(' '.join(("The madrigal database requries a username",
                                   "and password.  Please input these as",
                                   "user='firstname lastname' and",
                                   "password='myname@email.address' in this",
                                   "function.")))

    return
