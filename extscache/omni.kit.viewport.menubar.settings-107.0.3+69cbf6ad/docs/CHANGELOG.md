# CHANGELOG

This document records all notable changes to ``omni.kit.viewport.menubar.settings`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [107.0.3] - 2024-06-11
### Changed
- Updated documentation with AI agent.

## [107.0.2] - 2024-05-30
### Changed
- Linting

## [107.0.1] - 2024-03-18
### Changed
- Custom timeouts for resolution test to more standard versions and single constants.

## [107.0.0] - 2024-03-18
### Changed
- Move version to 107.0.0

## [105.1.1] - 2024-01-29
### Changed
- Increase test coverage to 90.83%

## [105.1.0] - 2023-12-18
### Fixed
- Missing maximum for transform-manipulator setting range.

## [105.0.9] - 2023-04-21
### Fixed
- Missing maximum for transform-manipulator setting range.

## [105.0.8] - 2023-04-06
### Added
- Settings to control fly mode limits
### Fixed
- Visibility model changes after second Viewport menu is built.

## [105.0.7] - 2023-02-13
### Changed
OM-73286: Only update resolution when width/height edit end and set min resolution to 64x64

## [105.0.6] - 2023-02-07
### Added
- Slider step argument forwarding to omni.ui.

## [105.0.5] - 2022-12-12
### Fixed
- Settings for object-centric viewport control.

## [105.0.4] - 2022-12-05
### Changed
- Move resolution setting into ViewportWidget to honor F7/F11 whether menu exists or not.
### Fixed
- "Reset To Defaults" menu item throwing Exception

## [105.0.3] - 2022-11-17
### Added
- Add settings for manipulator-transform

## [105.0.2] - 2022-11-17
### Changed
- Add more default resolutions and aspect ratios
- Do not show save dialog when right click in viewport if resolution menu torn off

## [105.0.0] - 2022-10-11
### Changed
- Made Viewport resolution settings persistent.
### Fixed
- Issues when "Viewport" resolution is selected.

## [104.2.4] - 2022-10-08
### Changed
- Custom resolution

## [104.2.3] - 2022-10-04
### Added
- Added functionality for Fill Viewport to watch for setting changes.

## [104.2.2] - 2022-09-23
### Added
- Add custom resolution
- Checkbox for gamepad controller.

## [104.2.1] - 2022-09-20
### Added
- Checkbox for applying inertia to all movements.

## [104.2.0] - 2022-08-15
### Added
- Animation clamping slider for camera manipulator.
### Fixed
- Spurious print statement
### Changed
- Make resolution and fit menus act like legacy Viewport did.

## [104.1.3] - 2022-08-09
### Changed
- Add some missing carb.settings defaults, and set speed-scaler to new default of 1.1
- Animation clamping slider for camera manipulator.
### Fixed
- Focusing the Preferences page when tab exists already but isn't active.

## [104.1.2] - 2022-07-26
### Changed
- OM-55152: Re-adjust viewport dashboard and icons for VP2
- Settings icon in menubar
- Add menu item to show Viewport preference
- OM-57156: add reset box to settings
- Allow camera scale to always be set independent of constant scale enabled state.

## [104.1.1] - 2022-07-13
### Fixed
- Set selection interection color with outline color.

## [104.1.0] - 2022-07-08
### Changed
- Make sub-menus not tearble by default.
### Fixed
- Use new Viewport resolution scaling API to control resolution and scaling factor.
- Fix issue with render settings changed and resolution.

## [104.0.7] - 2022-06-05
### Changed
- Simplify test to use default Viewport and window size.
- Make failure of one test not cause failure of others.
- Don't create a new Viewport for every menu-item test.

## [104.0.6] - 2022-05-25
### Changed
- Split up settings menu

## [104.0.5] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.0.5] - 2022-03-31
### Added
- Setting for visible and Order

## [1.0.4] - 2022-03-31
### Fixed
- Implement Proper aperture selection
- Remove legacy settings that wont be implemented

## [1.0.3] - 2022-03-29
### Fixed
- Gizmo Constant Scale checkbox and slider incorrect/overlapping names

## [1.0.2] - 2022-03-28
### Changed
- Update UI brightness value range

## [1.0.1] - 2022-03-27
### Added
- Remove legacy speed multiplier

## [1.0.0] - 2022-03-11
### Added
- Split from omni.kit.viewport.menubar
