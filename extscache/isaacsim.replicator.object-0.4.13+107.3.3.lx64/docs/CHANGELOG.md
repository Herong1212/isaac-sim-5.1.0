# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.4.13] - 2025-10-01
- writer trigger bugfix; remove smallest version 

## [0.4.12] - 2025-07-30
- Asset path update

## [0.4.11] - 2025-07-10
- correction to data validation

## [0.4.10] - 2025-07-09
- path fix 5.0

## [0.4.9] - 2025-06-25
- Use absolute path as writer output path

## [0.4.8] - 2025-06-12
- fix test settings in extension.toml

## [0.4.7] - 2025-06-05
- Menu items relocated to Tools>Action and Event Data Generation

## [0.4.6] - 2025-05-29
- Internal code change

## [0.4.5] - 2025-05-28
- Added a couple of IRO config files as samples with IRC writers

## [0.4.4] - 2025-05-23
- distribution visualizer fix
- physic fix 

## [0.4.3] - 2025-05-19
- Ensure consistent extension name and title

## [0.4.2] - 2025-05-20
- Camera focus in embedded mode, embedded environment setup, toggle visibility fix, visualizer prim validation

## [0.4.1] - 2025-05-13
- Event 2.0, xformOp warnings, material binding warnings, ui hot reload error, shader create input error, distribution visualizer visual and xformOps

## [0.4.0] - 2025-04-17
- UI enhancements and refactoring

## [0.3.26] - 2025-04-07
- Embedded interface.
- Randomized material with procedural layers.
- Scene editing UI and UI panel adjustments.
- Legacy code cleanup.
- Upgrades to Kit 107.2.

## [0.3.25] - 2025-03-01
- Republished due to repo URL change

## [0.3.24] - 2025-02-24
- Scene_DEV attribute updates

## [0.3.23] - 2025-02-07
- Version bump bug fix

## [0.3.22] - 2025-01-29
- Added patch for empty segmentation or no segmentation required in IRO
- Give early warning about mongodb_uri missing

## [0.3.21] - 2025-01-10
- bump up version

## [0.3.21] - 2025-01-09
- Minor fixes for QA https://nvbugspro.nvidia.com/bug/5043519 https://nvbugspro.nvidia.com/bug/5006513 https://nvbugspro.nvidia.com/bug/5043593

## [0.3.20] - 2024-12-19
- dynamic scale bin pack
- Tongwei's CI/CD windows fix

## [0.3.19] - 2024-12-18
- comments and simulation/rendering time options

## [0.3.18] - 2024-12-07
- UI dev code
- Bug fix for image processing output error
- Bug fix for bottle physics description
- Bug fix for multi-camera
- Bug fix for file name composition with number
- Added 2 more special macros for camera name and index

## [0.3.17] - 2024-11-21
- Reorganized writer for easier class inheritance
- Added segmentation data filter for caption case

## [0.3.16] - 2024-11-20
- Accommodate Isaacsim.replicator.caption writer

## [0.3.15] - 2024-11-01
- Rename to isaacsim.replicator.object

## [0.3.14] - 2024-10-31
- asset loading checks
- removed unneeded async waits
- parallelized i/o
- shows simulation process in main perspective camera
- moved capture to writer.write, and fix relevant annotator calls
- simple profiling wrappers

## [0.3.13] - 2024-10-18
- remove redundant dependencies

## [0.3.12] - 2024-10-14
- Integrating florance label generation into ORO

## [0.3.11] - 2024-10-10
- Integrated omni.replicator.caption to the extension. Now scene graph map is able to be generated in the runtime with other ORO outputs.
- Added switches of caption related function: `caption` and `caption_rgb` at `output_switches`
- Reorganized 2d & 3d bbox filtering logics. When `caption` switch is on, the annotator will not remove labels on non-oro prims.

## [0.3.10] - 2024-10-01
- sphere light update; fix seed when choosing from set sequentially; py3dbp license header

## [0.3.9] - 2024-09-09
- adding florance like captioning support calling isaac.replicator.caption (experimental for now)

## [0.3.8] - 2024-09-03
- misc bug fix https://nvbugspro.nvidia.com/bug/4844920

## [0.3.7] - 2024-08-30
- path fix

## [0.3.6] - 2024-08-27
- tracy profiling wrappers
- nucleus/s3 URL switch
- segmentation mask filter based on occlusion
- point sampling from mesh
- UI drop box
- randomized order bin packing

## [0.3.5] - 2024-07-23
- record physics resolved transform, process multiple files; regex windows bug; bins of bins examples

## [0.3.4] - 2024-07-16
- version issue

## [0.3.3] - 2024-07-11
- https://nvbugspro.nvidia.com/bug/4737470

## [0.3.2] - 2024-06-28
- recursive randomized bin pack; small bug fixes; descriptions clean up

## [0.3.1] - 2024-06-26
- testing unittest runs + wp. fix from S.

## [0.3.0] - 2024-06-13
- resolution symbols dev and miscellaneous features

## [0.2.16] - 2024-05-15
- QA bugs, segmentation etc.

## [0.2.15] - 2024-05-10
- Remove cv2 dependency; add normal map

## [0.2.14] - 2024-04-15
- Tidy up for Isaac May release

## [0.2.13] - 2024-03-26
- Testing isaac-sim.sh as the main driver code

## [0.2.12] - 2024-03-20
- Physics bug fix and trimesh

## [0.2.11] - 2024-03-08
- Adding /deep/debug parameter to send crash reports also adding this to jenkins runs

## [0.2.10] - 2024-03-01
- relax restrictions on eval()

## [0.2.9] - 2024-02-29
- fix macro parsing safety issue

## [0.2.8] - 2024-02-27
- Add new texture operations to the Texture Mutable Attribute

## [0.2.7] - 2024-02-24
- Bump up version to avoid conflict.

## [0.2.6] - 2024-02-23
- Bin pack harmonizer bug fixes, physics options, etc. (details are in commit messages)

## [0.2.5] - 2024-02-12
- Updating coco output to address the images that do not have annotations.

## [0.2.4] - 2024-02-07
- Jenkins updates for unittests

## [0.2.3] - 2024-01-29
- Occlusion threshold; depth annotator; mutable attribute texture, update on the fly

## [0.2.2] - 2024-01-23
- Shader attributes randomization

## [0.2.1] - 2024-01-16
- Precision fix

## [0.2.0] - 2024-01-08
- Bumping up the version number to 0.2.0. Any 0.2.x versions are for the upcoming release.

## [0.1.12] - 2024-01-03
- Bin pack harmonizer, flexible constant size

## [0.1.11] - 2023-12-13
- Change inf to 0.

## [0.1.10] - 2023-12-13
- Change depth map to output npy, allowing inf.

## [0.1.9] - 2023-12-12
- Change depth map range, change to camera distance.

## [0.1.8] - 2023-12-12
- Add depth map.

## [0.1.7] - 2023-12-11
- MR to isaac-sim develop.

## [0.1.6] - 2023-12-07
- Fix semantics conflict bug

## [0.1.5] - 2023-12-06
- Turn off grids in IsaacSim

## [0.1.4] - 2023-11-30
- UI; description files; usd_path harmonizer bug. Test code update in registry.

## [0.1.2] - 2023-10-11
### Changed
- Implemented harmonizer.

## [0.1.1] - 2023-10-09
### Changed
- Changed name to omni.replicator.object.

## [0.1.0] - 2023-02-27
- Initial version of the omni.replicator.retail extension.
