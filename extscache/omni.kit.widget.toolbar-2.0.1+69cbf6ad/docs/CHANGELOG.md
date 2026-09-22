# CHANGELOG

This document records all notable changes to ``omni.kit.window.toolbar`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`.

## [2.0.1] - 2025-04-15
### Fixed
- OMPE-43816: ensured some extension enable/disable hook objects are cleaned up.

## [2.0.0] - 2025-01-20
### Changed
- OMPE-31531: Remove deprecated APIs

## [1.7.3] - 2024-10-16
### Fixed
- OMPE-31330: Fix typo of shortcut of rotation.

## [1.7.3] - 2024-10-16
### Fixed
- OMPE-22600: Deprecated get_data_path from public api.

## [1.7.2] - 2024-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.7.1] - 2024-04-22
### Removed
- Removed docs for submodules.

## [1.7.0] - 2024-04-04
### Added
- Improved documentation.

## [1.6.1] - 2024-02-29
### Changed:
- OM-110315: OM-121433: Add custom radio entry to Move tool

## [1.6.0] - 2023-12-01
### Changed:
- OM-110315: Apply new options menu

## [1.5.7] - 2023-09-21
### Fixed:
- OM-109903: Deregister hotkey before register again when rebuilding toolbar

## [1.5.6] - 2023-08-01
### Fixed:
- OM-101580: Fixed Hotkey error where button is not created before assigning callback(s).

## [1.5.5] - 2023-07-13
### Fixed
- OM-101803: Fixed error accessing _play_button and _stop_button

## [1.5.4] - 2023-06-20
### Fixed
- Toggling selection mode with the T hotkey will cause the icon to disappear sometimes

## [1.5.3] - 2023-06-13
### Fixed
- Replace log warning deprecation by log_deprecation

## [1.5.2] - 2023-06-06
### Changed
- Removed fallback hotkey that directly hooks into carb.input.

## [1.5.1] - 2023-06-05
### Changed
- Fixed selection icon not changing when toggling prim/model mode

## [1.5.0] - 2023-05-10
### Changed
- Rename `omni.kit.window.toolbar` into `omni.kit.widget.toolbar`

## [1.3.8] - 2023-04-25
### Changed
- Fix for selection settings not changing when icon is clicked

## [1.3.7] - 2023-04-25
### Added
- Added icon updates for select modes

## [1.3.6] - 2023-03-28
### Added
- Added context menu to selection button to allow for kind and/or type selection filters

## [1.3.5] - 2023-03-27
### Changed
- Timeline control buttons are hidden when the timeline has a director.
## [1.3.4] - 2023-02-17
### Changed
- Prevent the `Q` and `R` hotkeys from being applied during camera manipulation.

## [1.3.3] - 2022-09-26
### Changed
- Updated to use `omni.kit.actions.core` and `omni.kit.hotkeys.core` for hotkeys.

## [1.3.2] - 2022-09-01
### Changed
- Context menu without compatibility mode.

## [1.3.1] - 2022-06-23
### Changed
- Change how hotkey `W` is skipped during possible camera manipulation.

## [1.3.0] - 2022-05-17
### Changed
- Changed Snap button to legacy button. New snap button will be registered by extension.

## [1.2.4] - 2022-04-19
### Fixed
- Slienced menu_changed error on create exit

## [1.2.3] - 2022-04-06
### Fixed
- Message "Failed to acquire interface while unloading all plugins"

## [1.2.1] - 2021-06-22
### Added
- Fixed height of increment settings window

## [1.2.0] - 2021-06-04
### Added
- Moved all built-in toolbutton's flyout menu to use omni.kit.context_menu, making it easier to add additional menu items to exiting button from external extension.

## [1.1.0] - 2021-04-16
### Added
- Added "Context" concept to toolbar that can be used to control the effective scope of tool buttons.


## [1.0.0] - 2021-03-04
### Added
- Started tracking changelog. Added tests.
