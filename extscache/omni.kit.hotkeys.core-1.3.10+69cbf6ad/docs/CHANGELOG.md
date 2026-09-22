# Changelog

This document records all notable changes to the **omni.kit.hotkeys.core** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.3.10] - 2024-12-04
### Changed
- OMPE-24897: OVC: RuntimeError: Failed to acquire interface: card::windowing::IWindowing

## [1.3.9] - 2024-12-03
### Changed
- OMPE-24897: No carb.windowing on OVC

## [1.3.8] - 2024-11-04
### Changed
- OMPE-24897: Support different keyboard layouts with carb.windowing.translate_key

## [1.3.7] - 2024-09-25
### Changed
- OMPE-22565: add KeyboardLayoutDelegate in public API

## [1.3.6] - 2024-09-23
### Changed
- OMPE-21262: Fix issue that hotkey not work if key combinations are exchanged when switch Keyboard layout 

## [1.3.5] - 2024-01-24
### Changed
- OM-118968: Window "Debug##Default" should be ignored in hotkey trigger

## [1.3.4] - 2024-01-18
### Fixed
- OMPRW-513: Fix for hotkeys can still be triggered on destroyed windows.

## [1.3.3] - 2024-01-09
### Added
- OM-117920: Send deregister event when restore user hotkey

## [1.3.2] - 2023-11-17
### Added
- Add disable_hotkey to disable system hotkeys

## [1.3.1] - 2023-07-31
### Added
- OM-76181: isolated modifier keys are not invalid hotkey, warn if they are used.

## [1.3.0] - 2023-07-20
### Added
- OM-102413: Add setting for hotkey allow list

## [1.2.3] - 2023-07-19
### Added
- OM-97180: Add setting to globally disable all hotkeys

## [1.2.2] - 2023-06-21
### Changed
- OM-98697: TAB is a valid key for QuickSearch window

## [1.2.1] - 2023-04-13
### Changed
- OM-88070: Bring docs up to standards for omni.kit.hotkeys.core

## [1.2.0] - 2023-03-22
### Added
- OM-77340: Add keyboard layouts with 3 defaults: U.S., German and French

## [1.1.1] - 2023-01-13
### Changed
- OM-63678: Add API to check if hotkey is user defined
- OM-70929: change extension category from "Rendering" to "Internal"

## [1.1.0] - 2022-11-21
### Changed
- OM-55820: Linting for omni.kit.hotkeys.core

## [1.0.8] - 2022-11-10
### Changed
- OM-67801: Filter keyboard event only

## [1.0.7] - 2022-10-26
### Changed
- OM-67426: Change "KEY_X" to "X" in key string. For example, "KEY_1" to "1".

## [1.0.6] - 2022-10-12
### Changed
- OM-65313: Clear saved hotkeys from user config if restore default
- OM-65505: Make get hovered window work for docked ui.ToolBar

## [1.0.5] - 2022-10-05
### Changed
- Only check KEY_PRESS and KEY_RELEASE event for hotkey (ignore KEY_CHAR and KEY_REPEAT)

## [1.0.4] - 2022-09-28
### Added
- Add API to restore all hotkeys

## [1.0.3] - 2022-09-27
### Changed
- Support different DPI when finding hovered window

## [1.0.2] - 2022-09-26
### Added
- Add feature flag

## [1.0.1] - 2022-09-23
### Added
- Add fastShutdown for test since it failed in 104

## [1.0.0] - 2022-05-23
### Added
- First release
