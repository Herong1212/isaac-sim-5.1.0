# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.7] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [2.0.6] - 2025-04-23
### Updated
- OMPE-41797: Corrected docs to use CreateAttribute instead of GetAttribute

## [2.0.5] - 2025-04-18
### Fixed
- OMPE-39917: PrimWatcher always being bound to default UsdContext

## [2.0.4] - 2025-04-15
### Fixed
- OMPE-43816: ensured some extension enable/disable hook objects are cleaned up.

## [2.0.3] - 2025-02-21
### Changes
- OMPE-29401: Add support for /app/properties/material/mdlForceRawForUsage setting.

## [2.0.2] - 2025-01-13
### Changes
- OMPE-27796, OMPE-27800: Updated public API

## [2.0.1] - 2025-02-03
### Changes
- OMPE-35909: Test fixes

## [2.0.0] - 2025-01-17
### Changes
- OMPE-34006: Bump major version after removal of deprecated APIs

## [1.5.19] - 2025-01-14
### Changes
- OMREQ-1786: Removed absolute paths from cache file

## [1.5.18] - 2024-12-30
### Changes
- OMPE-31517: Remove deprecated APIs from omni.kit.material.library

## [1.5.17] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [1.5.16] - 2024-12-16
### Changed
- OMPE-28754 - Update call to CreateShaderPrimFromSdrCommand in CreateAndBindMtlxSurfaceFromLibrary to include passing of the node_type - mtlx.

## [1.5.15] - 2024-11-27
### Changes
- Fixed duplicate OmniPBR materials

## [1.5.14] - 2024-11-22
### Changes
- Fixed "Create Material" window leak
- Added MaterialLibraryTestHelper.DialogError when UI don't build correctly so test can retry

## [1.5.13] - 2024-11-14
### Changes
- OMPE-28542: Fixed issue with registering actions multiple times
- add_to_mtl_lib/remove_from_mtl_lib has is_private flag to prefix action names with "_", hiding them from actions_api.md
- get_mdl_lib_paths/get_mdl_list_async has optional get_private flag, which adds is_private info to returned list

## [1.5.12] - 2024-10-30
### Changes
- OMPE-26832: Fix for bind_material_to_prims_dialog getting called before extension has fully initialized
- Downgraded wait_stage_loading from error to warning

## [1.5.11] - 2024-09-10
### Changes
OMPE-21217: Make MaterialX via omni.materialx.libs optional

## [1.5.10] - 2024-09-25
### Changes
- Updated API and __all__ exports

## [1.5.9] - 2024-09-20
### Removed
- OMPE-22158: Remove MDL Distilling setting.

## [1.5.8] - 2024-08-29
### Changed
- OMPE-20059: Add dependency to omni.ui

## [1.5.7] - 2024-08-13
### Changed
- OMPE-8922: Update icon of menu item in Content context menu

## [1.5.6] - 2024-07-30
### Changed
- OMPE-16450: Don't add bad mdl to cache

## [1.5.5] - 2024-07-16
### Changed
- OMPE-14781: Made omni.kit.context_menu optional
- Made omni.kit.menu.utils optional
- Made omni.kit.notification_manager optional
- Make omni.kit.window.file_importer optional

## [1.5.4] - 2024-07-11
### Fixed
- OMPE-14517: updated `_reload_material_subids()` so it clear/sets material_ready_state. This forces `get_mdl_list_async()` to wait until new material info has been read.

## [1.5.3] - 2024-07-02
### Added
- OMPE-14014: Added MaterialX stage context menu "OpenPBR" and "Standard Surface"
- Added command tests for CreateAndBindMtlxSurfaceFromLibrary, CreateAndBindPreviewSurfaceFromLibrary and CreateAndBindPreviewSurfaceTextureFromLibrary

### Changed
- Changed context menu label `Add MaterialX File` to `Add MaterialX Reference`
- Renamed `MaterialLibraryExtension._on_create_custom_material()` to `MaterialLibraryExtension._on_create_custom_mdl_material()`

## [1.5.2] - 2024-06-06
### Fixed
- OMPE-10780: Create preferences UI for MaterialX related settings.

## [1.5.1] - 2024-06-06
### Fixed
- OMPE-3852: Load MDL modules in a coroutine to not block the UI thread. Fixed processing of modules loaded at startup.

## [1.5.0] - 2024-06-06
### Fixed
- OM-118687: Remove UsdMaterialWatcher from Kit, add displayBaseShader preference

## [1.4.7] - 2024-06-05
### Updated
- Updated `get_mdl_list_async(get_mdl_list_async(use_hidden=False, wait_for_ready=True)` with new param `wait_for_ready`, which waits for app ready and json loaded when True. This prevents menu refresh during tests.

## [1.4.6] - 2024-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.4.5] - 2024-05-31
### Fixed
- OMPE-8816: "/app/hydra/material/renderContext" renamed to "/app/hydra/material/renderContexts" to avoid collisions with older user configs.

## [1.4.4] - 2024-05-28
### Fixed
- OMPE-3852: Load MDL modules in a coroutine to not block the UI thread.

## [1.4.3] - 2024-04-25
### Fixed
- OMPE-8265: Preferences/Material/renderContext updated to sortable list.

## [1.4.2] - 2024-04-25
### Fixed
- OM-122859: Fixed double slashes in file picker apply handler.

## [1.4.1] - 2024-04-12
### Fixed
- Fixed material.config.toml was not saved properly when custom paths are removed on UI.

## [1.4.0] - 2024-04-01
### Added
- Created documentation

## [1.3.57] - 2024-03-25
### Added
- added /exts/omni.kit.material.library/ui_show_list for filtering Create list.
-  defaults to []
-  "ui_show_list" when set, the UI "Create" material menus will only list materials listed. EG. ["OmniPBR*", "OmniSurface*"]
-  This uses fnmatch, so wild-cards can be used.
- added /exts/omni.kit.material.library/show_ui_groups which can show/hide material groups in "Create" material menus.

## [1.3.56] - 2024-03-14
### Fixed
- Add missing omni.kit.context_menu dependency

## [1.3.55] - 2024-02-13
### Added
- Added function `add_usd_source_asset_path_to_mtl_lib` to register an individual material to the create material menu and the context menu
- Added function `remove_usd_source_asset_path_from_mtl_lib` to unregister and remove the entries from the menus again

## [1.3.54] - 2024-02-05
### Added
- Moved RenderingPreferences from omni.kit.window.preferences into here as they are all material based settings

## [1.3.53] - 2023-12-18
### Added
- Added function `get_config_from_carb_settings()`

## [1.3.52] - 2023-12-18
### Changed
- Updated to use fabric adapter

## [1.3.51] - 2023-11-30
### Added
- Material binding purpose support
- Custom filtering as a parameter to `get_materials_from_stage` and `get_materials_from_stage_async`
- Custom filtering for UsdBindingAttributeWidget

## [1.3.50] - 2023-11-27
### Fixed
- Fixed custom material path browser does not select directory

## [1.3.49] - 2023-10-04
### Changes
- Updated to use omni.kit.window.file_importer
- Changed invalid config file in `save_config_file()`

## [1.3.48] - 2023-09-20
### Fixed
- Fixed the issue of material config custom search paths being out of sync in some cases

## [1.3.47] - 2023-09-13
### Added
- Material combobox style update to more closely match real ui.ComboBox's

## [1.3.46] - 2023-09-12
### Added
- Fixed remove_materials_from_stage_filter_func

## [1.3.45] - 2023-09-07
### Added
- Added functions `add_to_mtl_lib` and `remove_from_mtl_lib` for easier method of adding/removing material library paths

## [1.3.44] - 2023-09-01
### Added
- Added `Add MaterialX File` context menu

## [1.3.43] - 2023-08-29
### Changed
- Material "None" doesn't have "X" button to clear

## [1.3.42] - 2023-08-31
### Changed
- `get_subidentifier_from_mdl` only show sublist errors when show_alert is True

## [1.3.41] - 2023-08-16
### Changed
- build_ui_popup has "missing" parameter, default is False
- When "missing" is True, material name is shown in red

## [1.3.40] - 2023-07-28
### Added
- Added tests for material write back when non-anon sublayer is insert into session layer.

## [1.3.39] - 2023-07-20
### Changes
- Add "/app/distill_and_bake/baking_to_new_material" global settings for distill_and_bake extension

## [1.3.38] - 2023-07-17
### Changes
- Populate shader prims first before watching fro prim cache changes.

## [1.3.37] - 2023-06-29
### Changes
- Added test for shader input writeback.

## [1.3.36] - 2023-06-21
### Changes
- Added context menu widget for material drag and drop

## [1.3.35] - 2023-06-21
### Added
- Fix for material_dialogs error during tests

## [1.3.34] - 2023-06-12
### Added
- Added test to populate MDL parameters from default and secondary USD context.

## [1.3.33] - 2023-05-25
### Changes
- Prevent `add_material_list_item` from calling material_list_refresh too early and logging "mdl_list_cache is not complete" warning
- Prevent MaterialExtensions from calling 'get_material_list' too early and logging "mdl_list_cache is not complete" warning

## [1.3.32] - 2023-06-02
### Changes
- exts/omni.kit.material.library/lib_paths works with omni.client paths

## [1.3.31] - 2023-05-04
### Changes
- Preload base materials when app ready

## [1.3.30] - 2023-05-04
### Changes
- Add global settings for distill_and_bake extension

## [1.3.29] - 2023-04-24
### Changes
- OM-91518: Fix the test failed by remove the slash of ComboBox widget identifier

## [1.3.28] - 2023-03-21
### Changes
- Added on_created_fn parameter to CreateAndBindMdlMaterialFromLibrary command. Called when material is full created

## [1.3.27] - 2022-12-19
### Changes
- added context menu material support

## [1.3.25] - 2023-02-16
### Changes
- Support material enums using display_name

## [1.3.24] - 2023-02-01
### Changes
- Added app info to material cache version

## [1.3.23] - 2023-05-06
### Changes
- Fix test when searchfield is visible

## [1.3.22] - 2023-01-17
### Changes
- Update test with content browser to use content browser helper

## [1.3.21] - 2022-11-10
### Changes
- Read base materials on 1st run & store info in cache

## [1.3.20] - 2022-10-17
### Changes
- Fixed `on_selected_mdl` to add slash after directory

## [1.3.19] - 2022-09-13
### Changes
- Fixed action descriptions

## [1.3.18] - 2022-08-24
- OM-58169 Material Dropdown Prim

## [1.3.18] - 2022-09-21
- Fixed create material with mesh selected

## [1.3.17] - 2022-08-17
- Set persistent/app/stage/materialStrength default to "weakerThanDescendants"

## [1.3.16] - 2022-07-21
- Fixed actions for core material. Paths should be relative to material folder.

## [1.3.15] - 2022-06-22
- Fixed issue with material prims having filename name not material name

## [1.3.14] - 2022-07-01
- Added MaterialLibraryTestHelper to aid UI updates in unittests (ported from omni.kit.test_suite.helpers)

## [1.3.13] - 2022-06-08
- Updated menus to use actions

## [1.3.12] - 2022-05-23
- Support legacy and new Viewport API
- Add dependency on omni.kit.viewport.utility

## [1.3.11] - 2022-05-13
- Moved material search path to setting "/exts/omni.kit.material.library/lib_paths"
- Updates subid list and create menu when "/exts/omni.kit.material.library/lib_paths" changes

## [1.3.10] - 2022-05-06
-  Updated searchwidget to cleanup UI problems

## [1.3.9] - 2022-04-20
-  Delay `preload_base_material_subids` to prevent startup time hogging

## [1.3.8] - 2022-02-22
-  Updated unittests to retrieve the treeview widget from content browser.

## [1.3.7] - 2022-02-15
-  Added `multi_descendents_dialog`

## [1.3.6] - 2022-01-11
-  Updated UsdUVTexture attributes

## [1.3.5] - 2022-01-10
-  Fixed material creation issue

## [1.3.4] - 2022-01-05
-  Added material grouping to create menu

## [1.3.3] - 2021-12-02
### Changes
- Fixed browser leak and update with testing identifiers

## [1.3.2] - 2021-11-29
### Changes
- Fix for potential empty selection in listbox widget

## [1.3.1] - 2021-11-22
### Changes
- Fix for add_material_list_refresh_callback triggering before create menu ready

## [1.3.0] - 2021-11-03
### Changes
- Updated to use rtx.neuraylib to get material subid
- Fixed changing "info:mdl:sourceAsset"

## [1.2.5] - 2021-11-04
### Changes
- Change "Custom MDL Material" to "Add MDL File"

## [1.2.4] - 2021-10-29
### Changes
- Added destroy_material_utils to release MaterialUtils and called on shutdown

## [1.2.3] - 2021-09-16
### Changes
- Added widget identifiers
- Prevented Sdf.Path warnings

## [1.2.2] - 2021-08-19
### Changes
- Added custom filtering to `get_materials_from_stage` with `add_materials_from_stage_filter_func`/`remove_materials_from_stage_filter_func`

## [1.2.1] - 2021-08-11
### Changes
- Added relative path support to `custom_material_dialog`

## [1.2.0] - 2021-06-30
### Changes
- Added `MaterialUtils`, `MaterialListBoxWidget`, `SearchWidget`, `ThumbnailLoader`, `MaterialListModel` & `MaterialListDelegate`
- For creation of async Treeview with searchbar and material caching

## [1.1.3] - 2021-06-16
### Changes
- Materials with multiple subitems are tagged in `get_mdl_list()`
- Tagged multiple items materials appear in create submenu

## [1.1.2] - 2021-06-16
### Changes
- Create material menu doesn't use full path for .mdl

## [1.1.1] - 2021-05-05
### Changes
- Removing MDL schema from the Rendering menu.

## [1.1.0] - 2021-04-29
### Changes
- Added sub-material selector for multi-materials

## [1.0.4] - 2021-03-12
### Changes
- Added get_material_filename_from_prim

## [1.0.3] - 2020-11-25
### Changes
- Added create_mdl_material function to load & create material from mdl file

## [1.0.2] - 2020-11-25
### Changes
- Added PreviewSurfaceTexture material

## [1.0.1] - 2020-11-19
### Changes
- Added select material after created

## [1.0.0] - 2020-10-30
### Changes
- created (converted from omni.kit.builtin.material_library)
  - adds Create material menu
  - adds functions bind_material_to_selected_prims, get_material_prim_path, get_material_list
  - adds commands CreateAndBindMdlMaterialFromLibrary, CreateAndBindPreviewSurfaceFromLibrary
- added hinting
