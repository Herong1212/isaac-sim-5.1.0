# Changelog

The format is base on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

# [107.3.4] - 2025-09-03
### Changed
- Adding support for linux aarch64

# [107.3.3] - 2025-08-20
### Changed
- Updated unit tests timeout duration

# [107.3.2] - 2025-07-16
### Changed
- Updated to kit-sdk 107.3.2
- Fixing dependency issues
- Replace omni.renderer_capture to omni.kit.renderer_capture

# [107.3.1] - 2025-06-22
### Changed
- Updated to kit-sdk 107.3.1

# [107.3.0] - 2025-05-02
### Changed
- Updated to kit-sdk 107.3.0

# [107.0.26] - 2025-04-02
### Changed
- Support for linux aarch64

# [107.0.25] - 2025-02-27
### Changed
- Updated for kit-sdk 107.0.3

# [106.5.4] - 2025-02-20
### Changed
- Enables UJITSO asset caching

# [106.5.3] - 2025-02-04
### Changed
- Updates to kit-sdk 106.5.2

# [106.5.2] - 2025-02-03
### Changed
- Changed to NV Digital Human Rig v4

# [106.5.1] - 2024-12-11
### Changed
- Updated anim_core_sdk with fix for blend shapes

# [106.5.0] - 2024-12-03
### Changed
- Updated for kit-sdk 106.5.0

# [106.4.1] - 2024-11-12
### Changed
- Updated extension description

# [106.4.0] - 2024-10-29
### Changed
- Updated for kit-sdk 106.4.0

# [106.3.2] - 2024-10-16
### Changed
- Fix for numpy depenency

# [106.3.1] - 2024-10-11
### Changed
- Fix for removing yaml/xml importer and exporter

# [106.3.0] - 2024-09-26
### Changed
- Updated for kit-sdk 106.3.0

# [106.1.3] - 2024-09-11
### Changed
- Updates omni.anim.asset compatibility.

# [106.1.2] - 2024-08-22
### Changed
- Fixes for USD schema import warnings

# [106.1.1] - 2024-08-16
### Changed
- Fixed anim.graph.core test image
- Support mesh export in YAML format.
- Support referencing an external animation graph file in YAML format.
- Fixed mm_path_point.usda due to make_array node update

# [106.1.0] - 2024-08-08
### Changed
- Updated for kit sdk 106.1
- Fixed incorrect translation changes from retargeter
- Enable SkelRoot to reference an external animation graph file (currently in XML format).
- Change `ApplyAnimationGraphAPICommand` interface to support external file
- Add xml samples in data/tests/xml folder
- Add unit test for external graph files
- XML mesh exporter
- Update assets for unittest.
- Updates for new omni.anim.asset extension.
- Replace pinocchio with anim_core_sdk
- Add YAML exporter
- Fixed performance on Linux
- Update anim graph XML exporter.
- Add pose XML exporter and importer.
- Updates omni.anim.asset for fixing controlRig:retargetTags
- Fix crash when multiple state machines are built.
- Add XML exporter for animation graph.
- Fixed Schema dependency version lock.
- Fxied asset cache not always work.
- Add python api to get final pose data and blendshape weights
- Temp fixed ForceUSD mode character disappear since usdskel omnihydra does not handle both fabric + USD change well.

# [106.0.0] - 2024-03-11
### Changed
- Updated for kit sdk 106.0

# [105.2.20] - 2024-02-29
### Changed
- Added settings for optinal use existed compatible SkelAnimation prim as output.

# [105.2.19] - 2024-02-22
### Changed
- Add two bone IK node.

# [105.2.18] - 2024-02-07
### Changed
- Add advanced blend settings to blend node for additive support.

# [105.2.17] - 2024-01-20
### Changed
- Fixed world forward axis calculation.

# [105.2.16] - 2024-01-13
### Changed
- Bump `omni.anim.asset` version.

# [105.2.15] - 2023-12-29
### Changed
- Addressed an unintentional version number increment in the previous release.
- This update serves as a corrective release with no operational changes.

# [105.2.14] - 2023-12-13
### Changed
- Remove self asset compiler.
- Use asset compiler extension.

# [105.2.13] - 2023-12-12
### Changed
- Release OmniGraph nodes to allow reloading of extension.

# [105.2.12] - 2023-12-08
### Changed
- Fixed poseprovider blendshape crash.

# [105.2.11] - 2023-11-27
### Changed
- Update kit sdk and fix build errors

# [105.2.10] - 2023.11-13
### Changed
- Avoid carb acquireInterface warnings

# [105.2.9] - 2023.11-02
### Changed
- Fix FBIK initialization issue

# [105.2.8] - 2023.10-24
### Changed
- Fix issue for when the chain has only one item

# [105.2.7] - 2023-10-20
### Changed
- Fixed MM nan output crash.
- Change BlendShape output order.

# [105.2.6] - 2023-10-4
- Filter node support for blend shapes.

# [105.2.5] - 2023-09-12
### Changed
- Remove skeljoint output interface and dependency.

# [105.2.4] - 2023-09-07
### Changed
- Force Output to a new SkelAnimation prim, and rename it to "AnimGraphOutputPose".

# [105.2.3] - 2023-08-31
- Fix retarget issue with order of evaluation - causing character to tilt

# [105.2.2] - 2023-08-21
- Motion matching fix for non-clamped use cases.

# [105.2.1] - 2023-08-17
- Pose Provider node support for blend shapes.

# [105.2.0] - 2023-08-01
- Kit branch.

# [105.1.7] - 2023-07-17
### Changed
- Fixed fabric attribute type.
- Fixed unit test.

# [105.1.6] - 2023-07-13
### Changed
- ETM fix for mm node test.
- Fixes perf issue in variable service using usdrt

# [105.1.5] - 2023-07-06
### Changed
- Fixed startup warnings

# [105.1.4] - 2023-05-23
### Changed
- Publish for fix Linux tests.

# [105.1.3] - 2023-05-22
### Changed
- Update Kit SDK.

# [105.1.2] - 2023-04-27
### Fixed
- Fix crash when stageReaderWrite is invalid.

# [105.1.1] - 2023-04-24
### Changed
- Remove dependency on omni.anim.shared.

# [105.1.0] - 2023-04-18
### Changed
- Upgrade to Kit 105.1.

# [105.0.26] - 2023-03-30
### Changed
- omni.anim.skeljoint ABI change.

# [105.0.25] - 2023-03-20
### Changed
- omni.anim.skeljoint ABI change.

# [105.0.24] - 2023-03-20
### Changed
- omni.anim.skeljoint ABI change.

# [105.0.23] - 2023-03-17
### Changed
- Upgrade to Python 3.10.

# [105.0.22] - 2023-03-14
### Changed
- Enable omni.skel setPose interface as the output.

# [105.0.21] - 2023-03-13
### Changed
- Republish for kit-sdk.

# [105.0.20] - 2023-03-10
### Changed
- Use omni.skel setPose interface as the output.

# [105.0.19] - 2023-03-08
### Changed
- Republish for kitsdk.

# [105.0.18] - 2023-03-02
### Changed
- Fixed test timeout.

# [105.0.17] - 2023-02-27
### Changed
- Update Kit SDK, fix tests due to timeline update.

# [105.0.16] - 2023-02-24
### Changed
- Fixed memory issue with FBIK node

# [105.0.15] - 2023-02-21
### Changed
- Update Kit SDK

# [105.0.14] - 2023-02-19
- Another kit SDK update, updated golden images.

# [105.0.13] - 2023-02-16
- Kit SDK update, build fixes.

# [105.0.12] - 2023-02-14
### Changed
- FBIK: add enable joint limits
- FBIK: split weight to position_alpha and rotation_alpha

# [105.0.11] - 2023-02-10
- Built with new schema

# [105.0.10] - 2023-02-07
### Changed
- Add Min Linear/Angular Strength support for Fullbody IK node
- Fixed Allow Pelvis to Translate to work

# [105.0.9] - 2023-02-04
### Changed
- Kit SDK Upgrade
- schema extension dependency

# [105.0.8] - 2023-1-28
### Changed
- Kit SDK Upgrade, Test data update.

# [105.0.7] - 2023-1-25
### Changed
- Kit SDK Upgrade, OmniGraph node update.

# [105.0.6] - 2023-1-19
### Changed
- Update Pinocchio SDK to handle Linux motion matching problem.

# [105.0.5] - 2023-1-12
### Changed
- Update test_apis.py to use local VisualTest data, replace references with character with no materials.
# [105.0.4] - 2022-12-21
### Changed
- Improved retargeting issue when the spine/clavicle joints are very aligned

# [105.0.3] - 2022-11-21
### Changed
- Fabric update.

# [105.0.2] - 2022-10-21
### Changed
- Fixes startup errors.

# [105.0.1] - 2022-08-22
### Changed
- FBIK support rotational target

# [105.0.0] - 2022-08-18
### Changed
- Update Kit SDK to 105

## [104.0.28] - 2022-08-12
### Changed
- Pinocchio SDK upgrade, fix retargeting crash when many overlapping chains exists.

## [104.0.27] - 2022-08-11
### Changed
- Pinocchio SDK upgrade, fix Pose Provider crash with State Machine

## [104.0.26] - 2022-08-08
### Changed
- Pinocchio SDK upgrade, fix FBIK crash with Pose Provider node

## [104.0.25] - 2022-07-28
### Changed
- Pinocchio SDK upgrade, fix FBIK with multiple instance

## [104.0.24] - 2022-07-22
### Changed
- Pinocchio SDK upgrade, FBIK crash fix for Motion Matching node

## [104.0.23] - 2022-07-21
### Changed
- Pinocchio SDK upgrade, FBIK crash fix.
- More unit test coverage.

## [104.0.22] - 2022-07-20
### Changed
- Kit SDK Upgrade, omni.timeline change.
- Python unit tests: coverage and fixes.

## [104.0.21] - 2022-07-10
### Changed
- Pinocchio SDK Update: Fullbody IK Node!
- Minor compiler fixes.

## [104.0.20] - 2022-06-29
### Changed
- kit-sdk upgrade

## [104.0.19] - 2022-06-28
### Changed
- GetJointTransform

## [104.0.18] - 2022-06-27
### Changed
- Improved node errors and logging without UI.
- Move to token constants to avoid problems with mismatched schema versions.

## [104.0.17] - 2022-06-14
### Changed
- Pinocchio SDK Upgrade.

## [104.0.16] - 2022-06-14
### Changed
- Test dependency update.
- Character bindings

## [104.0.15] - 2022-05-31
### Changed
- Fixes to Character bindings. Don't require play mode for certain calls, more consistent handling of that check.

## [104.0.14] - 2022-05-31
### Changed
- Added Animation Graph error handling

## [104.0.13] - 2022-04-21
### Changed
- Pinocchio SDK Upgrade (crash fixes)
- Enter play mode performance on large scenes.
- PhysX dependency is optional and tracked internally when loaded.

## [104.0.12] - 2022-04-05
### Changed
- Parity with 103.1 branch after Create beta release.
  - SDK update.
  - Compile/validation fixes.
  - Python API and commands.

## [104.0.11] - 2022-03-13
### Changed
- State machine inertial blend transition fix.
- Fix retargeting offset issue

## [104.0.10] - 2022-03-10
### Changed
- Fixes for omni.anim.graph.ICharacter api error messages.

## [104.0.9] - 2022-03-07
### Changed
- Added ConditionAND and ConditionOR

## [104.0.8] - 2022-03-03
### Changed
- Fixed PoseProvider

## [104.0.7] - 2022-02-22
### Changed
- Fix extension dependency

## [104.0.6] - 2022-02-19
### Changed
- Split from omni.anim.graph from commit 4b61003c

## [104.0.5] - 2022-02-18
### Changed
- API update
- UI bug fix

## [104.0.4] - 2022-02-14
### Changed
- Major update for UI and AnimGraphSchema

## [104.0.3] - 2022-02-09
### Changed
- Fix crash when no overlapping tag is found when retargeting

## [104.0.2] - 2022-01-10
### Changed
- Motion Matching maintanance
- AnimGraph UI maintanance

## [104.0.1] - 2022-01-20
### Changed
- Motion Matching maintanance

## [103.0.2] - 2022-01-19
### Changed
- Fixed retargeting joint mapping issue in AnimGraph

## [103.0.1] - 2022-01-01
### added
- Porting from old extension based on commit c2c6d6f5
