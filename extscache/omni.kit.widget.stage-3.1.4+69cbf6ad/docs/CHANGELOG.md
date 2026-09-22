# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [3.1.4] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [3.1.3] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [3.1.2] - 2025-04-02
### Changes
- OMPE-31619: Updated /app/stage/movePrimInPlace as its now int 0/1/2

## [3.1.1] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [3.1.0] - 2025-02-21
### Added
- OMPE-31959: Add support for renaming prims with unicode NFC normalization.

## [3.0.2] - 2025-01-13
### Changed
- OMPE-27796, OMPE-27800: Updated public API.

## [3.0.1] - 2025-01-23
### Added
- Updated missing `UsdStageHelper` public API.

## [3.0.0] - 2025-1-23
### Changes
- OMPE-31530: Remove deprecated APIs from omni.kit.widget.stage.

## [2.11.7] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters, update test with unicode data.
- OMPE-31902: Allow inputing unicode characters when renaming prims or dropping in to add payload/references.

## [2.11.6] - 2024-11-11
### Added
- OMPE-25213: Add show abstract prims to stage widget options, add support for filtering abstract prims.

## [2.11.5] - 2024-11-08
### Changed
- OMPE-22599: Update public API for stage widget.

## [2.11.4] - 2024-11-05
### Changed
- OMPE-26551: Add show inactive prims to stage widget options.

## [2.11.3] - 2024-10-11
### Changed
- OMPE-24958: Add UsdSkel.Skeleton and UsdSkel.Root in stage filters
- Removed OmniSkel schemas out of stage filters.

## [2.11.2] - 2024-08-20
### Fixed
- OMPE-19784: Additional check drop accepted to make sure drop could be handled by DragAndDropRegistry.

## [2.11.1] - 2024-08-20
### Changed
- OMPE-19203: New stage clears search string

## [2.11.0] - 2024-08-06
### Changed
- Make the treeview resizeable so that resizing columns can go beyond the app.
- Add horizontal scrollbar when the treeview is rezised to be wider.

## [2.10.31] - 2024-07-23
### Changed
- Fixed private class access (accessing functions/variables with _)

## [2.10.30] - 2024-07-26
### Fixed
- OMPE-15459: Add test for update_filter_menu_state.
- OMPE-16039: Fix the filter audio.
- OMPE-15720: Fix the options reset.

## [2.10.29] - 2024-07-12
### Changed
- Made Omni schema extensions optional dependencies

## [2.10.28] - 2024-07-11
### Fixed
- Fixed tests to not focus on treeview items during drag & drop.

## [2.10.27] - 2024-05-28
### Fixed
- Fixed error when clicking on "Root"

## [2.10.26] - 2024-05-30
### Fixed
- Defensive check for selection when selection is not set.

## [2.10.25] - 2024-05-23
### Changed
- Reduce test time.

## [2.10.24] - 2024-05-10
### Fixed
- Fix menu name of activation for multiple selections.

## [2.10.23] - 2024-05-09
### Fixed
- Update toggle_prims_active_state parameters for context menu

## [2.10.22] - 2024-05-07
### Fixed
- OM-87457: Fixed duplicated prims when exporting selected parent and child prims.

## [2.10.21] - 2024-04-25
### Fixed
- OM-122859: Fixed double slashes in file picker apply handler.

## [2.10.20] - 2024-04-22
### Added
- Fix issue of stage widget to support reactivating all selected stage items.

## [2.10.19] - 2024-03-26
### Added
- Added public API docs
- Delay stage icon folder calculating in styles

## [2.10.18] - 2024-03-25
### Changed
- OM-116179: Improve behavior to set visibilty for multi-selections.

## [2.10.17] - 2024-03-07
### Changed
- Make omni.kit.context_menu dependency optional

## [2.10.16] - 2024-03-06
### Changed
- OM-85989: Avoid applying rules of prim naming while renaming display name.
- Fix issues for unittest.

## [2.10.15] - 2024-02-21
### Changed
- OMPRW-856: Verify drag/drop file is valid file

## [2.10.14] - 2024-02-20
### Changed
- OM-120427: Changed search field to be dependent on omni.kit.widget.searchfield.

## [2.10.13] - 2024-02-19
### Changes
- Change an empty typename'd item to be interpreted as a class for icon resolution

## [2.10.12] - 2024-01-12
### Changed
- OMPM-836: Add settings for stage filters

## [2.10.11] - 2023-12-15
### Changed
- Fix search issue when filter text includes prim path with suffix slash.

## [2.10.10] - 2023-12-6
### Changed
- OM-114639: Refactor Content browser code for registration of collections

## [2.10.9] - 2023-11-08
### Fixed
- OMFP-3328: Fix undo for rename prim.

## [2.10.8] - 2023-10-18
### Changes
- Added `get_name_column_delegate` function

## [2.10.7] - 2023-09-26
### Changes
- Add overlay icons for prims with inherits and specializes arcs.

## [2.10.6] - 2023-09-21
### Changes
- OM-90363: Add support for exporting variants on prims and added test.

## [2.10.5] - 2023-09-21
### Fixed
- OM-108940: Show/hide 'Expand' and 'Collapse' menu item depending on the hovered primitive in stage widget.

## [2.10.4] - 2023-09-06
### Changes
- Improve get_drag_mime_data to return items from multiple selections.

## [2.10.3] - 2023-08-25
### Changes
- Added additional getters and setters to enable overrides capability for omni.kit.widget.stage_fabric

## [2.10.2] - 2023-08-22
### Fixed
- OM-97047: Prevent an invalid stage when a prim rename fails. UI item label is corrected on fail.

## [2.10.1] - 2023-08-18
### Changes
- Fix search issue when it searches with prim path.

## [2.10.0] - 2023-08-09
### Changes
- New options button with order columns work

## [2.9.7] - 2023-08-11
### Changes
- Fix regression that undoing delete command does not revert stage item back.

## [2.9.6] - 2023-08-01
### Changes
- Modified private function names and added getters and setters to enable overrides capability for omni.kit.widget.stage_fabric

## [2.9.5] - 2023-07-31
### Changes
- OM-76599: Show a load asset activity prompt window when drag and drop asset into stage window.

## [2.9.4] - 2023-07-31
### Changes
- Supports active/inactive workflow

## [2.9.3] - 2023-10-10
### Changes
- Add more tests to improve code coverage.

## [2.9.2] - 2023-07-24
### Changes
- Improve sorting inside stage widget to take consideration of order suffix.

## [2.9.1] - 2023-07-13
### Changes
- Improve layer events handling to only handle interested events.

## [2.9.0] - 2023-06-29
### Changes
- OM-97999: New filter button

## [2.8.3] - 2023-06-14
### Changes
- Fixed expand and collapse functions so all cases are handled gracefully.

## [2.8.2] - 2023-06-14
### Changes
- Make sure name label and renaming field cover the whole column.

## [2.8.1] - 2023-06-08
### Changes
- Don't show missing color when prim is loaded with payloads disabled.

## [2.8.0] - 2023-06-01
### Changes
- Refactoring codebase of StageWindow for more clear structure.
- Extend column delegate to support minimum width of column.
- Extend column delegate for easier column sort support.
- Extend StageModel to support new column sort API.
- Fix renaming issue in search mode.
- Match behavior of column resize to Windows File Explorer.

## [2.7.48] - 2023-05-19
### Changes
- OM-95462: Remove hotkey for Save Selected Prim

## [2.7.47] - 2023-05-10
### Changes
- Fix issue to show hash string for displayName.

## [2.7.46] - 2023-05-05
### Fixed
- Collapse ALL in the stage made everything disappear.

## [2.7.45] - 2023-04-28
### Changes
- Added support for global reload setting to affect the rest of UI.

## [2.7.44] - 2023-04-28
### Updated
- Auto reload per prim functionality now affects column widgets

## [2.7.43] - 2023-04-25
### Removed
- Attach/detach group items

## [2.7.42] - 2023-04-21
### Updated
- Don't include live layers inside payrefs list of stage item.

## [2.7.41] - 2023-04-14
### Updated
- Track outdate and live status for reference/payload prim.
- Tweaked UI to be more responsive
- Extracted stage widget CSS to an external file

## [2.7.40] - 2023-04-10
### Updated
- Add stage open sub on start up, update default save directory on export

## [2.7.39] - 2023-03-28
### Updated
- Add supports to re-order prims.
- Expose APIs to customize settings for stagewidget so it does not use global settings that influence all instances.

## [2.7.38] - 2023-03-17
### Added
- Changed hotkey binding for save_prim to SHIFT+CTRL+S

## [2.7.37] - 2023-03-27
### Added
- Expand/collapse context menus
- Set kind context menu
- Yes, this is the same as 2.7.31, but that version was reverted while the changelog wasn't

## [2.7.36] - 2023-02-07
### Updated
- Uppated as omni.kit.material.library is no longer loaded by omni.kit.context_menu

## [2.7.35] - 2023-03-22
### Added
- Emits File Saved event upon saving stage prim.

## [2.7.34] - 2023-03-17
### Added
- Adds auto-reload support to reload outdated prims.

## [2.7.33] - 2023-03-17
### Added
- Adds auto-reload support to reload outdated prims.

## [2.7.32] - 2023-03-16
### Added
- Fix stage filtering when new sublayer is inserted if search text is not empty.

## [2.7.31] - 2023-03-09
### Added
- Expand/collapse context menus
- Set kind context menu

## [2.7.34] - 2023-03-17
### Added
- Adds auto-reload support to reload outdated prims.

## [2.7.33] - 2023-03-17
### Added
- Adds auto-reload support to reload outdated prims.

## [2.7.32] - 2023-03-16
### Added
- Fix stage filtering when new sublayer is inserted if search text is not empty.

## [2.7.30] - 2023-02-13
### Added
- Context menu action with hotkey binding for save_prim

## [2.7.29] - 2023-03-08
### Fixed
- OM-82577: Drag&drop of flowusd presets will call flowusd command to add a reference.

## [2.7.28] - 2023-02-17
### Fixed
- Fix for opening context menu twice & doing double processing

## [2.7.26] - 2023-02-26
### Changed
- Replaced asyncio.ensure_future calls in stage_model.py and usd_property_watch.py with
  omni.kit.async_engine.run_coroutine function.

## [2.7.25] - 2023-02-16
### Fixed
- OM-81767: Drag&drop behaviour of sbsar files now consistent with viewport's behaviour.

## [2.7.24] - 2023-02-10
### Added
- OM-66949: Able to drag and drop from SimReady explorer to stage window

## [2.7.23] - 2023-02-02
### Updated
- Add filepath of saved prim selections to recent files.
- Use selected prim name as the default filename when exporting selected.

## [2.7.22] - 2023-01-11
### Updated
- Allow to select children under instance.
- Fix selection issue after clearing search text.
- Move SelectionWatch from omni.kit.window.stage to provide default implementation.

## [2.7.21] - 2022-12-9
### Updated
- Fixed issue where drag & drop material urls with encoded subidentifiers were not being handled.

## [2.7.20] - 2022-12-14
### Updated
- Improve drag and drop style.

## [2.7.19] - 2022-12-09
### Updated
- Improve filter and search.
- Fix issue that creates new prims will not be filtered when it's in filtering mode.
- Add support to search with prim path.

## [2.7.18] - 2022-12-08
### Updated
- Fix style of search results in stage window.

## [2.7.17] - 2022-11-29
### Updated
- Don't show context menu for converting references or payloads if they are not in the local layer stack.
- Don't show context menu for header of stage widget.

## [2.7.16] - 2022-11-15
### Updated
- Fixed issue with context menu & not hovering over label

## [2.7.15] - 2022-11-14
### Updated
- Supports sorting by name/visibility/type.

## [2.7.14] - 2022-11-14
### Updated
- Fix issue to search or filter stage window.

## [2.7.13] - 2022-11-07
### Updated
- Optimize more loading time to avoid populating tree item when it's to get children count.

## [2.7.12] - 2022-11-04
### Updated
- Refresh prim handle when it's resyced to avoid access staled prim.

## [2.7.11] - 2022-10-17
### Updated
- Don't use "use_hovered" for context menu objects when user click nowhere

## [2.7.10] - 2022-11-03
### Updated
- Support to show 'displayName' of prim from metadata.

## [2.7.9] - 2022-11-02
### Updated
- Drag and drop assets to default prim from content browser if default prim is existed.

## [2.7.8] - 2022-11-01
### Updated
- Fix rename issue.

## [2.7.7] - 2022-10-25
### Updated
- More optimization to stage window refresh without traversing.

## [2.7.6] - 2022-09-13
### Updated
- OM-44838: Enable drag and drop from environment window

## [2.7.5] - 2022-09-10
### Updated
- Add TreeView drop style to show hilighting.

## [2.7.4] - 2022-09-08
### Updated
- Added "use_hovered" to context menu objects so menu can create child prims

## [2.7.3] - 2022-08-30
### Fixed
- Moved eye icon to front of ZStack to receive mouse clicks.

## [2.7.2] - 2022-08-12
### Fixed
- Updated context menu behaviour

## [2.7.1] - 2022-08-13
- Fix prims filter.
- Clear prims filter after stage switching.

## [2.7.0] - 2022-08-06
- Refactoring stage model to improve perf and fix issue of refresh.

## [2.6.26] - 2022-08-04
-  Support multi-selection for toggling visibility

## [2.6.25] - 2022-08-02
### Fixed
- Show non-defined prims as well.

## [2.6.24] - 2022-07-28
### Fixed
- Fix regression to drag and drop prim to absolute root.

## [2.6.23] - 2022-07-28
### Fixed
- Ensure rename operation non-destructive.

## [2.6.23] - 2022-07-25
### Changes
- Refactored unittests to make use of content_browser test helpers

## [2.6.22] - 2022-07-18
### Fixed
- Restored the arguments of ExportPrimUSD

## [2.6.21] - 2022-07-05
- Replaced filepicker dialog with file exporter

## [2.6.20] - 2022-06-23
-  Make material paths relative if "/persistent/app/material/dragDropMaterialPath" is set to "relative"

## [2.6.19] - 2022-06-22
- Multiple drag and drop support.

## [2.6.18] - 2022-05-31
-  Changed "Export Selected" to "Save Selected"

## [2.6.17] - 2022-05-20
-  Support multi-selection for toggling visibility

## [2.6.16] - 2022-05-17
-  Support multi-file drag & drop

## [2.6.15] - 2022-04-28
-  Drag & Drop can create payload or reference based on /persistent/app/stage/dragDropImport setting

## [2.6.14] - 2022-03-09
-  Updated unittests to retrieve the treeview widget from content browser.

## [2.6.13] - 2022-03-07
-  Expand default prim

## [2.6.12] - 2022-02-09
-  Fix stage window refresh after sublayer is inserted/removed.

## [2.6.11] - 2022-01-26
-  Fix the columns item not able to reorder

## [2.6.10] - 2022-01-05
-  Support drag/drop from material browser

## [2.6.9] - 2021-11-03
-  Updated to use new omni.kit.material.library `get_subidentifier_from_mdl`

## [2.6.8] - 2021-09-24
- Fix export selected prims if it has external dependences outside of the copy prim tree.

## [2.6.7] - 2021-09-17
- Copy axis after export selected prims.

## [2.6.6] - 2021-08-11
-  Updated drag/drop material to no-prim to not bind to /World
-  Added drag/drop test

## [2.6.5] - 2021-08-11
-  Updated to lastest omni.kit.material.library

## [2.6.4] - 2021-07-26
-  Added "Refesh Payload" to context menu
-  Added Payload icon
-  Added "Convert Payloads to References" to context menu
-  Added "Convert References to Payloads" to context menu

## [2.6.3] - 2021-07-21
-  Added "Refesh Reference" to context menu

## [2.6.2] - 2021-06-30
-  Changed "Assign Material" to use async show function as it could be slow on large scenes

## [2.6.1] - 2021-06-02
-  Changed export prim as usd, postfix name now lowercase

## [2.6.0] - 2021-06-16
### Added
- "Show Missing Reference" that is off by default. When it's on, missing
  references are displayed with red color in the tree.
### Changed
- Indentation level. There is no offset on the left anymore.

## [2.5.0] - 2021-06-02
-  Added export prim as usd

## [2.4.2] - 2021-04-29
-  Use sub-material selector on material import

## [2.4.1] - 2021-04-09
### Fixed
- Context menu in extensions that are not omni.kit.window.stage

## [2.4.0] - 2021-03-19
### Added
- Supported accepting drag and drop to create versioned reference.

## [2.3.7] - 2021-03-17
### Changed
- Updated to new context_menu and how custom functions are added

## [2.3.6] - 2021-03-01
### Changed
- Additional check if the stage and prim are still valid

## [2.3.5] - 2021-02-23
### Added
- Exclusion list allows to hide prims of specific types silently. To hide the
  prims of specific type, set the string array setting
  `ext/omni.kit.widget.stage/exclusion/types`

  ```
    [settings]
    ext."omni.kit.widget.stage".exclusion.types = ["Mesh"]
  ```

## [2.3.4] - 2021-02-10
### Changes
- Updated StyleUI handling

## [2.3.3] - 2020-11-16
### Changed
- Updated Find In Browser

## [2.3.2] - 2020-11-13
### Changed
- Fixed disappearing the "eye" icon when searched objects are toggled off

## [2.3.1] - 2020-10-22
### Added
- An interface to add and remove the icons in the TreeView dependin on the prim type

### Removed
- The standard prim icons are moved to omni.kit.widget.stage_icons

## [2.3.0] - 2020-09-16
### Changed
- Split to two parts: omni.kit.widget.stage and omni.kit.window.stage

## [2.2.0] - 2020-09-15
### Changed - Detached from Editor and using UsdNotice for notifications
