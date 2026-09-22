# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

# [107.3.6] - 2025-10-03
### Changed
- Fix stage create context menu

# [107.3.5] - 2025-09-25
### Changed
- Adds viewport create context menu

# [107.3.4] - 2025-09-03
### Changed
- Adding support for linux aarch64

# [107.3.3] - 2025-08-12
### Changed
- Add agent config for minimum island radius

# [107.3.2] - 2025-07-16
### Changed
- Updated to kit-sdk 107.3.2
- Fixing dependency issues

# [107.3.1] - 2025-06-22
### Changed
- Updated to kit-sdk 107.3.1
- Fixes for new SDF based collision avoidance

# [107.3.0] - 2025-05-02
### Changed
- Updated to kit-sdk 107.3.0

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
- Updated for kit-sdk 106.5.0

# [106.4.2] - 2024-11-19
### Changed
- Added options for navigation vizualization options for border only

# [106.4.1] - 2024-11-12
### Changed
- Minor UI tweaks

# [106.4.0] - 2024-10-29
### Changed
- Updated for kit-sdk 106.4.0

# [106.3.1] - 2024-10-02
### Changed
- Fix for navmesh progress and baking.
- Fix for geometry tab in NavMesh window.

# [106.3.0] - 2024-09-26
### Changed
- Updated for kit-sdk 106.3.0

# [106.2.0] - 2024-09-25
### Changed
- Updated for kit-sdk 106.2.0

# [106.1.6] - 2024-09-24
### Changed
- Updated APIs for removing queryFilters and updated NavMesh events

# [106.1.5] - 2024-09-20
### Changed
- Remove exclude dependency on behavior:interactive objects

# [106.1.4] - 2024-09-17
### Changed
- Updated the AWS samples folder to 106.2

# [106.1.3] - 2024-09-11
### Changed
- Updated the AWS samples folder for asset compatibility for kit-sdk 106.1

 [106.1.2] - 2024-09-03
### Changed
 - Fixes for unit tests due to USD errors on NavMesVolume.box

# [106.1.1] - 2024-08-22
### Changed
- Changes the NavMesh Geometry to a menu bar style.

# [106.1.0] - 2024-08-08
### Changed
- Updated for kit sdk 106.1
- Minor updates to NavMesh Geometry buttons
- Updates for updated omni.anim.navigation.core apis.
- Support other variable types in condition_compare_node
- Add joint/blendshape mapping for pose-provider node
- Simplified Navigation Exclusion List UI

# [106.0.0] - 2024-03-11
### Changed
- Updated for kit sdk 106.0

# [105.2.3] - 2023-11-27
### Changed
- Update kit sdk and fix build errors

# [105.2.2] - 2023-09-25
- Fixes for menu warnings.

# [105.2.1] - 2023-08-22
- Update NavMesh window layout and areas support.

# [105.2.0] - 2023-08-01
- Kit branch.

# [105.1.3] - 2023.07-13
- Test fix.

# [105.1.2] - 2023.06-07
### Changed
- Fixed startup warnings.

# [105.1.1] - 2023.05-09
### Changed
- Kit SDK Upgrade.
- Release bugfixes, window design overhaul.

# [105.1.0] - 2023.04-18
### Changed
- Upgrade to Kit 105.1.

# [105.0.18] - 2022-04-02
### Changed
- Force republish for registry.

# [105.0.17] - 2022-03-17
### Changed
- Upgrade to Python 3.10.

# [105.0.16] - 2023-03-06
### Changed
- Debug mode: exposing extra Recast parameters in the ui only when in debug mode

# [105.0.15] - 2023-02-21
### Changed
- Updated Kit SDK

# [105.0.14] - 2023-02-17
### Changed
- Remove display settings Navigation sub-menu.

# [105.0.13] - 2023-02-04
### Changed
- Kit SDK Upgrade
- schema extension dependency

# [105.0.12] - 2023-01-24
### Changed
- Adding `--/app/fastShutdown=true` to fix tests

# [105.0.11] - 2022-12-19
### Changed
- Only showing NavPath Obstacle properties for the selected shape

# [105.0.10] - 2022-12-06
### Changed
- Changed NavPath to use BasisCurves instead of experimental NavSchema.NavPath

# [105.0.9] - 2022-12-01
### Fixed
- Fixed cache buttons errors if cache directory doesn't exist.

# [105.0.8] - 2022-11-18
### Added
- Added unittest for NavMesh Window.

# [105.0.7] - 2022-11-15
### Added
- Added tooltips and annotations to NavMesh bake settings.

# [105.0.6] - 2022-11-07
### Added
- Added property widget for `NavMeshObstacleAPI`.
- Added `Cache` section in `NavMesh` window to enable/open/clear cache.
- Added `Cancel All` button to cancel all pending baking request.
### Changed
- The first NavMeshVolume to be created from the menu will try to enclose the entire stage.
- Adding NavMeshObstacle to a prim automatically set the obstacle size from prim's extents.

# [105.0.5] - 2022-11-01
### Added
- Add context menu item to apply/remove `NavMeshObstacleAPI` schema.

# [105.0.4] - 2022-10-20
### Added
- Add context menu item to apply/remove NavMeshExcludeAPI schema
- NavMesh Exclusions window that lists excluded prims
- Automatically exclude prims with Physcs RigidBodies

# [105.0.3] - 2022-10-13
### Changed
- Added NavMesh Tool.

# [105.0.2] - 2022-09-29
### Changed
- Fixes for NavPath stage loading.

# [105.0.1] - 2022-09-27
### Changed
- Initial NavPath support

# [105.0.0] - 2022-08-18
### Changed
- Initial extension created.
