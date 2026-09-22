# Changelog

This document records all notable changes to the **omni.kit.viewport.legacy_gizmos** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.0.19] - 2025-07-30
### Fixed
- Issue drawing camera representations when RTX is not loaded
- OMPE-52086: invisibleToSecondaryRays primvar to lessen lighting contribution of usd-camera-mesh
- OMPE-6254: /app/viewport/gizmo/camera/setEmptyExtent to control clearing any camera-mesh extents
### Changed
- OMPE-6254: Create camera mesh as a component kind

## [1.0.18] - 2025-04-24
### Changed
- OMPE-42905: Use carb::getCachedInterface for performance

## [1.0.17] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.0.16] - 2024-01-17
### Added
- OM-84741: Leave /app/viewport/boundingBoxes/enabled to show/hide bounding box, do not update when prim mode changed any more

## [1.0.15] - 2023-11-02
### Removed
- Previous code that only fixed issue intermittently in favor of lower-level USD fix.

## [1.0.14] - 2023-07-28
### Fixed
- Remove SdfPrimSpec from session layer for usd-camera-mesh on newer versions of USD.

## [1.0.13] - 2023-06-13
### Fixed
- Additional validity checks when resolving usd-camera geometry.

## [1.0.12] - 2023-02-03
### Fixed
- Prim test against new Omni Audio Listener schema
- Issue drawing listeners when orientationFromView is enabled.
- Drawing of sounds when stage is not default world scale.

## [1.0.11] - 2023-02-03
### Fixed
- Prim test against new Omni Audio schema

## [1.0.10] - 2023-01-31
### Added
- /app/viewport/grid/offset setting to control grid placement in relation to origin.
- Ability to disable bounding box updates during user intraction.

## [1.0.9] - 2023-01-25
### Added
- /app/viewport/grid/trackCamera setting to automatically update grid based on camera.

## [1.0.8] - 2022-12-09
### Fixed
- Issue with slow billboard updates during camera movement.

## [1.0.7] - 2022-10-24
### Fixed
- Clearing of gizmo prims when exiting live session.

## [1.0.6] - 2022-08-22
### Fixed
- Acquire Usd read lock in draw call.

## [1.0.5] - 2022-08-22
### Fixed
- Support latest UsdContext r/w lock pattern.

## [1.0.4] - 2022-08-08
### Fixed
- Performance issues when updating many USD scene representation cameras.

## [1.0.3] - 2022-08-05
### Added
- Remove camera gizmo if camera prim is removed or camera visibility turns off.

## [1.0.2] - 2022-07-26
### Added
- Honor camera scale independent of gizmo constant scale enabled state.
- Ability to create and update legacy USD camera mesh representations.
- Push values to /app/viewport/boundingBoxes/enabled as legacy Viewport did.

## [1.0.1] - 2022-02-03
- Added tests.

## [1.0.0] - 2021-10-15
- Initial version
