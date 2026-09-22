# Changelog

This document records all notable changes to the **omni.kit.window.file_exporter** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.0.33] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [1.0.32] - 2025-03-06
- OMREQ-923: Only set the current directory for selection change in treeview pane.

## [1.0.31] - 2024-10-09
- OM-122859: Update public API.

## [1.0.30] - 2024-04-22
- OM-122859: Update documentation of export handler.

## [1.0.29] - 2024-03-25
- OM-122349: Update api docs for omni.kit.window.file_importer.

## [1.0.28] - 2023-12-18
- Add argument to show_window to provide cancel callback.

## [1.0.27] - 2023-12-15
### Fixed
- OM-117267: Fix typo in test click apply

## [1.0.26] - 2023-11-16
- OMFP-3823: remove calling focus_filename_input after show() to fix crash

## [1.0.25] - 2023-09-19
### Fixed
- OM-109022: Enable the apply button only if the file name does not contain illegal characters.

## [1.0.24] - 2023-08-28
### Fixed
- OM-83885: Load default derectory only if it's server is in current servers.

## [1.0.23] - 2023-08-21
### Fixed
- OM-105857: Don't hide the app's main window when destory dialog.

## [1.0.21] - 2023-04-27
### Added
- Added several api for detaching window(detach_from_main_window)
- Added property for accessing visibility (is_window_visible)
- hide_window now handles hiding detached window
- click_apply now allows for specification of postfix and extension
- click_cancel now allows for cancel_handler specification

## [1.0.20] - 2023-04-10
### Changed
- show_window will use recorded default directory name if kwarg filename_url only passed in a filename

## [1.0.19] - 2023-03-31
### Changed
- Strip out file extensions from filename in on_export if filename ends with any available extension option

## [1.0.18] - 2023-02-22
### Added
- Added test for show_only_folders option.

## [1.0.17] - 2023-02-16
### Changed
- Fixed issue when apply button is disabled when only showing folders.

## [1.0.16] - 2023-01-30
### Changed
- Disable apply button for file bar if no filename is specified.

## [1.0.15] - 2023-01-20
### Changed
- Added show_only_folders option

## [1.0.14] - 2023-01-19
### Changed
- Set file postfix and extension directly rather than restoring from settings

## [1.0.13] - 2023-01-06
### Changed
- Test helper function wait_for_popup returns more precisely to fix race condition in some unittests.

## [1.0.12] - 2022-12-16
### Changed
- Fixed export_handler typing & docstring to align with the implementation.

## [1.0.11] - 2022-11-16
### Changed
- Updated the docs.

## [1.0.10] - 2022-10-24
### Changed
- Decouple USD dependency from extension.

## [1.0.9] - 2022-10-21
### Changed
- Add flag for show_window if file name input should be enabled.

## [1.0.8] - 2022-10-01
### Changed
- Add flag for if file name validation should be performed.

## [1.0.7] - 2022-09-19
### Added
- Added file name validation for file exports, do not allow empty filenames when exporting.

## [1.0.6] - 2022-07-07
### Added
- Added test helper function that waits for UI to be ready.

## [1.0.5] - 2022-06-15
### Added
- Adds test helper.

## [1.0.4] - 2022-04-06
### Added
- Disable unittests from loading at startup.

## [1.0.3] - 2022-03-17
### Added
- Disabled checkpoints.

## [1.0.2] - 2022-02-09
### Added
- Adds click_apply and click_cancel methods.

## [1.0.1] - 2022-02-02
### Added
- Adds postfix and extension options.

## [1.0.0] - 2021-11-05
### Added
- Initial add.
