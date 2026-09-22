# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

# [107.3.3] - 2025-09-03
### Changed
- Adding support for linux aarch64

# [107.3.2] - 2025-07-16
### Changed
- Updated to kit-sdk 107.3.2
- Fixing dependency issues

# [107.3.1] - 2025-06-22
### Changed
- Updated to kit-sdk 107.3.1

# [107.0.11] - 2025-02-27
### Changed
- Updated for kit-sdk 107.0.3

# [106.5.2] - 2025-02-11
### Changed
- Changed legacy viewport extension to new viewport extension

# [106.5.1] - 2025-02-04
### Changed
- Updates to kit-sdk 106.5.2

# [106.5.0] - 2024-12-03
### Changed
- Updates to kit-sdk 106.5.2

# [106.4.1] - 2024-11-12
### Changed
- Removed external animation graph menu

# [106.4.0] - 2024-09-29
### Changed
- Updated for kit-sdk 106.4.0

# [106.3.1] - 2024-10-11
### Changed
- Fix for removing yaml/xml importer and exporter

# [106.3.0] - 2024-09-26
### Changed
- Updated for kit-sdk 106.3.0

# [106.2.0] - 2024-09-25
### Changed
- Updated for kit-sdk 106.2.0

# [106.1.3] - 2024-09-17
### Changed
- Updated the AWS samples folder to 106.2

# [106.1.2] - 2024-09-11
### Changed
- Updated the AWS samples folder for asset compatibility for kit-sdk 106.1

# [106.1.1] - 2024-08-22
### Changed
- Fixes for USD schema import warnings
- Enable export in YAML format through context menu.

# [106.1.0] - 2024-08-08
### Changed
- Updated for kit sdk 106.1
- Fix ui_test issue in test_apply_external_graph when setting path to omni.kit.widget.path_field with new kit-sdk
- Enable SkelRoot to reference an external animation graph file (currently in XML format).
- Add new `External Animation Grpah` option in AnimGraphAPIPropertiesWidget
- Add xml samples in data/tests/xml folder
- Add unit test for external graph files
- Add context menu for XML mesh exporter
- Add YAML export function for animation graph.
- Add XML export function for animation graph.

# [106.0.0] - 2024-03-11
### Changed
- Updated for kit sdk 106.0

# [105.2.6] - 2024-02-22
- Add two bone IK node.
- Fix ETM failure

# [105.2.5] - 2024-2-8
- Additive blend support.

# [105.2.4] - 2023-11-10
- Fix issues with variable type.

# [105.2.3] - 2023-10-4
- Filter node support for blend shapes.

# [105.2.2] - 2023-09-25
- Fixes for menu warnings.

# [105.2.1] - 2023-08-17
- Pose Provider node support for blend shapes.

# [105.2.0] - 2023-08-01
- Kit branch.

# [105.1.2] - 2023.07-07
### Changed
- Optimize traversal

# [105.1.3] - 2023-07-07
### Changed
- Fixes issue with drag/drop SkelAnimations from stage to Animation Graph

# [105.1.2] - 2023-07-06
### Changed
- Fixed startup warnings

# [105.1.1] - 2023-05-22
### Changed
- Update Kit SDK.

# [105.1.0] - 2023-04-18
### Changed
- Upgrade to Kit 105.1.

# [105.0.18] - 2022-04-02
### Changed
- Force republish for registry.

# [105.0.17] - 2022-03-17
### Changed
- Upgrade to Python 3.10.

# [105.0.16] - 2023-02-24
### Changed
- Fixes for menus.

# [105.0.15] - 2023-02-21
### Changed
- Updated Kit SDK

# [105.0.14] - 2023-02-14
### Changed
- FBIK: add enable joint limits
- FBIK: split weight to position_alpha and rotation_alpha

# [105.0.13] - 2023-02-10
### Changed
- Fix thresholds for unit tests

# [105.0.12] - 2023-02-09
### Changed
- Updated mm_relationship_widget to correctly leverage legacy widget.

# [105.0.11] - 2023-02-07
### Changed
- Add Min Linear/Angular Strength support for Fullbody IK node
- Fixed Allow Pelvis to Translate to work

# [105.0.9] - 2023-02-04
### Changed
- Kit SDK Upgrade
- schema extension dependency

# [105.0.8] - 2023-01-12
### Changed
- Remove unused import

# [105.0.7] - 2022-11-21
### Changed
- Test fixes.
- MM Relationship update

# [105.0.6] - 2022-11-21
### Changed
- Fabric update.

# [105.0.5] - 2022-10-26
### Changed
- Added stage load activity.

# [105.0.4] - 2022-10-21
### Changed
- Remove prototype menu items.

# [105.0.3] - 2022-10-13
### Changed
- Fixed variable service usd change notice.

# [105.0.2] - 2022-09-29
### Changed
- Fixed the bug where navigation ui tries to view deleted nodes.

# [105.0.1] - 2022-09-15
### Changed
- Updates from new Kit SDK
- Remove the sample window, register directory with kit sample (ported from 104)

# [105.0.0] - 2022-08-18
### Changed
- Update from new Kit SDK 105

## [104.0.11] - 2022-06-27
### Changed
- Added Animation Graph error handling

## [104.0.9] - 2022-04-05
### Changed
- Parity with 103.1 branch after Create beta release.
  - Several fixes.
  - Production sample content location.
  - Add visualization nodes dependency for samples.

## [104.0.8] - 2022-03-07
### Changed
- Added ConditionAND and ConditionOR

## [104.0.7] - 2022-03-03
### Changed
- Fixed PoseProvider

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
