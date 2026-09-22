# Changelog

This document records all notable changes to the **omni.kit.window.file_importer** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.1.18] - 2025-05-30
### Changed
- OMPE-49994: File path validation should be done asynchronously to avoid blocking the main thread.

## [1.1.17] - 2025-04-28
### Changed
- OMPE-45235: Fix test failed in OVC2.

## [1.1.16] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [1.1.15] - 2025-03-06
- OMREQ-923: Only set the current directory for selection change in treeview pane.

## [1.1.14] - 2024-10-09
### Changed
- OMPE-22606: Update public API.

## [1.1.13] - 2024-07-23
### Changed
- Fixed private class access (accessing functions/variables with _)

## [1.1.12] - 2024-04-22
### Changed
- OM-122859: Update documentation of import handler.

## [1.1.11] - 2024-03-25
### Changed
OM-122349: Update api docs for omni.kit.window.file_importer.

## [1.1.10] - 2024-03-07
### Fixed
OMPRW-957: Supports multi-selections as an option.

## [1.1.9] - 2024-02-01
### Fixed
OMPRW-733 & OMPRW-734: Navigate to the folder when apply a folder path.

## [1.1.8] - 2024-01-25
### Fixed
- OM-119336: Fix couldn't import checkpoint file.

## [1.1.7] - 2023-12-15
### Fixed
- OM-117267: Fix typo in test click apply

## [1.1.6] - 2023-11-16
### Changed
- OMFP-3823: remove calling focus_filename_input after show() to fix crash

## [1.1.5] - 2023-11-02
### Added
- OM-104306: Entering a valid path would open the file instead of just navigating to it inside the browser window.

## [1.1.4] - 2023-09-21
### Fixed
- OM-109022: Enable the apply button only if the file name does not contain illegal characters.

## [1.1.3] - 2023-09-20
### Fixed
- OM-88666: Fix for file picker open button not disabled during multiple selection.

## [1.1.2] - 2023-08-22
### Added
- OM-39070: Added `should_validate` kwarg to show_window to turn on validation on file existence

## [1.1.1] - 2023-08-28
### Fixed
- OM-83885: Load default derectory only if it's server is in current servers.

## [1.1.0] - 2023-08-09
### Changed
- Match new options button in file picker

## [1.0.22] - 2023-11-02
### Changed
- OMFP-3205: More defensive coding to clear ownership.

## [1.0.21] - 2023-06-02
### Changed
- Delay computation of usd file exts so it doesn't take up startup time

## [1.0.20] - 2023-05-31
### Changed
- Added `show_only_folders` to import show_window to filter only folders, and allow empty filename to apply

## [1.0.19] - 2023-05-10
### Changed
- Focus keyboard on filename input field on show

## [1.0.18] - 2023-05-10
### Fixed
- File importer default extension handler now correctly filters file extensions

## [1.0.17] - 2023-04-27
- Added several api for detaching window(detach_from_main_window)
- Added property for accessing visibility (is_window_visible)
- hide_window now handles hiding detached window
- click_apply now allows for specification of postfix and extension
- click_cancel now allows for cancel_handler specification

## [1.0.16] - 2023-03-06
### Changed
- Added timestamp

## [1.0.15] - 2023-02-17
### Changed
- Added `hide_window_on_import` to file importer show_window to allow caller to handle the dialog accept in on_import
  handler.

## [1.0.14] - 2023-01-30
### Changed
- Disable apply button for file bar if no filename is specified.

## [1.0.13] - 2023-01-17
### Changed
- Added `get_config_menu_settings` & `set_config_menu_settings`

## [1.0.12] - 2023-01-19
### Changed
- Set file postfix and extension directly rather than restoring from settings

## [1.0.11] - 2023-01-06
### Changed
- Test helper function wait_for_popup returns more precisely to fix race condition in some unittests.

## [1.0.10] - 2023-01-03
### Changed
- Made omni.usd extension an optional dependency.

## [1.0.9] - 2022-12-20
### Changed
- Improve the file extension filter.

## [1.0.8] - 2022-11-08
### Added
- Updated the docs.

## [1.0.7] - 2022-10-13
### Added
- Added `select_items_async` to file_importer ext and test helper.

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
- Selected file extension defaults to USD type.

## [1.0.2] - 2022-02-09
### Added
- Adds click_apply and click_cancel functions.

## [1.0.1] - 2022-02-03
### Added
- Adds postfix and extension options.

## [1.0.0] - 2021-11-16
### Added
- Initial add.
