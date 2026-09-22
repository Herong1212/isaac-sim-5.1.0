# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

# [107.3.8] - 2025-09-26
### Changed
- Fix for navmesh test 

# [107.3.7] - 2025-09-25
### Changed
- Removed deps on deprecated omni.debugdraw using carb.scenerenderer
- Fixes for repeatable results for random_point
- Changes for CreateNavMeshVolumeCommand
- Improvements for NavMesh visualization

# [107.3.6] - 2025-09-03
### Changed
- Adding support for linux aarch64
- Fixes navmesh navmesh area clipping
- Added INavController parameters

# [107.3.5] - 2025-08-28
### Changed
- Fixes for dynamic collision avoidance
- Adds api for debug line filtering with optionmal agentMaxRadius

# [107.3.4] - 2025-08-12
### Changed
- Add agent config for minimum island radius

# [107.3.3] - 2025-07-29
### Changed
- Disable navmesh bake signature test

# [107.3.2] - 2025-07-16
### Changed
- Updated to kit-sdk 107.3.2
- Fixing dependency issues

# [107.3.1] - 2025-06-22
### Changed
- Updated to kit-sdk 107.3.1
- Fixes for new SDF based collision avoidance
- Adds default NotWalkable area

# [107.3.0] - 2025-05-02
### Changed
- Updated to kit-sdk 107.3.0

# [107.0.21] - 2025-02-27
### Changed
- Updated for kit-sdk 107.2.0

# [107.0.20] - 2025-04-15
### Changed
- Updated to mesh_tools based GPU based crowd and collision avoidance
- Fix for query_closest_point with area probabilities support

# [107.0.19] - 2025-04-02
### Changed
- Support for linux aarch64

# [107.0.18] - 2025-02-27
### Changed
- Updated for kit-sdk 107.0.3

# [106.5.8] - 2025-02-21
### Changed
- Update for meshtool upgrade.

# [106.5.7] - 2025-02-04
### Changed
- Updates to kit-sdk 106.5.2
- Adds setting to support forcing persistent cache on navmesh baking instead of session cache

# [106.5.6] - 2025-02-03
### Changed
- Fixes navmesh shutdown crash
- Minor changes to APIs

# [106.5.5] - 2024-12-20
### Changed
- Fixes for flaky unit tests.

# [106.5.4] - 2024-12-19
### Changed
- Fixes for navigation python bindings obstacle_ids array type.

# [106.5.3] - 2024-12-16
### Changed
- Updated for enabling meshtools as a testing extension to be loaded with specific version instead of test dependency.
- Added exact version for navigation schema dependency.

# [106.5.2] - 2024-12-13
### Changed
- Fixes start_navmesh_baking_and_wait() to return true when baking succeeds.

# [106.5.1] - 2024-12-07
### Changed
- Added API for debug visualization for navmesh obstacles

# [106.5.0] - 2024-12-03
### Changed
- Updated for kit-sdk 106.5.0

# [106.4.3] - 2024-12-02
### Changed
- Add method startNavMeshBakingAndWait waiting for navmesh baking to complete

# [106.4.2] - 2024-11-21
### Changed
- Adds method isNavMeshBaking for checking if navmesh is currently baking.
- Adds setting for navmesh visualization for border only and sets this to the default.

# [106.4.1] - 2024-11-12
### Changed
- Updated testing golden data processing that is independent of omni.usd

# [106.4.0] - 2024-10-29
### Changed
- Updated for kit-sdk 106.4.0

# [106.3.5] - 2024-10-28
### Changed
- Fix for improved navmesh cache management

# [106.3.4] - 2024-10-18
### Changed
- Fix for startNavMeshBaking() return being not correct and related logging

# [106.3.3] - 2024-10-16
### Changed
- Fix for crash in navmesh and navmesh path memory leak
- Fix for crash in navmesh visualization
- Fix for missing numpy dependency

# [106.3.2] - 2024-10-11
### Changed
- Fix for navmesh caching.

# [106.3.1] - 2024-10-02
### Changed
- Fix for navmesh baking progress.
- Fix for adjusting navmesh height offset closer to geometry.
- Fix for excessive baking logging.
- Fix in pathfinding queries that jumped to upper geometry along path results.
- Fix for Navigation APIs and simplified event stream baking events.
- Fix for auto-exclude rigid bodies with child colliders.
- Fix to correct the navmesh area color and picker to match.
- Fix for navmesh area persistence.

# [106.3.0] - 2024-09-26
### Changed
- Updated for kit-sdk 106.3.0

# [106.2.1] - 2024-09-25
### Changed
- Fix for prim with rigid bodies duplicated are not excluded.
- Fix to clear NavMesh when no NavMeshVolumes remain in the stage.

# [106.2.0] - 2024-09-25
### Changed
- Updated for kit-sdk 106.2.0

# [106.1.8] - 2024-09-24
### Changed
- Updated APIs for removing queryFilters and updated NavMesh events

# [106.1.7] - 2024-09-20
### Changed
- Remove exclude dependency on behavior:interactive objects

# [106.1.6] - 2024-09-17
### Changed
- Updated test navmesh extension dependency

# [106.1.5] - 2024-09-11
### Changed
- Fixes to python bindings for improved object definition

# [106.1.4] - 2024-09-03
### Changed
 - Fixes for unit tests due to USD errors on NavMesVolume.box

# [106.1.3] - 2024-08-28
### Changed
 - Fixes for unit tests

# [106.1.2] - 2024-08-27
### Changed
- Fixes NavMesh bake settings for agentMaxStepHeight and agentMaxFloorSlope

# [106.1.1] - 2024-08-22
### Changed
- Update to INavigation version to 2.1

# [106.1.0] - 2024-08-08
### Changed
- Updated for kit sdk 106.1
- Update to INavigation version to 2.0
- Removed INavMeshAgent
- Fixed performance on Linux
- Fixes for geometry instancing and exclusion.

# [106.0.0] - 2024-03-11
### Changed
- Updated for kit sdk 106.0

# [105.2.8] - 2024-01-20
### Changed
- Fixed output data space.

# [105.2.7] - 2023-11-29
### Changed
- Create python binding for setting random seed

# [105.2.6] - 2023-11-27
### Changed
- Integrated pinocchio with NavMesh random point improvements
- Update kit sdk and fix build errors

# [105.2.5] - 2023-09-25
- Updated golden images for navigation core to fix OM-93894 which is renderer update in kit.

# [105.2.4] - 2023-09-25
- Additional fixes for NavMesh Areas settings.

# [105.2.3] - 2023-08-30
- Fix for NavMesh Area settings migration.

# [105.2.2] - 2023-08-22
- Update NavMesh window layout and areas order support.

# [105.2.1] - 2023-08-01
- Navigation Area and Query Filters

# [105.2.0] - 2023-08-01
- Kit branch.

# [105.1.2] - 2023.05-22
### Changed
- Kit SDK Upgrade for tests.

# [105.1.1] - 2023.05-09
### Changed
- Kit SDK Upgrade.
- Release bugfixes, random and closest points, visualization updates.

# [105.1.0] - 2023.04-18
### Changed
- Upgrade to Kit 105.1.

# [105.0.31] - 2023-04-02
### Changed
- The advanced navmesh parameters are ignored by Pinocchio (this is temporary until we decide what to do, either remove them or enable them, I want to remove them).
- The generated navmesh should have good performance. I've increased the cell size a bit, which lowers the fidelity somewhat, but it improves the speed of the baking, and it looks fine (of course we have to test).
- The navmesh cache file name extension changed from .nav to .nvc (format change).
- The voxel grid that used to be discarded is no longer discarded, it's persisted in the navmesh cache file.
- The voxel grid is used to adjust the height for path points as well as for validate_point.

# [105.0.30] - 2022-03-21
### Changed
- Fixed "cache keeps reloading"
- Fixed unwanted baking when there is cached navmesh
- Improved log messages

# [105.0.29] - 2022-03-17
### Changed
- Upgrade to Python 3.10.

# [105.0.28] - 2023-03-08
### Changed
- Republish for kitsdk.

# [105.0.27] - 2023-02-28
### Added
- NavMeshAgent support

# [105.0.26] - 2023-02-21
### Changed
- Updated Kit SDK

# [105.0.25] - 2023-02-15
### Changed
- Removed spamming on NavMesh missing.

# [105.0.24] - 2022-02-13
### Changed
- Fixes for NavNesh events

# [105.0.22] - 2022-02-13
### Changed
- Fixes for NavMesh baking.

# [105.0.22] - 2022-02-13
### Changed
- Built with new schema

# [105.0.21] - 2023-02-04
### Changed
- Kit SDK Upgrade
- schema extension dependency

# [105.0.20] - 2023-01-31
### Changed
- Fixing the navmesh memory leak in path query

# [105.0.19] - 2023-01-25
### Changed
- Fixing the undesired vertical offset in navmesh in Pinocchio, making it always the minimum acceptable unit
- Update Pinocchio version

# [105.0.18] - 2023-01-24
### Changed
- Adding `--/app/fastShutdown=true` to fix tests

# [105.0.17] - 2022-12-20
### Changed
- Refreshing the property panel when a schema is applied/removed

# [105.0.16] - 2022-12-06
### Changed
- Changed NavPath to use BasisCurves instead of experimental NavSchema.NavPath

# [105.0.15] - 2022-12-02
### Changed
- Updated Pinocchio version that uses different approach to find path, which may give better result (shorter).
- Exposed `overrideRayCastProportions` on `queryNavMeshPath` allowing caller to customize the range to look for shortcuts on the path.

# [105.0.14] - 2022-12-01
### Changed
- Changed cache folder name from `navmesh` to `navmeshcache`.

# [105.0.13] - 2022-11-23
### Fixed
- Fixed validate_navmesh_point

# [105.0.12] - 2022-11-15
### Added
- Added `offset` support on `NavMeshObstacle`.
- Added unittest.
### Changed
- Allow up to 63 vertical layers in one navmesh tile.
- Changed default NavMesh agent configuration to more sensible values.
### Fixed
- NavMeshVolume placement now reverses its parent transform and places into world space.

# [105.0.11] - 2022-11-07
### Added
- Added ability to stop NavMesh baking.
- Added `draw` to `NavMeshPath` object to visualize the path.
### Fixed
- Fixed agent size and path query on NavMesh read from Cache.
- Fixed NavMeshObstacle running out of free slot if it is not touching any NavMesh tile.
- Properly crops the NavMesh if tile size is not a integer multiply of bound size.
### Changed
- Only changed NavMeshObstacle will be updated.
- `query_navmesh_path` and `validate_navmesh_point` now accept additional `half_extents` parameter to set the query range.

# [105.0.10] - 2022-11-02
### Fixed
- Fixed NavMeshVolume visualization not removed after prim is deleted.

# [105.0.9] - 2022-11-01
### Changed
- `NavMeshVolume` now only works as include volume. Exclude feature is now moved to `NavMeshObstacleAPI`.
- Reduced OOM during NavMesh baking with updated pinocchio library.

# [105.0.8] - 2022-10-26
### Fixed
- Crash in NavPathManager

# [105.0.7] - 2022-10-21
### Added
- OM-65636: NavMeshExcludeAPI UI
- Add context menu item to apply/remove NavMeshExcludeAPI schema
- NavMesh Exclusions window that lists excluded prims
- Automatically exclude prims with Physcs RigidBodies

# [105.0.6] - 2022-10-21
### Fixed
- Fixed crash on exit.
# [105.0.5] - 2022-10-20
### Added
- Save/Load navmesh baking parameters with USD file.
- Save/Load baked navmesh to/from cache.
- Added NavMesh event stream.
### Fixed
- Fixed navmesh bounds range.
### Changed
- Various module cleanups.

# [105.0.4] - 2022-10-14
### Changed
- Properly use of pinocchio up axis for navmesh.
- Improved performance for larger scene.
- Included overlapping face if it's partially within range.
- Excluded mesh with NavMeshExcludeAPI.

# [105.0.3] - 2022-10-11
### Changed
- Initial version of NavMesh baking, visualization and path query.

# [105.0.2] - 2022-09-28
### Changed
- Fixes for NavPath stage loading.

# [105.0.1] - 2022-09-27
### Changed
- Initial NavPath support

# [105.0.0] - 2022-08-18
### Changed
- Initial extension created.
