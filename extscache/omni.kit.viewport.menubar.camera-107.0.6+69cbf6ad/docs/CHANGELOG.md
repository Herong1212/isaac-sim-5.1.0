# Changelog

This document records all notable changes to the **omni.kit.viewport.menubar.camera** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [107.0.6] - 2025-07-17
### Changed
- OMPE-54320: Breaking reference cycles to clear memory leak.

## [107.0.4] - 2025-07-15
### Changed
- OMPE-54754: Fix issue with crash in `_CameraList.__delayed_prim_change`.

## [107.0.3] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [107.0.2] - 2024-06-12
### Changed
- Updated documentation with AI agent.
- Add tests for custom camera button/menu item delegates

## [107.0.1] - 2024-05-21
### Changed
- Linting

## [107.0.0] - 2024-03-18
### Changed
- Move version to 107.0.0

## [105.1.8] - 2023-10-11
### Added
- Tests to increase the test coverage

## [105.1.7] - 2023-09-13
### Added
- Show hotkey text

## [105.1.6] - 2023-06-06
### Fixed
- Fix more ui test failures

## [105.1.5] - 2023-06-03
### Fixed
- Intermittent test failures.

## [105.1.4] - 2023-05-16
### Added
- Add test for `get_instance`, `SingleCameraMenuItemBase`, `SingleCameraMenuItem`.

## [105.1.3] - 2023-05-15
### Added
- Use prim displayName metadata fro camera label if available.
- Faster camera prim queries when UsdRt is available.

## [105.1.2] - 2023-05-15
### Fixed
- Missing cameras in menubar

## [105.1.1] - 2023-05-10
### Added
- Feature to be able to override viewport menu item type
- Be able to deffer the creation of the menu

## [105.1.0] - 2023-04-21
### Fixed
- Range and stepping for lens slider.

## [105.0.9] - 2023-04-04
### Changed
- Early return in camera_dirty if the stage is invalid (fix  OM-84459)

## [105.0.8] - 2023-03-28
### Changed
- Add supports to track users that are following the bound cameras in a Live Session.

## [105.0.7] - 2023-03-08
### Changed
- OM-84472: Add unique identifiers for camera setting menu items

## [105.0.6] - 2023-02-26
### Changed
- Replaced asyncio.ensure_future calls in camera_menu_container.py with omni.kit.async_engine.run_coroutine function.

## [105.0.5] - 2023-01-25
### Fixed
- "Create From View" when triggered from Viewport attached to custom UsdContext.
### Changed
- Use omni.ui shown_changed_fn callback to delay building stage-camera menu until shown.

## [105.0.4] - 2022-11-17
### Changed
- Hide camera from camera list if it's instructed.

## [105.0.3] - 2022-11-17
### Fixed
- Validate Usd.Stage validity before beginning a traversal.

## [105.0.2] - 2022-10-14
### Changed
- Update global expand status when it is changed in a single Viewport

## [105.0.1] - 2022-10-03
### Changed
- Update for new ViewportMenuDelegate

## [105.0.0] - 2022-09-30
### Changed
- Move camera options icon to omni.kit.viewport.menubar.core
- Use carb.tokens API for icon path
- Make omni.kit.window.cursor an optional dependency.

## [104.1.2] - 2022-09-13
### Changed
- OM-62401: Do not show Waypoint/markup cameras in camera list

## [104.1.1] - 2022-08-23
### Added
- Multiple VP support

## [104.1.0] - 2022-08-15
### Fixed
- When lens changed, update range combobox to match.

## [104.0.24] - 2022-08-09
### Fixed
- Fallback to implicit Perspective camera when reading the boundCamera meta-data fails in USD.

## [104.0.23] - 2022-08-05
### Changed
- Handle missing camera with a more defined fallback, and try to detect a remote camera rename event.
### Fixed
- Issue with camera name sorting using capitalization.

## [104.0.22] - 2022-08-04
### Changed
- Don't copy any camera xform attributes to force them to inherit default rotation order in TransformPrim command.

## [104.0.21] - 2022-07-28
### Changed
- Don't toggle camera selection off when clicking already active camera.

## [104.0.20] - 2022-07-27
### Changed
- Do not listen camera changes if no stage

## [104.0.19] - 2022-07-26
### Fixed
- Fix lock-button hover for lockable cameras.
- Re-enable Auto Exposure in default configuration.

## [104.0.17] - 2022-07-21
### Changed
- Do not allow implicit cameras to be locked.
- Do not close camera menu when option/select item clicked.
- Do not close camera menu when new camera is created.
### Fixed
- Exceptions being thrown from uninitialized values.
- Issue with cameras being removed staying in menu.
- Scene cameras list not begin sorted at all.
### Removed
- Unused and dead CameraLock class

## [104.0.16] - 2022-07-21
### Added
- Resize menu when required

## [104.0.15] - 2022-07-16
### Changed
- OM-55152: Re-adjust viewport dashboard and icons for VP2
- OM-46899: Remove Auto Exposure from Viewport menubar

## [104.0.14] - 2022-07-13
### Fixed
- Don't create default xformOps when duplicating Viewport camera.

## [104.0.13] - 2022-07-12
### Fixed
- Rebuild Camera property widgets after active camera changes.

## [104.0.12] - 2022-07-11
### Fixed
- Rebuild menubar after an external change to Viewport camera.
- Set bound-camera meta-data to the Usd.Stage's root-layer.

## [104.0.11] - 2022-07-01
### Added
- Make sub-menus not tearable, and try to disable hide_on_click
- Make clicking not hide the Camera menu
### Fixed
- Test window size for Linux.
- Unnecessary imports.
- Typo.

## [104.0.10] - 2022-06-23
### Added
- OptionBox item to select/open camera property window.

## [104.0.9] - 2022-06-16
### Added
- Ability to register/unregister menu items

## [104.0.8] - 2022-06-05
### Changed
- Simplify test to use default Viewport and window size.
- Make failure of one test not cause failure of others.

## [104.0.7] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.0.6] - 2022-04-08
### Changed
- Match omni.kit.viewport.menubar.core v1.1.12

## [1.0.6] - 2022-03-31
### Added
- Setting for visible and Order

## [1.0.5] - 2022-03-30
### Fixed
- OM-47005: Restore ability to load/save Viewport camera from/into file

## [1.0.4] - 2022-03-28
### Changed
- Fix 1.0.3 focus distance picking from a drag operation.
- Remove redundant imports
- Add explicit dependency to omni.kit.commands

## [1.0.3] - 2022-03-28
### Changed
- Improve sample focus distance (Block until valid result picked and restore mouse cursor with no result picked)

## [1.0.2] - 2022-03-27
### Added
- Set focus with button and mouse-clock / sample in viewport

## [1.0.1] - 2022-03-24
### Changes
- Properly namespace locking attribute as omni:kit:cameraLock
### Fixed
- Make Camera Attribute setting from menubar undo-able
- Make "Create From View" undo-able
- Camera settings enable state based on camera change and lock state
### Added
- Tests

## [1.0.0] - 2022-03-11
### Added
- Split from omni.kit.viewport.menubar
