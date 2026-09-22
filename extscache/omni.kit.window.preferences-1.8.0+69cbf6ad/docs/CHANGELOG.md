# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.8.0] - 2025-04-02
### Changed
- OMPE-31619: /app/stage/movePrimInPlace is now int 0/1/2

## [1.7.5] - 2025-04-07
### Fixed
- OMPE-28324: Fixed a leaked registered 'show window' function that leads to problems during Kit's normal shutdown.

## [1.7.4] - 2025-04-03
### Added
- OMPE-38764: Add setting to enable pick through objects with RTX

## [1.7.3] - 2025-03-18
### Added
- OMPE-31959: Add default unicode normalization method if not set

## [1.7.2] - 2025-02-21
### Added
- OMPE-31959: Add Unicode normalization method setting in stage page, default to NFC, and Disabled to disable normalization

## [1.7.1] - 2025-02-06
### Fixed
OMPE-32734: Fix relaunching kit on linux

## [1.7.0] - 2025-07-03
### Added
- Viewport section for behavior on stage-open (auto framing).

## [1.5.2] - 2025-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.5.1] - 2024-04-08
## Added
- OM-122905: Added dependency for omni.kit.window.popup_dialog

## [1.5.0] - 2024-03-20
## Added
- OM-122352: Added documentation

## [1.4.3] - 2024-03-14
### Changed
- Reworked developer page
- Pages can now have `show_page()` and return True/False
- Added `get_shown_page_list()` function

## [1.4.2] - 2024-03-13
## Changed
- OM-31127: Add show save options setting.

## [1.4.1] - 2024-02-15
### Changed
- Updated window closing so it calls `refresh_menu_items()` instead of `rebuild_menus()`

## [1.4.0] - 2024-01-19
### Changed
- OM-118790: Reduced dependencies by moving pages out of omni.kit.window.preferences

## [1.3.30] - 2024-01-16
### Changed
- OM-118226: Fixed warning caused by combobox changes when using dict and default arguments.

## [1.3.29] - 2024-01-09
### Changed
- OM-113643: Turn "Capture only the 3D Viewport" option ON by default for F10 Screen Capture

## [1.3.28] - 2023-11-16
### Added
- OM-114885: Moved live file format setting to omni.kit.collaboration.debug_options

## [1.3.27] - 2023-11-07
### Added
- OM-110067: forbid illegal time range input from user input with dynamic range update

## [1.3.26] - 2023-11-07
### Changed
- Added settings to show/hide Audio, Rendering, Resource Monitor and Tagging preference pages.
- Added setting to show/hide mdl frame within Thumbnail Generation preference page.

## [1.3.25] - 2023-09-19
### Added
- added setting "/exts/omni.kit.window.preferences/show_globals" to disable "Reset to Default"

## [1.3.24] - 2023-10-10
### Changed
- Developer pacing presets now set `/app/runLoops/*/rateLimitEnabled`

## [1.3.23] - 2023-09-26
### Changed
- OM-105264: Set proper range for TimeCodesPerSecond field

## [1.3.22] - 2023-09-19
### Changed
- OM-103837: This extension may be enabled after app ready

## [1.3.21] - 2023-09-18
### Added
- OM-94687: Add "Generate until all assets loaded" to thumbnail generate page.

## [1.3.20] - 2023-08-02
### Added
- Moved Throttle Rendering preferences to Developer Section

## [1.3.19] - 2023-07-18
### Added
- Added "Requires Scene Reload" to White Mode Exceptions setting.

## [1.3.18] - 2023-06-14
### Changed
- Changed rebuild_menus to refresh_menu_items

## [1.3.17] - 2023-05-31
### Changed
- Added "show_only_folders" to show_file_importer to allow filtering to only folders when browsing

## [1.3.16] - 2023-05-16
### Changed
- Added "rendering_1" settings for "Viewport 2"

## [1.3.15] - 2023-05-17
### Changed
- Set horizontal scrollbar policy for PreferenceBuilderUI page frame from "SCROLLBAR_ALWAYS OFF" to "SCROLLBAR_AS_NEEDED"

## [1.3.14] - 2023-05-11
### Changed
- Rename "None Precise" frame pacing preset to "No Pacing", enabled DLSS-G

## [1.3.13] - 2023-02-28
### Changed
- Added optional dependency on omni.resourcemonitor and resourcemonitor preferences page.

## [1.3.12] - 2023-02-08
### Changed
- Added ui.Workspace.show_window("Preferences", True/False) support

## [1.3.11] - 2023-02-02
### Changed
- Material preferences where moved into omni.kit.material.library

## [1.3.10] - 2023-01-30
### Changed
- Add rendering Opacity Multimap setting

## [1.3.9] - 2023-01-10
### Changed
- Use file_importer for setting path-like settings, instead of directly using filepicker dialog.

## [1.3.8] - 2022-12-06
### Changed
- Added rendering Multi-GPU setting

## [1.3.7] - 2022-09-13
### Changed
- Prevented "Material render context has been changed" message when stage not saved

## [1.3.6] - 2022-08-23
### Changed
- Alpha sorted page names

## [1.3.5] - 2022-08-17
### Changed
- Added /persistent/app/stage/nestedGprimsAuthoring to stage page.

## [1.3.4] - 2022-07-27
### Changed
- Added "/omnihydra/staticMaterialNetworkTopology" to stage page

## [1.3.3] - 2022-06-22
### Changed
- Added "/persistent/app/material/dragDropMaterialPath" to materials page

## [1.3.2] - 2022-06-08
### Changed
- Updated menus to use actions

## [1.3.1] - 2022-06-06
### Changed
- Removed omni.kit.ui support

## [1.2.2] - 2022-02-22
### Changed
- Added stage import usd method payload/reference
- Added identifier to `ui.CollapsableFrame` in `add_frame`

## [1.2.1] - 2022-02-22
### Changed
- Changed implementation on label function

## [1.2.0] - 2022-02-16
### Added
- Allow widgets to display tooltip information

## [1.1.5] - 2021-10-20
### Changed
- Cleans up on shutdown, including releasing handle to FilePickerDialog.

## [1.1.4] - 2021-10-18
### Changed
- Use float type for rateLimitFrequency in preferences.

## [1.1.3] - 2021-07-10
### Added
- Added support for "deep linking" of specific Preference pages from external components.

## [1.1.2] - 2021-05-19
### Changed
- Force "Preferences" to always at the bottom of the edit menu

## [1.1.1] - 2021-05-06
### Changed
- Added feeback when user changes `/app/hydra/material/renderContext`

## [1.1.0] - 2021-03-25
### Changed
- Added `PreferenceBuilder` for new `omni.ui`
- Updated existing Pages to use `PreferenceBuilder`
- Updated `PreferencePage` it still works, but now deprecated

## [1.0.3] - 2021-03-02
### Changed
- Added test

## [1.0.2] - 2020-12-17
### Changed
- Updated menu to use `omni.kit.menu.utils`

## [1.0.1] - 2020-10-17
### Changed
- Added filepicker API
- Updated pages to use new filepicker API

## [1.0.0] - 2020-08-13
### Changed
- Converted to extension 2.0
