# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.7.5] - 2025-08-08
### Fixed
- OMPE-45202: Fix test failures while temporary directory used.

## [1.7.4] - 2025-05-20
### Fixed
- OMPE-45202: Use temporary directory to fix test failures in OVC2

## [1.7.3] - 2025-04-28
### Changed
- Updated documentation with AI agent.

## [1.7.2] - 2025-04-28
### Changed
- Updated documentation with AI agent.

## [1.7.1] - 2025-04-04
### Removed
- Legacy Viewport conditionals

## [1.7.0] - 2025-03-23
### Added
- OMPE-35647: Add new capture render preset for real time 2.0

## [1.6.0] - 2025-01-016
### Fixed
- Increase file name index for render product capture
### Changed
- Limit CaptureOption.get_full_path for video only
- Re-enable some tests
### Added
- Add CaptureExtension.done to verify capture is done
- Add CaptureExtension.get_outputs to Get output file names when capture is done

## [1.5.5] - 2025-01-07
### Fixed
- OMPE-32078: Read fill viewport setting from defaults if not found in persistent

## [1.5.4] - 2024-12-19
### Fixed
- Running capture (and tests) in headless mode

## [1.5.3] - 2024-09-06
### Changed
- Add an additional wait for render-product capture to execute the post-processing graph

## [1.5.2] - 2024-09-06
### Changed
- Bump the version to avoid extensions accidentally use the latest version in kit-tools (1.5.1)

## [1.5.1] - 2024-04-04
### Changed
- Use more standard wait_n_updates method rather than custom version

## [1.5.0] - 2024-01-29
### Added
- Add new capture option to set the time to wait for renderer to resolve, e.g. temporal effects, before capturing the image in RT capture
- Add new capture option to set the time limit of capturing a frame so that batch jobs can quit early and get retried if frame time reaches the limit

## [1.4.12] - 2023-12-14
### Changed
- Make sure to finish the capture process at the end of testcases starting a capture
- Remove the viewport error message from exclude list and the use of gc from the tests

## [1.4.11] - 2023-12-10
### Added
- Add checks to capture options to make sure it's valid to actually start the capture
- Make the CaptureExtension.start API to return a True/False value to tell if the capture start successfully or not

## [1.4.10] - 2023-11-30
### Fixed
- Fix the issue that when samples per pixel number is very small, e.g. 1, it's possilbe that capture can't proceed with default settle latency frames setting

## [1.4.9] - 2023-11-01
### Added
- Add more testcases to improve test coverage

## [1.4.8] - 2023-10-12
### Fixed
- Turn on the premultiply color by alpha flag to improve alpha output quality for .exr captures

## [1.4.7] - 2023-09-28
### Fixed
- Fix the render product capture failure introduced by using sequencer camera

## [1.4.6] - 2023-08-22
### Fixed
- Fix the issue that progress is not estimated correctly for certain cases

## [1.4.5] - 2023-08-21
### Fixed
- Fixed the issue that motion blur doesn't work in PT
- Fixed the issue that estimated time of capture every nth frame may show negative numbers for the last a few frames that we don't need

## [1.4.4] - 2023-08-18
### Fixed
- Fixed the issue that total sample per pixel number during capture is capped by the setting in render settings
- Improve the performance of the capture of every nth frames

## [1.4.3] - 2023-08-17
### Added
- Added dependency to omni.graph.image.core.

## [1.4.2] - 2023-08-08
### Removed
- Obsolete OmniGraph references

## [1.4.1] - 2023-07-31
### Changed
- Use new Viewport action API to batch toggling and record/restore state more efficiently.

## [1.4.0] - 2023-07-30
### Added
- Added dependency on new extension containing GPU interop nodes

## [1.3.7] - 2023-07-25
### Fixed
- Fixed the sequencer cameras don't play issue by forcing the use sequencer camera setting to be true during capture

## [1.3.6] - 2023-07-20
### Fixed
- Fixed the camera hiding not working issue for Kit 105

## [1.3.5] - 2023-07-13
### Changed
- Set omni.videoencoding to be an optional dependency.

## [1.3.4] - 2023-05-25
### Added
- Add a new option to allow capture with different FPS for animation
### Changed
- Don't touch the viewport displayOptions during capture
- Make sure timeline's minibar to be hidden during capture
- Clean unnecessary Iray capture setting for time sync-up

## [1.3.3] - 2023-05-18
### Fixed
- Fixed the error given out when capturing a single image in application level

## [1.3.2] - 2023-05-03
### Added
- Add application level capture support so that we can capture ui.scene elements

## [1.3.1] - 2023-04-24
### Added
- Add encoding settings to control MP4 movie quality

## [1.3.0] - 2023-04-03
### Changed
- Move the extension into Kit SDK

## [1.2.2] - 2023-04-03
### Fixed
- Set animation timeline play start and end frame range for capture to fix the issue that when capture's start frame is
  out of the timeline's start and end frame range, the first captured frame will be the start frame of the animation

## [1.2.1] - 2023-03-22
### Fixed
- Fixed the iray capture's samples per pixel could be capped at 512 issue

## [1.2.0] - 2023-03-20
### Added
- Added support to Path Tracing adaptive sampling to save performance in Path Tracing capture when the samples per pixel number is big

## [1.1.24] - 2023-01-04
### Changed
- Keep tuning the tests to try to fix the GPU related crash in 105

## [1.1.23] - 2022-12-21
### Changed
- Tuned testcases to try to make them more stable

## [1.1.22] - 2022-12-16
### Changed
- Reduce GPU memory consumption of render product tests
- reenable `test_capture_1_default_rp` on ETM

## [1.1.21] - 2022-12-14
### Changed
- Disable `test_capture_1_default_rp` on ETM - need GPU with 16GB RAM

## [1.1.20] - 2022-12-12
### Fixed
- Fixed the Iray capture failure happening when Iray renderer plugin hasn't been loaded yet.

## [1.1.19] - 2022-12-07
### Fixed
- Fixed the XR Output Alpha in composited images is not correct issue
- Set Fill Viewport to false during capture so that it can capture in the resolution specified in movie capture UI

## [1.1.18] - 2022-10-27
### Changed
- Updated the progress report when there are existing frames to skip

## [1.1.17] - 2022-09-28
### Changed
- Will not force multithread rendering to be disabled as the original bug has been fixed.

## [1.1.16] - 2022-09-27
### Changed
- When captureing with render product, it no longer sets OmniGraph stage pipeline setting useLegacySimulationPipeline to True during capture.

## [1.1.15] - 2022-09-26
### Added
- Added support to capture the viewport when it's not visible. Please be noted that this feature works for viewport next only and doesn't work for legacy viewport.

## [1.1.14] - 2022-08-18
### Added
- Added support to exr compression formats

## [1.1.13] - 2022-07-20
### Added
- Set more rendering flags during capture
### Changed
- Make capture options's fps the MP4 encoding fps only now, that said, the stage's timeline's time codes per second will not be touched during movie capture. This decouple of fps definition has been wanted for a while and now it gets higher priority as it can also avoid a OmniGraph issue, which will make the capture take long time to start and even crash.

## [1.1.12] - 2022-07-06
### Changed
- Improve test coverage by adding more tests.

## [1.1.11] - 2022-06-15
### Changed
- Get active camera from omni.kit.viewport.utility

## [1.1.10] - 2022-05-27
### Changed
- Changed IRay to take the same way to calculate the number of default settle latency frames to Path Trace.

## [1.1.9] - 2022-05-23
### Added
- Added motion blur support for Iray capture

## [1.1.8] - 2022-05-23
### Added
- Added settle latency progress report into the progress window for if users set settle latency
### Fixed
- Fixed the flashing blended image during capture issue for single frame capture

## [1.1.7] - 2022-05-23
### Added
- Added set of synchronous render flag for Iray capture
### Changed
- Let Iray capture have a default respect settle latency value to produce right capture results in case Iray iterations number is too small

## [1.1.6] - 2022-05-22
### Changed
- Refined the settle latency setting for potential performance issue and iray capture problem

## [1.1.5] - 2022-05-11
### Added
- Default to a minimum 5-frame delay when capturing a sequence.
- Added /app/captureSequence/waitFrames setting to explicitly wait N number of frames for sequence capture.

## [1.1.4] - 2022-04-26
### Added
- Add frame count info into the default progress window for sequence capture

## [1.1.3] - 2022-03-30
### Changed
- Update repo_build and repo_licensing

## [1.1.2] - 2022-03-21
### Fixed
- Fix a crash when capturing in ream-time mode in .exr with HDR on

## [1.1.1] - 2022-03-17
### Changed
- Disable async texture streaming during capturing

## [1.1.0] - 2022-03-12
### Fixed
- Fixed the issue the temp render product is not deleted successfully issue

## [1.0.9] - 2022-02-28
### Changed
- Change render product capture to use the given camera and resolution capture options instead of the values in render product

## [1.0.8] - 2022-02-15
### Changed
- Change render product capture behavior to also capture the primary scene image

## [1.0.7] - 2022-02-10
### Fixed
- Fix the issue that when the target folder is read-only, capture still continues but saves no images. Now it will early quit and send a warning message to console.

## [1.0.6] - 2022-02-09
### Fixed
- Fix capture of PhysX simulation can't do full capture range simulation if timeline window's end time setting is earlier than the end time setting in movie capture UI

## [1.0.5] - 2022-02-03
### Fixed
- Fix Reshade cropping issue

## [1.0.4] - 2022-01-29
### Added
- Add checks to required omnigraph extensions and Kit SDK api to make sure it can capture with given render product
- Respect render product file name pattern when getting frame path for single frame capture with render product

## [1.0.3] - 2022-01-20
### Added
- Support multiple buffer capture via a RenderProduct Prim

## [1.0.2] - 2021-12-21
### Added
- Added single frame progress for iray capture

## [1.0.1] - 2021-12-15
### Changed
- Update to use omni.kit.viewport_legacy
### Fixed
- Fixed HDR test cases

## [1.0.0] - 2021-09-09
### Added
- Move `omni.kit.capture` out from kit master to kit-tools repo, and rename it to `omni.kit.capture.viewport`


## [0.4.8] - 2021-09-08
### Changed
- Merge fixes from the release/102 branch; fixes includes:
- Fix the iray capture produces duplicated images issue
- Fix corrupted EXR image capture under certain circumstances, due to the rendering not behaving according to the value of the `asyncRendering` setting
- Backport required features of the plugin related to validation of frame counts and erroneous selection of Hydra engine when switching between RTX and Iray
- Add current frame index and total frame count to the notification system during frame capture

## [0.4.4] - 2021-07-05
### Added
- Added current frame index and total frame count to the notification system during frame capture.

## [0.4.3] - 2021-07-04
### Fixed
- Fixed the issue that can't switch to iray mode to capture images

## [0.4.2] - 2021-06-14
### Added
- Added support to renumber negative frame numbers from zero
### Changed
- Negative frame number format changed from ".00-x.png" to ".-000x.png"

## [0.4.1] - 2021-06-09
### Added
- Added the handling of path tracing iterations for capturing in Iray mode, also added a new entry to show number of iterations done on the progress window for Iray capturing

## [0.4.0] - 2021-05-25
### Fixed
- Fixed the issue that animation timeline's current time reset to zero after capture, now it's restored to the time before capture

## [0.3.9] - 2021-05-20
### Added
- Added a settle latency for capture in RTX real time mode to set the number of frames to be settled to improve image quality for each frame captured

## [0.3.8] - 2021-05-11
### Added
- Added support to the overwrite existing frame option; now if the frame path exists already, will warn either it will be skipped or it will be overwritten
- Added capture end callback in case users want it
### Fixed
- Fixed the issue that capture doesn't end in time if there are skipped frames
- Fixed the issue that all frames with number greater than start frame number in the output folder will be encoded into the final mp4 file, now only captured frames will be added.

## [0.3.7] - 2021-04-29
### Added
- Add support to new movie type sunstudy

## [0.3.6] - 2021-04-15
### Changed
- Change the name pattern of images of mp4 to be the same to capture Nth frames name pattern

## [0.3.5] - 2021-04-10
### Added
- Add support to skip existing frames at capturing sequence

## [0.3.4] - 2021-04-02
### Added
- Add preroll frames support so that it can run given frames before starting actual capturing. To save performance
for the preroll frames, "/rtx/pathtracing/spp" for path tracing will be set to 1

## [0.3.3] - 2021-03-01
### Added
- Add progress report of single frame capture in PT mode
- Update progress timers for video captures per iteration instead of per frame

## [0.3.2] - 2021-02-03
### Fixed
- Fix the time precision is a bit much issue

## [0.3.1] - 2021-02-03
### Fixed
- Fixed the PhysX and Flow simulation speed is much faster than normal in the captured movie issue
- Fixed the path tracing options are wrongly taken in the ray tracing mode during capture issue

## [0.3.0] - 2020-12-03
### Added
- Add support to capture in IRay mode

## [0.2.1] - 2020-11-30
### Removed
- Removed verbose warning during startup

## [0.2.0] - 2020-11-19
### Added
- Added functionality to capture with Kit Next

## [0.1.7] - 2020-10-19
### Fixed
- Hide lights and grid during capturing

## [0.1.6] - 2020-10-08
### Fixed
- Correct the update of motion blur subframe time
- Make sure frame count is right with when motion blur frame shutter open and close difference is not 1

## [0.1.5] - 2020-10-07
### Fixed
- Pass through the right file name
- Make sure padding is applied for files
