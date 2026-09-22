# Changelog

This document records all notable changes to the **omni.kit.viewport.menubar.render** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [107.0.10] - 2025-07-17
### Changed
- OMPE-54320: Breaking reference cycles to clear memory leak.

## [107.0.9] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [107.0.8] - 2024-09-26
### Changed
- OMPE-21518: Add a separate RTPT (Experimental) render mode

## [107.0.7] - 2024-08-13
### Changed
- OMPE-8954: Sync "Camera Light" with "/rtx/useViewLightingMode"

## [107.0.6] - 2024-07-31
### Fixed
- Handling invalid /renderer/enabled setting better.

## [107.0.5] - 2024-07-17
### Changed
- OMPE-3099: Do not change debug view target settings when current debug view target may not in list

## [107.0.4] - 2024-07-04
### Changed
- OMPE-3099: Show current debug view target as none instead of first value ("Off") if it is not in the list when renderer/render mode changed.

## [107.0.3] - 2024-06-06
### Changed
- Updated documentation with AI agent.

## [107.0.2] - 2024-05-28
### Changed
- Linting

## [107.0.1] - 2024-04-25
### Fixed
- OM-122859: Fixed double slashes in file picker apply handler.

## [107.0.0] - 2024-03-18
### Changed
- Move version to 107.0.0

## [106.0.4] - 2024-03-01
### Added
- OM-121568: Do not add empty engine to "/renderer/enabled"

## [106.0.3] - 2024-02-27
### Added
- OMPRW-274: Added more tests to increase test coverage to 92.18%

## [106.0.2] - 2024-01-16
### Fixed
- Update available render menu through omni.kit.viewport.renderer toggle as well.
- Special case Iray settings extension to toggle available render menu.
### Added
- Show "RTX - RTPT (Experimental)" in viewport's menubar if RTPT mode is enabled.

## [106.0.1] - 2024-01-12
### Fixed
- Auto enable autoManageEnabledList menu-entires on startup (not only on toggle).

## [106.0.0] - 2023-12-12
### Changed
- Support omni.hydra.pxr engine instance per UsdContext instead of a single global engine.

## [105.1.2] - 2023-09-18
### Changed
- OM-109145: Hover state for shade modes and render options

## [105.1.1] - 2023-09-12
### Added
- OM-105300: Show hotkey in renderer menu item if hotkey is defined

## [105.1.0] - 2023-06-27
### Added
- Response to mutating /renderer/enabled and extension loading for background render startup.
- Concrete sorting order for known renderers
- Tests for above

## [105.0.10] - 2023-05-16
### Added
- Add test for `get_instance`, `SingleRenderMenuItemBase`, `SingleRenderMenuItem`.

## [105.0.9] - 2023-05-10
### Added
- Feature to be able to override viewport menu item type
- Be able to deffer the creation of the menu

## [105.0.8] - 2023-04-26
### Added
- Updated render presets

## [105.0.7] - 2023-04-14
### Added
- Added render presets menu

## [105.0.6] - 2023-02-10
### Added
- Watch for render-settings changed on the Viewport to update labeling.

## [105.0.5] - 2023-02-03
### Changed
- Renamed "Render Options" to "Preferences"
- Renamed all Debug Views that are intended to be RT-specific with RT prefix and removed alphabetic sorting.

## [105.0.4] - 2022-11-22
### Changed
- Renamed all Debug Views that are intended to be RT-specific with RT prefix and alphabetic sorting is now done manually.

## [105.0.3] - 2022-11-17
### Changed
- For photosentivity/seizure concerns, included [WARNING: Flashing Colors] to Debug View names known to flash.

## [105.0.2] - 2022-10-26
### Changed
- Improved PT AOV names for clarity, now all have PT AOV prefix.

## [105.0.1] - 2022-10-11
### Changed
- Change menu-item wording to "Camera Light".
- Add additional Path Trace AOVs and normalize menu item labeling with RT/PT prefix.

## [105.0.0] - 2022-10-02
### Added
- Flash Light mode entry.
- Show RenderSettings window option box.
- Ability to disable and enable materials.
### Fixed
- Typo on "Timgin Heat Map" debug view.

## [104.0.12] - 2022-08-26
### Added
- Multiple VP support

## [104.0.11] - 2022-08-25
### Changed
- Don't remap renderer name to different display text.
- Change "Debug Shading" to "Debug View"

## [104.0.10] - 2022-08-21
### Changed
- Add Index to supported builtin render list.
- Handle possibility of no valid renderer better.

## [104.0.9] - 2022-07-29
### Changed
- Build debug-shading menu based on renderer and renderer's mode.

## [104.0.8] - 2022-07-21
### Added
- Resize menu when required

## [104.0.7] - 2022-07-16
### Changed
- OM-55152: Re-adjust viewport dashboard and icons for VP2

## [104.0.6] - 2022-07-08
### Changed
- Remap renderer-menu names to requested compacted names.
- Keep Renderer menu open after clicking.
### Fixed
- Incorrect value for turning off shading white-mode.

## [104.0.6] - 2022-07-01
### Changed
- Use RadioMenuCollection instead of RatioMenuCollection

## [104.0.4] - 2022-06-21
### Changed
- Sort debug-view menu items alphabetically
- Make sure to show "Preferences" window when "Render Options" is selected

## [104.0.3] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.0.3] - 2022-03-28
### Added
- Setting for visible and Order

## [1.0.2] - 2022-03-24
### Changed
- Put the list of renderers to the first level

## [1.0.1] - 2022-03-17
### Added
- OM-45021: Update renderer names to latest.

## [1.0.0] - 2022-03-11
### Added
- Split from omni.kit.viewport.menubar
