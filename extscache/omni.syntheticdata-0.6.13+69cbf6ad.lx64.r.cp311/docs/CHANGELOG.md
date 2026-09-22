(changelog_omni_syntheticdata)=

# Changelog

This document records all notable changes to the **omni.syntheticdata** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [0.6.13] - 2025-05-20
### Changed
- Disable per-tile 2D bounding box annotations for multi-tiled rendering (introduced in 0.6.12)

### Fixed
- Fix incorrect 2D bounding box output when using tiled rendering

## [0.6.12] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [0.6.11] - 2025-03-05
### Fixed
- Correct 2D bounding box output when using render tiles to output multiple cameras in one viewport (OMPE-17395 OMPE-17396)
### Removed
- Removed deprecated semanticId fields from renderer sensor types for bounding boxes and occlusion values

## [0.6.10] - 2024-09-10
### Fixed
- Fix security issues (OMPE-18747).

## [0.6.9] - 2024-07-17
### Fix
- Prep for Numpy upgrade.

## [0.6.8] - 2024-03-27
### Fixed
- Removed assumption that OmniGraph always runs on GPU 0.

## [0.6.7] - 2024-02-23
### Added
- Added test to ensure the SDG graphs continue to work when USD loading is disabled gloabally in OmniGraph

## [0.6.6] - 2024-01-11
### Fix
- Visualizer window update callback.
- Instance mapping number of semantics update.

## [0.6.5] - 2024-01-10
### Fix
- OgnSdPostRenderVarTextureToBuffer graphic copy fallback.

## [0.6.4] - 2024-01-09
### Added
- Unit test to verify that SyntheticData-generated OmniGraphs respond to USD authoring changes.
### Changed
- All SyntheticData-related OmniGraphs (e.g., post-process graphs, pre- and post-render graphs, etc.)
  are treated as "global graphs" so that USD change processing can be performed successfully by the
  OmniGraph core.

## [0.6.3] - 2023-12-05
### Changed
- Change DistanceToCamera values for pinhole cameras to not be dependent on near clipping range

## [0.6.2] - 2023-11-17
### Changed
- Changed deprecated functions to their new version

## [0.6.1] - 2023-09-20
### Removed
- Unnecessary evaluate call in test which causes irrelevant error message

## [0.6.0] - 2023-09-18
### Added
- Added test for getting the value of the PtrToPtrKind in GPU data

## [0.5.2] - 2023-09-07
### Fixed
- Deprecated python function bindings

## [0.5.1] - 2023-09-05
### Fixed
- Automatic deactivation of intergraph connected nodes

## [0.5.0] - 2023-08-19
### Removed
- Tests that rely on omni.graph.action_nodes - moved to the OmniGraph repo
- Dependency on the downstream extension omni.graph.ui

## [0.4.14] - 2023-08-14
### Added
- Post-render nodes for dispatching renderVar IO works.

## [0.4.13] - 2023-08-11
### Fixed
- Replace inter-graph node connections by internal node attributes of downstream node_handle dependency list
### Added
- Setting to disable the backing of the graphs by USD

## [0.4.12] - 2023-08-08
### Added
- Custom Semantic filter node (SdSemanticLabelsMap)

## [0.4.11] - 2023-08-02
### Fixed
- 3D bounding boxes realtime preview regression

## [0.4.10] - 2023-07-30
### Added
- Added dependency on new extension containing GPU interop nodes

## [0.4.9] - 2023-07-12
### Added
- Instance-mapping Fabric update timestamp.
- Texture renderVar buffer stride information.

## [0.4.8] - 2023-07-11
### Fixed
- Realtime preview flickering in asynchronous rendering.

## [0.4.7] - 2023-07-10
### Added
- Default activation of visualization node templates

## [0.4.6] - 2023-07-03
### Fixed
- OgnPostRenderVarToHost node : memory leak when creating texture host renderVar data.
- OgnPostInstanceMapping node : memory leak when fetching instance mapping transforms from Fabric.
- OgnSdStageInstanceMapping : double Fabric lock when fetching instance mapping transforms from Fabric.

## [0.4.5] - 2023-06-28
### Fixed
- OgnSdPostSemantic3dBoundingBoxCameraProjection: check input semanticWorldTransformSDCudaPtr before launching CUDA task to avoid potential crash.
### Changed
- Restored implementation of OgnSdPostSemantic3dBoundingBoxCameraProjection, OgnSdPostSemantic3dBoundingBoxFilter and OgnSdPostSemanticBoundingBox.

## [0.4.4] - 2023-06-27
### Fixed
- Fixed up some documentation errors
### Added
- Documentation page for accessing the OmniGraph node definitions

## [0.4.3] - 2023-06-27
### Changed
- Set up the extension to load python nodes and tests in parallel

## [0.4.2] - 2023-06-24
### Fixed
- Crashes due to instance mapping unprotected concurrent read/write.
- Missing empty buffer and host renderVars.
### Added
- Instance mapping local to world transform interpolation.
### Removed
- Omnigraph computeParamsBuilder support

## [0.4.1] - 2023-06-20
### Fixed
- Crash when enabling 3d bounding boxes sensors.

## [0.4.0] - 2023-05-26
### Changed
- Refactored the nodes which schedule CUDA tasks to use a common API.

## [0.3.0] - 2023-05-18
- Deprecate obsolete semantic ID management through renderer (see below)
- Deprecate SemanticSegmentationSD sensor from renderer
- Remove SemanticIdSegmentation from visualizer
- Deprecate omni.syntheticdata functions to retrieve semantic from renderer (get_semantic_segmentation_...)
- Deprecate semantic ID filtering through renderer

## [0.2.9] - 2022-12-28
### Fixed
- Clear visualizer selection menu on new stage opened (OM-72422)

## [0.2.8] - 2022-12-21
### Changed
- Refactored CUDA build to consolidate build functions and remove unnecessary rebuilds

## [0.2.7] - 2022-12-14
### Changed
- Re-enabled pipeline tests.

## [0.2.6] - 2022-11-26
### Changed
- Enable TestSemanticSeg tests.

## [0.2.5] - 2022-10-26
### Changed
- Flagged all "cube" tests in TestSemanticSeg as unreliable.

## [0.2.4] - 2022-09-22
### Changed
- Update icon to match Viewport 2.0 style

## [0.2.3] - 2021-08-16
### Fixed
- Call dict.discard instead of non extistant dict.remove.

## [0.2.2] - 2021-05-18
### Changed
- Add dependency on omni.kit.viewport.utility

## [0.2.1] - 2022-03-23
### Changed
- Support Legacy and Modern Viewport

## [0.1.8] - 2021-12-10
### Changed
- Deprecated Depth and DepthLinear sensors and added DistanceToImagePlane and DistanceToCamera
### Added
- Cross Correspondence Sensor

## [0.1.7] - 2021-10-16
### Changed
- Move synthetic data sensors to AOV outputs that can be specified in USD and used in OmniGraph nodes

## [0.1.6] - 2021-06-18
### Fixed
- Instance Segmentation is now always returned as uint32
- Fixed parsed segmentation mode
- Fixed Pinhole projection which incorrectly used the camera's local transform instead of its world transform
### Added
- Linear depth sensor mode

## [0.1.5] - 2021-03-11
### Added
- Motion Vector visualization and helper function

### Changed
- BBox3D corners axis order to be Y-Up for consistency with USD API
- All parsed data return uniqueId field, along with list of instanceIds
- `instanceId` field removed from parsed output to avoid confusion with renderer instanceId
- Add `get_instance` function to extension
- Improve returned data of `get_occlusion_quadrant` for consistency with other sensors

### Fixed
- Fix BBox3D parsed mode when dealing with nested transforms
- Fix BBox3D camera_frame mode, previously returned incorrect values
- Use seeded random generator for shuffling colours during visualization

## [0.1.4] - 2021-02-10
### Changed
- Moved to internal extension
- Minor bug fixes
## [0.1.3] - 2021-02-05
### Added
- Python 3.7 support

### Changed
- Bug fixes
## [0.1.2] - 2021-01-28
### Added
- Occlusion Quadrant Sensor
- Metadata Sensor

### Changed
- Metadata (SemanticSchemas of Type != 'class') added to sensor outputs
- UI changed to better suit multi-viewport scenarios
- Misc. sensor fixes and improvements
## [0.1.1] - 2021-01-25
- Linux support

## [0.1.0] - 2021-01-18
- Initial version
