# Changelog


This document records all notable changes to the **omni.usd** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.13.10] - 2025-06-06
### Fixed
- OMPE-52452: Issue resolving relative files for crate version testing

## [1.13.9] - 2025-05-22
### Fixed
- OMPE-46871: usd crate file version check asset path resolve need to happen before file extension check.

## [1.13.8] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [1.13.7] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [1.13.6] - 2025-04-14
### Fixed
- OMPE-39917: PrimWatcher always being bound to default UsdContext

## [1.13.5] - 2025-04-08
### Changed
- OMPE-41247: Use omni.kit.async_engine.run_coroutine in watcher to schedule async tasks to avoid error when not running in main thread.

## [1.13.4] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.13.3] - 2025-03-31
### Changed
- OMPE-37291: Improved error reporting for USD crate file version mismatch on stage open and adding payloads/references.

## [1.13.2] - 2025-03-03
### Changed
- Opening a new stage now clamps current time to stage start/end time if it is out of the range.
### Added
- Added tests for USD timeline.

## [1.13.1] - 2025-02-21
### Added
- OMPE-31959: Update omni.usd.get_stage_next_free_path with added source prim kwarg to fix issue with jumping suffix when renaming prims.

## [1.13.0] - 2025-02-11
### Changed
- OMPE-33113: added "AppendAPIToPrimsCommand", "RemoveAPIFromPrimsCommand"

## [1.12.11] - 2025-01-31
### Fixed
- OMPE-34395: Cleanup check for omni.kit.stage_template.core
- OMPE-34395: Removed duplicated functions

## [1.12.10] - 2025-01-17
### Fixed
- OMPE-32704: remove omni.kit.usd.mdl extension from Kit startup.

## [1.12.9] - 2025-01-13
### Changed
- next_frame_async to use new Viewport only

## [1.12.8] - 2024-12-31
### Changed
- OMPE-32142: Add tests for UTF-8 support for variants and variant sets.

## [1.12.7] - 2024-12-20
### Changed
- OMPE-31902: Add omni.usd.make_valid_identifier to public API that makes a valid identifier that supports unicode characters.
- OMPE-31903: Add test for omni.usd.make_valid_identifier, update test with unicode data.

## [1.12.6] - 2024-12-16
### Changed
- OMPE-28754 - Rework logic for CreateShaderPrimFromSdrCommand, CreatePreviewSurfaceTextureMaterialPrimCommand and CreatePreviewSurfaceTextureMaterialPrimCommand.
   so that shader input properties are not created by default.

## [1.12.5] - 2024-12-03
### Changed
- OMPE-28550: Add check for invalid stage when passed in for usd commands; Add initialization for MovePrimCommand for stage selection.

## [1.12.4] - 2024-11-21
### Changed
- OMPE-22619: Update public API

## [1.12.3] - 2024-10-29
### Changed
- OMPE-6208: Remove USDIMAGING_ALLOW_UNREGISTERED_SHADER_IDS

## [1.12.2] - 2024-09-05
### Added
- OMPE-12316: Add file scheme prefix in ` make_path_relative_to_current_edit_target` if the current relative url is an absolute local path, and the layer is non-local.

## [1.12.1] - 2024-07-09
### Added
- OMPE-14277: Fixed infinite loop crash in UngroupPrimsCommand.

## [1.12.0] - 2024-06-10
### Changed
- Rework FramePrimCommands for the Viewport's auto-frame case

## [1.11.2] - 2024-06-18
### Added
- OMPE-9290: When adding reference or payload of a local asset to a non-local layer, the asset path will be prefixed with
    ``file:``scheme to avoid the ambiguity of whether it's a relative path on Linux

## [1.11.1] - 2024-06-13
### Fixed
- Fix omni.usd.merge_layers to resolve external dependencies correctly during merge.

## [1.11.0] - 2024-06-04
### Fixed
- OM-118687: load_mdl_parameters_for_prim_async marked as deprecated due to UsdMaterialWatcher being removed from Kit.
- clean up args passed to RemovePropertyCommand

## [1.10.39] - 2024-04-02
### Added
- Selection filter unit tests

## [1.10.38] - 2024-03-21
### Added
- Improve docs.
- Retire deprecated layers interfaces from omni.usd.
- Move commands from omni.command.usd into omni.usd to deprecate omni.command.usd.

## [1.10.37] - 2024-003-14
### Changed
- SensorSim Core API POC changes for mutex-locking.

## [1.10.36] - 2024-03-13
### Added
- OM-122149: Remove schema dependencies.
- OM-118750: Hydra engine destruction.

## [1.10.35] - 2024-02-22
### Added
- "persistent/app/primCreation/highQuality" default setting
- get_geometry_standard_prim_list and get_light_prim_list
### Changed
- Sensor-sim to coreapi server
### Removed
- Execution graph compilation

## [1.10.34] - 2024-02-21
### Added
- Exposed `recreate` kwarg to `UsdContext.load_mdl_parameters_for_prim_async`
- Rename FabricLanes to FabricRenderingViews

## [1.10.33] - 2024-01-17
### Added
- Cpp command to serialize asset at 'asset_path' to disk at 'serialized_path'
- SensorSim Core API POC integration.

## [1.10.32] - 2023-01-15
## Changed
- Fix issue that APP_READY is released before new stage creation.

## [1.10.31] - 2023-12-27
## Changed
- Use omni.kit.stage_template.core

## [1.10.30] - 2023-12-26
### Fixed
- Typo

## [1.10.29] - 2023-12-25
### Changed
- Fix DeletePrims command to restore default prim for undo.

## [1.10.28] - 2023-12-18
### Changed
- Workaround to avoid flushing colorSpace value when inserting a new sublayer.

## [1.10.27] - 2023-12-14
### Changed
- [OM-114474]: ChangePropertyCommand clears attribute value when input value is None.
- OM-115814: make `make_path_relative_to_current_edit_target` more robust

## [1.10.26] - 2023-12-05
### Changed
- Post-process (formerly known as post-execute) tasks are now scheduled via the default ExecutionController.

## [1.10.25] - 2023-11-30
### Fixed
- Don't resolve property change in MaterialWatcher when current edit context is session layer

## [1.10.24] - 2023-11-21
### Fixed
- Improved undo of some commands.
- Fixed errors with variants.

## [1.10.23] - 2023-11-20
### Changed
- Fix CreateUsdAttributeCommand issue to avoid caching prim handle.

## [1.10.22] - 2023-10-11
### Changed
- Re-factoring UsdWatcher to improve performance, fix issues and cover tests.

## [1.10.21] - 2023-09-06
### Changed
- OM-67061: Add `remove_from_layers` kwarg to RemovePropertyCommand to specify layers to remove property from.

## [1.10.20] - 2023-09-19
### Changed
- Update python bindings for omni.usd.Selection, replace deprecated ones

## [1.10.19] - 2023-09-01
### Added
- Added `CreateMtlxMaterialPrimCommand` command

## [1.10.18] - 2023-08-22
### Changed
- Improve MovePrim command to return valid results.

## [1.10.17] - 2023-08-03
### Changed
- Add `source` argument to `clear_selected_prim_paths` and `is_prim_path_selected` to allow getting and setting selection for either USD and Fabric stage.
- Maintain an ordered selection list to track selection from both USD and Fabric stages

## [1.10.16] - 2023-08-02
### Changed
- Add `source` argument to `getSelectedPrimPaths` and `setSelectedPrimPaths` to allow getting and setting selection for either USD and Fabric stage.

## [1.10.17] - 2023-10-17
### Changed
- Increase code coverage above 85%.

## [1.10.16] - 2023-10-11
### Changed
- Re-factoring UsdWatcher to improve performance, fix issues and cover tests.

## [1.10.15] - 2023-07-25
### Changed
- Added context_name to CreatePrimsCommand

## [1.10.14] - 2023-07-31
### Changed
- Add command to toggle active state of prims.

## [1.10.13] - 2023-07-28
### Changed
- Do not skip writeback on non-anon sublayer of session layer in UsdMaterialWatcher.

## [1.10.12] - 2023-07-17
### Changed
- Removed `inputs:excludeFromWhiteMode` population from UsdMaterialWatcher.

## [1.10.11] - 2023-07-12
- Pop up notification for ChangePropertyCommand when it has stronger overrides.

## [1.10.10] - 2023-07-04
- Improve CreateMdlMaterialPrimCommand, add param to set stage.

## [1.10.9] - 2023-07-03
- Improve undo of ToggleVisibilitySelectedPrimsCommand.

## [1.10.8] - 2023-06-26
- Improve MovePrimCommand to be UsdContext aware.
- Fix commands call that should be UsdContext aware.

## [1.10.7] - 2023-06-20
### Changed
- Pop up notification when reference or payload has no default prim.

## [1.10.6] - 2023-06-12
### Changed
- Allow UsdMaterialWatcher in secondary USDContext.

## [1.10.5] - 2023-06-12
### Fixed
- Fix regression that cannot save sublayers.

## [1.10.4] - 2023-06-09
### Fixed
- More thorough checking for editing of Gprim hierarchies in move and copy commands.

## [1.10.3] - 2023-05-29
### Added
- Don't reload render settings when root layer is reloaded or flushed.

## [1.10.2] - 2023-05-26
- Improve omni.usd.get_introducing_layer to check local layer stack firstly.
- Improve duplication to duplicate prim defined in the local layer stack firstly.

## [1.10.1] - 2023-05-26
### Added
- Improve save to avoid data loss caused by path comparison.
- Fix save issue to avoid data loss when target layer of save-as is opened already.

## [1.10.0] - 2023-05-11
### Added
- Added ability to disable material watcher using settings.

## [1.9.2] - 2023-05-05
### Added
- Selection filter settings documentation

## [1.9.1] - 2023-04-23
### Fixed
- Removed attach/detach commands because they are no longer used.

## [1.9.0] - 2023-04-17
### Fixed
- OmniUsdTimelineControl setting to stage without lock begin held.
### Added
- Interpret string render settings properly for restoration.
- Additional default preferences.

## [1.8.12] - 2023-04-12
### Added
- Fix duplication issues to prims inside reference of reference.

## [1.8.11] - 2023-04-04
### Added
- UsdPreviewSurfaceTexture: set fallback value on normal map to [0, 0, 1, 0]

## [1.8.10] - 2023-04-04
### Added
- If property has custom data "nonpersistant" write it to session layer.

## [1.8.9] - 2023-03-31
### Fixed
- Fixed incorrect indentation in `TransformPrimSRTCommand` when fetching individual axis rotation ops.

## [1.8.8] - 2023-03-15
### Added
- Added persistent.app.primCreation.typedDefaults
- Added function `gather_default_attributes()` to get typedDefaults
- Updated `CreatePrimWithDefaultXformCommand` to call `gather_default_attributes` to get prim defaults

## [1.8.7] - 2023-03-16
### Fixed
- Added error handling for AddReference command

## [1.8.6] - 2023-03-16
### Fixed
- Update usd_commands.py for UsdPreviewSurface refactor.

## [1.8.5] - 2023-03-16
### Fixed
- Fix material watch to avoid populating default params into current edit target.

## [1.8.4] - 2023-03-10
### Fixed
- Fix regression that opening a stage will not include stage url in the event.

## [1.8.3] - 2023-03-01
### Added
- Add interface to open stage with specified session layer.

## [1.8.2] - 2023-02-26
### Changed
- Replaced asyncio.ensure_future calls in utils.py with omni.kit.async_engine.run_coroutine function.

## [1.8.1] - 2023-02-22
### Fixed
- Renamed omni.kit.exec references to omni.kit.exec.core

## [1.8.0] - 2023-02-18
### Added
- Additional enum `eHierarchyChanged` to StageEventType

## [1.7.15] - 2023-02-08
### Fixed
- Improve omni.usd.set_prop_val to support predicate when auto_target_layer is True.

## [1.7.14] - 2023-02-03
### Fixed
- Issue with ChangePropertyCommand when called with an omni.usd.UsdContext object.
- Export get_context_from_stage_id as 104.2 had done.

## [1.7.13] - 2022-01-17
### Added
- Added `correct_filename_case` to workaround windows paths being lower-case

## [1.7.12] - 2022-01-17
### Fixed
- Detect external relationships for instancing command and post notification.

## [1.7.11] - 2022-01-12
### Fixed
- Fix outline issue to select instance.

## [1.7.10] - 2022-12-15
### Fixed
- Fix material watcher to resolve undo issue of material inputs.

## [1.7.9] - 2022-12-13
### Fixed
- Add API to get usd context from stage.

## [1.7.8] - 2022-12-08
### Fixed
- Fix issue that will open stage as payloads disabled after saving new stage.

## [1.7.7] - 2022-11-23
### Fixed
- Fix material watcher: don't set param value in session layer if it's non-empty already.

## [1.7.6] - 2022-11-17
### Added
- Add omni:kit:hideInUI meta for the purpose of hiding prims inside editor.

## [1.7.5] - 2022-11-14
### Fixed
- Fix material create commands when Looks prim is inactive.

## [1.7.4] - 2022-11-09
### Fixed
- Fix CreateInstance command that cannot reference bindings that are outside of prototype prim's namespace.

## [1.7.3] - 2022-11-08
- Add separate usd context support to material commands.

## [1.7.2] - 2022-10-31
### Fixed
- Open stage auto-connects to Nucleus server.

## [1.7.1] - 2022-10-28
### Fixed
- Crash when ChangePropertyCommand undo invoked with a non-existing path

## [1.7.0] - 2022-10-21
### Fixed
- Issue with Audio being created from incorrect HdRPrim visibility.
### Removed
- Code to control UsdAudio's effective visibility outside of the UsdStage.
### Added
- Argument to select prim when for Create References, Payload, and Audio commands.

## [1.6.12] - 2022-10-20
### Changed
- Try/Catch omni.usd_resolver query as it's possible called before it's initialized.

## [1.6.11] - 2022-10-14
### Changed
- Add InitialLoadSet argument to omni.usd.UsdContext.new_stage().

## [1.6.10] - 2022-09-22
### Changed
- Added new parameter to `create_material_input(prim, name, value, vtype, def_value=None, min_value=None, max_value=None, display_name=None, display_group=None, color_space=None)`

## [1.6.9] - 2022-09-21
### Fixed
- Issue with custom selection not being cleared making drag drop hovering sticky.

## [1.6.8] - 2022-09-13
### Changed
- Improve save-as to keep load/unload set after saving.

## [1.6.7] - 2022-09-05
### Changed
- Adds support to group non-xformable prims.

## [1.6.6] - 2022-08-12
### Changed
- added `omni.usd.is_ancestor_prim_type`
- added `omni.usd.can_prim_have_children`
- updated `CopyPrimCommand` & `MovePrimCommand` to use omni.usd.is_ancestor_prim_type

## [1.6.5] - 2022-08-26
### Changed
- Reload render settings if root layer is flushed or reloaded.

## [1.6.4] - 2022-08-19
### Changed
- Added undo to `ClearRefinementOverridesCommand`.

## [1.6.3] - 2022-08-25
### Changed
- Add settings to control nested gprims authoring.

## [1.6.2] - 2022-08-23
### Changed
- Updated `TransformPrimSRTCommand`, `TransformPrimCommand` and `TransformPrimSRTCpp` to auto target session layer on a per-xformOp basis rather than per-prim.
### Added
- Added test coverage for `TransformPrimSRTCpp` and session layer auto targeting.

## [1.6.1] - 2022-08-08
### Changed
- `ChangePropertyCommand` now clears the attribute value if it was not authored before during undo.

## [1.6.0] - 2022-08-02
### Added
- Added `omni.usd.cppcommands` plugin that provides USD related commands in C++.
- `TransformPrimSRTCpp` and `TransformMultiPrimsSRTCpp` are the first batch of C++ commands added.
- Additional arguments to ChangePropertyCommand to for custom and variability.

## [1.5.11] - 2022-08-02
### Fixed
- Use relative path by default for path authoring.

## [1.5.10] - 2022-07-25
### Fixed
- Fix duplicate that will not keep transform when prim is defined in references or payloads but has overrides in the current edit target.

## [1.5.9] - 2022-07-22
### Fixed
- Handle camera renames better for all Viewports.

## [1.5.8] - 2022-05-20
### Added
- Added `make_path_relative_to_current_edit_target` function
-   This makes material path relative if "/persistent/app/material/dragDropMaterialPath" is set to "relative"

## [1.5.7] - 2022-06-08
### Fixed
- Improve DeletePrims/MovePrims/GroupPrims to support non-desctutive authoring.

## [1.5.6] - 2022-06-06
### Fixed
- CreatePayloadCommand to make a relative path as CreateReferenceCommand does.

## [1.5.5] - 2022-06-02
### Fixed
- Issue with BindMaterialCommand and strength-list with empty strengths

## [1.5.4] - 2022-05-20
### Added
- Open_stage script checks that url exists before trying to open it.

## [1.5.3] - 2022-03-31
### Added
- Refactoring omni.usd to separate all layers interfaces as extension `omni.kit.usd.layers`.

## [1.5.2] - 2022-02-10
### Added
- Made DeletePrimsCommand not deletable/ancestral prim warnings as they break tests

## [1.5.1] - 2022-02-17
### Added
- Added `get_prim_descendents`

## [1.5.0] - 2022-02-10
### Added
- Added get_callback_info() override to CopyPrimCommand.

## [1.4.9] - 2022-01-11
### Changes
- Updated PreviewSurfaceTextureMaterial with additional UsdUVTexture parameters

## [1.4.8] - 2021-12-10
### Added
- Additional enums to StageEventType

## [1.4.7] - 2021-11-16
### Changes
- Moved kit/source/python/extensions-bundled/omni/kit/builtin/init.py into omni.usd

## [1.4.6] - 2021-11-03
### Changes
- depreciated `get_subidentifier_from_material` and `get_subidentifier_from_mdl`. New versions are now in omni.kit.material.library

## [1.4.5] - 2021-07-29
### Added
- Added PayloadCommands `AddPayloadCommand`, `RemovePayloadCommand`, `ReplacePayloadCommand` and `CreatePayloadCommand`
- Added function `get_composed_payloads_from_prim`

## [1.4.4] - 2021-06-01
### Added
- Updated CopyPrimCommand to fixup References when chaning layers

## [1.4.3] - 2021-05-10
### Added
- Updated Sdf.Reference creation so it doesn't use windows slash "\"

## [1.4.2] - 2021-05-03
### Changes
- Added `get_subidentifier_from_mdl` a version `get_subidentifier_from_material` which takes URL path

## [1.4.1] - 2021-05-02
### Changes
- Update material related property widgets

## [1.4.0] - 2021-04-15
### Changes
- Added `loadInputs` (default True) to `addToPendingCreatingMdlPaths`.

## [1.3.1] - 2021-04-09
### Changed
- Add API for Selection to handle SdfPath directly to avoid string/SdfPath conversion.

## [1.3.0] - 2021-03-10
### Changed
- Moved `omni.kit.utils.get_stage_next_free_path` to `omni.usd.get_stage_next_free_path`. Added path validity check and tests.

## [1.2.1] - 2021-03-09
### Added
- Added `exts/omni.usd/mdl/populateInputsOnLoaded` settings to optionally populate MDL inputs on loaded. Default to false.

## [1.2.0] - 2021-02-23
### Added
- Added `TransformPrimSRTCommand` command and test.

## [1.1.0] - 2021-02-19
### Changed
- `CreateReferenceCommand` now sets `Instanceable` flag according to preference settings.

## [1.0.1] - 2021-02-17
### Changed
- Rewrite `ReplaceReferenceCommand`.

## [1.0.0] - 2021-01-19
### Added
- Started maintaining Changelog. Bumpped omni.usd version to 1.0.0.
