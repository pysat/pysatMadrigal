Loading DMSP IVM
================

pysatMadrigal uses `pysat <https://github.com/pysat/pysat>`_ to download, load,
and provide an analysis framework for data sets archived at the Madrigal
database.  As specified in the
`pysat tutorial <https://pysat.readthedocs.io/en/latest/tutorial.html>`_,
data may be loaded using the following commands.  Defense Meteorological
Satellite Program (DMSP) Ion Velocity Meter (IVM) data is used as an example.

::


   import datetime as dt
   import pysat
   import pysatMadrigal as py_mad

   stime = dt.datetime(2012, 5, 14)
   ivm = pysat.Instrument(inst_module=py_mad.instruments.dmsp_ivm,
                          tag='utd', inst_id='f15', update_files=True)
   ivm.download(start=stime, user="Name+Surname", password="email@org.inst")
   ivm.load(date=stime)
   print(ivm)


The output includes a day of data with UTDallas quality flags from the F15
spacecraft (as implied by the `tag` and `inst_id`), for the specified date.
At the time of publication this produces the output shown below.

::

   pysat Instrument object
   -----------------------
   Platform: 'dmsp'
   Name: 'ivm'
   Tag: 'utd'
   Instrument id: 'f15'

   Data Processing
   ---------------
   Cleaning Level: 'clean'
   Data Padding: None
   Keyword Arguments Passed to load: {'xarray_coords': [], 'file_type': 'hdf5'}
   Keyword Arguments Passed to list_remote_files: {'user': None, 'password': None, 'url': 'http://cedar.openmadrigal.org', 'two_digit_year_break': None}
   Custom Functions: 0 applied

   Local File Statistics
   ---------------------
   Number of files: 1
   Date Range: 31 December 2014 --- 1 January 2015

   Loaded Data Statistics
   ----------------------
   Date: 31 December 2014
   DOY: 365
   Time range: 31 December 2014 00:00:04 --- 31 December 2014 23:18:20
   Number of Times: 4811
   Number of variables: 30

   Variable Names:
   year     month    day      
               ...            
   rms_x    sigma_vy sigma_vz 

   pysat Meta object
   -----------------
   Tracking 7 metadata values
   Metadata for 30 standard variables
   Metadata for 0 ND variables


