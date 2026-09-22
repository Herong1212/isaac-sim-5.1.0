# Changelog

This document records all notable changes to the **omni.kit.hotkeys.window** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.4.9] - 2025-02-28
### Changed
- Add setting "--/exts/omni.ui/Image/syncTextureLoad=true" for test to make sure images loaded when comparing to golden

## [1.4.8] - 2024-12-04
### Changed
- OMPE-24897: OVC: RuntimeError: Failed to acquire interface: card::windowing::IWindowing

## [1.4.7] - 2024-12-03
### Changed
- OMPE-24897: No carb.windowing on OVC

## [1.4.6] - 2024-11-04
### Changed
- OMPE-24897: Support different keyboard layouts with carb.windowing.translate_key

## [1.4.5] - 2024-04-09
### Changed
- OM-123086: Use data assertion instead of UI comparison

## [1.4.4] - 2023-11-17
### Changed
- OM-112134: Able to delete system hotkeys

## [1.4.3] - 2023-11-02
### Changed
- Updated menus to use omni.kit.menu.utils

## [1.4.2] - 2023-07-31
### Changed
- Update test for changes in omni.kit.hotkeys.core

## [1.4.1] - 2023-10-30
### Changed
- OMFP-3332: Fix error when context hotkey enabled
- Increase test coverage to 86.44%

## [1.4.0] - 2023-07-04
### Changed
- OM-97997: Apply new filter button

## [1.3.1] - 2023-03-22
### Changed
- OM-91490: Fix error when exporting preset

## [1.3.0] - 2023-03-22
### Added
- OM-77340: Add options menu for keyboard layout

## [1.2.4] - 2023-02-11
### Changed
- Update style for HighlightLabel changes

## [1.2.3] - 2023-02-13
### Changed
- Fixed a couple random-order tests

## [1.2.2] - 2023-01-13
### Changed
- OM-63678: For user hotkeys, show different color and no reset
- Update restore warning message

## [1.2.1] - 2022-11-28
### Changed
- OM-66069: The pencil should appear on hover over the entire lane

## [1.2.0] - 2022-11-21
### Changed
- OM-55820: Linting for omni.kit.hotkeys.window

## [1.1.4] - 2022-10-25
### Changed
- Update docs

## [1.1.3] - 2022-10-18
### Changed
- OM-66070: shift buttons in warning dialog to bottom right
- OM-66069: show edit/delete image when item selected or hovered
- OM-66067: Auto resize widgets in Actions column

## [1.1.2] - 2022-10-17
### Changed
- OM-65558: Warn user before restore defaults
- Update UI since style moved to Actions Window changed

## [1.1.1] - 2022-10-12
### Changed
- OM-65434: Fix issue that "On Release" does not work
### Added
- OM-65374: Add filter for "Windows"

## [1.1.0] - 2022-10-10
### Added
- Highlight search result
### Changed
- Fix crash issue when changing hotkey during searching

## [1.0.10] - 2022-10-08
### Changed
- Text/image color of Window column when selected

## [1.0.9] - 2022-10-07
### Added
- OM-64993: instruct what to do when adding a key binding

## [1.0.8] - 2022-10-06
### Changed
- When searching or filtering, only show categories have children

## [1.0.7] - 2022-10-05
### Changed
- No case sensitive for searching
- Show background rectangle as branch widget for Window column when no sub hotkeys found for search/filter

## [1.0.6] - 2022-10-01
### Changed
- Show background color for Window category
- Always show Add Action button instead of hovered only

## [1.0.5] - 2022-09-28
### Added
- Add Option menu to Restore Defaults
### Changed
- OM-63810: Fix height of widget in window column to be 28 for do not change when Add Actions displayed

## [1.0.4] - 2022-09-27
### Added
- "Remove" icon to clean input key
### Changed
- Do not show window title with UUID in window picker
- Auto show actions picker when adding action

## [1.0.3] - 2022-09-26
### Changed
- Always capture key for editor (double click to clean key input)
- Exit capture if tree refreshed or window invisible
- Change the filter/option window to right align with widget to make sure it will be not out of window
- Add feature flag

## [1.0.2] - 2022-09-22
### Changed
- Fix display error when no key input
- Make window search work

## [1.0.1] - 2022-09-20
### Added
- Windows picker
- Show "Add Window"
### Changed
- Increase height of actions picker
- Enable empty key

## [1.0.0] - 2022-08-22
- First version
