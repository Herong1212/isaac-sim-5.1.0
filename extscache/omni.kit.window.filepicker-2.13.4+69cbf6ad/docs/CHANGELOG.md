# Changelog
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.13.4] - 2025-08-2
### Fixed
- OMPE-58033: Make sure test server not exist before adding

## [2.13.3] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [2.13.2] - 2025-04-29
### Changed
- OMPE-43083: Remove warnings if download from content browser.

## [2.13.1] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [2.13.0] - 2025-04-13
### Added
- Bump minor version since API changed.

## [2.12.2] - 2025-04-07
### Changed
- OMPE-38740: Add API register_collection_item/deregister_collection_item to register/deregister collection item to the file picker.
- Add "order" field for collections to control the display order of collections in the file picker.
- Find items by path instead of name because name may be different from path

## [2.12.1] - 2025-04-09
### Fixed
- OMPE-42787: Fix content browser sorting.

## [2.12.0] - 2025-03-06
### Changed
- Refactor for collections

## [2.11.8] - 2025-03-05
### Changed
- OMREQ-923: Only set the current directory for selection change in treeview pane.

## [2.11.7] - 2024-11-25
### Changed
- OMPE-22603: Expose ConnectionContextMenu to public API.

## [2.11.6] - 2024-11-05
### Changed
- OMPE-22606: Update public API.

## [2.11.5] - 2024-11-15
### Fixed
OMPE-28290: Fix the ui sometimes not refresh correct after delete

## [2.11.4] - 2024-11-12
### Fixed
OMPE-27824: make sure destroy filepicker after add server not trigger error

## [2.11.3] - 2024-10-23
### Fixed
- OMPE-25568: Fix enabling omni.kit.widget.extended_searchfield raises exception issue.

## [2.11.2] - 2024-10-07
### Fixed
- OM-65585: Delete folder in File Picker auto select and center it's parent.

## [2.11.1] - 2024-09-10
### Changed
- ISIM-1673: Change detail view's init/min/max width to settings.

## [2.11.0] - 2024-07-30
### Changed
- OMPE-8922: Update icon of context menu items

## [2.10.39] - 2024-07-17
### Changed
- OMPE-15119: Handled add new connection and None error

## [2.10.38] - 2024-07-12
### Changed
- OMPE-14560: catch error with drag drop in content window without search delegate

## [2.10.37] - 2024-06-18
### Changed
- OMPE-11887: Avoid calling navigate_to_async when current directory is "omniverse://" in a new dialog.

## [2.10.36] - 2024-05-24
### Changed
- OMPE-5058: Resolve some flaky test and improve test times of omni.kit.window.filepicker.

## [2.10.35] - 2024-05-20
### Changed
- OMPE-5058: Profile and Improve test times of omni.kit.window.filepicker.

## [2.10.34] - 2024-05-07
### Changed
- OM-120250: Replaced psutil imports with internal disk_partitions module.

## [2.10.33] - 2024-04-22
### Changed
- OM-122859: Ensure apply and cancel handler is passed with a directory path with an ending slash.

## [2.10.32] - 2024-03-19
### Changed
- Make versioning and search_delegate dependencies optional.

## [2.10.31] - 2024-03-27
### Changed
- OM-122350: Update docs.

## [2.10.30] - 2024-03-25
### Changed
- OM-117841: Temporarily revert the changes ENTER key-press to open file

## [2.10.29] - 2024-02-28
### Changed
- Remove dependency on dateutil and psutil

## [2.10.28] - 2024-01-08
### Changed
- OM-114855: Removed extra space in save as options dropdown.

## [2.10.27] - 2024-01-05
### Fixed
- OMFP-2569: Save server's login/logout status regardless of whether the item exists or not.

## [2.10.26] - 2024-01-05
### Changed
- OM-51243: Refresh drives only when there is new drive.

## [2.10.25] - 2023-12-14
### Changed
- OMFP-4028: Improve rename_server, make it not trigger delete_server.

## [2.10.24] - 2023-12-12
### Changed
- OM-116672: Revert OM-115594 in favor of OM-113503

## [2.10.23] - 2023-12-12
### Changed
- Fix new folder crash sometimes.

## [2.10.22] - 2023-12-6
### Changed
- OM-114639: Refactor Content browser code for registration of collections

## [2.10.21] - 2023-11-29
### Changed
- OM-115594: Use os mkdir to create folder under local point.

## [2.10.20] - 2023-11-28
### Changed
- OM-114747: Fix for test issues.

## [2.10.19] - 2023-11-28
### Changed
- OM-93605: Fix ETM failed caused by asyncio not import.

## [2.10.19] - 2023-11-23
### Changed
- OMFP-2948 & OM-114223: Remove New Folder from connection context menu, and add local context menu for local folder under my-computer, improve the rename operation.

## [2.10.18] - 2023-11-17
### Changed
- OM-114457: Changed dependency from omni.kit.context_menu to omni.kit.widget.context_menu.

## [2.10.17] - 2023-11-16
### Changed
- OMFP-3823: set the focus for the input filename field at the right time for FilePickerWidget

## [2.10.16] - 2023-11-14
### Fixed
- OMFP-3807: Update file info when server's file changed.

## [2.10.15] - 2023-11-10
### Fixed
- OMFP-3796: Fix Loading Spinner does not go away even when cancel is clicked issue.

## [2.10.14] - 2023-11-03
### Fixed
- OM-104306: Adding apply_path_handler to FilePickerWidget constructor.

## [2.10.13] - 2023-11-02
### Fixed
- OMFP-3205: More defensive coding to clear ownership.

## [2.10.12] - 2023-10-27
### Fixed
- OMPM-817: Filter out partitions reserved for Linux hugepages.

## [2.10.11] - 2023-10-27
### Fixed
- OMFP-2569: Keep consistent  of a same server's login/logout status between different file dialog.

## [2.10.10] - 2023-10-26
### Fixed
- OMFP-1307: Increased code coverage to 85%.
- Fixed an exception when when setting file bar postfix.

## [2.10.9] - 2023-10-24
### Fixed
- OMFP-2994: Use a setting to control whether show Add New Connection.

## [2.10.8] - 2023-10-19
### Fixed
- OMFP-3175: Fix for file picker text typos and alignment issues.

## [2.10.7] - 2023-10-19
### Fixed
- OMFP-2407: Use a setting value instead of defalut localhost connection.

## [2.10.6] - 2023-10-11
### Fixed
- OMFP-2152: Fix FilePicker RMB delete menu item doesn't show when FilePicker is in external window.

## [2.10.5] - 2023-10-11
### Fixed
- OMFP-649: Hide the loading icon when selection changed to make it clean and consistent.

## [2.10.4] - 2023-10-10
### Fixed
- OM-111583: In windows system use windll interface to get real user folder path.

## [2.10.3] - 2023-09-20
### Changed
- Fix for menu text in context menu not being aligned properly.

## [2.10.2] - 2023-08-21
### Changed
- Use platform-agnostic omni.kit.clipboard instead of pyperclip

## [2.10.1] - 2023-08-14
### Fixed
- OM-104350&OM-104870: Fix some menu item doesn't appear after right clicking inside content window.

## [2.10.0] - 2023-08-09
### Changed
- New options button

## [2.9.5] - 2023-08-02
### Changed
- OM-103188: Add default location for `FilePickerDialog` when no current directory is set, which could be configured via
  extension setting `default_open_directory`

## [2.9.4] - 2023-07-05
### Changed
- OM-100532: Fix error log when use recycle bin in content browser.

## [2.9.3] - 2023-06-23
### Changed
- Add hint text field to filebar if filename input is disabled

## [2.9.2] - 2023-06-28
### Added
- OM-98801: Add 'show only collections' setting, if it not set in init param use the setting value instead.

## [2.9.1] - 2023-06-28
### Added
- OM-54203: implement soft delete in content browser
- OM-77963: Make use of environment variable to disable check for soft-delete features in Content Browser
- OM-54464: add source url in moved/renamed item checkpoint

## [2.9.0] - 2023-06-27
### Changed
- OM-97996: Able to add widgets after search bar (For Content window, need put filter button just behind search bar)

## [2.8.19] - 2023-06-27
### Changed
- OM-99312: Hide the loading pane whenever no item exists in 'navigate to' progress.

## [2.8.18] - 2023-06-21
### Changed
- OM-92223: Don't navigate to https item to avoid the warning log.

## [2.8.17] - 2023-06-20
### Changed
- OM-98255: Fix local variable 'current_bookmarks' referenced before assignment issue.

## [2.8.16] - 2023-06-013
### Changed
- Update filebar file name label hint text color with more contrast

## [2.8.15] - 2023-06-09
### Changed
- OM-97764: remove test.usda to avoid confuse.

## [2.8.14] - 2023-06-06
### Fixed
- OM-97027: Fix navigate to api performance issue.

## [2.8.13] - 2023-05-30
### Changed
- OM-42020: Always recreate config menu to make position right in external window

## [2.8.12] - 2023-05-23
### Added
- Added auto cancellation behavior for initial navigation on Filepicker init, cancels when user type in path field or
  manually browse to another location

## [2.8.11] - 2023-05-16
### Fixed
- OM-94624: Fix grammatical error in the delete confirmation pop-up window of content browser
- OM-94622: Add "About" section in connect context menu in the content browser

## [2.8.10] - 2023-05-09
### Added
- Added focus_filename_input to focus filebar filename input field

## [2.8.9] - 2023-05-10
### Added
- OM-93184: Able to use FilePickerWidget in modal window

## [2.8.8] - 2023-05-08
### Added
- Added set_postfix to set filebar postfix

## [2.8.7] - 2023-04-20
### Added
- Added Log Out/In context menu item for Connection item

## [2.8.6] - 2023-04-17
### Added
- Get selected file name even file bar not enabled
- New argument to set label of cancel button

## [2.8.5] - 2023-04-17
### Changed
- Update "new folder" show_fn so in list view menu it shows up with empty selection

## [2.8.4] - 2023-04-11
### Changed
- Updated add_context_menu api, added separator_name kwarg as the position anchor for index
- Re-ordered context menu options to match Navigator UX

## [2.8.3] - 2023-04-10
### Added
- Add ENTER key func to Filepicker Dialog, use apply handler for ENTER key

## [2.8.2] - 2023-03-31
### Added
- Add property for file extension options for file bar, and add api for getting that on FilepickerDialog

## [2.8.1] - 2023-03-29
### Added
- Added test for fast destruction resilience for filepicker dialog

## [2.8.0] - 2023-03-27
### Changed
- Merge existing diffs from content browser to facilite sub-classing from the widget

## [2.7.36] - 2023-03-28
### Fixed
- Update file path when solve timestamp enabled and datetime changed

## [2.7.35] - 2023-03-24
### Changed
- Refactor the context menu and the set of file operations

## [2.7.34] - 2023-03-23
### Changed
- Use pytz in prebundle

## [2.7.33] - 2023-03-22
### Fixed
- Fixed omni+kit+window+content_browser-viewport_next-test_mount_default_servers failing

## [2.7.32] - 2023-03-21
### Fixed
- Fixed unit test.

## [2.7.31] - 2023-03-20
### Added
- Added timestamp.

## [2.7.30] - 2023-03-09
### Changed
- Replace pyperclip with linux-friendly copy/paste using omni.kit.clipboard

## [2.7.29] - 2023-03-13
### Updated
- Added dedicated context menu for udim items
- Light code cleanup

## [2.7.28] - 2023-03-08
### Updated
- Update bookmark edit/add dialog to match Navigator UX
- Update bookmark item context menu, should only show edit and delete for bookmarks

## [2.7.27] - 2023-03-08
### Changed
- Swapped a couple asyncio.ensure_future calls with run_coroutine

## [2.7.26] - 2023-03-01
### Updated
- Replace navigation prompt popup with a loading pane inside filebrowser list view stack

## [2.7.25] - 2023-03-02
### Added
- New kwarg "enable_tool_bar" to enable/disable tool bar.  Default True.
- New kwarg "enable_zoombar" to enable/disable zoombar. Default True.
- New kwarg "save_grid_view" to save grid view mode if toggled. Default True.
- Make get_selected_filename_and_directory works even "enable_filename_input" set to False

## [2.7.24] - 2023-02-27
### Updated
- OM-78338: Make the filepicker dialog filebar's drop down menus stay intact.

## [2.7.23] - 2023-02-09
### Updated
- Moved search field to its own extension

## [2.7.22] - 2023-02-03
### Updated
- Add update_checkpoint_fn for ContextMenu, as checkpoint updated callback.
- List checkpoints to update checkpoint list upon checkpoint created.

## [2.7.21] - 2023-02-02
### Fixed
- Fixed a couple of unittests.

## [2.7.20] - 2023-01-30
### Updated
- Add enable_apply_button to FileBar that exposes apply button enable control.
- Add filename_changed_handler kwarg to FilePickerWidget for customization by callers.

## [2.7.19] - 2023-01-26
### Updated
- Fix tests when run in random order.

## [2.7.18] - 2023-01-17
### Updated
- Added UDIM support
- `navigate_to` enables `show_udim_sequence` if URL is UDIM

## [2.7.17] - 2023-01-20
### Updated
- Enable_filename_input hides all filename widgets

## [2.7.16] - 2023-01-16
### Updated
- Update local disk partition filtering for linux

## [2.7.15] - 2023-01-13
### Updated
- Enables expanding/collapsing of bookmarks folder.

## [2.7.14] - 2023-01-11
### Updated
- Refactored asset_types to common file_utils extension.
- UI_READY event emitted more precisely to fix race condition in some unittests.

## [2.7.13] - 2023-01-11
### Updated
- Followup refactor of the BookmarkModel to simplify the interface and fix thumbnails.
- Applied similar refactor to SearchResultsModel.

## [2.7.12] - 2023-01-11
### Updated
- Add BookmarkModel and BookmarkItem to handle bookmarks
- Bookmarks in Kit now behave more similar to Navigator, and a user can bookmark a file or folder
- Bookmarks are now unexpandable, and it jumps to the bookmarked url rather than populate items as its children

## [2.7.11] - 2023-01-06
### Updated
- Add CollectionContextMenu that handles context menu for collection nodes
- Right click context for collection nodes now matches Navigator, where Omniverse has a add server right click menu,
  and other collection nodes will not populate context menu

## [2.7.10] - 2022-12-20
### Updated
- Change the ComboBoxMenu's window to scrollable.

## [2.7.9] - 2022-12-19
### Updated
- Update toolbar widget spacer

## [2.7.8] - 2022-12-12
### Updated
- Do not skip the default item filters when a custom filter is specified

## [2.7.7] - 2022-12-12
### Updated
- Fixes detail view regression

## [2.7.6] - 2022-12-08
### Updated
- Replaces omni.client.stat with async call to fix hanging app
- Refreshes the server item after a successful connection

## [2.7.5] - 2022-12-07
### Updated
- Add callback for toggling grid view and changing grid view scale, record grid view settings.

## [2.7.4] - 2022-11-29
### Updated
- Rename/delete/create context menu will not show for read-only context item

## [2.7.3] - 2022-11-08
### Updated
- Workaround for random self.view == None exception during shutdown when running tests

## [2.7.2] - 2022-11-22
### Updated
- Refresh server after successfully making a connection

## [2.7.1] - 2022-11-09
### Updated
- Updated the tooltip for connection errors

## [2.7.0] - 2022-11-08
### Updated
- Added move functionality to FilePickerModel
- Update context menu rename handling for file/folder

## [2.6.14] - 2022-11-07
### Updated
- Add option for copy_items_with_callback to specify a destination relative path, instead of always using
  the source relative path.

## [2.6.13] - 2022-11-01
### Updated
- Checks for existence before connecting server

## [2.6.12] - 2022-10-31
### Updated
- Don't destroy search delegate.

## [2.6.11] - 2022-10-25
### Updated
- Fixes flaky unittests.

## [2.6.10] - 2022-10-31
### Updated
- Decouple USD from extension.

## [2.6.9] - 2022-10-27
### Updated
- Improve FilePickerView initialization performance on Windows

## [2.6.8] - 2022-10-14
### Updated
- Flag test_get_item_from_grid_view, test_get_item_from_table_view, test_get_item_from_tree_view, and
  test_update_connections_when_settings_changed as unreliable.

## [2.6.7] - 2022-10-05
### Updated
- Don't allow dialog window to be docked

## [2.6.5] - 2022-10-03
### Updated
- Fix typo in add_bookmark menu
- Don't copy bookmark settings from carb.settings, don't destroy setings for earlier Create versions.

## [2.6.4] - 2022-09-27
### Updated
- Bookmarks stored in omni.client

## [2.6.3] - 2022-09-23
### Updated
- Don't set the warning badge for the placeholder item.

## [2.6.2] - 2022-09-20
### Updated
- Clean and reload driver when refresh ui, ensure show OV driver correctly.

## [2.6.1] - 2022-09-01
### Updated
- Reverts removal of localhost from servers list.
- Fixes flaky unittests that utilize the test helper.

## [2.6.0] - 2022-08-30
### Updated
- Refactored thumbnails provider.

## [2.5.1] - 2022-09-01
### Updated
- Reverts removal of localhost from servers list.
- Fixes flaky unittests that utilize the test helper.

## [2.5.0] - 2022-08-22
### Updated
- Moves server connection handling into separate 'nucleus_connector' extension.

## [2.4.33] - 2022-07-19
### Added
- Fixes latency in navigation.

## [2.4.32] - 2022-07-13
### Added
- Minor fixes.

## [2.4.31] - 2022-07-07
### Added
- Adds UI ready event
- Catches exceptions from delayed function calls; often raised by unit tests where the dialog is rapidly being created and destroyed.

## [2.4.30] - 2022-05-27
### Added
- Updated unit of file size to Mebibyte (instead of Megabyte)

## [2.4.29] - 2022-05-12
### Added
- Ensures add server popup is displayed within window

## [2.4.27] - 2022-04-19
### Added
- Fixes navigating to url that contains Url-encoded characters.
- Adds async versions to navigate_to and find_item functions.
- Adds select_items function to facilitate unittests.

## [2.4.26] - 2022-04-18
### Added
- Limits extent that splitter can be dragged, to prevent breaking.

## [2.4.25] - 2022-04-12
### Added
- Adds splitter to adjust width of detail pane.

## [2.4.24] - 2022-04-06
### Added
- Disable unittests from loading at startup.

## [2.4.23] - 2022-04-04
### Updated
- Fixes fullpath of filename when file selected from treeview.

## [2.4.22] - 2022-03-31
### Updated
- Removed toml setting for enabling checkpoint, passed in a kwarg instead.
- Fixed destructor for DetailDelegate.

## [2.4.21] - 2022-03-18
### Updated
- Updates search results when directory changed.

## [2.4.20] - 2022-03-14
### Updated
- Adds extended file info into detail view.
- Refactored handling of asset type.

## [2.4.18] - 2022-03-07
### Updated
- Adds custom search delegate.

## [2.4.17] - 2022-03-07
### Updated
- Added postfix name thumbnails and icons.

## [2.4.16] - 2022-02-07
### Updated
- Fixes options_pane_build_fn regression due to detail view refactoring.

## [2.4.15] - 2021-11-30
### Updated
- Introduced DetailFrameController to simplify API for adding detail frame.

## [2.4.14] - 2021-11-24
### Updated
- Added `show_grid_view` to get grid or table view.

## [2.4.13] - 2021-11-03
### Updated
- Added search box, which combines the best features from Asset Browser and Content Browser.

## [2.4.12] - 2021-11-01
### Updated
Cleaned up message dialogs in FilePickerView, fixed unittest errors.

## [2.4.11] - 2021-10-27
### Updated
- Added notification on connection error.

## [2.4.10] - 2021-10-20
### Updated
- Don't return paths with windows slash

## [2.4.9] - 2021-09-17
### Updated
- Added widget identifers

## [2.4.8] - 2021-09-17
### Updated
- Updated "Add Connection" interaction to be more intuitive.

## [2.4.7] - 2021-09-16
### Updated
- Add API to configure name label for file bar.

## [2.4.6] - 2021-08-20
### Updated
- Added UI stress test for auto-refreshing current directory when adding and deleting many files in quick succession.

## [2.4.5] - 2021-08-04
### Updated
- Fixed get_filename API.

## [2.4.4] - 2021-07-20
### Updated
- Fixes checkpoint selection

## [2.4.3] - 2021-07-13
### Updated
- Added "enable_checkpoints" setting to toml file to enable checkpoints everywhere

## [2.4.2] - 2021-07-13
### Updated
- Fixed destructor bug causing calls to init_view with invalid object instances

## [2.4.1] - 2021-07-12
### Updated
- Added detail view and corresponding menu item in combox box to active/deactivate it
- Added API methods for adding custom frames to detail view
- Moved checkpoint panel to detail view
- Updated look of file bar

## [2.3.11] - 2021-06-23
### Updated
- Pass `open_file` function to omni.kit.widget.versioning

## [2.3.10] - 2021-06-21
### Updated
- Always show "Create Checkpoint" context menu option when server supported

## [2.3.9] - 2021-06-18
### Updated
- Persist the width of the versioning panel

## [2.3.8] - 2021-06-09
### Updated
- When local windows path not found, doesn't try to connect to it.

## [2.3.7] - 2021-06-16
### Updated
- More graceful cancellation of navigation futures.

## [2.3.6] - 2021-06-09
### Updated
- Added stronger checkpoint overwrite messages

## [2.3.5] - 2021-06-10
- Always show versioning pane when enabled

## [2.3.4] - 2021-06-08
- Fixes window resize messes up versioning splitter bar.
- Relocates zoom bar out of versioning panel.

## [2.3.3] - 2021-06-07
### Updated
- Added splitter bar for resizing checkpoints panel.
- Refactored checkpoints panel and zoom bar into FilePickerView widget.
- More thorough destruction of class instances upon shutdown.

## [2.3.2] - 2021-06-04
### Updated
- Added optional message parameter to `ConfirmItemDeletionDialog` so it can be used for overrite too

## [2.3.1] - 2021-06-01
### Updated
- Eliminates manually initiated refresh of the UI when creating new folder and deleting items; these  conflict with the new auto refresh.

## [2.3.0] - 2021-05-11
### Added
- Added support for `ENTER` and `ESC` keys.
- Added support for creating new empty USD files through the "New USD File" contextual menu.
- Added support for opening the browser location using the operating system's file explorer through the "Open in File Browser" contextual menu.
- Added ability to select checkpoints from the contextual menu.

## [2.2.1] - 2021-04-09
### Changed
- Show <head> entry in versioning pane.

## [2.2.0] - 2021-03-23
### Added
- Added optional versioning pane on supported server (only when omni.kit.widget.versioning is enabled) and `enable_versioning_pane` constructor parameter to enable/disable it.
- Added `Options` pane to the right of file picker. Can be enabled by passing `options_pane_build_fn` and provide custom UI build function.

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
- Extracted ZoomBar into its own widget.

## [2.0.1] - 2021-02-03
### Updated
- Refactored code for getting auto-generated thumbnails. The simplification allowed for easier testing.
- Fixed bug that was causing artifacts and mismatched thumbnails in grid view
### Added
- Unittests for navigating directories
- Unittests for persistent settings
- Unittests for asset types

## [2.0.0] - 2021-01-03
### Updated
- Refactored for async directory listing to improve overall stability in case of network delays.

## [1.3.10] - 2020-12-10
### Updated
- Detects bad server connections before opening files
- Removes callback from 'navigate_to' API

## [1.3.9] - 2020-12-05
### Updated
-  Adds 'reconnect server' action to context menu

## [1.3.8] - 2020-12-03
### Updated
-  Adds ability to rename connections and bookmarks

## [1.3.7] - 2020-12-01
### Updated
- Correctly resolves connections whose label names differ their path names

## [1.3.6] - 2020-11-26
### Updated
- Defaults browser bar to display real path

## [1.3.5] - 2020-11-25
### Updated
- Code refactor: Consolidates ListViewMenu into ContextMenu and eliminates PopupMenu base class.

## [1.3.4] - 2020-11-23
### Updated
- Double clicking on item immediately executes apply callback.

## [1.3.3] - 2020-11-20
### Updated
- Allows multi-selection deletion.

## [1.3.2] - 2020-11-19
### Updated
- Context menu responds to multi-selection actions.

## [1.3.1] - 2020-11-13
### Added
- Fixes multi-selection and added option to turn off file bar.
- Keeps connections and bookmarks between content browser and filepicker in sync.
- Scrolls to a given path upon showing dialog.

## [1.3.0] - 2020-10-31
### Added
- Now able to resolve URL paths pasted into the browser bar

## [1.2.0] - 2020-10-29
### Added
- User folders in "my-computer" collection

## [1.1.0] - 2020-10-27
### Added
- Ported context menu from omni.kit.window.content_browser.
- Consolidated API methods into api module.
- Correctly process persistent settings for connections and bookmarks.
- Display svg files as their own thumbnails.

## [0.1.5] - 2020-09-16
### Added
- Initial commit to master.
