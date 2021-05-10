# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.0.4] - TBD
- Made changes to structure to comply with updates in pysat 3.0.0
- Migrated CI tests from Travis CI to GitHub Actions
- Deprecations
  - Restructed Instrument methods, moving `madrigal` to `general` and extracting
    local methods from the instrument modules to platform-specific method files
- Enhancements
  - Added coords from pysat.utils
  - Added Vertical TEC Instrument
  - Added documentation
- Bug Fix
  - Updated madrigal methods to simplify compound data types and enable
    creation of netCDF4 files using `Instrument.to_netcdf4()`.
  - Updated load for multiple files in pandas format
  - Fixed remote listing routine to return filenames instead of experiments

## [0.0.3] - 2020-06-15
- pypi compatibility

## [0.0.2] - 2020-05-13
- zenodo link

## [0.0.1] - 2020-05-13
- Alpha release
