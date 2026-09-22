# Changelog

## [2.6.1] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [2.6.0] - 2025-03-31
### Changed
- OMPE-41172: Added persistent setting for show inactive prims in stage window.

## [2.5.11] - 2024-11-26
### Added
- OMPE-25213: Add setting of stage widget setting show_abstract_prim and default to True.

## [2.5.10] - 2024-06-05
### Fixed
- OMPE-10552: Fix issue with show_undefined_prims settings not reflected in stage window.

## [2.5.9] - 2024-05-30
### Changed
- Initialize selection before visibility changed listener.

## [2.5.8] - 2024-03-26
### Changed
- Add docs for stage window.

## [2.5.7] - 2024-03-12
### Changed
- Add missing omni.kit.context_menu dependency to tests.

## [2.5.6] - 2024-02-27
### Changed
- Make omni.kit.window.drop_support dependency optional

## [2.5.5] - 2024-02-23
### Changed
- OM-120427: Changed search field to be dependent on omni.kit.widget.searchfield.

## [2.5.4] - 2023-11-02
### Changed
- Updated menus to use omni.kit.menu.utils

## [2.5.3] - 2023-10-18
### Added
- Added `get_treeview`, `get_delegate` and `get_widget` functions

## [2.5.2] - 2023-10-17
### Fixed
- OM-112296: Add reset user flag for test to fix flaky test.

## [2.5.1] - 2023-10-13
### Added
- OMFP-2281: Improve test code coverage.

## [2.5.0] - 2023-08-09
### Added
- Update golden since option button in stage widget changed

## [2.4.1] - 2023-07-31
### Added
- Add options to filter undefined prims.

## [2.4.0] - 2023-04-06
### Added
- Update golden since filter button in stage widget changed

## [2.3.13] - 2023-04-06
### Added
- Make persistence of stage settings to be window specific for default usd context.

## [2.3.12] - 2023-01-11
### Added
- Move SelectionWatch into omni.kit.widget.stage to provide default implementation.

## [2.3.11] - 2022-11-29
### Added
- Unitests for header of name column.

## [2.3.10] - 2022-11-01
### Added
- Test for renaming prim.

## [2.3.8] - 2022-08-04
### Added
- Test for toggling visibility for multiple prims

## [2.3.7] - 2022-05-24
### Changed
- Optimize selection of stage window by reducing allocations of Sdf.Path.

## [2.3.6] - 2022-03-03
### Changed
- Use command for selection in widget so it can be undoable.

## [2.3.5] - 2021-10-20
### Changed
- External drag/drop doesn't use windows slashes

## [2.3.4] - 2021-05-25
### Fixed
- Bug when hide and show the Stage window

## [2.3.3] - 2021-04-27
## Removed
- `omni.stageupdate` is deprecated and doesn't work well with multiple usd
  contexts

## [2.3.2] - 2020-11-19
### Changed
- Refusing selection of grayed prims in search mode

## [2.3.1] - 2020-10-22
### Added
- Dependency on omni.kit.widget.stage_icons

## [2.3.0] - 2020-09-16
### Changed
- Split to two parts: omni.kit.widget.stage and omni.kit.window.stage

## [2.2.0] - 2020-09-15
### Changed
- Detached from Editor and using UsdNotice for notifications
