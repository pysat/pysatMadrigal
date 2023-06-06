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


Madrigal_Pandas
---------------

A general instrument for Madrigal time-series data.  This
:py:class:`pysat.Instrument` uses Madrigal instrument codes and kindats to
support the use of any of the Madrigal time-series data sets.  There are some
further constraints in that the data set's Madrigal naming convention must be
parsable by pysat.  Currently nine Madrigal instrument codes are supported by
this :py:class:`pysat.Instrument`.  When possible, using a specific instrument
module is recommended, since that instrument module will have additional
support (e.g., cleaning methods, experiment acknowledgements, and references).

.. automodule:: pysatMadrigal.instruments.madrigal_pandas
   :members:


      
