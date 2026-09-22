# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.5.14] - 2025-07-30
- Do not show import options by default
- Set default import settings assuming IndeX and no cache generation
- Show error window on drag and drop

## [1.5.13] - 2025-05-28
- Fix e57 load of Nucleus files

## [1.5.12] - 2025-05-28
- Fix USD not loaded when after failed import

## [1.5.11] - 2025-03-19
- Fix renderer option

## [1.5.9] - 2025-03-18
- Use ConvertToPotreeCommand instead of ConvertToPotreeAsyncCommand in potree cache job

## [1.5.8] - 2025-03-14
- Fix default renderers in the E57 importer

## [1.5.7] - 2025-03-13
- Add renderer option to the E57 importer

## [1.5.6] - 2025-02-25
- Fix import if a very old version of PCM is loaded

## [1.5.5] - 2025-02-24
- Fixed import of multiple USD cached e57 files

## [1.4.8] - 2025-02-20
- Fixed import of multiple USD cached e57 files

## [1.5.4] - 2025-01-16
- Fix path

## [1.5.3] - 2025-01-15
- Support export folder for cached usd from the e57

## [1.5.2] - 2025-01-15
- Fix Flow check version error and Nucleus files conversion

## [1.5.1] - 2025-01-15
- Add python public APIs

## [1.5.0] - 2024-11-25
- Update kit-sdk

## [1.4.3] - 2024-07-18
- Loading Lidar points into a single Point prim

## [1.4.2] - 2024-07-17
- Added Lidar bin fileformat importer

## [1.4.1] - 2024-06-19
- Fixes in importing PTS files

## [1.4.0] - 2024-06-18
- Added PTS fileformat importer

## [1.3.10] - 2024-06-11
- Loading E57 with existing USD will not do the conversion again

## [1.3.9] - 2024-06-07
- Update copyright, use service farm uri settings from PCM

## [1.3.7] - 2024-06-04
- Update point cloud prim source after Potree conversion

## [1.3.5] - 2024-05-14
- Create point cloud prim when conversion task is completed

## [1.3.4] - 2024-04-11
- Change importing pointcloud cache path to the source

## [1.3.3] - 2024-01-25
- Missing test dependency

## [1.3.2] - 2024-01-25
- Missing error icon

## [1.3.1] - 2024-01-19
- Tests without a dependency on PCM

## [1.3.0] - 2024-01-19
- Making most of the extensions optional and loading e57 as UsdGeom points by default

## [1.2.36] - 2024-01-11
- Changing the cache path

## [1.2.34] - 2023-12-19
- Command rename from E57 to more general

## [1.2.33] - 2023-12-11
- Job definitions update

## [1.2.32] - 2023-12-08
- Supporting multiple sample locations
- Moving sample locatations to a setting

## [1.2.31] - 2023-12-07
- Adding sample E57 files to the pointcloud browser

## [1.2.30] - 2023-12-07
- Adjust test

## [1.2.29] - 2023-12-05
- Adding cache path tests for E57 potree api delegate

## [1.2.28] - 2023-12-04
- Moving E57 Potree API delegate to omni.kit.pointclouds

## [1.2.27] - 2023-11-23
- Job run to generated potree is chained request_e57_cache_and_vdb_task instead of request_e57_to_vdb

## [1.2.26] - 2023-11-23
- Adjust tests

## [1.2.25] - 2023-11-16
- Adjust tests

## [1.2.23] - 2023-11-08
- Fix obsolete import path adjustment

## [1.2.22] - 2023-11-03
- PTS import with no renderer selected will set rtx skip flag to false

## [1.2.21] - 2023-10-03
- Check export path is not same as the cache path

## [1.2.20] - 2023-09-26
- Unlock flowusd version

## [1.2.19] - 2023-09-22
- RunVdbTask command changed to request_e57_to_vdb

## [1.2.18] - 2023-09-22
- Lock flowusd version

## [1.2.17] - 2023-09-19
- RunVdbTask command to test request_e57_cache_and_vdb_task

## [1.2.15] - 2023-09-14
- Adjust tests to be compatible with both 105.1 and 105.2

## [1.2.12] - 2023-09-12
- Fix local cache generation importer option

## [1.2.10] - 2023-09-04
- Update Kit SDK, fix asset path

## [1.2.8] - 2023-08-25
- Setting for triggering local cache generation

## [1.2.7] - 2023-08-22
- Appending cloud.js to the PointCloud prim source path

## [1.2.6] - 2023-08-16
- E57 Importer UI has default Points selected

## [1.2.5] - 2023-08-16
- E57 Importer UI changes to reflect loading cached files

## [1.2.4] - 2023-08-15
- In place conversion only allowed for local files

## [1.2.3] - 2023-08-15
- Cache options in the importer UI

## [1.2.2] - 2023-08-02
- Settings to use cache and cache root

## [1.2.1] - 2023-07-28
- Create directory for potree export

## [1.2.0] - 2023-07-14
- Simplified importer UI

## [1.1.1] - 2023-06-22
- Added Potree conversion option
## [1.1.0] - 2023-05-09
- IndeX renderer option

## [1.1.0] - 2023-05-09
- IndeX renderer option

## [1.0.4] - 2023-05-02
- No rendering option

## [1.0.3] - 2023-05-02
- RTX on/off option

## [1.0.2] - 2023-03-31
- Import options UX

## [1.0.1] - 2023-03-29
- Added selection of point cloud preset

## [1.0.0] - 2023-03-18
### Changes
- Async and multithreaded import
- Point transforms are kept in scan's xforms (OM-52424)
- Improved UX: import progress, option to cancel import

## [0.1.0] - 2023-03-14
### Changed
- Python 3.10 update

## [0.0.17] - 2023-02-13
### Changed
- Display color interpolation set to vertex (OM-72158)

## [0.0.15] - 2022-11-09
### Changed
- PTS importer viewport error fix

## [0.0.14] - 2022-09-05
### Changed
- Add test for converting to usd

## [0.0.13] - 2022-08-25
### Changed
- Fix test to ignore unsaved on exit

## [0.0.12] - 2022-05-25
### Changed
- Added pts importer

## [0.0.11] - 2022-05-17
### Added
- Option to center pointcloud on import

## [0.0.10] - 2022-03-25
### Changed
- Update flow menu command

## [0.0.9] - 2021-09-06
### Changed
- Add omni:rtx:skip to imported pointclouds by default

## [0.0.8] - 2021-08-16
### Changed
- Added unit tests and updated dependencies

## [0.0.7] - 2021-07-19
### Changed
- Updated rendering option to create global pointcloud

## [0.0.6] - 2021-07-09
### Changed
- Added ability to convert to USD
- Made e57 loading error more generic

## [0.0.5] - 2021-07-01
### Changed
- Updated default options to mirror new flow features
- Made the extension featured

## [0.0.4] - 2021-06-25
### Changed
- Fixed Xform transform operation order in copied scans

## [0.0.3] - 2021-06-24
### Changed
- Add copy/combine option on import

## [0.0.2] - 2021-06-23
### Changed
- Changed name to Pointclouds
- Changed notes for default settings
- Prompt restart if e57 fails to import

## [0.0.1] - 2021-05-25
### Changed
- Added CHANGELOG.md
- Added README.md
- Added index.rst
- Added flowusd and e57 dependencies
