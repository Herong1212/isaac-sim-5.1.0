# CHANGELOG

This document records all notable changes to ``omni.kit.manipulator.camera`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [106.0.4] - 2025-03-31
### Changed
- OMPE-38551: By default, gamepad input is ignored if the app is not focused. This can be changed by setting
  */exts/omni.kit.manipulator.camera/gamePad/mustBeFocused* to `false`.

## [106.0.3] - 2024-10-11
### Fixed
- OMPE-22569: Update public API.

## [106.0.2] - 2024-09-05
### Fixed
- OMPE-14095: Fixed gesture test not inside scene view.

## [106.0.1] - 2024-04-09
### Changed
- OM-122317: Update docs.

## [105.0.4] - 2023-08-22
### Changed
- Handle stage-up axis in case insensitive way

## [105.0.4] - 2023-04-06
### Added
- Additional fly-mode settings and up limit.
- Gamepad action to adjust speed (defaulting to A-B keys)

## [105.0.3] - 2023-02-07
### Added
- Global setting keys for camera control mode speeds.

## [105.0.2] - 2022-11-17
### Fixed
- Lock users out of keyboard and gamepad navigation when lockCamera attribute is set to True.

## [105.0.1] - 2022-10-24
### Fixed
- Navigation in odd cases where Y-up or Z-up camera is renderenced into an opposing up stage.
- Rotation test skipping on Linux due to floating-point issues.
### Added
- Expose object-centric manipulation via carb setting /exts/omni.kit.manipulator.camera/objectCentric/type

## [105.0.0] - 2022-10-02
### Added
- Broadcast camera manipulator mode changes per-viewport.
- Support for gamepad control in ViewportWindow.

## [104.0.18] - 2022-09-08
### Fixed
- Unintialized variable causing logging of error/exceptions.

## [104.0.17] - 2022-08-30
### Added
- Inertia settings for movements other than flight-mode.

## [104.0.16] - 2022-08-24
### Added
- Flight mode speed adjustment for left Shift and Control keys.

## [104.0.15] - 2022-08-08
### Fixed
- Honor setting for USD camera manipulation through TransformPrimSRTCommand.
### Changed
- Keep applying look values even when inertia is active.
- Reduce animation clamping from 0.5 to 0.15 and add a setting for it.

## [104.0.14] - 2022-08-02
### Fixed
- Issue with flight mode jumping after inertia when a rotation begins.

## [104.0.13] - 2022-08-02
### Fixed
- Issue with flight mode when a numeric field is stealing any keyboard input for flight-mode.

## [104.0.12] - 2022-07-27
### Fixed
- Kill any inertia being applied if camera transform changes from external source.

## [104.0.11] - 2022-07-25
### Changed
- Remove any rotational intertia.
### Fixed
- Possible drift or stutter from opposing diagnonal movement.

## [104.0.10] - 2022-07-05
### Changed
- Make implicit Viewport camera movements not undoable.

## [104.0.9] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.0.9] - 2022-03-24
### Added
- Ability to lock out camera movement with omni:kit:cameraLock property

## [1.0.8] - 2022-02-22
### Changed
- Add carb.profiler decorators

## [1.0.7] - 2022-02-10
### Fixed
- Remove GestureManager that winds up blocking context-menu.

## [1.0.6] - 2022-02-08
### Fixed
- Fix possible divide-by-zero when inertia-seconds is set to zero.

## [1.0.5] - 2022-02-07
### Changed
- Refactor to more model-centric manipulator and add smoother flight-mode, ability for animations, and inertia.

## [1.0.4]
### Changed
- Optimize settting of some omni.ui.scene model values
- Update to new omni.kit.kydra_texture APIs

## [1.0.3]
### Changed
- Move to API's that were only available in release/103.0, now that it is availbale in master.
- Fix issue with Viewport-1 interop and nested cameras
- Remove conditionals for support of release/103.0 and master

## [1.0.2]
### Changed
- Use new Viewport1.get_usd_context_name() api to sync camera moves across mutliple contexts.

## [1.0.1]
### Changed
- Add UsdCameraManipulator and ViewportCameraManipulator
- Expose disable_undo on model
- Update omni.ui.scene usage to use SceneView.model concepts

## [1.0.0]
### Changed
- Initial release

## [0.9.0]
### Changed
- Fix arbitrary Camera manipulator bindings
- Make gestures invocable outside of omni.ui.scene

## [0.8.1]
### Changed
- When Viewport-1 is loaded, make center-of-interest 1 dimensional and synchronize with CameraController radius

## [0.8.0] - unrelease
### Changed
- first release
