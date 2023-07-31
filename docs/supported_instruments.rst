Supported Instruments
=====================

DMSP_IVM
--------

Supports the Defense Meteorological Satelitte Program (DMSP) Ion Velocity
Meter (IVM) Madrigal data.


.. automodule:: pysatMadrigal.instruments.dmsp_ivm
   :members:

DMSP_SSJ
--------

Supports the Defense Meteorological Satelitte Program (DMSP) Special Sensor J
(SSJ) Madrigal data.


.. automodule:: pysatMadrigal.instruments.dmsp_ssj
   :members:

GNSS_TEC
--------

The Global Navigation Satellite System (GNSS) Total Electron Content (TEC)
provides a measure of column plasma density over the globle.  The Madrigal
TEC is provided by MIT Haystack.

.. automodule:: pysatMadrigal.instruments.gnss_tec
   :members:

JRO_ISR
-------

The incoherent scatter radar (ISR) at the
`Jicamarca Radio Observatory <http://jro.igp.gob.pe/english/>`_ regularly
measures the velocity, density, and other ionospheric characteristics near the
magnetic equator over Peru.

.. automodule:: pysatMadrigal.instruments.jro_isr
   :members:


Madrigal_Dst
------------

An instrument for the Madrigal Dst index data.  This data set spans the years
of 1957 through a period close to today, with all data saved in a single file.
Because of this, you only need to download the data once and any desired time
period may be loaded (unless you require a time between your last download and
now).

.. automodule:: pysatMadrigal.instruments.madrigal_dst
   :members:


Madrigal_Geoind
---------------

An instrument for the Madrigal geomagnetic index data.  This data set spans the
years of 1950 through a period close to today, with all data saved in a single
file. Because of this, you only need to download the data once and any desired
time period may be loaded (unless you require a time between your last download
and now).

.. automodule:: pysatMadrigal.instruments.madrigal_geoind
   :members:


Madrigal_Pandas
---------------

A general instrument for Madrigal time-series data.  This
:py:class:`pysat.Instrument` uses Madrigal instrument codes and kindats to
support the use of any of the Madrigal time-series data sets.  There are some
further constraints in that the data set's Madrigal naming convention must be
parsable by pysat.  Currently three Madrigal instrument codes are supported by
this :py:class:`pysat.Instrument`.  When possible, using a specific instrument
module is recommended, since that instrument module will have additional
support (e.g., cleaning methods, experiment acknowledgements, and references).

.. automodule:: pysatMadrigal.instruments.madrigal_pandas
   :members:


NGDC_AE
-------

An instrument for the Geophysical indices from NGDC, which include AE AL, AU,
and AO.  The :py:attr:`name` is AE due to the Madrigal naming conventions.  The
data set spans the years of 1978 through 1987, will all data saved in a single
file.  Because of this, you only need to download the data once and any desired
time period may be loaded.

.. automodule:: pysatMadrigal.instruments.ngdc_ae
   :members:


OMNI2_IMF
---------

An instrument for the interplanetary magnetic field (IMF) data from Omni 2. The
data starts in 1963 and the entire data set is contained in a single file.  The
file is occasionally updated, and so obtaining the most recent data means that
all historic data must also be downloaded (or re-downloaded). OMNI data may
also be obtained more directly using
`pysatNASA <https://pysatnasa.readthedocs.io/en/latest/supported_instruments.html#omni-hro>`_.

.. automodule:: pysatMadrigal.instruments.omni2_imf
   :members:
