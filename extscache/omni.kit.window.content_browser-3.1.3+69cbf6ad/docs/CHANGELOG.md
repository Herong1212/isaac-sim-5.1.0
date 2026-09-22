# Changelog

This document records all notable changes to the **omni.kit.window.content_browser** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [3.1.3] - 2025-05-09
### Fixed
- OMPE-45229: Need to set permission after shutil.copytree in OVC2

## [3.1.2] - 2025-04-30
### Fixed
- OMPE-45229： Fix test failures in OVC2
- Update tests to remove warnings that item not found

## [3.1.1] - 2025-04-07
### Fixed
- OMPE-28324: Fixed a leaked registered 'show window' function that leads to problems during Kit's normal shutdown.

## [3.1.0] - 2025-03-06
### Changed
- OMPE-38740: Export `ContentBrowserWidget` class for possible use in Isaac Asset Browser

## [3.0.0] - 2025-01-20
### Changed
- Bump the major version since deprecated public API was removed.

## [2.10.6] - 2024-12-16
### Fixed
- Error on shutdown introduced in 2.10.4

## [2.10.5] - 2024-12-16
### Changed
- OMPE-31532: Remove deprecated APIs from omni.kit.window.content_browser

## [2.10.4] - 2024-12-16
### Fixed
- OMPE-31771: Fix deprecated warning for ContentBrowser

## [2.10.3] - 2024-12-06
### Fixed
- OMPE-30931: None window fix

## [2.10.2] - 2024-10-17
### Changed
- OMPE-22603: Update public API for content browser.

## [2.10.1] - 2024-10-07
### Fixed
- OM-65585: delete folder in Content browser auto select and center it's parent.

## [2.10.0] - 2024-07-30
### Changed
- OMPE-8922: Update icon of context menu items

## [2.9.18] - 2024-07-18
### Fixed
- Fix for test helper doesn't focus on a tree view item.

## [2.9.17] - 2024-07-11
### Fixed
- Fix for test helper doesn't correctly select tree view items when they are out of focus.

## [2.9.16] - 2024-06-04
### Changed
- Updated documentation with AI agent.

## [2.9.15] - 2025-05-29
### Fixed
- Removed usage of omni.kit.ui

## [2.9.14] - 2024-05-29
### Changed
- OMPE-5051: Improve the drop function in test helper to improve test times.

## [2.9.13] - 2024-05-03
### Changed
- OM-124342: Disable detail panel by default.

## [2.9.12] - 2024-03-27
### Changed
- Make versioning and search_delegate optional dependencies.

## [2.9.11] - 2024-03-18
### Fixed
- OM-117552: Content browser startup warning fix.

## [2.9.10] - 2024-02-05
### Changed
- OM-118804: Fix Content browser test_multi_selection's flaky failed.

## [2.9.9] - 2023-12-6
### Changed
- OM-114639: Refactor Content browser code for registration of collections

## [2.9.8] - 2023-11-10
### Updated
- OM-113490: Updated to use omni.kit.menu.utils

## [2.9.7] - 2023-11-23
### Changed
- OM-114223: Add local context menu for local folder under my-computer.

## [2.9.7] - 2023-11-10
### Fixed
- OMFP-2928: Avoid copying parent folder to child folder.

## [2.9.6] - 2023-10-27
### Updated
- OMFP-2525: Show notification when download completed

## [2.9.5] - 2023-10-24
### Updated
- OMFP-2884: Add setting to control whether to show download menuitem in context menu.

## [2.9.4] - 2023-10-17
### Updated
- OMFP-1308: Increase Code Coverage of omni.kit.window.content_browser to 86%.

## [2.9.3] - 2023-09-11
### Updated
- Improve usage of content browser registry.

## [2.9.2] - 2023-09-08
### Updated
- Add hotkey F2 for rename
- Add hotkey ESC for clear clipboard
- Add warning when failed to Copy/Cut/Paste/Delete

## [2.9.1] - 2023-09-06
### Updated
- OM-104958: Fix typo in Cut description

## [2.9.0] - 2023-08-30
### Updated
- OM-104958: Add hotkey for Cut, Copy, Paste, Delete selection

## [2.8.1] - 2023-08-22
### Updated
- Add API to register context menu for checkpoints.

## [2.8.0] - 2023-08-09
### Updated
- Match new options button in file picker

## [2.7.14] - 2023-07-14
### Updated
- Filter popup menu width fix to 150

## [2.7.13] - 2023-06-29
### Updated
- fixes for drag_and_drop_tree_view when window needs to scroll

## [2.7.12] - 2023-06-28
### Added
- OM-54203: implement soft delete in content browser
- OM-77963: Make use of environment variable to disable check for soft-delete features in Content Browser
- OM-54464: add source url in moved/renamed item checkpoint

## [2.7.12] - 2023-06-26
### Updated
- OM-97996: Use new FilterButton

## [2.7.11] - 2023-06-23
### Updated
- Fix regression with apply button disabled when multiple items are selected.

## [2.7.10] - 2023-06-08
### Updated
- Fix regression to open stage with payloads disabled.

## [2.7.9] - 2023-05-30
### Updated
- OM-42020: Always recreate filter menu to make position right in external window.

## [2.7.8] - 2023-05-23
### Updated
- Added begin edit handler same as filepicker for tool bar

## [2.7.7] - 2023-05-22
### Fixed
- Fix flaky test for cut and paste

## [2.7.6] - 2023-05-16
### Fixed
- OM-94626: Improve the context menu item's show logic

## [2.7.5] - 2023-04-26
### Updated
- Moved clipboard tracker to FileBrowser
- Added cut context menu and updated paste behavior to work with both cut and copy

## [2.7.4] - 2023-04-21
### Updated
- Update external drop to use same code path for copy as interal drop
- Add test for external drag drop

## [2.7.3] - 2023-04-17
### Updated
- Update context menu order for copy/paste
- Paste context menu only shows up if clipboard is not empty

## [2.7.2] - 2023-04-11
### Updated
- Update context menu orders to match Navigator UX.

## [2.7.1] - 2023-04-03
### Updated
- Set timestamp widget to disable by default.

## [2.7.0] - 2023-03-27
### Updated
- Refactor to sub-class from FilePicker widget and minimize code drift.

## [2.6.25] - 2023-03-22
### Updated
- Refactor the context menu and the set of file operations.

## [2.6.24] - 2023-03-20
### Updated
- Fix unreliable unittest.

## [2.6.23] - 2023-03-20
### Added
- Added timestamp.

## [2.6.22] - 2023-03-15
### Updated
- Added context menu for udim items.

## [2.6.21] - 2023-02-13
### Updated
- Improve flaky tests for rename, move and copy.

## [2.6.20] - 2023-03-08
### Updated
- Update bookmark edit/add dialog to match Navigator UX
- Update bookmark item context menu, should only show edit and delete for bookmarks

## [2.6.19] - 2023-03-07
### Updated
- Receive file opened events from file_utils.

## [2.6.18] - 2023-02-06
### Updated
- Update where SearchField is imported from.

## [2.6.17] - 2023-02-03
### Updated
- List checkpoints to update checkpoint list upon checkpoint created.

## [2.6.16] - 2023-02-01
### Updated
- Changed test to look for local file rather than nucleus path.

## [2.6.15] - 2023-01-31
### Updated
- Update TestDownload.test_no_selection to be able to run in random test order.

## [2.6.14] - 2023-01-17
### Updated
- Added UDIM support

## [2.6.13] - 2023-01-20
### Updated
- Update download default directory, use resolved user downloads folder directory

## [2.6.12] - 2023-01-18
### Updated
- Change default view to list view
- Record the last browsed directory, and navigate to that upon open

## [2.6.11] - 2023-01-17
### Updated
- Removed restriction on moving/copying files between servers.
- Added UDIM support

## [2.6.10] - 2023-01-11
### Updated
- Adds dependency on new file_utils module.

## [2.6.9] - 2023-01-11
### Fixed
- Removed minor warning when deleting bookmarks.

## [2.6.8] - 2023-01-06
### Updated
- Use CollectionContextMenu for collection nodes
- Match context menu options for collection nodes to Navigator

## [2.6.7] - 2023-01-03
### Updated
- Skipping 2 tests that cannot be run in random order.

## [2.6.6] - 2022-12-07
### Updated
- Add callback for toggling grid view and changing grid view scale, record grid view settings.

## [2.6.5] - 2022-11-29
### Updated
- Rename/delete/create/paste context menu will not show for read-only context item.

## [2.6.4] - 2022-11-17
### Updated
- Switch out pyperclip with linux-friendly copy & paste

## [2.6.3] - 2022-11-15
### Updated
- Updated the docs.

## [2.6.1] - 2022-11-09
### Updated
- Auto-connects user specified server at startup

## [2.6.0] - 2022-11-08
### Updated
- Added rename/move features to content browser, UX is similar to Navigator.

## [2.5.8] - 2022-11-07
### Updated
- Add option to overwrite downloading a single file/folder using user input, and pre-populate filename
- Downloading with multi-selection will disable filename field input
- Added tests for download

## [2.5.7] - 2022-11-03
### Fixed
- Restores 'mounted_servers' setting for specifying default server connections.

## [2.5.5] - 2022-11-01
### Updated
- Persist customizations when window is closed and re-opened.

## [2.5.4] - 2022-10-27
### Updated
- When opening a stage, auto-connect to nucleus.

## [2.5.3] - 2022-10-24
### Updated
- Decouple USD from extension.

## [2.5.2] - 2022-09-28
### Updated
- Use omni.client instead of carb.settings to store bookmarks.

## [2.5.1] - 2022-09-20
### Updated
- Change menu refresh to use interal async for not block ui.

## [2.5.0] - 2022-08-30
### Fixed
- Refactored thumbnails provider

## [2.4.33] - 2022-07-27
### Fixed
- Fixed the window when changing layout (OM-48414)

## [2.4.32] - 2022-07-26
### Added
- Don't invadvertently try to open directories as USD files during navigation
- Strip spaces around Url
- Adds unittests for test helper

## [2.4.31] - 2022-07-19
### Added
- Fixes placement of filter menu

## [2.4.30] - 2022-07-13
### Added
- Added test helper.

## [2.4.29] - 2022-07-08
### Fixed
- the issue of 'ContentBrowserExtension' object has no attribute '_window' while calling `shutdown_extensions` function of omni.kit.window.content_browser

## [2.4.28] - 2022-05-11
### Added
- Prevents copying files from one server to another, which currently crashes the app.

## [2.4.27] - 2022-05-03
### Added
- Adds api to retrieve the checkpoint widget.
- Adds async option to navigate_to function.

## [2.4.24] - 2022-04-26
### Added
- Restores open with payloads disabled to context menus.

## [2.4.23] - 2022-04-18
### Added
- Limits extent that splitter can be dragged, to prevent breaking.

## [2.4.22] - 2022-04-12
### Added
- Adds splitter to adjust width of detail pane.

## [2.4.21] - 2022-04-11
### Fixed
- Empty window when changing layout (OM-48414)

## [2.4.20] - 2022-04-06
### Added
- Disable unittests from loading at startup.

## [2.4.19] - 2022-04-04
### Updated
- Removed "show real path" option.

## [2.4.18] - 2022-03-31
### Updated
- Removed "Open with payloads disabled" from context menu in widget.

## [2.4.17] - 2022-03-18
### Updated
- Updates search results when directory changed.

## [2.4.16] - 2022-03-18
### Fixed
- `add_import_menu` is permanent and the Import menu is not destroyed when the
  window is closed

## [2.4.15] - 2022-03-14
### Updated
- Refactored asset type handling

## [2.4.13] - 2022-03-08
### Updated
- Sends external drag drop to search delegate

## [2.4.12] - 2022-02-15
### Updated
- Adds custom search delegate

## [2.4.11] - 2022-01-20
### Updated
- Adds setting to customize what collections are shown

## [2.4.10] - 2021-11-22
### Updated
- Simplified code for building checkpoint widget.

## [2.4.9] - 2021-11-16
### Updated
- Ported search box to filepicker and refactored the tool bar into a shared component.

## [2.4.8] - 2021-09-17
### Updated
- Added widget identifers

## [2.4.7] - 2021-08-13
### Updated
- Added "Open With Payloads Disabled" to checkpoint menu

## [2.4.6] - 2021-08-12
### Updated
- Fixed the "copy URL/description" functions for checkpoints.

## [2.4.5] - 2021-08-09
### Updated
- Smoother update of thumbnails while populating a search filter.

## [2.4.4] - 2021-07-20
### Updated
- Disables "restore checkpoint" action menu for head version

## [2.4.3] - 2021-07-20
### Updated
- Fixes checkoint selection

## [2.4.2] - 2021-07-12
### Updated
- Starts up in tree view if "show_grid_view" setting is set to false.

## [2.4.1] - 2021-07-12
### Updated
- Moved checkpoints panel to new detail view

## [2.3.7] - 2021-06-25
### Updated
- Enabled persistent pane settings

## [2.3.6] - 2021-06-24
### Updated
- Pass open_file to `FilePickerView`
- `get_file_open_handler` ignore checkpoint

## [2.3.5] - 2021-06-21
### Updated
- Update the directory path from either tree or list view.

## [2.3.4] - 2021-06-10
### Updated
- Menu options are persistent

## [2.3.3] - 2021-06-08
### Updated
- When "show checkpoints" unchecked, the panel is hidden and remains so.

## [2.3.2] - 2021-06-07
### Updated
- Added splitter bar for resizing checkpoints panel.
- Refactored checkpoints panel and zoom bar into FilePickerView widget.
- More thorough destruction of class instances upon shutdown.

## [2.3.1] - 2021-05-18
### Updated
- Eliminates manually initiated refresh of the UI when creating new folder, deleting items, and
copying items; these conflict with auto refresh.

### [2.2.2] - 2021-04-09
### Changes
- Added drag/drop support from outside kit

## [2.2.1] - 2021-04-09
### Changed
- Show <head> entry in versioning pane.

## [2.2.0] - 2021-03-19
### Added
- Supported drag and drop from versioning pane.

## [2.1.3] - 2021-02-16
### Updated
- Fixes thumbnails for search model.

## [2.1.2] - 2021-02-10
### Changes
- Updated StyleUI handling

## [2.1.1] - 2021-02-09
### Updated
- Fixed navigation slowness caused by processing of thumbnails.
- Uses auto thumbnails generated by deeptag if manual thumbnails not available.

## [2.1.0] - 2021-02-04
### Added
- Added `subscribe_selection_changed` to extension interface.
- Added optional versioning pane on supported server (only when omni.kit.widget.versioning is enabled).

## [2.0.0] - 2021-01-03
### Updated
- Refactored for async directory listing to improve overall stability in case of network delays.

## [1.8.10] - 2020-12-10
### Updated
- UI speedup: Opens file concurrently with navigating to path.

## [1.8.9] - 2020-12-5
### Updated
- Adds 'reconnect server' action to context menu

## [1.8.8] - 2020-12-03
### Updated
- Adds ability to rename connections and bookmarks

## [1.8.7] - 2020-12-01
### Updated
- Renamed to just "Content".
- Applies visibility filter to search results.

## [1.8.6] - 2020-11-26
### Updated
- Defaults browser bar to display real path

## [1.8.5] - 2020-11-25
### Updated
- Adds file_open set of APIs to open files with user specified apps.
- Pasting a URL into browser bar opens the file.

## [1.8.4] - 2020-11-23
### Updated
- Allows multi-selection copies.

## [1.8.3] - 2020-11-20
### Updated
- Allows multi-selection deletion.
- Updates and scrolls to download folder upon downloading files.

## [1.8.2] - 2020-11-19
### Updated
- Allows multi-selection downloads.

## [1.8.1] - 2020-11-06
### Added
- Keep connections and bookmarks between content browser and filepicker in sync.

## [1.8.0] - 2020-10-31
### Added
- Now able to resolve URL paths pasted into the browser bar

## [1.7.1] - 2020-10-30
### Fixed
- Fix reference leak when shutting down content browser

## [1.7.0] - 2020-10-29
### Added
- API methods to add menu items to the import button
- User folders to "my-computer" collection
- Refactored Options Menu into generic popup_dialog window
- Fixed opening of USD files and updated to use the open_stage function from omni.kit.window.file

## [1.6.0] - 2020-10-27
### Added
- Ported context menu to omni.kit.window.filepicker.
- Consolidated API methods into api module.

## [1.0.0] - 2020-10-14
### Added
- Initial commit for internal release.
