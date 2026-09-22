# Changelog

## [107.3.12] - 2025-09-25
### Updated
- Updated mesh tools version

## [107.3.11] - 2025-09-16
### Fixed
- Fixed crash where buffer overflow when processing primvars when merging and checking out of bounds with better handling

## [107.3.10] - 2025-09-08
### Updated
- Updated mesh tools version

## [107.3.9] - 2025-06-02
### Updated
- Updated mesh tools version

## [107.3.8] - 2025-05-29
### Fixed
- Timeouts in unit testing CI

### Updated
- Updated mesh tools version

## [107.3.7] - 2025-05-20
### Added
- Support for USDPhysics angular velocity and distant lights in Edit Stage Metrics 
- Support for USD predicate expressions in operations

## [107.3.6] - 2025-05-14
### Fixed
- Merge meshes with custom output name

## [107.3.5] - 2025-05-08
### Updated
- Updated kit version

## [107.3.4] - 2025-05-06
### Fixed
- Manifold handling for face winding order

## [107.3.3] - 2025-05-01
### Fixed
- Compute pivot updated checks for empty points attributes

## [107.3.2] - 2025-04-29
### Updated
- Updated unit tests to specify a temporary directory location

## [107.3.1] - 2025-04-24
### Fixed
- MaterialBind on subset indexed attributes are handled to display correct material binding

## [107.3.0] - 2025-04-23
### Added
- New Generate Normals operation
- New Manifold Meshes operation

### Updated
- Merge vertices operation now has make manifold option on by default

## [107.1.4] - 2025-04-14
### Fixed
- Pivot transform Ops are handled correctly in Deduplicate Geometry operation

## [107.1.3] - 2025-04-08
### Fixed
- Primvars re-indexes attributes that originally had indices
- Merge Meshes better handling for Original Prim merge point
 - Ensured conflicting double xformOp pivots do not retain their type
 - Cleaned up the behavior of splitting and clustering invisible prims

### Updated
- Removed extra copies of libraries from core path

## [107.1.2] - 2025-03-25
### Fixed
- Expose ui extension to public API

## [107.1.1] - 2025-03-24
### Added
- Crease and sharpness support for subdivide meshes
- Public API rework and added repo checks

### Fixed
- Auto uv library is dynamically linked on windows
- Setting indices on referenced prims fixed for indexing primvars
- Moving ancestral prims is handled correctly in mesh checks
- Modify Instances - Merge Mesh preset update with SDF path expressions usage

### Updated
- Merge, Optimize Skeleton Roots, Deduplicate Geometry  use new mesh restructuring modules
- VirtualMesh updated to support splitting meshes with hole indices and subdivision surface data
- SpatialClustering and VirtualMesh updated to support all features needed for Merge operations

## [107.1.0] - 2025-03-03
### Added
- Split Meshes spatial clustering supports:
  - Keeping materials separate when splitting meshes
  - Merge boundaries like Merge Mesh operation for output mesh hierarchy location
  - Strict attribute mode like Merge Meshes operation
- Split Meshes has Original Prim merge boundary that uses the original prim that meshes have been split as a boundary specifier
- Compute Pivot can now add pivot xformOp to xforms
- Added support for string types for Optimize Primvars

### Fixed
- Mesh normals were not handled correctly with Split Meshes
- Decimate Meshes crash with NaNs and updated UI reporting
- Compute Pivot points weren't being computed in operation
- Improved performance of Compute Pivot operation

### Updated
- Updated default behavior for considering materials in Merge and Split mesh operations, users now specify to keep materials separated if needed

## [107.0.6] - 2025-02-14
### Added
- ABI upgrade

## [107.0.5] - 2025-02-04
### Added
- Optimize Primvars supports sting arrays to be simplified/indexed 
- Recently used JSON configs are viewable in preset menu

### Fixed
- Updated stats handling and reporting, uses JSON payload
- UI update to remove duplicate actions registering with Kit actions

## [107.0.4] - 2025-01-27
### Added
- SDF Prim based filtering, regex removed
- Subdivide Meshes operation

### Updated
- Split Meshes has spatial merge option

## [107.0.2] - 2025-01-07
### Added
- License update for 2025

### Fixed
- Fix mismatch with malloc/delete

## [107.0.1] - 2024-12-17
### Fixed
- Fix mismatch with malloc/delete

## [107.0.0] - 2024-11-25
### Added
- Update Kit SDK version to 107.0.2

## [106.1.10] - 2024-10-29
### Fixed
- Updated CI pipeline configs

## [106.1.5] - 2024-10-25
### Fixed
- Remesher added index primvar support and overall improved performance

## [106.1.4] - 2024-10-24
### Added
- Release bump to debug pipeline

## [106.1.3] - 2024-10-24
### Added
- Remesher operation
- Organize prototypes
- Updated kit verison

### Fixed
- Tessellation updates
- UI updates to allow UI window to be saved in app layout

## [106.1.1] - 2024-08-15
### Added
- Update Kit kernel version to 106.1
- Consider attributes option in fuzzy deduplicate

### Fixed
- Compute OBBs more accurately to improve fuzzy deduplication matching algorithm
- Improve geometry references/instanceable references reporting
- Change up axis of individual xformOps without needing to collapse them to matrices
- Remove Redundant UV primvars opinions on references
- UV generation ignores instance prototypes restrictions
- Stop report output logging to kit/console to reduce data amount
- Update Delete Hidden Prims to use internal method instead of kit method
- Skip time varying meshes to avoid crashes in some SO operations

## [106.0.16] - 2024-07-16
### Added
- Update Kit SDK version to 106.0.1

## [106.0.14] - 2024-07-15
### Added
- Release bump for master branch

## [106.0.13] - 2024-07-15
### Added
- Delete prims update

### Fixed
- Decimate meshes crash fix for invalid USD meshes

## [106.0.12] - 2024-07-01
### Added
- Release bump to debug pipeline

## [106.0.11] - 2024-07-01
### Added
- Decimate meshes accounts for world space scale, uses input mesh normals, and color variation to guide decimation algorithm
- Edit stage metrics operation

### Fixed
- Decimate meshes improved stability in multi-operations and misplaced output parts
- Find coinciding meshes new UI/UX to allow for copying of paths of found coinciding mesh prim generated report UI
- Find hidden meshes fix instance where CUDA was crashing

## [106.0.10] - 2024-05-16
### Added
- Tessellate meshes operation refactor

## [106.0.9] - 2024-05-09
### Added
- Test release to include linux binaries

## [106.0.8] - 2024-05-09
### Added
- Test release to include linux binaries

## [106.0.7] - 2024-05-09
### Added
- Test release to include linux binaries

## [106.0.6] - 2024-04-23
### Added
- Test release to include operation plugin libraries

## [106.0.5] - 2024-04-22
### Added
- Migrated pipeline to Gitlab-ci

## [106.0.4] - 2024-03-15
### Added
- Added new option for Fuzzy Deduplication

## [106.0.3] - 2024-02-26
- Updated version number to match bundle and core releases

## [106.0.1] - 2024-02-23
- Updated kit version to match connectors for security updates

## [106.0.0] - 2024-02-16
- Adopted kit-sdk 106.0

## [105.2.19] - 2024-02-13
- core update release

## [105.2.18] - 2024-02-13
### Added
- Merge Meshes UX report updated catagories and tracking

## [105.2.17] - 2024-02-08
### Added
- Added support to load json config files from nucleus paths

## [105.2.16] - 2024-02-01
### Changed
- Improve tooltip for Find Hidden Meshes
- Updated UI for setting GPU threshold for Decimate Meshes

## [105.2.15] - 2024-01-30
### Added
- New operation: Find Hidden Meshes

## [105.2.14] - 2024-01-16
### Added
- Optimize Primvars
- Triangulate Meshes

## [105.2.13] - 2024-01-03
### Changed
- Updates for new Brep schema

## [105.2.12] - 2023-12-14
### Changed
- Updated version number to match bundle version

## [105.2.8] - 2023-12-13
### Fixed
- Updated default options for AutoUVs

## [105.2.7] - 2023-12-06
### Added
- New AutoUVs menu options

## [105.2.6] - 2023-11-23
### Added
- New operation: Merge Vertices

## [105.2.5] - 2023-11-20
### Added
- Tessellation: Flag to separate parts
- New presets in `Load Preset` button that ship with USD Explorer
- Load presets from nucleus links
### Changed
- Sort Operations alphabetically
- Added scroll bar to account for multiple report tabs
- UI test coverage 100%

## [105.2.4] - 2023-09-19
### Added
- Decimation: Expose parallel CPU and GPU vertex count thresholds
- AutoUV: Equalize texel density + add padding between UV islands
- Spatial merge: add spatial clustering mode
- Unbind materials utility function

## [105.2.2] - 2023-08-25
### Added
- Added support for drag/drop of prims to the Edit Paths window

## [105.2.1] - 2023-08-13
- Exposed "Allow Single Meshes" option to Merge operation

## [105.2.0] - 2023-07-17
- Adopted kit-sdk 105.2

## [105.1.2] - 2023-06-28
### Added
- Operation arguments can define conditional enable state logic.

## [105.1.1] - 2023-05-12
### Added
- New Merge Results GUI for easier debugging of merge operations.

## [105.1.0] - 2023-04-27
### Added
- A Security Warning dialog is shown when loading config files that contain python scripts.
- Prune Leaf Xforms operation can now be filtered by prim path.

## [105.0.7] - 2023-04-03
### Changed
- Preliminary visualization of Operation feedback reports
- Updated omni.scene.optimizer.core version dependency to be un-versioned

## [105.0.6] - 2023-03-23
### Changed
- Updated omni.scene.optimizer.core version dependency to 105.0.6

## [105.0.5] - 2023-03-15
### Changed
- Updated omni.scene.optimizer.core version dependency to 105.0.5
- Explicit stage for commands
- Decouple UI from core

## [105.0.4] - 2023-03-07
### Changed
- Updated omni.scene.optimizer.core version dependency to 105.0.4

## [105.0.3] - 2023-02-28
### Added
- New operation to execute a python script on a Usd Stage
- New operation to Generate Projection UVs on a Usd Stage

## [105.0.2] - 2023-02-09
### Added
- Updated how json files are exported, now have better readability

## [105.0.1] - 2023-01-27
### Added
- Added Split Meshes operation

## [105.0.0] - 2022-12-07
### Added
- Updated scene.optimizer.core version dependency

## [104.1.5] - 2022-11-11
### Change
- UI exposes tolerance value for geometry deduplication.

## [104.1.3] - 2022-11-10
### Changed
- UI improvements for "Process Point Clouds" operation.

## [104.1.2] - 2022-11-03
### Changed
- Command names prefixes changed from "DataAdapter" to "SceneOptimizer"

## [104.1.1] - 2022-10-20
### Added
- Added "Parent Prim" option to "Merge Boundary" argument of "Merge Static Meshes" operation

## [104.1.0] - 2022-10-03
### Changed
- First version of 104.1

## [104.0.10] - 2022-09-28
- Updated arguments for Merge Static Meshes
- Minor UI bug fixes

## [104.0.9] - 2022-09-21
- Updated data.adapter.core version dependency

## [104.0.8] - 2022-09-20
- Updated data.adapter.core version dependency

## [104.0.7] - 2022-09-01
- Added confirmation dialog before clearing processes
- UI look and feel improvements

## [104.0.6] - 2022-08-29
- New icons

## [104.0.5] - 2022-08-29
- Added Center Pivot command
- Update DataAdapter UI per UX design

## [104.0.4] - 2022-07-11
- Added Compute Extents command
- Added Optimize Materials command
- Added Print Stage Stats command
- Added new options to Merge/Deduplicate commands based on core features
- Commands now show a readable display name
- Arguments now show tooltips
- Removed some unncessary commands

## [104.0.3] - 2022-05-11
- Move menu to Window->Utilities.

## [104.0.2] - 2022-03-24
- Specifying which version of *.core we depend on

## [104.0.1] - 2022-02-04
### Changed
- Added default values in UI and the ability to make features mutually exclusive

## [104.0.0] - 2022-01-27
### Changed
- Bump version to 104.

## [103.0.10] - 2022-01-24
- Renamed to omni.data.adapter.ui

## [103.0.9] - 2022-01-24
- Moved UI to standalone extension

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
