# CHANGELOG

This document records all notable changes to ``omni.kit.window.toolbar`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`.

## [2.0.0] - 2025-01-20
### Changed
- OMPE-31534: Remove deprecated APIs

## [1.6.2] - 2024-09-25
### Changed
- OMPE-22613: Remove unnecessary public API from python_api.md

## [1.6.1] - 2024-02-27
### Changed
- Made omni.kit.context_menu optional import

## [1.6.0] - 2023-12-13
### Changed
- Update golden images since options menu in omni.kit.widget.toolbar changed

## [1.5.6] - 2023-11-02
### Changed
- Updated menus to use omni.kit.menu.utils

## [1.5.5] - 2023-10-19
### Fixed
- Improved deprecated warning to include source
- Prevented omni.kit.window.toolbar from generating deprecated warnings

## [1.5.4] - 2023-06-27
### Fixed
- Fixed toolbar icons sometimes not displaying.

## [1.5.3] - 2023-06-27
### Fixed
- Context menu invocation error from previous changes.

## [1.5.2] - 2023-06-07
### Changed
- Updated test dependencies.

## [1.5.1] - 2023-05-25
### Fixed
- Remove deprecated warning and use `omni.kit.app.log_deprecation()`

## [1.5.0] - 2023-05-10
### Changed
- Create `omni.kit.widget.toolbar` from `omni.kit.window.toolbar`

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
