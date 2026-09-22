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

# [107.3.1] - 2025-06-22
### Changed
- Updated to kit-sdk 107.3.1

# [107.3.0] - 2025-05-02
### Changed
- Updated to kit-sdk 107.3.0

# [107.0.13] - 2025-04-30
### Changed
- Updated for kit-sdk 107.2.0

# [107.0.12] - 2025-04-02
### Changed
- Support for linux aarch64

# [107.0.11] - 2025-02-27
### Changed
- Updated for kit-sdk 107.0.3

# [106.5.5] - 2025-02-18
### Changed
- More fixes for Digital Human Rig

# [106.5.4] - 2025-02-04
### Changed
- Updates to kit-sdk 106.5.2

# [106.5.3] - 2025-02-03
### Changed
- Changed to NV Digital Human Rig v4

# [106.5.2] - 2025-02-03
### Changed
- Fix to not overwrite the retarget pose if already exist.

# [106.5.1] - 2024-12-11
### Changed
- Updated anim_core_sdk with fix for blend shapes.

# [106.5.0] - 2024-12-03
### Changed
- Updated for kit-sdk 106.5.0

# [106.4.1] - 2024-11-12
### Changed
- Updated Human rig to have required clavicle tags and optional tags
- Fix for custom actions

# [106.4.0] - 2024-10-29
### Changed
- Updated for kit-sdk 106.4.0

# [106.3.2] - 2024-10-11
### Changed
- Renamed rig from Biped to Human

# [106.3.1] - 2024-10-02
### Changed
- Fix for updated biped automappings.

# [106.3.0] - 2024-09-26
### Changed
- Updated for kit-sdk 106.3.0

# [106.2.0] - 2024-09-25
### Changed
- Updated for kit-sdk 106.2.0

# [106.1.4] - 2024-09-17
### Changed
- More updates for the Biped rig automap for Digital Human.

# [106.1.3] - 2024-09-11
### Changed
- Updated the Biped rig automap for Digital Human.

# [106.1.2] - 2024-08-28
### Changed
- Fixes for unit tests not completing in the timemout duration.

# [106.1.1] - 2024-08-22
### Changed
- Fixes for USD schema import warnings

# [106.1.0] - 2024-08-08
### Changed
- Updated for kit sdk 106.1
- Fixed incorrect translation changes from retargeter
- Replace pinocchio with anim_core_sdk
- Fixed performance on Linux
- Updated to the new updated Biped Rig that includes Neck, Chest and Hips

# [106.0.0] - 2024-03-11
### Changed
- Updated for kit sdk 106.0

# [105.2.3] - 2023.10-24
### Changed
- Fix issue for when the chain has only one item

# [105.2.2] - 2023-10-03
- Fix load/unload retarget to use skeljoint switch mode

# [105.2.1] - 2023-08-31
- Fix retargeter - evaluation order issue - causing tilting the character

# [105.2.0] - 2023-08-01
- Kit branch.

# [105.1.3] - 2023.07-13
### Changed
- Increase the golden image test threshold

# [105.1.2] - 2023.05-22
### Changed
- Update Kit SDK.

# [105.1.1] - 2023.05-19
### Fixed
- Fix tag error.

# [105.1.0] - 2023.04-18
### Changed
- Upgrade to Kit 105.1.

# [105.0.12] - 2022-04-02
### Changed
- Force republish for registry.

# [105.0.11] - 2022-03-17
### Changed
- Upgrade to Python 3.10.

# [105.0.10] - 2023-03-08
### Changed
- Republish for kitsdk.

# [105.0.9] - 2023-02-23
### Changed
- SkelJoint V2 support.

# [105.0.8] - 2023-02-15
### Changed
- Code cleanup

# [105.0.7] - 2022-02-09
### Changed
- Fixed test

# [105.0.6] - 2022-02-07
### Changed
- Fixed test

# [105.0.5] - 2022-12-27
### Changed
- Update test

# [105.0.4] - 2022-12-21
### Changed
- Improved retargeting issue when the spine/clavicle joints are very aligned

# [105.0.3] - 2022-12-14
### Changed
- RetargetController API change :  supports different stage by providing stage_id for target skeleton

# [105.0.2] - 2022-11-18
### Changed
- Fabric update.

# [105.0.1] - 2022-11-18
### Changed
- Remove auto mapping file to read Up/Forward Axes
- Improved a popping issue when retarget pose contains twist
- Added a warning if the bind/rest pose is invalid
- Fixed issue the retarget pose is not visible when it said "visible"

# [105.0.0] - 2022-08-18
### Changed
- Update Kit SDK to 105

## [104.0.15] - 2022-08-16
### Changed
- Added shoulder/knee tags

## [104.0.14] - 2022-08-12
### Changed
- Pinocchio SDK upgrade, fix retargeting crash when many overlapping chains exists.

## [104.0.13] - 2022-07-21
### Changed
- Pinocchio SDK Upgrade
- Unit Test fixes and coverage.

## [104.0.12] - 2022-06-14
### Changed
- Pinocchio SDK Upgrade

## [104.0.11] - 2022-05-31
### Changed
- Error and Log handling

## [104.0.7] - 2022-04-25
### Changed
- Pinocchio SDK Upgrade - Motion matching, state machine, and retargeting fixes.
- fix get_forward_up_axis
- Update retarget core API
- Upgrade the repo build tools
- Update SDK
- Updated preview animations of idle and walk
- Fix for retargeting offset when twisted
- Auto pose now has more strict rule on tweaking pose
- sort use stable_sort
- Updated reference assets to the latest
- Update Icon

## [104.0.6] - 2022-03-03
### Changed
- Fix for character controller crash in compiler
- Fix for retargeting when root has rotation
- Fix of std::sort for linux - now uses std::stable_sort

## [104.0.5] - 2022-02-19
### Changed
- Minor version has changed
- Updated the Biped rig assets

## [104.0.4] - 2022-02-16
### Changed
- Description for extention
- Fixed issue with root has non identity rotation

## [104.0.3] - 2022-02-09
### Changed
- Added min tag options for has_retarget_setup
- Fixed crash when no tag is found

## [104.0.2] - 2022-01-24
### Changed
- Fixed issue with auto facing

## [104.0.1] - 2022-01-22
### Changed
- Kit version upgrade

## [103.0.5] - 2022-01-19
### Changed
- Add more keywords for Biped

## [103.0.4] - 2022-01-10
### Changed
- Improve auto set up

## [103.0.3] - 2021-12-10
### CHANGED
- Fix bugs with CC RL character set up

## [103.0.2] - 2021-12-2
### CHANGED
- Fix bugs with initial set up


## [103.0.1] - 2021-11-11
### Added
- Initial version
- Split Retarget_Window to retarget.core and retarget extension
- Provide APIs for auto tag and auto pose
