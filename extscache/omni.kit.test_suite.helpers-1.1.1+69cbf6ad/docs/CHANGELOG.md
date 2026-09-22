# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.1] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.1.0] - 2025-03-10
### Changed
- Updated support level to sample.

## [1.0.13] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [1.0.12] - 2024-07-10
### Changes
- updated wait_stage_loading to use stage events

## [1.0.11] - 2024-07-02
### Changes
- updated get_random_material_list to exclude hidden materials

## [1.0.10] - 2024-05-23
### Changes
- added get_random_material_list

## [1.0.9] - 2023-11-27
### Changes
- added StageEventHandler to omni.kit.test_suite.helpers

## [1.0.8] - 2023-10-04
### Changes
- Increased delay in handle_multiple_descendents_dialog

## [1.0.7] - 2022-07-13
### Changes
- Marked content_browser functions for deprecation.

## [1.0.6] - 2022-07-11
### Changes
- Deprecated handle_save_dialog.  We want users to switch to file_exporter instead.

## [1.0.5] - 2022-07-01
### Changes
- Moved material library helpers to said extension. Marked functions for deprecation.

## [1.0.4] - 2022-05-23
### Changes
- Support legacy and new Viewport API
- Add dependency on omni.kit.viewport.utility

## [1.0.3] - 2022-05-03
### Changes
- Updated function `arrange_windows(topleft_window, topleft_height, topleft_width)`
- Handles no viewport correctly

## [1.0.2] - 2022-05-04
### Changes
- Refactored get_content_browser_path_item
- Added get_content_browser_treeview_item

## [1.0.1] - 2022-04-27
### Changes
- Small fix to handle_add_material_dialog

## [1.0.0] - 2021-10-01
### Changes
- Created
- Added function `get_test_data_path(module: str, subpath: str = "") -> str`
- Added function `wait_stage_loading(usd_context=omni.usd.get_context())`
- Added function `open_stage(path: str, usd_context=omni.usd.get_context())`
- Added function `select_prims(paths, usd_context=omni.usd.get_context())`
- Added function `set_content_browser_grid_view(grid_view_enabled: bool)`
- Added function `get_content_browser_path_item(path: str)`
- Added function `get_prims(stage, exclude_list=[])`
- Added function `wait_for_window(window_name: str)`
- Added function `handle_assign_material_dialog(index)`
- Added function `handle_create_material_dialog(mdl_path: str, mtl_name: str)`
- Added function `handle_add_material_dialog(mdl_path: str, mtl_name: str)`
- Added function `delete_prim_path_children(prim_path: str)`
- Added function `build_sdf_asset_frame_dictonary()`
- Added function `get_prim_viewport_position(prim_path: str)`
- Added function `push_window_height(cls, window_name, new_height=None)`
- Added function `pop_window_height(cls, window_name)`
- Added function `handle_multiple_descendents_dialog(stage, prim_path: str, target_prim: str)`
