Change Log
==========
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

[0.1.0] - 2023-04-11
--------------------
* Enhancements
   * Improved definitions of general and GNSS meta data
   * Removed unused logic in cleaning routines
   * Moved warning for no cleaning of JRO ISR data to preprocess
   * Added a general Madrigal instrument for time-series data
   * Added functions to specify all known Madrigal instrument codes and
     file formats
   * Adapted general listing functions to allow file formats with '*' wildcards
     between '.' delimiters, required for some Madrigal file formats
   * Standardized the Instrument method kwarg defaults
   * Added 'site' tag to the GNSS TEC Instrument
   * Added support for varied use of `two_digit_year_break` to
     `methods.general.list_remote_files`
   * Implemented `two_digit_year_break` support for `vtec` GNSS TEC Instrument
   * Implemented directory creation function in pysat
* Documentation
   * Added examples for JRO and GNSS data
   * Improved the docstring and CHANGELOG style
* Testing
   * Added unit tests for DMSP, general, JRO, and GNSS methods
   * Added the packaging module to handle version logic
   * Added quick-fail for main pytest command
* Bug
   * Fixed bugs in the coordinate conversion functions
* Maintenance
   * Updated GitHub action and NEP29 versions
   * Updated the minimum Madrigal version to allow HDF4 downloads
   * Update pysat instrument testing suite, pytest syntax
   * Add manual GitHub Actions tests for pysat RC

[0.0.4] - 2021-06-11
--------------------
* Made changes to structure to comply with updates in pysat 3.0.0
* Migrated CI tests from Travis CI to GitHub Actions
* Deprecations
  * Restructed Instrument methods, moving `madrigal` to `general` and extracting
    local methods from the instrument modules to platform-specific method files
  * Cycled testing support to cover Python 3.7-3.9
* Enhancements
  * Added coords from pysat.utils
  * Added Vertical TEC Instrument
  * Added documentation
  * Added load routine for simple formatted data
  * Expanded feedback during data downloads
  * Updated documentation configuration to improve maintainability
  * Updated documentation style, displaying logo on sidebar in html format
  * Changed zenodo author name format for better BibTeX compliance
  * Updated CONTRIBUTING and README information
* Bug Fix
  * Updated Madrigal methods to simplify compound data types and enable
    creation of netCDF4 files using `Instrument.to_netcdf4()`
  * Updated load for multiple files in pandas format
  * Fixed remote listing routine to return filenames instead of experiments
  * Fixed bug introduced by change in xarray requiring engine kwarg
  * Fixed bug that would not list multiple types of files
  * Updated JRO ISR drift variable names

[0.0.3] - 2020-06-15
--------------------
* pypi compatibility

[0.0.2] - 2020-05-13
--------------------
* zenodo link

[0.0.1] - 2020-05-13
--------------------
* Alpha release
