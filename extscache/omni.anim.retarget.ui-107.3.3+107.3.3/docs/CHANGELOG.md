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

# [107.3.0] - 2025-05-02
### Changed
- Updated to kit-sdk 107.3.0

# [107.0.8] - 2025-04-15
### Changed
- Fixes for extension dependencies

# [107.0.7] - 2025-02-27
### Changed
- Updated for kit-sdk 107.0.3

# [106.5.6] - 2025-02-18
### Changed
- More fixes for Digital Human Rig

# [106.5.5] - 2025-02-04
### Changed
- Updates to kit-sdk 106.5.2

# [106.5.4] - 2025-02-03
### Changed
- Changed to NV Digital Human Rig v4

# [106.5.3] - 2025-02-03
### Changed
- Fix to not overwrite the retarget pose if already exist.

# [106.5.2] - 2024-12-13
### Changed
- Fixes for disabling preview and retarget buttons when no skeleton selected

# [106.5.1] - 2024-12-03
### Changed
- Updates for preview workflow

# [106.5.0] - 2024-12-03
### Changed
- Updated for kit-sdk 106.5.0

# [106.4.1] - 2024-11-12
### Changed
- Updated rig with new optional tags and tag sets

# [106.4.0] - 2024-10-29
### Changed
- Updated for kit-sdk 106.4.0

# [106.3.5] - 2024-10-28
### Changed
- Fix for selecting current skeleton in stage

# [106.3.4] - 2024-10-21
### Changed
- Fix for incorrect icon extension path.

# [106.3.3] - 2024-10-18
### Changed
- Fix for joint selection svg icon rasterization error

# [106.3.2] - 2024-10-16
### Changed
- Fix for svg icon loading errors

# [106.3.1] - 2024-10-11
### Changed
- Renamed rig from Biped to Human
- New Retarget window ux

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

# [106.1.0] - 2024-08-08
### Changed
- Updated for kit sdk 106.1
- Attempt fix UI test delay issue
- Changed test window size
- Updated to the new update Biped Rig that includes Neck, Chest and Hips

# [106.0.0] - 2024-03-11
### Changed
- Updated for kit sdk 106.0

# [105.2.1] - 2023-10-03
- Add Hide Pose for retarget pose

# [105.2.0] - 2023-08-01
- Kit branch.

# [105.1.4] - 2023.07-06
### Changed
- Optimize stage attach

# [105.1.3] - 2023.07-06
### Changed
- Fix an issue with creating character

# [105.1.2] - 2023.07-06
### Changed
- Optimize attach/detach of skeleton

# [105.1.1] - 2023.05-22
### Changed
- Update Kit SDK.

# [105.1.0] - 2023.04-18
### Changed
- Upgrade to Kit 105.1.

# [105.0.7] - 2022-04-02
### Changed
- Force republish for registry.

# [105.0.6] - 2022-03-17
### Changed
- Upgrade to Python 3.10.

# [105.0.5] - 2023-02-23
### Changed
- SkelJoint V2 support

# [105.0.4] - 2023-02-15
### Changed
- Code cleanup

# [105.0.3] - 2022-02-07
### Changed
- Fixed test

# [105.0.2] - 2022-12-14
### Fixed
- RetargetController API change

# [105.0.1] - 2022-10-11

### Fixed
- Making a new ui.Window named Viewport that breaks functionality in the original one.
### Changed
- Unregister samples fix.
- Samples reorganization.

# [105.0.0] - 2022-08-18
### Changed
- Update Kit SDK to 105

## [104.0.9] - 2022-4-25
### Changed
- Updated to use new retarget core API changes
- Upgrade the repo build tools
- Fix shutdown error
- Updated SDK
- Tweaked preview so now it only shows mesh during preview
- missing recommended tags will display warning sign and also change tag color to error color
- fixed issue with forward/up axis visualizer for multi viewport

## [104.0.8] - 2022-03-14
### Changed
- Updated icon

## [104.0.7] - 2022-02-23
### Changed
- Fix extension restart error

## [104.0.6] - 2022-02-19
### Changed
- Minor version has changed
- Fixed a bug with loading preview asset in wrong axis

## [104.0.5] - 2022-02-17
### Changed
- Rename to omni.anim.retarget.ui

## [104.0.4] - 2022-02-16
### Changed
- Fixed UI typo/description
- Fixed assign skeljoint

## [104.0.3] - 2022-02-09
### Changed
- Added facing visualizer

## [104.0.2] - 2022-02-1
### Changed
- Open window command support

## [104.0.1] - 2022-01-21
### Changed
- Kit version upgrade

## [103.0.9] - 2022-01-19
### Changed
- Support extra tags - only overlapping tags are used

## [103.0.8] - 2022-01-10
### Changed
- Improve auto set up

## [103.0.7] - 2021-12-13
### Changed
- Update Pinocchio SDK to 0.1.34

## [103.0.6] - 2021-12-10
### Changed
- Removed exact version dependency

## [103.0.5] - 2021-12-8
### Changed
- Move to omni.kit.viewport_legacy

## [103.0.4] - 2021-12-2
### CHANGED
- Fixed window to be able to still maximize

## [103.0.3] - 2021-12-2
### CHANGED
- Fixed tagging bug initially
- Made sure Skeleton always stays on the top
- Avatar window now supports assign/delete tags using context menu

## [103.0.2] - 2021-11-22
### CHANGED
- Updated UX for retarget pose/facing/preview
- Added default skeleton/preview options for auto pose and preview


## [103.0.1] - 2021-11-11
### Added
- Initial version
- Split Retarget_Window extension to retarget.core and retarget extension
- Retarget_Window is no omni.anim.retarget extension
