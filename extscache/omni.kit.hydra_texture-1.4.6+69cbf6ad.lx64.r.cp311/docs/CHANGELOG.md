# CHANGELOG

This document records all notable changes to ``omni.kit.hydra_texture`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [1.4.6] - 2025-06-25
### Fixed
- Issue syncing carb-settings from cmd-line to Usd on creation

## [1.4.5] - 2025-06-10
### Added
- Setting to block specific carb settings from contributing to a UsdRender.Product sync

## [1.4.4] - 2025-05-24
### Added
- Setting to control the allowed types that a prim can be when set to camera_path

## [1.4.3] - 2025-05-20
### Fixed
- Issue with async rendering possibly creating a camera from a closed scene in a newly opened scene.

## [1.4.2] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.4.1] - 2025-03-26
### Added
- Support for unique event Observer names with /app/events/qualifiedNames setting

## [1.4.0] - 2024-11-22
### Added
- Wrappers for deprecation with python_api.md

## [1.3.9] - 2024-07-16
### Added
- swh_frame_number access when requesting frame-info

## [1.3.8] - 2024-04-25
### Added
- Documentation generation
### Changed
- Release Python GIL for most methods
### Fixed
- Issue broadcasting changes/events when renderer has completed asynchronous startup.

## [1.3.8] - 2024-04-10
### Added
- Auto apply AppliedAPI schemas to UsdRender.Product prims.

## [1.3.7] - 2024-03-16
### Fixed
- More present-thread texture expiration issues.

## [1.3.6] - 2024-03-26
### Changed
- Delay RaycastQueryManager warning until first query-request and promote to error.

## [1.3.5] - 2024-03-15
### Changed
- DeviceMask support for a hydra engine config with additional arguments for hydra texture.

## [1.3.4] - 2024-03-13
### Changed
- SensorSim Core API POC changes.

## [1.3.3] - 2024-02-16
### Fixed
- Possibility of preparing present thread to present textures that never materialize.
### Changed
- Integrated Core POC changes.

## [1.3.2] - 2024-02-06
### Fixed
- Issues with texture name and RenderProduct and carb.settings path.
- Initial return value of RenderProduct path.
### Changed
- Create RenderProducts grouped into a common scope.
- Reset to implicit RenderProduct by setting it to an empty path.
### Added
- Settings to control texture name and RenderProduct path.
- Settings to control re-application of camera, resolution, and render-product overrides on open.
- SensorSim Core API POC merge.

## [1.3.1] - 2024-02-06
### Changed
- Make "omni.kit.renderer.core" dependency optional.

## [1.3.0] - 2023-12-12
### Changed
- Conform setting path to kit extension style.

## [1.2.0] - 2023-10-12
### Added
- Accelerated ray queries when rendering with RTX

## [1.1.8] - 2023-09-25
### Fixed
- Do legacy compat work on main thread to avoid possible crash in carb-subscriptions.

## [1.1.7] - 2023-08-09
### Changed
- Destroy viewport when updatesEnabled is set to false.
- Make sure to aquire USD mutex for more render-product writes.

## [1.1.6] - 2023-05-31
### Added
- Additional arguments and tests for create_hydra_texture

## [1.1.5] - 2023-05-31
### Fixed
- Release Python GIL when creating or destroying an new HydraTexture instance.

## [1.1.3] - 2023-02-10
### Added
- Push kEventTypeRenderSettingsChanged event when underlying HydraEngine has changed.

## [1.1.2] - 2022-11-23
### Changed
- Handle possibility of asynchronous GPU foundation startup.
### Fixed
- Advance the elapsed time in viewport stats only if rendering was a success.

## [1.1.1] - 2022-11-01
### Added
- HydraTexture now contains metadata that can be passed to image saving.

## [1.1.0] - 2022-10-27
### Fixed
- Possibility of over invalidation from carb change subscriptions which could propogate to a Viewport rebuild.

## [1.0.9] - 2022-10-20
### Added
- Store devices used to render the image in HydraTexture.

## [1.0.8] - 2022-09-10
### Added
- Watch for changes to /app/captureFrame/hdr changes to emulate legacy Viewport.
- Ability to cancel all in-flight picking from Python.
### Fixed
- Cancel any in flight picking on a change that may make them never complete.

## [1.0.7] - 2022-09-06
### Added
- Ability to draw with new presentation thread.

## [1.0.6] - 2022-08-10
### Fixed
- Incorrect value pushed into render-settings changed event.

## [1.0.5] - 2022-07-19
### Added
- Ability to update legacy camera-mesh representations in USD.

## [1.0.4] - 2022-05-18
### Changed
- Push viewport handle into USD RenderProduct for SDG/OG usage.
- Track TokenH from Python strings better.
- Setup LdrColor AOV once and preserve subsequent AOV changes from USD.

## [1.0.3] - 2022-03-05
### Changed
- Use default UsdContext for current test suite rather than a custom one.

## [1.0.2] - 2022-02-23
### Fixed
- Validate usd-context on every subscription event.

## [1.0.1] - 2022-02-10
### Fixed
- Fixed possibility of crash requesting an AOV's RpResource that the renderer didn't deliver.
