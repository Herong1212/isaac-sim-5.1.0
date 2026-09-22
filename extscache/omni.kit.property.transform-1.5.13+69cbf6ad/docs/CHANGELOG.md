# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.5.13] - 2025-07-15
### Fixed
- Fixed a bug when selecting an xformable prim before saving a stage, which results in "Ill-formed SdfPath" warning message.

## [1.5.12] - 2025-02-12
### Fixed
- Fixed a bug when updating Fabric transform into single model transform widgets.

## [1.5.11] - 2024-12-16
### Changes
- Added "test_transform_time_samples" test

## [1.5.10] - 2024-10-11
### Changes
- Updated API and __all__ exports

## [1.5.9] - 2024-08-29
### Fixed
- Re-added xform_op_utils function get_inverse_op_Name

## [1.5.8] - 2024-08-05
### Fixed
- Fixed argument forwarding in FabricGfMatrixAttributeModel.

## [1.5.7] - 2024-07-23
### Changed
- Fixed private class access (accessing functions/variables with _)

## [1.5.6] - 2024-07-12
### Changed
- Updated documentation with AI agent.

## [1.5.5] - 2024-06-13
### Changed
- Remove _add_key from USDXformOpWidget
- Remove _settings from USDXformOpOrientWidget because it is defined in base class USDXformOpWidget

## [1.5.4] - 2024-06-07
### Fixed
- Fixed linting typo
- Added "test_transform_add_transforms" test

## [1.5.3] - 2024-05-29
### Fixed
- Fixed linting typo
- Added "test_transform_rotate_order_dropdown" test

## [1.5.2] - 2024-05-17
### Fixed
- Fixed linting issues

## [1.5.1] - 2024-03-27
### Changes
-  OM-122163: support latest omni.kit.manipulator.prim which write omni.fabric.localMatrix

## [1.5.0] - 2024-03-01
### Changes
-  OM-121330: Updated to use omni.kit.widget.context_menu

## [1.4.0] - 2024-01-29
### Changes
- OM-36400: Set change_on_edit_end default to True, though allowing dragging to always update every frame.

## [1.3.10] - 2023-08-03
### Fixed
- Changed silent exception message

## [1.3.9] - 2023-06-20
### Fixed
- Rotate widget's icon image display issue

## [1.3.8] - 2023-03-16
### Fixed
- Fixed property search

## [1.3.7] - 2023-03-01
### Changed
- Multi-prim selection mode change when no common xformOp, simply display "The selected prims have no common transforms to display" in the widget
-
## [1.3.6] - 2023-02-05
### Added
- Added property filter support

## [1.3.5] - 2022-09-30
### Added
- Added listener for `ADDITIONAL_CHANGED_PATH_EVENT_TYPE` event in message bus to trigger additional property invalidation.

## [1.3.4] - 2022-09-19
- Transform offset fields are now draggable

## [1.3.3] - 2022-08-03
- Linked scaling now works for resetting to defaults
- Linked scaling no longer breaks when value is zero

## [1.3.2] - 2022-06-16
- Support Reset all attributes for the Transform Widget
- Updating link scale button icon

## [1.3.1] - 2022-05-27
### Changed
- Support Copy/Paste all attribute for the Transform Widget
-
## [1.3.0] - 2022-05-12
### Changed
- Offset mode updated to consider add/multiply operations

## [1.2.0] - 2022-04-28
### Added
- Option to link scale components
- offset mode test

## [1.1.0] - 2022-03-09
### Added
- Added offset mode

## [1.0.2] - 2020-12-09
### Changes
- Added extension icon
- Added readme
- Updated preview image

## [1.0.1] - 2020-10-22
### Added
- removed `TransformPrimDelegate` so its now controlled by omni.kit.property.bundle

## [1.0.0] - 2020-10-7
### Added
- Created
