# Changelog

This document records all notable changes to the **omni.kit.window.popup_dialog** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [2.0.24] - 2024-04-02
### Updated
- OM-122351: Update docs.

## [2.0.23] - 2023-10-16
### Added
- OMFP-2292: added tests to increase the code coverage

## [2.0.22] - 2023-05-25
### Changed
- OM-42020: Able to recreate window when show OptionsMenu

## [2.0.21] - 2023-05-25
### Changed
- OM-95817: Wait a frame to make sure input dialog's field focus correctly

## [2.0.20] - 2023-03-08
### Changed
- Swapped a couple asyncio.ensure_future calls with run_coroutine

## [2.0.19] - 2023-02-01
### Changed
- Add focus method to FormWidget, and FormDialog will focus fields on show

## [2.0.18] - 2023-01-30
### Fixed
- Deleted unreliable unittest

## [2.0.17] - 2023-01-30
### Changed
- Add focused field to FieldDef for FormDialog, input fields can be set to focused

## [2.0.16] - 2022-12-12
### Changed
- Force test to run at 256x256 and add async / wait for omni.ui

## [2.0.15] - 2022-12-12
### Fixed
- Reverts popup flag, otherwise cannot click away the dialog

## [2.0.14] - 2022-12-08
### Fixed
- Removes popup flag from core dialog, which causes drawing issues when dialogs collide

## [2.0.13] - 2022-11-30
### Fixed
- Centre the okay or cancel button when either or both are enabled.

## [2.0.12] - 2022-11-17
### Changes
- Updated doc.

## [2.0.11] - 2022-11-04
### Changes
- Added warning_message kwarg to base dialog class, and ui build for the warning message.

## [2.0.10] - 2022-08-23
### Changes
- Added set_cancel_clicked_fn to base dialog class.

## [2.0.9] - 2022-07-06
### Changes
- Added title bar.

## [2.0.8] - 2022-05-26
### Changes
- Updated styling

## [2.0.7] - 2022-04-06
### Changes
- Fixes Filepicker delete items dialog.

## [2.0.6] - 2022-03-31
### Changes
- Added unittests and created separate widgets and dialogs.

## [2.0.5] - 2021-11-01
### Changes
- Added set_value method to programmatically set an options menu value.

## [2.0.4] - 2021-11-01
### Changes
- Add method to MessageDialog for updating the message text.

## [2.0.3] - 2021-09-07
### Changes
- Makes all dialog windows modal.
- Option to hide Okay button.
- Better control of window placement when showing it.

## [2.0.2] - 2021-06-29
### Changes
- Binds ENTER key to Okay button, and ESC key to Cancel button.

## [2.0.1] - 2021-06-07
### Changes
- More thorough destruction of class instances upon shutdown.

## [2.0.0] - 2021-05-05
### Changes
- Update `__init__` of the popup dialog to be explicit in supported arguments
- Renamed click_okay_handler and click_cancel_handler to ok_handler and cancel_handler
- Added support for `Enter` and `Esc` keys.
- Renamed okay_label to ok_label

## [1.0.1] - 2021-02-10
### Changes
- Updated StyleUI handling

## [1.0.0] - 2020-10-29
### Added
- Ported OptionsMenu from content browser
- New OptionsDialog derived from OptionsMenu

## [0.1.0] - 2020-09-24
### Added
-   Initial commit to master.
