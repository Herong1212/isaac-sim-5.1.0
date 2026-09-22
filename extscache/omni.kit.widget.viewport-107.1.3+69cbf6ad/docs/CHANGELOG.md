# CHANGELOG

This document records all notable changes to ``omni.kit.widget.viewport`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [107.1.3] - 2025-04-14
### Fixed
- Performance issue from SdfPath to string conversion

## [107.1.2] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [107.1.1] - 2025-03-12
### Changed
- Changed set_image_data call to pass imaging metadata needed for data window support.

## [107.1.0] - 2025-02-21
### Added
- RenderCapture support for capturing a specific SWH frame number.

## [107.0.8] - 2024-06-04
### Changed
- OMPE-35996: Make sure capture file generated in tests.

## [107.0.7] - 2024-06-04
### Changed
- python classmethod to staticmethod decorator

## [107.0.6] - 2024-06-04
### Added
- Viewport camera auto-framing

## [107.0.5] - 2024-05-29
### Changed
- Pass flake8 repo linting tests

## [107.0.4] - 2024-05-15
### Changed
- Setting name for single-camera-model to conform to proper /exts/ namespace

## [107.0.3] - 2024-04-25
### Added
- Additional documentation

## [107.0.2] - 2024-04-05
### Changed
- Demote render_settings_changed callback error for USdContext withoput a stage to a warning

## [107.0.1] - 2024-04-04
### Changed
- Increase testing timeout for tests that require RTX

## [107.0.0] - 2024-03-18
### Changed
- Move version to 107.0.0

## [106.0.1] - 2024-01-09
### Fixed
- Make OverlayViewportDisplayDelegate lock-off the previous/under image so it works when present-thread is enabled.

## [106.0.0] - 2023-12-12
### Changed
- Support omni.hydra.pxr engine instance per UsdContext instead of a single global engine.
- Reduce and optimize SceneCameraModel code and make it completely private.

## [105.2.0] - 2023-11-01
### Added
- Accelerate query-requests if rendering with RTX (enabled by default).
- More testing to bring coverage to 87% from 81%.

## [105.1.4] - 2023-09-28
### Added
- Using SceneCameraModel that is an enhanced camera model class designed specifically for scene navigation.
- SceneCameraModel instance management with app setting's condition check.

## [105.1.3] - 2023-08-22
### Changed
- Handle stage-up axis in case insensitive way

## [105.1.2] - 2023-07-13
### Fixed
- Possibile exception thrown on open of stage with implicit camera saved to with declared transform-ops that are not authored.
- Issue created with auto-attach from merge between 105.0.1 and 105.1.0.

## [105.1.1] - 2023-06-27
### Changed
- Allow autoAttach modes to choose when to attache renderer, possbily earlier in startup
### Added
- Ability for Viewport to enable renderer extensions when auto-attach occurs at startup.

## [105.1.0] - 2023-05-09
### Added
- Arguments to pass through arbitrary HydraEngine creation options from Widget creation

## [105.0.8] - 2023-03-17
### Added
- Add /exts/omni.kit.widget.viewport/autoAttachRenderer setting to attempt to attach engine on stage open

## [105.0.7] - 2023-03-08
### Changed
- Add /app/omni.usd/storeCameraSettingsToUsdStage (false not to write camera settings when saving, defaults to true)

## [105.0.6] - 2023-02-26
### Changed
- Replaced asyncio.ensure_future calls in widget.py with omni.kit.async_engine.run_coroutine function.

## [105.0.5] - 2023-02-10
### Fixed
- Possibility of ViewportWindow's timeline events forwarding to ViewportWidget when no stage is attached.

## [105.0.4] - 2023-02-03
### Fixed
- Issue restoring come orthographic cameras with non-orthogonal rotations.

## [105.0.3] - 2023-02-01
### Fixed
- Properly subscribe to render events for a renderer if stage was previosly opened with invalid renderer assigned.

## [105.0.2] - 2022-12-05
### Fixed
- omni.activity.core.ended not begin called
- Issue with omni.ui.scene elements stretching until resize completed.
- Some Python typing hints.
### Changed
- Make omni.activity.core an optional dependency
- Move Viewport / UI resolution tracking into ViewportWidget to function whether resolution menu is not loaded or hidden.
### Added
- Ellision and settings to control intermediate resize events when ui is driving resolution change.

## [105.0.1] - 2022-10-28
### Added
- Calls to Render Capture now include metadata from the previous frame.

## [105.0.0] - 2022-10-12
### Added
- Ability to explicitly specify a unique ID for a ViewportAPI.
### Removed
- Any stage-up rotation conversion when a camera was loaded from disk.

## [104.1.11] - 2022-09-27
### Fixed
- Issue with over compensating for stage-up axis changing with multiple ViewportWidgets.
- Setting target layer when compensating for stage-up axis changes.

## [104.1.10] - 2022-09-20
### Fixed
- Jittery synchronization of omni.ui.Scene and rendered results.
### Added
- freeze_frame API to stop pushing new renders to UI.
- DisplayDelegate API for affecting/transitioning ui.Images in the Viewport.
### Removed
- Legacy code for 103.1 that is no longer needed in 103.5 and above.

## [104.1.9] - 2022-09-09
### Fixed
- Top and Front orthographic views swapped when new stage is default to Z-up.
- Exceptions opening files wheere Kit's implicit cameras have somehow been saved into them.

## [104.1.8] - 2022-09-06
### Added
- Ability to draw with new presentation thread.

## [104.1.7] - 2022-08-25
### Changed
- Pass Viewport time when retrieving Gf.Camera.

## [104.1.6] - 2022-08-18
### Changed
- Implement default render choice in terms of legacy Viewport.
- Handle possibility of no valid renderer better.

## [104.1.5] - 2022-08-15
### Fixed
- Fallback to implicit Perspective camera when reading the boundCamera meta-data fails in USD.
- Incorrect value pushed into render-settings changed event.

## [104.1.4] - 2022-08-10
### Added
- Ability to specify format_desc dictionary to new capture-file API.

## [104.1.3] - 2022-07-25
### Fixed
- Always save camera-settings metadata to the root-layer.
- Handle Usd.Stage up-axis changes after open.

## [104.1.1] - 2022-07-13
### Added
- Assume single viewport and set legacy /renderer/active on render change.

## [104.1.0] - 2022-07-08
### Fixed
- Resolution scaling API and access to Viewport's full_resolution.
- Implicit orthographic camera rotation for non Y-up stages.

## [104.0.12] - 2022-06-09
### Fixed
- Interpret all startup values for built-in Camera creation.
- Move to common refactored image comparison routines.

## [104.0.11] - 2022-05-31
### Fixed
- Issue with Viewport seelection-outline settings not honoring incomnig defaults.

## [104.0.10] - 2022-05-19
### Fixed
- Issue with restoration of very old usd files and bound orthographic cameras.

## [104.0.9] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.0.9] - 2022-05-04
### Added
- Read default Perspective focalLength from carb.setttings
- Methods to match LegacyViewport Camera, RenderProduct, and texture-resolution
### Changed
- Return an absolute path for the Viewport's implicit RenderProduct path.
- Resolve default renderer based on /renderer/active

## [1.0.8] - 2022-03-30
### Fixed
- OM-47005: Add fallback to restore to previous sesion camera when explicit camera not requested
### Changed
- Re-enable capture tests
### Added
- Session camera restore tests
- Aperture projection adjustment

## [1.0.7] - 2022-02-09
### Added
- Capture frame API and first test-suite
- Async wait_for_rendered_frames and wait_for_render_settings_change convenience functions
### Changed
- Move ViewportAPI.set_updates_enabled method to property for consistency

## [1.0.6] - 2022-02-07
### Added
- ViewportAPI.lock_to_render_result property for pushing view and projection from the rendered result.
- ViewportAPI.id property for explicit key that is hashable.
- ViewportAPI.set_updates_enabled method

## [1.0.5] - 2022-01-31
### Changed
- Support possibility that Viewport has been destroyed before unregistering notification.

## [1.0.4]
### Changed
- Move to newer omni.kit.hydra_texture API.
- Add frame_info and fps properties
- Add notification on frame changed
- Optimize settting of some omni.ui.scene model values

## [1.0.3]
### Changed
- Fix issue on opening new Usd.Stage.
- Add new API for Viewport to track and push into SceneView models.
  This allows for moe automatice synching without having to worry about widget-size changes, but also opens door
  to locking to the View and Projection used to generate the rendered-frame.

## [1.0.2]
### Changed
- Fix some destruction and cleanup issues.

## [1.0.1]
### Changed
- Check possibility that omni.hydra.pxr supports async rendering.

## [1.0.0]
### Changed
- Fix issue with possibly conflicting hydra_texture names.

## [0.9.6]
### Changed
- Fix issue with Window close and shutdown when Viewport-1 is active

## [0.9.5]
### Changed
- Remove all omni.scene.ui inheritance

## [0.9.0]
### Changed
- Version bump

## [0.8.1]
### Changed
- version

## [0.8.0] - unrelease
### Changed
- first release
