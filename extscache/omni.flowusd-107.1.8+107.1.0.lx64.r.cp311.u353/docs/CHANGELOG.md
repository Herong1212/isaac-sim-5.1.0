# Changelog

## [107.1.8] - 2025-06-12
- Adjust golden test image threshold

## [107.1.7] - 2025-05-22
- Add golden test images

## [107.1.6] - 2025-05-19
- Add buffer_to_volume function

## [107.1.5] - 2025-05-08
- Added Python binding to get latest NanoVDB readback

## [107.1.4] - 2025-03-20
- Fix prim id for collision request id

## [107.1.2] - 2025-03-19
- Update physics package

## [107.1.1] - 2025-02-26
- Fixes for GCC 13.3.0 issues

## [107.1.0-abi1] - 2025-02-07
- abi1 compatibility

## [107.1.0] - 2025-01-15
- Kit-sdk update

## [107.0.22] - 2024-12-12
- Fix point cloud precision bug

## [106.5.1] - 2024-11-12
- Multiple import fix

## [106.5.0] - 2024-11-05
- Kit-sdk update

## [106.4.13] - 2024-10-31
- Voxelization automatically aligns to RTX device

## [106.4.12] - 2024-10-30
- Support float NanoVDB output on velocity voxelization

## [106.4.11] - 2024-10-28
- Support to use grid name instead of path for ICgns

## [106.4.10] - 2024-10-25
- Support for ICgns interop data

## [106.4.9] - 2024-10-24
- Bug fix. Interop handles should be duplicated before use

## [106.4.8] - 2024-10-24
- Voxelization setting to disable readback

## [106.4.7] - 2024-10-24
- EmitterNanoVdb interop support.

## [106.4.6] - 2024-10-21
- Sphere emitter trace support.

## [106.4.5] - 2024-10-19
- Align ICgns SDF timestamp to VDB timestamp.

## [106.4.4] - 2024-10-18
- Dense SDF to NanoVDB.

## [106.4.3] - 2024-10-16
- Support for debug volume to run before shadow.

## [106.4.2] - 2024-10-16
- Support for computing speed in NanoVDB emitter.

## [106.4.1] - 2024-10-15
- Velocity Voxelization Vec4 mode.

## [106.4.0] - 2024-10-11
- Kit-sdk update

## [106.3.5] - 2024-10-10
- Voxelization CUDA interop support.

## [106.3.4] - 2024-10-09
- Flow Standalone memory stats.

## [106.3.3] - 2024-10-07
- Support for FP32 precision mode.

## [106.3.2] - 2024-10-07
- Voxelize basic pressure support.

## [106.3.1] - 2024-10-05
- NanoVDB emitter absolute value.

## [106.3.0] - 2024-09-27
- Update kit-sdk

## [107.0.21] - 2024-09-27
- Bugfix. Make voxelized clear before each run.

## [107.0.20] - 2024-09-27
- ICgns callback.

## [107.0.19] - 2024-09-27
- ICgns bugfix.

## [107.0.18] - 2024-09-26
- ICgns better checking.

## [107.0.17] - 2024-09-26
- ICgns interface support.

## [107.0.16] - 2024-09-26
- Texture Emitter SDF support.

## [107.0.15] - 2024-09-19
- Voxelization ring buffer count setting.

## [107.0.14] - 2024-09-17
- Support for AABB on velocity voxelization.

## [107.0.13] - 2024-09-17
- Optimization for persistent voxelization context.

## [107.0.12] - 2024-09-11
- Support for persistent voxelization context.

## [107.0.11] - 2024-09-09
- Bug fix for voxelization python bindings.

## [107.0.10] - 2024-09-06
- Velocity point voxelization to vec3f NanoVDB.

## [107.0.9] - 2024-09-05
- RGB NanoVDB export.

## [107.0.8] - 2024-08-16
- Shader patch to resolve driver crash

## [107.0.7] - 2024-06-19
- PTS import code moved to omni.usd.fileformat.pts

## [107.0.6] - 2024-06-18
- Interpolation lazy update

## [107.0.5] - 2024-06-13
- Bugfix for interpolation

## [107.0.4] - 2024-06-12
- Better interpolation while streaming

## [107.0.3] - 2024-06-05
- Better Point Emitter Interpolation

## [107.0.2-dev] - 2024-05-25
- Point Emitter Interpolation

## [107.0.2] - 2024-05-13
- NanoVDB emitter channel swap support

## [107.0.1] - 2024-05-08
- NanoVDB emitter deduplication

## [107.0.0] - 2024-04-30
- Update kit-sdk

## [106.0.12] - 2024-04-19
- Bugfix. allocateActiveLeaves did not respond to change.

## [106.0.11] - 2024-04-16
- Ray march colormap temperature range.

## [106.0.10] - 2024-03-29
- Include render settings on FlowRender, to improve behavior with references/payloads.

## [106.0.9] - 2024-03-26
- Bugfix. Add missing self shadow parameters.

## [106.0.8] - 2024-03-26
- Bugfix. Flaky VDB export if simulation didn't run every frame.

## [106.0.7] - 2024-03-13
- Update kit-sdk

## [106.0.6] - 2024-03-08
- Fix lingering point/nanovdb emitter allocations after disable.

## [106.0.5] - 2024-03-08
- Fix false positive log warning on VDB size.

## [106.0.4] - 2024-03-07
- Bugfix. No longer load VDBs unless Flow prims present. Fixed grid name selection.

## [106.0.3] - 2024-03-07
- Update kit-sdk

## [106.0.2] - 2024-03-06
- Bugfix. Support legacy raymarch raw mode.

## [106.0.1] - 2024-03-05
- Added more debug volume parameters

## [106.0.0] - 2024-02-16
- Update kit-sdk

## [105.2.42] - 2024-02-08
- Add allLayers broadcast to Flow box emitter.

## [105.2.41] - 2024-02-06
- Physics collision now supports multiple active Flow layers.

## [105.2.40] - 2024-02-01
- Native nvflow_rtx builds.

## [105.2.39] - 2024-02-01
- Move NvFlow .so to hidden symbol visibility.

## [105.2.38] - 2024-01-30
- RayMarch bugfix.

## [105.2.37] - 2023-12-12
- Kit SDK update

## [105.2.36] - 2023-12-05
- Crash bugfix for invalid GridParams snapshot after resetParams.

## [105.2.35] - 2023-12-04
- Kit SDK update

## [105.2.34] - 2023-11-16
- Native FlowPointCloud, no longer writes USD.

## [105.2.33] - 2023-11-09
- Point voxelization VDB transform support.

## [105.2.32] - 2023-11-01
- Bug fixes for suppress clearing while VDB loads are pending.

## [105.2.31] - 2023-11-01
- Suppress clearing while VDB loads are pending.

## [105.2.30] - 2023-10-31
- Bug fix for missing auto level select on RGBA8 VDBs.

## [105.2.29] - 2023-10-30
- NvFlowContext resource format aliasing support.

## [105.2.28] - 2023-10-24
- NanoVDB export use unknown grid class for non-float formats.

## [105.2.27] - 2023-10-20
- Volume RGBA8 field. Omni client crash fixes.

## [105.2.26] - 2023-10-17
- NanoVDB emitter allocation uses minSmoke and maxSmoke to optimize.

## [105.2.25] - 2023-10-17
- NanoVDB emitter allocation bounds fix.

## [105.2.24] - 2023-10-17
- NanoVDB export metadata fixes.

## [105.2.23] - 2023-10-17
- Increase point cloud color precision. Reduce NanoVDB emitter VRAM usage.

## [105.2.22] - 2023-10-17
- RGBA8 NanoVDB emitter bug fixes.

## [105.2.21] - 2023-10-17
- RGBA8 and Vec4 NanoVDB export and point voxelization.

## [105.2.20] - 2023-10-11
- Reduce asset resolver overhead when on session layer.

## [105.2.19] - 2023-10-09
- Fixed missing VDB asset release.

## [105.2.18] - 2023-10-05
- Fix VDB loading with timeSampled asset path.

## [105.2.17] - 2023-10-03
- Improved UsdVol VDB loading performance.

## [105.2.16] - 2023-09-19
- Avoid redundant streaming clears.

## [105.2.15] - 2023-09-12
- Bug fix for streaming clear when points and volumes used together.

## [105.2.14] - 2023-09-12
- Initial UsdVol support.

## [105.2.13] - 2023-08-25
- Bug fix for bad Flow block bounding boxes

## [105.2.12] - 2023-08-23
- Creating a Flow preset won't unselect previous selection

## [105.2.11] - 2023-08-22
- Bug fix for lingering Flow blocks without simulation parameters.

## [105.2.10] - 2023-08-14
- Add session layer option to preset commands

## [105.2.9] - 2023-08-14
- Update Kit SDK

## [105.2.8] - 2023-08-10
- Set FlowPointCloud default couple rate to 10000.

## [105.2.7] - 2023-08-10
- Point emitter, reduce artifacts when restreaming same points.

## [105.2.6] - 2023-08-10
- Flow ray march rawMode now isosurface.

## [105.2.5] - 2023-08-10
- Expose CoupleRate on FlowPointCloud. Lower default value.

## [105.2.4] - 2023-08-09
- Improved Flow ray march dither.

## [105.2.3] - 2023-08-08
- Point emitter smoother level transitions.

## [105.2.2] - 2023-08-07
- Point emitter now keeps old blocks active during streaming to smooth transition.

## [105.2.1] - 2023-07-31
- Add widthScale to FlowPointCloud

## [105.2.0] - 2023-07-27
- Fix presets command

## [105.1.43] - 2023-07-25
- Better align levelCount defaults.

## [105.1.42] - 2023-07-25
- Bug fix for point emitter levelCount mixed with autoCellSize.

## [105.1.41] - 2023-07-24
- Adding new level parameter.

## [105.1.40] - 2023-07-24
- Rename LodLayerCount to LevelCount.

## [105.1.39] - 2023-07-22
- Bug fix for point emitter lodLayerCount xform scaling.

## [105.1.38] - 2023-07-22
- Flow LOD support.

## [105.1.37] - 2023-07-22
- Fix NanoVDB emitter coordinate inconsistency.
- Point cloud preset on selected prim fix.

## [105.1.36] - 2023-07-14
- Improved Flow native rendering sorting.

## [105.1.35] - 2023-07-12
- Throttle point streaming compute dispatches.

## [105.1.34] - 2023-07-12
- Point Emitter refactor to remove flicker.

## [105.1.33] - 2023-06-06
- Add FlowVoxelizePointsAndSync Kit command.

## [105.1.32] - 2023-05-22
- Fix leak in V2 USD prim tracking

## [105.1.31] - 2023-05-22
- Free stage reference sooner. Point voxelization.

## [105.1.30] - 2023-05-16
- Timesampled Xform fix

## [105.1.29] - 2023-05-03
- Global preset copy fix

## [105.1.28] - 2023-05-02
- Added support for emitterPoint to point to N UsdGeomPoints by relationship

## [105.1.27] - 2023-05-02
- Fixed dependencies

## [105.1.26] - 2023-04-18
- Added NanoVDB readback OGN node

## [105.1.25] - 2023-04-12
- Separated UI code into omni.flowusd.ui

## [105.1.24] - 2023-04-04
- Fix save dialog appearing in tests

## [105.1.23] - 2023-03-24
- Added Point cloud streaming preset

## [105.1.22] - 2023-03-22
- Update Kit SDK

## [105.1.21] - 2023-03-21
- Update Kit SDK

## [105.1.20] - 2023-03-06
- Fix layer id of referenced presets for the stage window

## [105.1.19] - 2023-03-01
- Update Kit SDK

## [105.1.18] - 2023-02-17
- Fix layer id of referenced presets

## [105.1.17] - 2023-01-25
- Kit SDK update, fixes

## [105.1.16] - 2023-01-04
- Bumped Kit SDK version

## [105.1.15] - 2022-12-01

- Fixed ReadUsdAttributeRange prim changed callback

## [105.1.14] - 2022-11-28

- Fixed drag and drop of Flow presets

## [105.1.13] - 2022-11-28

- New setting /exts/omni.flowusd/vdb_cache_size default is 8GB

## [105.1.12] - 2022-11-24

- Scalar ramp widget shows range on y axis

## [105.1.11] - 2022-11-14

- Kit SDK update

## [105.1.10] - 2022-11-06

- Added ReadUsdAttributeRange OG node

## [105.1.8] - 2022-11-02

- Point cloud preset defaults to bunny if no point is selected
- FlowPointCloud property sheet UX
- Non point cloud global preset also uses increased layer ID

## [105.1.7] - 2022-10-27

- Property sheets won't reorder schema attributes

## [105.1.6] - 2022-10-17

- Deprecated `onclick_fn` changed to `onclick_action` in Flow Create menu

## [105.1.5] - 2022-10-16

- Monitor in Viewport reverted

## [105.1.4] - 2022-10-14

### Changes
 - Codeless schemas

## [105.1.3] - 2022-10-11

### Changes
 - Point cloud preset
 - Monitor in viewport fix

## [105.1.2] - 2022-10-04

### Changes
 - OG Flow stats nodes

## [105.1.1] - 2022-09-26

### Changes
 - Monitor window moved to Viewport

## [0.3.10] - 2022-09-11

### Changes
 - NanoVDB emitter coordinate bugfix. Remove need for translate when replaying cached VDBs.
 - Flow OG nodes removed.

## [0.3.9] - 2022-08-31

### Changes
 - Added tests

## [0.3.8] - 2022-08-30

### Changes
 - Improved robustness with USD Layers. Better handling of missing Flow child prims.

## [0.3.7] - 2022-08-23

### Changes
 - Flow NanoVDB emitter is registered in the omni.vdb_timesamples_editor to have attributes with time sampled assets displayed in the Time Samples section in the Property window

## [0.3.6] - 2022-08-11

### Changes
 - Release inactive VDBs when system memory usage is high

## [0.3.5] - 2022-08-09

### Changes
 - Drop helper update with new viewport
 - OGN deprecated function changed

## [0.3.4] - 2022-07-27

### Changes
 - Multithreaded FlowUsd update


## [0.3.3] - 2022-06-28

### Changes
 - Added `FlowCreatePresets` command


## [0.3.2] - 2022-05-30

### Changes
 - Removed point cloud import from Flow menus
 - Setting the pointcloud default color in RGB


## [0.3.1] - 2022-05-25

### Changes
 - Presets are adjusted in the stage with Z up axis
 - Added pointcloud preset command
 - Function for setting the pointcloud default color


## [0.3.0] - 2022-05-10

### Changes
 - Include the Flow shared libraries


## [0.2.0] - 2022-05-10

### Changes
 - All changes ported over from building within KIT
 - This is the last version that ships without the Flow share libraries
 - This is the first version that is published through the extension registry


## [0.1.0] - 2020-12-08

### Known Issues
- System memory usage can increase with low render frame rates and async UI/rendering.
- Lighting interaction between Flow and RTX is not yet complete.
