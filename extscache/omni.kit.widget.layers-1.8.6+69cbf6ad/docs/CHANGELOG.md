# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.8.6] - 2025-04-25
### Fixed
- OMPE-42902: Fix issue accessing internal deprecated APIs.

## [1.8.5] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omniverse".

## [1.8.4] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.8.3] - 2024-01-09
### Changes
- OM-117869: Fix issue with regression on drag-n-drop to change layer hierarchy.

## [1.8.2] - 2024-11-06
### Fixed
- Fix test failure for test_remove_sublayers

## [1.8.1] - 2024-08-13
### Fixed
- OMPE-8922: Update icon of menu item in Content context menu

## [1.8.0] - 2024-06-05
### Fixed
- OM-118687: Removal of TestMaterialWatcher testing class due to the removal of the UsdMaterialWatcher from Kit.

## [1.7.9] - 2024-05-22
### Changed
- OMPE-5056: Decrease time for running unit-test.

## [1.7.8] - 2024-04-26
### Added
- OM-122341: Update docs.

## [1.7.7] - 2024-03-21
### Changed
- Remove deprecated tests as omni.usd.UsdContext.get_layers is removed.

## [1.7.6] - 2024-03-07
### Changed
- OMPRW-957: Replace self-built filepicker as omni.kit.window.file_importer/file_exporter to fix regressions.

## [1.7.5] - 2024-01-12
### Changed
- OM-120427: Changed search fields to be dependent on omni.kit.widget.searchfield.

## [1.7.4] - 2023-11-10
### Changes
- Updated to use omni.kit.menu.utils

## [1.7.3] - 2023-11-17
### Changes
- Fix flaky tests.

## [1.7.2] - 2023-11-13
### Changes
- Fix display of user widgets for live layer when sublayers are live session.

## [1.7.1] - 2023-08-09
### Changes
- In live mode, always show session layer

## [1.7.0] - 2023-08-09
### Changes
- New options button

## [1.6.30] - 2023-10-27
### Changes
- Fix issue that reloading outdate layer does not update sublayer list.

## [1.6.29] - 2023-10-18
### Changes
- Enable live session tests for more code coverage.

## [1.6.28] - 2023-10-09
### Changes
- Fix layer re-order.

## [1.6.27] - 2023-10-08
### Changes
- Add more tests to increase code coverage to be above 85%.

## [1.6.26] - 2023-07-13
### Changes
- Fixed expand/collapse tree menu items

## [1.6.25] - 2023-07-13
### Changes
- Improve layer event handling to only handle interested events.

## [1.6.24] - 2023-07-12
### Changes
- Move stronger overrides checking into omni.usd.

## [1.6.23] - 2023-07-04
### Changes
- Replace layer remove icon.

## [1.6.22] - 2023-06-29
### Changes
- Don't restore edit target from root when it opens stage with live session.

## [1.6.21] - 2023-06-14
### Changes
- Supports to remove multiple sublayers at the same time.

## [1.6.20] - 2023-06-02
### Changes
- Disable drag and drop layers during live session.

## [1.6.19] - 2023-05-23
### Changes
- Add settings to ignore outdate notifications.

## [1.6.18] - 2023-05-10
### Changes
- Use readable exts for USD instead of writable ones to support more exts.

## [1.6.17] - 2023-04-28
### Changes
- Added support for global reload setting to affect the rest of UI.

## [1.6.16] - 2023-04-25
### Changes
- Update "reload widget" to enable auto reloading per layer.
## [1.6.15] - 2023-04-11
### Changes
- Update "insert sublayer" context menu position after add_context_menu api change.

## [1.6.14] - 2023-03-14
### Changes
- Adds auto-reload support to reload outdated layers.

## [1.6.13] - 2023-01-26
### Changes
- Added quick join live session feature.

## [1.6.12] - 2022-01-14
### Changes
- Change user icon style of live user.

## [1.6.11] - 2023-01-13
### Changes
- Save edit target into root layer before in SETTINGS_SAVING only to avoid actively change root layer.

## [1.6.10] - 2022-12-14
### Changes
- Improve drag and drop style.

## [1.6.9] - 2022-11-22
### Changes
- Swap out pyperclip for linux-friendly copy & paste.

## [1.6.8] - 2022-11-14
### Changes
- Fix issue to search in layer window.

## [1.6.7] - 2022-11-07
### Changes
- Optimize more loading time to avoid populating layer item when it's to request children count.

## [1.6.6] - 2022-11-03
### Changes
- Fix empty menu issue, and improve context menu display.

## [1.6.5] - 2022-10-18
### Changes
- Fix hotkey registration warnings.

## [1.6.4] - 2022-10-12
### Changes
- More guardrails for live session.

## [1.6.2] - 2022-10-06
### Changes
- Add hotkey support for removing prim specs.

## [1.6.1] - 2022-10-05
### Changes
- Fix layer move regression.

## [1.6.0] - 2022-09-29
### Changes
- Add sublayer live session support.

## [1.5.36] - 2022-09-08
### Added
- Explicit hover style/color for drag drop.

## [1.5.35] - 2022-09-02
### Changes
- Supports to remove multiple layers.

## [1.5.34] - 2022-08-15
### Changes
- Add more tests for layer window to cover code of UI and context menu.

## [1.5.33] - 2022-08-09
### Changes
- Show correct outdate status for layer icon.

## [1.5.32] - 2022-08-09
### Changes
- Fix layer link window.

## [1.5.31] - 2022-07-25
### Changes
- Move outdate notifiction into omni.kit.usd.layers to not be dependent on layer view.

## [1.5.30] - 2022-07-25
### Changes
- Fix layer mute in global scope.

## [1.5.29] - 2022-07-25
### Changes
- Refactored unittests to make use of content_browser test helpers

## [1.5.28] - 2022-07-19
### Changes
- Disable save button when it's in a live session.

## [1.5.27] - 2022-07-14
### Changes
- Optimize performance to remove large bunch of prims.

## [1.5.26] - 2022-07-11
### Changes
- Fix stage treeview in layer linking window

## [1.5.25] - 2022-07-07
### Changes
- Supports to insert multiple sublayers.
- Fix regression for lock UI.

## [1.5.24] - 2022-07-04
### Changes
- Validate session name to support only alphanumeric letters, hyphens or underscores only.
- Use radio buttons instead of checkboxes for join/create session buttons.

## [1.5.23] - 2022-06-22
### Changes
- Multiple drag and drop support.

## [1.5.22] - 2022-06-15
### Changes
- Move session related widgets into omni.kit.widget.layers to decouple session management stuff with layers view.

## [1.5.21] - 2022-06-10
### Changes
- Use lazy loading to optimize performance of loading for layer window.

## [1.5.20] - 2022-06-09
### Changes
- Use notice to drive refresh of outdate states.

## [1.5.19] - 2022-06-02
### Changes
- Add new live workflow with Omni-Objects.

## [1.5.18] - 2022-04-22
### Changes
- Handle multi-file drag & drops

## [1.5.17] - 2022-04-19
### Changed
- Integrate omni.kit.usd.layers to replace old layers interfaces from omni.usd.

## [1.5.16] - 2022-04-15
### Fixed
- Avoid selection reset after a selected item is deleted and another is selected in the same update

## [1.5.15] - 2021-12-28
### Changed
- Fix save all button refresh.

## [1.5.14] - 2021-11-23
### Changed
- Add layer linking

## [1.5.13] - 2021-10-20
### Changed
- External drag/drop doesn't use windows slashes

## [1.5.12] - 2021-09-27
### Changed
- Improve prims remove in large stage.

## [1.5.11] - 2021-08-13
### Changed
- Added payload icon.

## [1.5.10] - 2021-08-25
### Fixes
- Add defensive check for ReplaceSublayerCommand.

## [1.5.9] - 2021-08-04
### Changed
- More unittests.

## [1.5.8] - 2021-08-03
### Changed
- Prompt to user before layers merge/flatten.

## [1.5.7] - 2021-07-29
-  Added "Refesh Payload" to context menu

## [1.5.6] - 2021-07-21
### Changed
- Use un-escaped filename for layer name.
- Replace "save as" menu as "save a copy" to avoid confuse, and "Save as and Replace" as "Save As"

## [1.5.5] - 2021-07-21
### Changed
- Added "Refesh Reference" to context menu

### [1.5.4] - 2021-07-22
### Fixes
- Fix layer insert when layer window is hidden.

### [1.5.3] - 2021-07-15
### Fixes
- Fixed `Select Bound Objects` in context menu

### [1.5.2] - 2021-07-02
### Fixes
- Fix sublayer refresh when it's switched from offine to live mode.

### [1.5.1] - 2021-04-19
### Changes
- Added drag/drop support from outside kit

## [1.5.0] - 2021-05-05
### Changes
- Add support for `Enter` and `Esc` buttons on prompts.

### [1.4.5] - 2021-05-05
### Changes
- Removed omni.kit.versioning
- Replaced omni.kit.versioning with omni.kit.widget.versioning for versioning support detection

### [1.4.4] - 2021-04-18
### Changes and Fixes
- Improve perf for multiple prim specs delete.
- Fix flicking of save icon in live mode.
- Fix layer move.
- Fix issue of disabling layer contents.

### [1.4.3] - 2021-04-09
### Changes
- Add support to find layer in content window.
- Don't allow to insert the sublayer if its parent already has the same layer.

### [1.4.2] - 2021-04-08
### Changes
- UI improvement.
- Fix possible exception caused by content refresh.

### [1.4.1] - 2021-04-06
### Changes
- Improve layer reload.
- Batch prim specs refresh to improve perf.

### [1.4.0] - 2021-04-05
### Changes
- Refactoring
- More tests and bug fixes.

### [1.2.0] - 2021-03-29
### Added
- Supported accepting drag and drop to insert versioned sublayer.

## [1.1.2] - 2021-03-25
### Changes
- Fixed `Save All` button to create checkpoint when applicable.

## [1.1.1] - 2021-03-17
### Changes
- Fixed leaks from content_browser

## [1.1.0] - 2021-02-10
### Changes
- Changed checkpoint comment message:
  - When using Save As to save an anonymous layer file and overwriting an existing file: "Replaced with new file"
  - When using Save As to save an existing layer file and overwriting an existing file: "Replaced with [the path of the file]"

## [1.0.2] - 2021-02-10
### Changes
- Updated StyleUI handling

## [1.0.1] - 2021-02-06
### Changed
- Remove old editor and content window dependencies.

## [1.0.0] - 2021-01-21
### Changed
- Initialize change log.
- Add context menu to insert USD as sublayer from content window.
