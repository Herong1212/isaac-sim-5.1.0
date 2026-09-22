# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.8.6] - 2025-04-24
### Changed
- OMPE-45205: Switch test renderer to rtx

## [1.8.5] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [1.8.4] - 2024-12-02
### Changes
- OMPE-5163: Remove references to omni.kit.window.viewport

## [1.8.3] - 2024-09-25
### Changes
- Updated API and __all__ exports

## [1.8.2] - 2024-08-13
### Fixed
- Update golden image for changes in omni.kit.widget.context_menu

## [1.8.1] - 2024-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.8.0] - 2024-03-20
### Changed
- Update documentation
- Removed color_tick_enabled & color_tick_disabled settings from toml as they are not used

## [1.7.5] - 2024-03-18
### Changed
- Handle omni.kit.material.library not found and hide "Assign Material"

## [1.7.4] - 2024-03-01
### Changed
- Moved add_menu, get_menu_dict, get_menu_event_stream, ContextMenuEventType into omni.kit.widget.context_menu

## [1.7.3] - 2024-02-07
### Changed
- Removed omni.kit.menu.create dependency

## [1.7.2] - 2023-11-29
### Changed
- Updated ViewportMenuDelegate so it can use new omni.kit.menu.core

## [1.7.1] - 2023-12-05
### Fixed
- Removed duplicate methods in ContextMenuExtension.

## [1.7.0] - 2023-11-15
### Changed
- Split the core functionality into a new extension `omni.kit.widget.context_menu`.
- Move custom menu dict into a new file.

## [1.6.9] - 2023-11-06
### Added
- Added `name` property for context menu to access current opened context menu name.

## [1.6.8] - 2023-11-06
### Fixed
- Fixed action execution may have invalid parameters.

## [1.6.7] - 2023-10-13
### Changes
- close_menu also clears clipboard
- viewport has hidden clear clipboard

## [1.6.6] - 2023-08-21
### Changes
- Option to hide Create UI items using;
-   /app/primCreation/hideShapes or /app/primCreation/enableMenuShape
-   /app/primCreation/enableMenuLight
-   /app/primCreation/enableMenuAudio
-   /app/primCreation/enableMenuCamera
-   /app/primCreation/enableMenuScope
-   /app/primCreation/enableMenuXform

## [1.6.5] - 2023-09-20
### Changes
- Fixed Separator not showing after async functions
- Added `get_context_menu()` function

## [1.6.4] - 2023-08-02
### Changes
- Added `close_menu()` function to close any open menus

## [1.6.3] - 2023-08-21
### Changes
- Use platform-agnostic omni.kit.clipboard instead of pyperclip

## [1.6.2] - 2023-08-03
### Changes
- Handle exceptions better

## [1.6.1] - 2023-07-27
### Changes
- Adjust submenu arrow size/spacing

## [1.6.0] - 2023-06-14
### Changes
- Support icons/glyphs with paths

## [1.5.19] - 2023-06-12
### Changed
- Propogate all Excpetions from omni.kit.context_menu other than AttributeError or ImportError.

## [1.5.18] - 2023-05-25
### Changes
- fixed issue with dictionaries not merging sub-menus correctly (PrimPathWidget)

## [1.5.17] - 2023-04-20
### Changes
- context menu can be tearable or non-tearable via `delegate.get_parameters("tearable")`

## [1.5.16] - 2023-04-25
### Changes
- Added ungroup menu items.

## [1.5.15] - 2023-03-10
### Changes
- created cameras execute action set_camera_defaults

## [1.5.14] - 2023-02-07
- Removed omni.kit.material.library dependency

## [1.5.13] - 2023-02-13
### Changes
- "Assign Material" doesn't check for materials to avoid performance impact in large scenes
- Added "/exts/omni.kit.context_menu/show_assign_material" setting for disabling menu item

## [1.5.12] - 2023-02-13
- Added actions support to menus can display action hotkey binding

## [1.5.11] - 2023-01-27
- Fixed issue with separator followed by populate_fn automatically hiding separator as its was the last item

## [1.5.10] - 2022-12-09
- Make sure "Convert reference to payload" and "Convert payload to reference" non-destructive.
- Tests for converting payloads/references.

## [1.5.9] - 2022-11-29
### Changes
- Don't allow grouping of default prim

## [1.5.8] - 2022-11-28
-  Add copy and paste functions that can be used across all extensions.

## [1.5.7] - 2022-11-10
- Create/Materials changed to Create/Material

## [1.5.6] - 2022-11-17
-  Fix reference/payload reload to reload all dependencies.

## [1.5.5] - 2022-11-01
-  Allow prims to be created outside default prim
-  Hovered doesn't show in menu when "use_hovered" is false
-  Scope/Xform don't create children when clicked nowhere

## [1.5.4] - 2022-09-21
-  Add setting to hide Create/Add menu for View

## [1.5.3] - 2022-09-08
-  Select prims after creation.

## [1.5.2] - 2022-09-08
-  Updated prims create children when selected/hovered so objects require "use_hovered" to prevent unwanted context menus from being effected

## [1.5.1] - 2022-09-01
-  Allowed passing additional kwargs to MenuItem.
-  Updated style for radio mark.

## [1.5.0] - 2022-08-04
-  Updated context menu style to match the viewport 2 menu style

## [1.4.9] - 2022-08-12
-  Created prims create children when selected/hovered (if allowed type)

## [1.4.8] - 2022-08-07
-  Fix perf issue to delete large bunch of prims.

## [1.4.7] - 2022-07-28
-  Created prims Xform and Scope can create children when selected/hovered

## [1.4.6] - 2022-07-01
-  Updated unittests to use material.library test_helper

## [1.4.5] - 2022-05-04
-  Added `set_value` function to `ComboListModel` used by `bind_material_to_prims_dialog`

## [1.4.4] - 2022-05-02
-  Fixed bind_material_to_prim exception

## [1.4.3] - 2022-04-06
-  Integrate omni.kit.usd.layers to replace old layers interfaces from omni.usd.

## [1.4.2] - 2022-04-01
-  Added `usd_context_name` to `ViewportMenu` object.

## [1.4.1] - 2022-02-15
-  Made create mesh/shape position undo/redoable

## [1.4.0] - 2022-02-15
-  Added explicit `MenuSubscription.release` function to release subscription.

## [1.3.7] - 2022-01-31
-  Absorb code from viewport_legacy's context menu creation and showing.

## [1.3.6] - 2022-01-05
-  Added material grouping to create menu

## [1.3.5] - 2021-11-15
-  Updated to use new omni.kit.material.library `get_subidentifier_from_mdl`

## [1.3.4] - 2021-11-12
-  Fixed bug preventing custom menus with multiple spacers
-  omni.kit.context_menu.add_menu now supports list of dictionaries

## [1.3.3] - 2021-08-11
-  Fixed leak

## [1.3.2] - 2021-07-26
-  Added "Refresh Payload" support
-  Added "Convert Payload to Reference" support
-  Added "Convert Reference to Payload" support

## [1.3.1] - 2021-07-21
-  Added "Refresh Reference" support

## [1.3.0] - 2021-06-30
-  Updated "Apply Material" dialog so it uses async population & search widget
-  Added "show_fn_async" an async show_fn for non-blocking show menu item logic

## [1.2.1] - 2021-06-17
-  Material create menu use submenu tag

## [1.2.0] - 2021-06-04
-  Added `checked_fn` to menu builder. If provided, the context menu can have a check mark when `checked_fn` returns True.
-  Added `min_menu_entries` parameter (default 0) to set the minimal number of menu entries required for menu to be visible.

## [1.1.3] - 2021-05-07
-  Fix when merging string menu items

## [1.1.2] - 2021-05-07
-  New icon for add menu

## [1.1.1] - 2021-04-29
-  Use sub-material selector on material import

## [1.1.0] - 2021-03-17
-   Added `omni.kit.context_menu.add_menu(menu, "MENU", "omni.kit.widget.stage")` so users can add context menus to specific extension menus without having to call that extension

## [1.0.7] - 2021-02-19
-   Added UI test

## [1.0.6] - 2021-02-03
-   Removed content_browser dependency
-   Updated find_in_browser to work with latest content_browser

## [1.0.5] - 2020-12-18
-   Use new locations for get_geometry_standard_prim_list, get_light_prim_list, get_audio_prim_list

## [1.0.4] - 2020-11-26
-   Added special handler for renaming active camera

## [1.0.3] - 2020-11-25
-   Added content window menu "Bind material to selected prim(s)"

## [1.0.2] - 2020-11-16
-   Updated Find In Browser

## [1.0.1] - 2020-10-05
-   Improved material list caching

## [1.0.0] - 2020-08-25
-   Added support for sub-menus

## [0.1.5] - 2020-06-21
-   Changes to prim grouping

## [0.1.4] - 2020-07-02
-   Changes to usd util path

## [0.1.3] - 2020-07-11
-   Changes to file browsing goto filenames

## [0.1.2] - 2020-08-04
-   Added bind material

## [0.1.1] - 2020-08-09
-   Changes to material binding strength

## [0.1.0] - 2020-04-23
-   Created
