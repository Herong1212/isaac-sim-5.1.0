# CHANGELOG

This document records all notable changes to ``omni.rtx.window.settings`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`.

## [0.6.19] - 2025-04-16
### Fixed
- Fix documentation build error

## [0.6.18] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

### Fixed
- OMPE-28324: Cleaned up a registered 'show window' function using the same name/object it was originally registered with.

## [0.6.17] - 2024-06-28
### Fixed
- OMPE-13747: Restored missing save overwrite function

## [0.6.16] - 2024-04-25
### Fixed
- OM-122859: Fixed double slashes in file picker apply handler.

## [0.6.15] - 2024-04-17
### Fixed
- OM-122859: Fix for double clicking in the import window doesn't work when loading render settings.

## [0.6.14] - 2024-02-07
### Changed
- added omni.kit.widget.searchable_combobox as it was removed from omni.kit.widget.settings

## [0.6.13] - 2024-02-02
### Updated
- Updated how "Don't show window while viewport is loading".

## [0.6.12] - 2024-01-17
### Added
- Automatically open the RTPT (Experimental) settings tab when switching to RTPT mode.

## [0.6.11] - 2023-12-15
### Added
- Don't show window while viewport is loading (requires extension omni.kit.viewport.ready.viewport_ready to be enabled).

## [0.6.10] - 2023-11-02
### Changed
- Updated menus to use omni.kit.menu.utils

## [0.6.9] - 2023-07-14
### Fixed
- API breakage of set_render_settings_to_viewport_renderer from transition from Window to Widget

## [0.6.8] - 2023-05-16
### Changed
- Split into window and widget

## [0.6.7] - 2023-05-19
### Fixed
- OM-76204 - Changing the Renderer combobox emits an event with the renderer name string.

## [0.6.6] - 2023-03-17
### Fixed
- ""Save Settings" overwrite fixed

## [0.6.5] - 2023-02-09
### Changed
- Replaced filepicker dialog to fix mysterious unittest failures.

## [0.6.4] - 2023-01-05
### Changed
- Fixed test_rtx_settings_all test so it works in random order.

## [0.6.2] - 2022-09-20
### Added
- API to switch to explicitly switch to a renderer's settings and show the window.

## [0.6.1] - 2022-02-15
### Changed
- Made test suite runnable for carb-settings paths other than 'rtx'

## [0.6.0] - 2020-11-27
### Changed
- Added RenderSettingsFactory interface as entry point for dependent extensions, and removed existing get_rtx_settings_window. This is an interface breaking change
- Cleaned up Reset Button logic so any changes to settings result in reset button status being checked
- Set an active tab when you add any Render Settings (previously wasn't set)
- Start frames collapsed, and store collapse state during session
- try and delete widgets/models etc that don't get destroyed/garbage collected when UI is rebuilt due to circular references

## [0.5.4] - 2020-11-25
### Changed
- Added Registration process
- Moved hardcoded RTX registration out
- Custom tooltips support

## [0.5.3] - 2020-11-18
### Changed
- Additional fix to make labels wider
- Additional fix to Default to centre panel when Renderer Changed
- removed IRay

## [0.5.2] - 2020-11-16
### Changed
- Made labels wider to accommodate longer label width on single line
- Changed colour of float/int drag bars
- Default to centre panel when Renderer Changed

## [0.5.1] - 2020-11-11
### Changed
- Cleaned up code - type annotations, comments etc
- Added some tests
- Added skip_draw_when_clipped=True performance optimisation

## [0.5.0] - 2020-11-04
### Changed
- initial release
