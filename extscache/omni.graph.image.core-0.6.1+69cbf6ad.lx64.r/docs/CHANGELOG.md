(changelog_omni_graph_image_core)=

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2024-12-16
### Added
- Remove explicit dependencies.

## [0.6.0] - 2024-12-10
### Added
- Add support for Fabric Scene Delegate in pre and post render graphs.

## [0.5.0] - 2024-08-29
### Fixed
- Fixed dirty Usd stage after the creation of a post render graph.

## [0.4.5] - 2024-05-22
### Fixed
- Ensure the RenderGraph is cached correctly for each Render Thread, in the pre and post render execution graph.

## [0.4.4] - 2024-03-25
### Fixed
- Fixed crash when setting the graph state variables after a fabric snapshot is applied on the farbric stage.

## [0.4.3] - 2024-03-07
### Fixed
- Fixed crash when building graphs where nodes have attributes with unknown types.

## [0.4.2] - 2024-02-28
### Changed
- Move the initialization of the state variables to a pre process task.

## [0.4.1] - 2024-02-26
### Changed
- Initialize the state variables during the build stage, to avoid spike at runtime and deadlock.

## [0.4.0] - 2024-02-14
### Added
- The CudaInteropExecutor now executes CUDA interop nodes both on the render thread and as cuda commands.
- The execution framework sets graph variables with the cudaStream_t and other execution state necessary for post render graph nodes
### Changed
- Changed the ComputeParamsBuilder methods to return a reference, to allow multiple separate add* calls on the same instance.

## [0.3.2] - 2024-01-02
### Changed
- Updated the description of the extension in the readme file.

## [0.3.1] - 2023-12-13
### Fixed
- Skip running the pre / post render graph when the state is invalid.

## [0.3.0] - 2023-11-22
### Added
- Added support for compound nodes in pre and post render graphs.

## [0.2.5] - 2023-11-16
### Added
- Added private interfaces for execution nodes CudaInteropEntryNodeDef and RenderProductInteropEntryNodeDef
### Fixed
- Fixed bad cast to check for CudaInteropEntryNodeDef nodes in the CudaInteropExecutor

## [0.2.4] - 2023-10-18
### Changed
- Using the added 'canEvaluate' ABI from core

## [0.2.3] - 2023-10-10
### Changed
- The RenderGraphState is now stored in thread local storage to avoid data races in MGPU setups
- Assert when attempting to update the PreRenderGraphDef in parallel from separate threads.

## [0.2.2] - 2023-08-31
### Fixed
- Attach execution definition to the pre-render and post-render stage update root nodes.

## [0.2.1] - 2023-08-25
### Fixed
- Ensure the runtime data is initialized before executing post render graphs.

## [0.2.0] - 2023-08-17
### Added
- Introduced the IPreRenderGraph and IPostRenderGraph interfaces.
- Implemented the execution graph for pre and post render graphs.

## [0.1.1] - 2023-07-14
### Changed
- Improved the documentation of ComputeParams and ComputeParamsBuilder types.

## [0.1.0] - 2023-05-12
### Initial Version
- Initial version introduces the ComputeParamsBuilder and ComputeParams types.
