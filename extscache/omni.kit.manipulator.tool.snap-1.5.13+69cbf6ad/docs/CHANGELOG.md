# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.5.13] - 2025-04-04
### Removed
- Legacy Viewport conditionals

## [1.5.12] - 2024-10-11
### Fixed
- OMPE-22569: Update public API.

## [1.5.11] - 2024-04-22
### Added
- Documentations

## [1.5.10] - 2024-03-26
### Changed
- Support both `pxr.Gf` and `usdrt.Gf`.

## [1.5.9] - 2023-12-06
### Changed
- OM-110315: apply new options menu

## [1.4.2] - 2023-10-24
### Changed
- Updated Grid snap to check on the new grid enabled setting path.

## [1.4.1] - 2023-10-20
### Fixed
- Fixed multi-snap not working with grid+prim or grid+surface (async provider that has higher priority).

## [1.4.0] - 2023-10-18
### Changed
- Renamed `Conform to Target` to `Align to Target`, `Conform Up-Axis` to `Align by Axis`.
- Supported `Align to Target` for Surface snap.
- Updated `Align to Target` and `Align by Axis` menu entries enabled state to reflect snap options.
- When changing transform operation, the currently opened snap menu will be closed.

## [1.3.1] - 2023-05-10
### Changed
- replace "omni.kit.manipulator.tool.snap" dependency from "omni.kit.window.toolbar" into "omni.kit.widget.toolbar"

## [1.3.0] - 2023-03-02
### Changed
- Use Usd.Stage and Camera in instead of global grid setting for determing ground plane for snapping.

## [1.2.2] - 2022-09-26
### Changed
- Updated to `omni.kit.actions.core` and `omni.kit.hotkeys.core`.

## [1.2.1] - 2022-09-01
### Changed
- Updated context menu to VP2 style.

## [1.2.0] - 2022-07-26
### Added
- Added option to choose up axis for conform to target.

## [1.1.2] - 2022-07-14
### Added
- Added tooltip for manipulator toolbar button.

## [1.1.1] - 2022-07-13
### Changed
- During rotation/scale mode, Snap and Explicit Transform is now toggled in sync.

## [1.1.0] - 2022-07-07
### Added
- `SnapProvider` now has:
  - `get_display_name`: an optional function to override to supply display name on snap menu.
  - `get_order`: order used for multi-snap provider.
### Changed
- More than one snap provider now can be enabled at the same time. Provider with lowest order will be used first. If it fails to snap, the next enabled provider with higher order will be tested and so on.

## [1.0.3] - 2022-06-23
### Added
- Added hotkey `S` to toggle snap mode on/off.
### Changed
- Hid Viewport-2-only snap options in main toolbar when Viewport 1 is available/focused.
- Skips incompatible snap options if viewport_api is not available.

## [1.0.2] - 2022-06-07
### Changed
- Accepts `SceneView` on `SnapProvider.on_snap`.
- Added `SnapProvider._get_ndc_to_screen_matrix` to help transform from NDC to viewport window screen space.

## [1.0.1] - 2022-06-01
### Changed
- Removed `Snap Options` from UI.
- Added check mark for `Explicit Transform`.

## [1.0.0] - 2022-05-19
### Added
- Initial commit of new snap framework and toolbar integration.
