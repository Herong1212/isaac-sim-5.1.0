# Changelog

This document records all notable changes to the **omni.kit.viewport.window** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [107.2.0] - 2025-08-20
### Fixed
- OMPE-50562: Issue allowing that viewport-message is canceled in current app-update-cycle (before next begins animation)

## [107.0.12] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

### Fixed
- OMPE-28324: Fixed a leaked registered 'show window' function that leads to problems during Kit's normal shutdown.

## [107.0.11] - 2025-03-31
### Changed
- OMPE-37291: Improved error reporting for USD crate file version mismatch when drag and dropping USD file in viewport window.

## [107.0.10] - 2025-03-31
### Changed
- OMPE-41177: Filter timeline event subscription by type at creation time


## [107.0.9] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [107.0.8] - 2024-10-19
### Added
- Setting to hide the title-bar by default

## [107.0.7] - 2024-05-30
### Changed
- Replaced "bad material" RuntimeError with warning

## [107.0.6] - 2024-05-31
### Changed
- Pass flake8 repo linting tests.

## [107.0.5] - 2024-04-29
### Changed
- Create menu "Window"-"Viewport" instead of "Window"-"Viewport"-"Viewport 1" if only one viewport window available

## [107.0.4] - 2024-04-25
### Changed
- Update documentation

## [107.0.3] - 2024-04-15
### Changed
- Hide SPP counter in RTPT mode.

## [107.0.2] - 2024-04-04
### Changed
- Made omni.kit.menu.utils optional.

## [107.0.1] - 2024-03-21
### Changed
- Replace deprecated interface omni.usd.UsdContext.get_layers() with omni.kit.usd.layers.

## [107.0.0] - 2024-03-18
### Changed
- Move version to 107.0.0

## [106.0.5] - 2024-01-17
### Changed
- OM-84741: Map /app/viewport/boundingBoxes/enabled to guide/boundingBox/visible in viewport

## [106.0.4] - 2023-11-09
### Changed
- Make name argument to ViewportWindow constructor optional.

## [106.0.3] - 2023-11-14
### Added
- Settings to control "Host Memory" HUD item information and label.

## [106.0.2] - 2023-12-04
### Changed
- Use omni.kit.raycast.query for rtx viewport query

## [106.0.1] - 2023-10-04
### Changed
- Fixed drag/drop for multiple materials onto multiple descendents prims

## [106.0.0] - 2023-09-11
### Added
- Multiple settings to confiugure number of Viewport menu entries and their labeling.

## [105.2.3] - 2023-09-05
### Fixed
- Set show_alert flag to `MaterialFileDropDelegate` default to True

## [105.2.2] - 2023-08-31
### Changed
- Added show_alert flag to `MaterialFileDropDelegate`

## [105.2.1] - 2023-08-22
### Changed
- Handle stage-up axis in case insensitive way
- Added "Viewport" menu item order priority

## [105.2.0] - 2023-08-09
### Changed
- Disable rendering updates on Viewport by default when hidden (/app/renderer/skipWhileInvisible setting)

## [105.1.7] - 2023-07-13
### Changed
- Fixed get_material_name to use omni.kit.material.library

## [105.1.6] - 2023-06-21
### Changed
- UI improvement for material drag and drop in model selection mode.

## [105.1.5] - 2023-06-20
### Changed
- Pop up notification when reference or payload has no default prim.

## [105.1.4] - 2023-06-12
### Changed
- Propogate all exceptions from omni.kit.context_menu other than AttributeError or ImportError.

## [105.1.3] - 2023-05-25
### Added
- Arguments to pass through arbitrary HydraEngine creation options from Window creation

## [105.1.2] - 2022-05-18
### Added
- Size setting for camera axis gizmo (app.viewport.defaults.guide.axis.size).

## [105.1.1] - 2022-05-10
### Added
- content_clipping flag for camera speed dialog buttons.
- Honor viewport background alpha for HUD items.
- Honor transient nature of legacy forceHideFps showLayerMenu settings better.

## [105.1.0] - 2022-04-06
### Added
- "Nav Height" button into camera-speed HUD item.
### Changed
- Default scroll wheel speed modification to what legacy Viepwort used when not set.
- Fly-mode speed adjustment calculation for stability with mice that generate scroll-wheel events other than 1.

## [105.0.12] - 2022-03-29
### Fixed
- Allow for new selection mode to be used and ensure old is supported

## [105.0.11] - 2022-02-16
### Fixed
- Incorrect setting keys for stage-visibility when starting up.

## [105.0.10] - 2022-02-07
### Fixed
- Fixed scroll tests by adding finalize_test_no_image calls to tests that needed them.

## [105.0.9] - 2022-02-03
### Added
- Honor /app/viewport/grid/trackCamera to not explicitly set Viepwort's current grid-plane.
### Added
- Setting to limit camera-speed from scroll-wheel and text-entry inputs, defaulting to on.

## [105.0.8] - 2022-02-01
### Added
- Ability to create Viewport layers when proper extension dependecny is loaded.
- Ability for extensions to register/unregister ignored file extensions to drag drop handlers

## [105.0.7] - 2023-01-03
### Added
- Never raster viewport windows.
### Fixed
- Registration issues from update to omni.kit.menu.utils

## [105.0.6] - 2022-12-14
### Changed
- Updated menus to use omni.kit.menu.utils

## [105.0.5] - 2022-12-12
### Added
- Settings for object-centric viewport control.

## [105.0.4] - 2022-10-24
### Added
- Honor legacy carb-setting to disable context menu.
- Setting to control startup dock-tab visibility (defaulting to visible for now)
### Fixed
- Possibility of wrapping camera-speed around due to change-notifications on text-entry.
- Don't close CameraSpeed dialog while mouse is hovered above it.
### Changed
- Dock second Viewport to the right of the default Viewport.

## [105.0.3] - 2022-10-24
### Added
- Change the color of unused GPUs to gray in the HUD stats.

## [104.5.2] - 2022-10-17
### Changed
- Serialize all per-viewport HUD items that can be, on the way to fully removing displayOptions bitmask.
- Add settings handlers to map all legacy displayOptions into new per-viewport state, but preserve legacy behavior.

## [105.0.1] - 2022-09-26
### Added
- Make camera-speed indicator editable by user.
- Tooltips for camera-speed dialog.
### Changed
- Menu item lables for Viewport entries.
- Restore a ViewportWindow's Viewport resolution settings from persistent data.
- Generate ViewportAPI id from the owning ViewportWindow.
### Fixed
- Incorrect stats update when reporting multi-line stats.

## [105.0.0] - 2022-10-02
### Changed
- Use new omni.ui.Window.focus_policy to take focus on any mouse down.
### Added
- Drag drop mode settings dragDrop/intersectMode and dragDrop/maxPlaneDistance under /exts/omni.kit.viewport.window/
- Support for gamepad controller.
- Static ViewportWindow.active_window property.
- Viewport HUD UI for fly-mode speed indicator.
### Removed
- Toast message when Viewpot speed changes.

## [104.1.6] - 2022-09-26
### Added
- Honor new Viewport freeze_frame state to lock progress and resolution in HUD stats.
- Accessor to underlying ViewportWidget that is held in ViewportWindow
### Fixed
- Check against total render progress when RTX is not loaded.
- Always display elpased time for PathTrace when inifite sampler per pixel is used.

## [104.1.5] - 2022-09-21
### Fixed
- Honor /app/renderer/skipWhileMinimized setting.
- Top and Front orthographic views swapped when new stage is default to Z-up.

## [104.1.4] - 2022-08-25
### Changed
- Watch for any changes on global flight-mode speed change and push to all Viewports.

## [104.1.4] - 2022-09-06
### Changed
- Watch for any changes on global flight-mode speed change and push to all Viewports.

## [104.1.3] - 2022-08-25
### Changed
- Push Viewport change on timeline event.

## [104.1.2] - 2022-08-22
### Changed
- Add a second menu entry for a secondary Viewport.

## [104.1.1] - 2022-08-19
### Fixed
- Handle hideUi startup state better for internal unit-tests.

## [104.1.0] - 2022-08-15
### Added
- omni.ui property to scroll only when hovered.
- Interpret hide-ui settings at runtime rather than just startup.
### Changed:
- Temporarily disable possibility of orbit and scroll wheel overlapping movement.
### Fixed
- Issue with unsupported _find_viewport_layer API.

## [104.0.34] - 2022-08-09
### Fixed
- Vertical text layout for stats HUD when reporting many GPUs.
- Stats background keeping a small bubble when stat is visible but empty.
- Low memory not showing up as an error label.
### Added
- Post/Toast message API to ViewportWindow
- Posting camera speed to the ViewportWindow when adjusted.
- Remove any horizontal scroll wheel change affecting zoom or speed.
- Dependency to omni.kit.menu.utils.
### Changed
- Demote external drag-drop warning to info in the log.

## [104.0.33] - 2022-07-27
### Changed
- Added support for external drag/drop of audio files

## [104.0.32] - 2022-07-22
### Fixed
- Issue when scroll bar is locked if omni.ui did not send a key-up event.
- Material assignment to properly chosen item in omni.kit.material.library callback.
- Handle Usd.Stage up axis change after stage-open.
- Add audio drop delegate
### Changed
- Hide default Viewport window without totally destroying it on menu/visibility change.

## [104.0.31] - 2022-07-13
### Fixed
- Fix issue with drag-drop of mdl material getting new name.
- Selection box clamping and click outside Viewport.

## [104.0.30] - 2022-06-22
### Changed
-  Make material paths relative if "/persistent/material/stage/dragDropMaterialPath" is set to "relative"

## [104.0.29] - 2022-07-05
### Fixed
- Camera axis label size and color.
- Selection box clamping and click outside Viewport.

## [104.0.28] - 2022-06-24
### Fixed
- Add ignore protocol for drag and drop
### Changed
- Do not handle "material::" protocol when dropping (by material browser instead)

## [104.0.27] - 2022-06-23
### Added
- Support multiple drag-drop items when mime_data is a new-line delimited string.
- Pass unique and contant drop_data dictionary to accepted drag-drop delegates.
### Changed
- Support scene drag drop of any omni.usd supported file-type.

## [104.0.26] - 2022-06-16
### Changed
- Skip camera zoom when a keyboard key is down

## [104.0.25] - 2022-06-05
### Added
- Support /app/window/hideUi flag on startup for testing fullscreen Viewport with no UI elements.
- Interpret dragDropImport setting for creating payload or reference form drag-drop operation.
### Removed
- Remove 'f' key handling for move to new actions / hot-key API.

## [104.0.24] - 2022-05-23
### Changed
- Merge ViewportWindow and ViewportLayer get_frame

## [104.0.23] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.0.23] - 2022-05-04
### Changed
- Create more ui.Frame objects with content_clipping or horizontal_clipping.
- Disable materialflattener when running tests
### Added
- Interpret /app/viewport/forceHideFps setting
- Interpret /app/docks/disabled setting
### Removed
- Som eexplicit dependencies that should be handled at a higher level

## [1.0.22] - 2022-04-05
### Added
- OM-47179: Support mdl file drops and use omni.kit.material.library if available.

## [1.0.22] - 2022-04-05
### Added
- OM-47179: Support mdl file drops and use omni.kit.material.library if available.

## [1.0.21] - 2022-03-28
### Removed
- Removed scene view inserted into `omni.kit.manipulator.viewport`.

## [1.0.20] - 2022-03-25
### Added
- Double click to set camera center-of-interest
- Interpret speed multiplier from right-click and scroll-wheel
- Add get_frame method to create unique omni.ui.Frame objects (from menu callbacks)

## [1.0.19] - 2022-03-25
### Fixed
- Drag drop of file with a name that is not a valid Usd identifier

## [1.0.18] - 2022-03-16
### Changed
- Update test images for menubar changes

## [1.0.17] - 2022-03-11
### Changed
- Remove omni.kit.viewport.menu from dependency

## [1.0.16] - 2022-02-18
### Added
- Add setting to control default ViewportWindow window and menu name.
- Add setting to control whether ViewportWindow is created on startup.

## [1.0.15] - 2022-02-17
### Changed
- Destroy all Viewport stats subscriptons when globally hidden.
- Update test images for AOV menu name change.

## [1.0.14] - 2022-02-16
### Fixed
- Issue with extension reload from save and updates_enabled state.
- Selection hilighting in RTX for "models" pick mode.

## [1.0.13] - 2022-02-14
### Added
- Class for handling Usd.Prim drags and implement for Usd.Shade material bindings.
- Ability to add ignore-protocols to default USD drop-handler.
### Fixed
- Issue with legacy-drag-drop API layer drop callback.

## [1.0.12] - 2022-02-11
### Fixed
- Inablity to pick after dropping usd-reference when preview is disabled.

## [1.0.11] - 2022-02-09
### Fixed
- Use new ViewportAPI.updates_enabled properties for consistent style.

## [1.0.10] - 2022-02-08
### Fixed
- Fix failure to dock when extension disabled and loaded by using omni.ui.Window.deferred_dock_in.

## [1.0.9] - 2022-02-07
### Fixed
- Inablity to drop USD reference unless previewing

## [1.0.8] - 2022-02-07
### Added
- Add ability to toggle between states in USD reference drop and use it to toggle with preview-on-peek setting.
- Docking behind existing Viewport when present.
- Disable Viewport updates when Window is docked and not visible.
### Changed
- Move to omni.kit.context_menu.ViewportMenu for context menu implementation.

## [1.0.7] - 2022-01-31
### Added
- Fix issues with stats area blocking mouse-events in dead space.
- Add support for external drag-drop of USD or user defined callback
- Add support for internal drag-drop of USD references.
- ViewportWindow.get_frame method

## [1.0.6]
### Added
- Viewport HUD stats
- Drag and Drop support
- Context menu support
- omni.ui event delegation
### Fixed
- Legacy grid drawing for stage-up axis

## [1.0.5]
### Changed
- Use new API for Viewport to push changes into known SceneView models.

## [1.0.4]
### Changed
- Disable live-selection.

## [1.0.3]
### Changed
- Add preview image.

## [1.0.2]
### Changed
- Move core camera-manipulation classes into omni.kit.manipulator.camera

## [1.0.1]
### Changed
- Add text to view-axis
- Hide origin and view axis by default.

## [1.0.0]
### Changed
- Re-enable multiple viewports
- Add more control to omni.kit.viewport.Window construction

## [0.9.6]
### Changed
- Add a styled-rect to control Viewport background color

## [0.9.5]
### Changed
- Remove all omni.scene.ui inheritance

## [0.9.0]
### Changed
- Remove omni.scene.ui.SceneView sub-classing
- Have scroll-wheel event trigger Zoom camera gesture

## [0.8.1]
### Changed
- Make MenuBar, Camera, and Selection direct dependencies for easier loading

## [0.8.0] - unrelease
### Changed
- first release
