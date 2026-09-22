# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [107.0.8] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [107.0.7] - 2024-11-26
### Fixed
- OMPE-29767: Fix code format.

## [107.0.6] - 2024-10-11
### Fixed
- OMPE-22569: Update public API.

## [107.0.5] - 2024-07-04
### Changed
- Fix flaky test failed.

## [107.0.4] - 2024-06-27
### Changed
- OMPE-8317: Update api docs for omni.kit.manipulator.prim.core with AI agent.

## [107.0.3] - 2024-05-29
### Changed
- OMPE-5050: Profile and Improve test times of omni.kit.manipulator.prim.core in Kit 107.

## [107.0.2] - 2024-03-27
### Changed
- Made omni.kit.manipulator.viewport optional.

## [107.0.1] - 2024-03-27
### Changed
- Fix cache errors in data accessor selector.

## [107.0.0] - 2024-03-21
### Changed
Renamed from `omni.kit.manipulator.prim2.core`.

## [105.0.13] - 2024-01-03
### Changed
- TransformMultiPrimsSRTFabricCpp command now uses int32 PathC

## [105.0.12] - 2023-12-05
### Fixed
- Fix function name

## [105.0.11] - 2023-11-16
### Changed
- prim2 changes synced to prim, now tests images set is the same for prim and prim2. prim 2 uses RTX rendered, FSD = ON for fabric data accessor, tests threshold decreased

## [105.0.10] - 2023-11-09
### Changed
- Enable tests for Fabric Accessor. (Local-axis related tests are excluded due to an issue of extracting negative scale from local matrix attribute.)

## [105.0.9] - 2023-06-09
### Fixed
- Split from omni.kit.manipulator.prim. Imported ViewportTransformModel, ViewportTransformChangedGestureBase ,ViewportTranslateChangedGesture ,ViewportRotateChangedGesture ,ViewportScaleChangedGesture
