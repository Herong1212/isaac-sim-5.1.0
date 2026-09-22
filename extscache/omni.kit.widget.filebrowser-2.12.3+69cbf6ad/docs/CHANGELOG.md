# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.12.3] - 2025-06-05
### Changed
- Fix for findthumbnail error when fetching search results.

## [2.12.2] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [2.12.1] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [2.12.0] - 2025-04-13
### Added
- Bump minor version since API changed.

## [2.11.1] - 2025-04-07
### Changed
- Able to sort item children by sort fields define in item
- Add new API populate_children_async to populate children easier

## [2.11.0] - 2025-03-06
### Changed
- OMPE-38740: Add public APIs: FileBrowserWidget.create_treeview_model, FileBrowserModel.create_root_item to customize the widget and model

## [2.10.52] - 2024-10-08
### Fixed
- OMPE-22588: Add '__all__' in init to explicit expose the public API.

## [2.10.51] - 2024-07-18
### Fixed
- OMPE-10272: Auto update Nucleus item when the file permissions changed.

## [2.10.50] - 2024-05-21
### Fixed
- OMPE-5500: Fix for File browser when double clicking on a folder throws Container::addChild warning.

## [2.10.49] - 2024-05-02
### Changed
- OM-123876: Handle more value types for treeview's column.

## [2.10.48] - 2024-03-21
### Changed
- OM-122340: Update API documentation.

## [2.10.47] - 2024-02-14
### Changed
- OMPRW-856: Verify drag/drop file is valid file

## [2.3.46] - 2024-01-05
- OM-115962: Fix for thumbnail warnings.

## [2.3.45] - 2023-12-07
### Changed
- OM-116452: Use `async_engine.run_coroutine` over running coroutine from saved event loop.

## [2.3.44] - 2023-12-06
### Changed
- OM-114639: Refactor Content browser code for registration of collections

## [2.3.43] - 2023-12-06
### Fixed
- Fix for event loop issue when calling function `populate_async`

## [2.3.42] - 2023-11-30
### Fixed
- OM-115872: Fix an issue while viewing a directory contains children that have no permission to visit.

## [2.3.41] - 2023-11-30
### Fixed
- OM-115384: Give view frame a name and identifier, then ui_test could find views by frame name.

## [2.3.40] - 2023-11-30
### Changed
- OM-114747: Use `async_engine.run_coroutine` over running coroutine from saved event loop.

## [2.3.39] - 2023-11-21
### Fixed
- OMFP-3551: Make refresh update Item changed when item permission changed,then it could trigger the ui update.

## [2.3.38] - 2023-10-16
### Fixed
- OMFP-2289: Increase test coverage to 85.1% and remove recycle widget relate code.

## [2.3.37] - 2023-08-18
### Fixed
- OM-104875: Don't show recycle widget.

## [2.3.36] - 2023-08-09
### Fixed
- OM-12985: Sort str by nature value.(For example: put 10.usd after 2.usd)

## [2.3.35] - 2023-08-08
### Fixed
- OM-103559: Fix Content browser doesn't list everything issue.

## [2.3.34] - 2023-06-28
### Fixed
- Add decorator and wrap file model item creation to handle exception, makes it more robust for cases where when listing
  a directory, if it contains child with illegal characters it won't fail the whole directory listing

## [2.3.33] - 2023-07-05
### Changed
- OM-100532: Fix error log when use recycle bin in content browser.

## [2.3.32] - 2023-06-28
### Added
- OM-54203: implement soft delete in content browser
- OM-77963: Make use of environment variable to disable check for soft-delete features in Content Browser
- OM-54464: add source url in moved/renamed item checkpoint

## [2.3.31] - 2023-05-26
### Fixed
- OM-35385: Fix the expand issue for left tree view

## [2.3.30] - 2023-05-23
### Fixed
- Hide list view stack when showing notification frame

## [2.3.29] - 2023-04-20
### Added
- Added NucleuseConnectionItem for describing connection item, with signed in status tracker
- Moved clipboard tracker from ContentBrowser to FileBrowser, add cut style for grid view / tree view items

## [2.3.28] - 2023-04-19
### Fixed
- OM-91073: check grid view's card paths to prevent build card more than once in sometimes

## [2.3.27] - 2023-04-04
### Updated
- Batch drop_fn calls if source item is FileBrowserItem, delay one frame then trigger drop_fn
- Added test for drop handler

## [2.3.26] - 2023-03-28
### Updated
- Add notification de-ref in browser widget destroy

## [2.3.25] - 2023-03-10
### Updated
- Removed deprecated functions from the base model
- Light re-organization of udim components

## [2.3.24] - 2023-03-02
### Updated
- Added a notification frame to list view stack
- Added method for hiding/showing notification frame

## [2.3.23] - 2023-03-01
### Added
- New layout LAYOUT_SINGLE_PANE_LIST to show list only
- New kwarg "enable_zoombar" to enable/disable zoombar. Default True.

## [2.3.22] - 2023-02-21
### Updated
- UDIM sequences can have thumbnails. Uses thumbnail for 1st image of the sequence

## [2.3.21] - 2023-02-15
### Updated
- Fixed issue with persisting selections between list view/grid view toggle when switch and scale
  happens within one frame
- Added listview selections on FileBrowserWidget for syncing up selections between the two views

## [2.3.20] - 2023-02-13
### Fixed
- Fixed grid zoom tests in random order

## [2.3.19] - 2023-01-27
### Fixed
- Fixed thumbnail and grid view tests

## [2.3.18] - 2023-01-27
### Fixed
- Fixed tests for random order testing

## [2.3.17] - 2023-01-17
### Updated
- Fixed issue with selections before cards created
- Fixed issue with NucleusItem calling `on_populated_async` with incorrect number of parameters

## [2.3.16] - 2023-01-20
### Updated
- Fix tests for ETM random order execution.

## [2.3.15] - 2023-01-13
### Updated
- Make item expandable & hideable attrs overridable on object instances.

## [2.3.14] - 2023-01-12
### Updated
- Add checkpoint information of src path in copied item's checkpoint

## [2.3.13] - 2023-01-11
### Updated
- Updated thumbnail interface to work better for the subclasses of the model.

## [2.3.12] - 2023-01-11
### Updated
- Add hideable and expandable class attribute to FileBrowserItem, tree view will use these flags to determine if the
  item can be hidden or expanded.

## [2.3.11] - 2023-01-09
### Updated
- Persist selections between grid view/list view toggle.
- Fix shift click issue when selection index is smaller than current index.

## [2.3.10] - 2023-01-03
### Updated
- Add the ability to center the selected item in grid view.

## [2.3.9] - 2022-11-08
### Updated
- Add callback for toggling grid view and changing grid view scale.

## [2.3.8] - 2022-11-30
### Updated
- OM-63433: Use content_clipping to speed up item display in file picker

## [2.3.7] - 2022-11-17
### Updated
- Fixes access flags for filesystem entries.

## [2.3.6] - 2022-10-21
### Updated
- Updated signature of copy_item_async to accept source and destination path, instead of always using
  the source relative path and destination root to compute the destination path.

## [2.3.5] - 2022-10-03
### Updated
- Commented out deprecation warnings.

## [2.3.4] - 2022-09-28
### Fixed
- Doc generation for date_format_menu.py

## [2.3.3] - 2022-09-21
### Updated
- Switching between different date formats.

## [2.3.2] - 2022-09-12
### Updated
- Updates cards in grid view on thumbnails generated.

## [2.3.1] - 2022-09-01
### Updated
- Unique identifier names for tree view and list view panes.

## [2.3.0] - 2022-08-30
### Updated
- Refactored thumbnails provider

## [2.2.31] - 2022-09-01
### Updated
- Unique identifier names for tree view and list view panes.

## [2.2.30] - 2022-07-19
### Updated
- Minor bug fix

## [2.2.29] - 2022-07-06
### Updated
- Fix regression to show context menu when right click on grid view.

## [2.2.28] - 2022-06-22
### Updated
- Multiple drag and drop support.

## [2.2.27] - 2022-05-26
### Updated
- Adds read-only badge to treeview items.
- Updated unit of file size to Mebibyte (instead of Megabyte)

## [2.2.25] - 2022-04-06
### Updated
- Fixes occasional startup error.

## [2.2.24] - 2022-02-18
### Updated
- Adds copy_presets method for FileBrowser models.

## [2.2.23] - 2022-02-15
### Updated
- Increases reconnect timeout to 10 mins.

## [2.2.22] - 2022-02-09
### Updated
- Fixes crash when browsing folders in grid view.

## [2.2.21] - 2022-01-20
### Updated
- Added `set_filter_fn` to the model class.

## [2.2.20] - 2022-01-05
### Updated
- Improved reconnection by skipping signout step, also increased timeout to 30 secs.

## [2.2.19] - 2021-11-24
### Updated
- Added `show_grid_view` to get grid or table view.

## [2.2.18] - 2021-11-16
### Updated
- Catches exception from tagging service that was crashing Kit.

## [2.2.17] - 2021-11-12
### Updated
- Fixes scaling of thumbnails.

## [2.2.16] - 2021-10-12
### Updated
- Notify on connection error.

## [2.2.15] - 2021-09-17
### Updated
- Added widget identifers

## [2.2.14] - 2021-09-07
### Updated
- Updated the reconnection to server flow.

## [2.2.13] - 2021-08-25
### Updated
- Fixes race condition that causes the table view to crash while auto-refreshing.

## [2.2.12] - 2021-08-12
### Updated
- Fixes multi-selection drag-n-drop from listview into viewport.

## [2.2.11] - 2021-08-09
### Updated
- Smoother update of thumbnails while populating a search filter.

## [2.2.10] - 2021-07-13
### Updated
- Moved zoom bar back from filepicker widget for better encapsulation.

## [2.2.9] - 2021-07-13
### Updated
- Update the directory path from either tree or list view.
  Fixes failure when opening a file under a nested directory in the right-pane when a hierarchial view.

## [2.2.8] - 2021-06-16
### Updated
- Syncs up folder upon entering but do so incrementally instead of re-creating it.
- Change above also fixes crashing when navigating to a folder, due to a race condition for populating that folder.

## [2.2.7] - 2021-06-10
### Updated
- Ignore omni.client.ListEvent.CREATED on existing directories

## [2.2.6] - 2021-06-07
### Updated
- More thorough destruction of class instances upon shutdown.

## [2.2.5] - 2021-06-04
### Updated
- Added overwrite dialog when copying files

## [2.2.4] - 2021-05-12
### Updated
- Eliminates too many concurrent redraws of the grid view causing it to crash.  This happens because
  manually initiated redraws conflict the new auto refresh.

## [2.2.3] - 2021-04-16
### Updated
- Double clicking on file icon in treeview opens it.
- Lock badge repositioned to not obstruct label.
- Small files show proper size instead of 0.00 Mb.

## [2.2.2] - 2021-04-15
### Updated
- Fixes auto refresh crash when copying large number of files, by limiting number of grid view redraws to
  at most once per frame.

## [2.2.1] - 2021-04-08
### Updated
- Auto refresh ignores update events, which breaks live sync mode.

## [2.2.0] - 2021-04-02
### Added
- Now auto refreshes current folder.

## [2.1.6] - 2021-03-25
### Updated
- Fixes thumbnail generator improperly skipped.

## [2.1.5] - 2021-02-16
### Updated
- Fixes thumbnails for search model.

## [2.1.4] - 2021-02-12
### Updated
- Fix for thumbnails not loading properly as part of the gather process.

## [2.1.3] - 2021-02-10
### Changes
- Updated StyleUI handling

## [2.1.2] - 2021-02-09
### Updated
- Added vertical spacing to the cards in grid view to accommodate larger font size.

## [2.1.1] - 2021-02-09
### Updated
- Fixed navigation slowness caused by processing of thumbnails.

## [2.1.0] - 2021-02-04
### Updated
- Extracted ZoomBar into its own widget and moved to omni.kit.window.filepicker extension.

## [2.0.1] - 2021-02-03
### Updated
- Refactored code for getting auto-generated thumbnails. The simplification allowed for easier testing.
- Fixed bug that was causing artifacts and mismatched thumbnails in grid view
### Added
- Unittests for navigating directories

## [2.0.0] - 2021-01-03
### Updated
- Implements omni.client.list_async to improve overall stability in case of network delays.

## [1.2.5] - 2020-12-10
### Updated
- Adds methods reconnect_url and stat_path_with_callback
- Removes method stat_path_async

## [1.2.4] - 2020-11-23
### Updated
- Fixes missing scroll bar in grid view.

## [1.2.3] - 2020-11-19
### Updated
- Supports multi-selection mouse press and double clicks.

## [1.2.2] - 2020-11-18
### Updated
- Updated to work with omni.client version 0.1.0
- Fixes: crash on double clicking in table view to open a folder.
- Fixes: cannot select item at bottom of table view.

## [1.2.1] - 2020-11-13
### Added
- Clear selections in list view whenever new directory is clicked.

## [1.2.0] - 2020-10-31
### Added
- Select and center in grid view.

## [1.1.0] - 2020-10-27
### Added
- Changed ui.Image to ui.ImageWithProvider almost everywhere in order to address UI lag.

## [0.2.5] - 2020-09-16
### Added
- Initial commit to master.
