# Changelog


This document records all notable changes to ``omni.kit.thumbnails.mdl`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [1.0.27] - 2025-05-08
### Fixed
- update golden images for omni.kit.thumbnails.mdl due to omni.ui Intdrag fix

## [1.0.26] - 2025-03-25
### Fixed
- Fix doc build issues.

## [1.0.25] - 2025-01-09
### Changed
- OMPE-27665: Add python API document.

## [1.0.24] - 2024-05-08
### Change
- Remove omni.kit.viewport.legacy_gizmos dependency

## [1.0.23] - 2023-06-02
### Change
- OM-96684: Fix ETM test failure

## [1.0.22] - 2023-03-20
### Change
- Skip test on linux
- Switch to use pxr render delegate instead of rtx

## [1.0.21] - 2023-02-21
### Change
- Fix errors for python 3.10

## [1.0.20] - 2022-11-09
### Fix
- Isolate thumbnail generation in separate context and viewport

## [1.0.19] - 2022-09-13
### Fix
- Fix mdl thumbnail test

## [1.0.18] - 2022-09-10
### changed
- Ignore some error messages for ETM test
- OM-47795: Select none before generating thumbnail to avoid bounding box

## [1.0.17] - 2022-09-02
### Fix
- Fix preferences page test

## [1.0.16] - 2022-08-31
### Fix
- Fix test in ETM tests for some kit where no Tagging in preferences page

## [1.0.15] - 2022-08-30
### Fix
- Disable linux test since always crash with kit 104

## [1.0.14] - 2022-07-29
### Fix
- Add missed import

## [1.0.13] - 2022-06-25
### Added
- VP2 support

## [1.0.12] - 2022-05-06
### Changed
- Update viewport capture

## [1.0.10] - 2022-02-22
### Changed
- Remove omni.kit.settings

## [1.0.9] - 2022-02-22
### Changed
- Material thumbnail generation settings
### Added
- A preference page for the settings

## [1.0.8] - 2022-02-11
### Changed
- Update viewport interface

## [1.0.7] - 2021-07-26
### Fixed
- Error when destroy

## [1.0.6] - 2021-06-08
### Added
- Retry (max 3 times) if timeout to generate thumbnail
### Changed
- Only check asset loaded event when bind commands found
- Check output file when generation done
- Do not load local template for every thumbnail

## [1.0.5] - 2021-05-29
### Changed
- Change thumbnail template

## [1.0.4] - 2021-05-28
### Added
- Turn off "Fill Resolution" when generating thumbnail
- Support vMaterials

## [1.0.3] - 2021-05-11
### Added
- Generate for multi materials in a usd file

## [1.0.2] - 2021-05-07
### Added
- Generate for single usd material

## [1.0.1] - 2021-04-27
### Changed
- Use local mdl template file

## [1.0.0] - 2021-04-23
### Added
- Initial release.
