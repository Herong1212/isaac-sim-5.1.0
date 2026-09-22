# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

# [107.3.3] - 2025-09-03
### Changed
- Adding support for linux aarch64

# [107.3.2] - 2025-07-16
### Changed
- Updated to kit-sdk 107.3.2
- Fixing dependency issues
- Replace omni.renderer_capture to omni.kit.renderer_capture

# [107.3.1] - 2025-05-22
### Changed
- Updated to kit-sdk 107.3.1

# [107.3.0] - 2025-05-02
### Changed
- Updated to kit-sdk 107.3.0

# [107.0.17] - 2025-04-02
### Changed
- Support for linux aarch64

# [107.0.16] - 2025-02-27
### Changed
- Updated for kit-sdk 107.0.3

# [106.5.2] - 2025-02-04
### Changed
- Updates to kit-sdk 106.5.2

# [106.5.1] - 2024-12-11
### Changed
- Updated anim_core_sdk with fix for blend shapes.

# [106.5.0] - 2024-12-03
### Changed
- Updated for kit-sdk 106.5.0

# [106.4.1] - 2024-11-12
### Changed
- Minor fixes in tests

# [106.4.0] - 2024-10-29
### Changed
- Updated for kit-sdk 106.4.0

# [106.3.2] - 2024-10-16
### Changed
- Fix for numpy dependency

# [106.3.1] - 2024-10-11
### Changed
- Fix for removing yaml/xml importer and exporter

# [106.3.0] - 2024-09-26
### Changed
- Updated for kit-sdk 106.3.0

# [106.2.0] - 2024-09-25
### Changed
- Updated for kit-sdk 106.2.0

# [106.1.2] - 2024-08-28
### Changed
- Fixes crash in linux builds

# [106.1.1] - 2024-08-22
### Changed
- Fixes for USD schema import warnings

# [106.1.0] - 2024-08-08
### Changed
- Updated for kit sdk 106.1
- Fixed incorrect translation changes from retargeter
- Adjust the argument of omni::fabric::toSdfPath() to adapt the update of rtx_plugins
- Append "Skeletons" to viewport menubar "Display" - "Show By Type" if this extension enabled and remove when disabled.
- Replace pinocchio with anim_core_sdk
- Add menu item for pose YAML importer/exporter.
- Add menu item for pose XML importer/exporter.
- Fixed tests.

# [106.0.0] - 2024-03-11
### Changed
- Updated for kit sdk 106.0

# [105.2.8] - 2023-12-08
### Changed
- Remove some unnecessary logs.

# [105.2.7] - 2023-11-27
### Changed
- Update kit sdk and fix build errors

# [105.2.6] - 2023.10-24
### Changed
- - Fix issue for when the chain has only one item

# [105.2.5] - 2023-10-17
### Fixed
- Fixed applying skelanimation with retargeting not work if no skeleton use it when stage loaded.

# [105.2.4] - 2023-09-12
### Added
- Remove skeljoint SetInput interface.

# [105.2.3] - 2023-09-06
### Added
- Added new general retargeting computation.

# [105.2.2] - 2023-08-15
- Fixed OmniJoint not sync with UsdSkel animation when animgraph stop playing.

# [105.2.1] - 2023-08-08
- OmniJoint Pose update Optimized.
- Fixed OmniJoint pose reset bugs when resync.

# [105.2.0] - 2023-08-01
- Kit branch.

# [105.1.12] - 2023-07-17
### Changed
- Fixed retargeted character joint pose initialization.
- Fixed bind pose mode UI.
- Fixed pose matching tolorance.
- Fixed fabric attribute type.

# [105.1.11] - 2023-07-06
### Changed
- Fixed startup warnings

# [105.1.10] - 2023-05-22
### Changed
- Fixed highlight colors.

# [105.1.9] - 2023-05-22
### Changed
- Update Kit SDK.

# [105.1.8] - 2023-05-16
### Changed
- UI unit test image fixes.

# [105.1.7] - 2023-05-09
### Changed
- Kit SDK Upgrade.

# [105.1.6] - 2023-05-09
### Changed
- Switch to animation mode when timeline moves or start play.

# [105.1.5] - 2023-05-09
### Added
- Supported independent OmniJoint rotation order change.
- New Animation Mode UI.
### Changed
- Changed Joint selection behavior and visualization.
### Fixed
- Fixed some undo problems for ResetToBindingCommand, ApplyJointRetargetPoseToSkeleonCommand, ApplyJointRestPoseToSkeleonCommand and SwitchSkeletonTransformMode commands.
- Fixed scaled joint visualization.

# [105.1.4] - 2023-04-20
### Changed
- Changed Using UsdGeomXformable Attribue API for OmniJoint.

# [105.1.3] - 2023-04-20
### Changed
- Changed Retarget Pose and RestPose not update when joint authoring to show the pose in skeleton.

# [105.1.2] - 2023-04-19
### Changed
- Renamed OmniSkel UI to SkelJoint.

# [105.1.1] - 2023-04-19
### Changed
- Changed OmniJoint UI.

# [105.1.0] - 2023.04-18
### Changed
- Upgrade to Kit 105.1.

# [105.0.111] - 2022-04-12
### Changed
- Moved anim drag/drop to omni.anim.skelJoint from omni.anim.shared

# [105.0.110] - 2022-03-30
### Changed
- Changed SetPose interface.

# [105.0.109] - 2022-03-27
### Changed
- Changed retarget/rest transform mode swtich/apply UI logic.
- Added apply animation pose to retargetTransforms.

# [105.0.108] - 2022-03-23
### Changed
- Added Rest Transform Apply and Populate.

# [105.0.107] - 2022-03-20
### Changed
- Added Retarget Transform Apply and Populate.

# [105.0.106] - 2022-03-17
### Changed
- Upgrade to Python 3.10.

# [105.0.105] - 2023.03.14
### Changed
- Temp disable fabric input fetch for all skelanimations.

# [105.0.104] - 2023.03.13
### Changed
- Republish for kit-sdk.

# [105.0.103] - 2023.03.10
### Changed
- SetPose interface.

# [105.0.102] - 2023-03-08
### Changed
- Republish for kitsdk.

# [105.0.101] - 2022-03-01
### Changed
- Changed - skeljoint can detect fabric/usdrt skelanimation data.

# [105.0.100] - 2022-02-23
### Changed
- SkelJoint V2 - OmniSkel

# [105.0.12] - 2022-02-22
### Fixed
- Republish for branch.

# [105.0.11] - 2022-02-07
### Fixed
- Optimized animQuery validation.

# [105.0.10] - 2022-02-07
### Fixed
- Republish for updating kit-sdk.

# [105.0.10] - 2022-02-07
### Fixed
- Republish for updating kit-sdk.

# [105.0.9] - 2022-02-03
### Fixed
- Republish for updating kit-sdk.

# [105.0.8] - 2022-01-30
### Fixed
- Republish for updating kit-sdk.

# [105.0.6] - 2022-12-14
### Fixed
- RetargetController API change

# [105.0.5] - 2022-10-08
### Changed
- Fix render failure due to scenerender.

# [105.0.4] - 2022-10-07
### Changed
- Fix retargeting animation visualization.

# [105.0.3] - 2022-09-26
### Changed
- Move aquire setting interface to initial instead of update.

# [105.0.2] - 2022-09-14
### Changed
- fix warning about skeljoint layer

# [105.0.1] - 2022-09-06
### Changed
- Remove preview when bindTransform changed.

# [105.0.0] - 2022-08-18
### Changed
- Update Kit SDK to 105

## [104.2.13] - 2022-08-12
### Changed
- Pinocchio SDK upgrade, fix retargeting crash when many overlapping chains exists.

## [104.2.12] - 2022-06-18
### Changed
- write full joints when create preview animation.

## [104.2.11] - 2022-05-26

### Changed
- Upgrade Kit SDK 104 to version 83968
### Fixed
- Performance issue when picking a large list of prims
- Error messages when manipulating multiple a joint from one of the multiple UsdSkel Meshs
-
# [105.0.7] - 2022-12-21
### Changed
- Improved retargeting issue when the spine/clavicle joints are very aligned

## [104.2.10] - 2022-05-06
### Changed
- Fixed crash/memory corruption when retargeting has failed

## [104.2.9] - 2022-03-13
### Changed
- Update Pinocchio SDK for retargeting

## [104.2.8] - 2022-2-22
### Added
- Added visualization for AnimGraph skeleton.
- Fxed a bug visualization of graph skeleton doesn't follow character.

## [104.2.7] - 2022-1-25
### Changed
- version up to 104
## [103.2.7] - 2022-1-10
### Fixed
- Rebuild to work with new renderer.

## [103.2.6] - 2021-12-17
### Added
- Added support for visualization of retargeting skeletons.

## [103.2.5] - 2021-11-12
### Fixed
- Fixed a memory leak.

## [103.2.4] - 2021-10-8
### Fixed
- Fixed a crash after extension is disabled.

## [103.2.3] - 2021-10-7
### Changed
- Skel joint prims are created even when visualization flag is off.

## [103.2.2] - 2021-8-19
### Fixed
- Update Kit SDK to 54225 to fix crash.

## [103.2.1] - 2021-8-10
### Fixed
- Fixed a crash and some USD warnings. OM-35592
- Sub layer trigger full resync.

## [103.2.0] - 2021-7-23
### Changed
- Do not enable save pose feature by default.

## [103.1.2] - 2021-7-14
### Changed
- Update Kit SDK to 49389

## [103.1.1] - 2021-06-23
### Changed
- Highlight descendent of selected joints.

## [103.0.1] - 2021-06-16
### Changed
- Version update to match Update 103 Kit SDK

## [102.0.1] - 2021-06-15
### Changed
- Add feature flag

## [102.0.0] - 2021-05-31
### Changed
- Update Kit SDK.

## [101.0.1] - 2021-05-17
### Fixed
- Fixed a crash in some conditions.

## [101.0.0] - 2021-05-10
### Added
- Initial publish.
