# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.5] - 2025-05-16
### Changed
- OMPE-48320: make sure edit_layer_path start with "file:/" if it is a file url

## [2.0.4] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [2.0.3] - 2025-04-07
### Removed
- OMPE-45233: Removed renderer from tests

## [2.0.2] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [2.0.1] - 2025-01-20
### Changed
- Update missing public api.

## [2.0.0] - 2025-01-20
### Changed
- Bump the major version since deprecated public API was removed.

## [1.3.59] - 2025-01-06
### Changed
- OMPE-31533: Remove deprecated APIs from omni.kit.window.file.

## [1.3.58] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [1.3.57] - 2024-11-05
### Changed
- OMPE-22606: Update public API

## [1.3.56] - 2025-10-16
### Fixed
- OMPE-25104: Do not run callback in draw thread to avoid possible crash

## [1.3.55] - 2025-07-11
### Fixed
- OMPE-14619: Fixed icon pathing in read_only_options_window.py

## [1.3.54] - 2024-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.3.53] - 2024-05-17
## Changed
- OMPE-5047: Profile and Improve test times of omni.kit.window.file.

## [1.3.52] - 2024-03-19
## Changed
- Make versioning dependency optional

## [1.3.51] - 2024-03-22
## Changed
- OM-122340: Update documentation.

## [1.3.50] - 2024-03-13
## Changed
- OM-31127: Add show save options setting.

## [1.3.49] - 2024-03-12
## Changed
- Fix for new stage without omni.kit.stage_template.core

## [1.3.48] - 2024-03-06
## Changed
- Use omni.kit.stage_template.core & make it optional

## [1.3.47] - 2023-12-27
## Changed
- Use omni.kit.stage_template.core

## [1.3.46] - 2023-11-22
## Changed
- Fix double slashes inside the saving path.

## [1.3.45] - 2023-11-07
## Changed
- OM-109022: Fix cannot open absolute path issue.

## [1.3.44] - 2023-10-09
## Changed
- increase the test coverage to over 85%

## [1.3.43] - 2023-08-22
## Changed
- OM-39070: Turn on validation for file open and add reference

## [1.3.42] - 2023-08-29
## Changed
- Re-enabled disabled tests test_file_open_with_new_edit_layer_overwrites_existing_file & test_file_saveas_flattened_with_session_layer

## [1.3.41] - 2023-07-05
## Changed
- Show detailed errors when file cannot be saved.

## [1.3.40] - 2023-06-18
## Changed
- Fix OM-100359: automatically change the window size by setting ui.Window.auto_resize=True

## [1.3.40] - 2023-06-18
## Changed
- Change the window size in order to avoid cut of widgets

## [1.3.39] - 2023-05-09
## Changed
- Don't prefill filename on save as

## [1.3.38] - 2023-04-26
## Changed
- Changed `exclusive_task_wrapper` to cancel previous task if still running

## [1.3.37] - 2023-04-24
## Changed
- Fix UI update with Omni UI rasterization optimization enabled

## [1.3.36] - 2023-03-23
## Changed
- OM-87635: Normalize incoming directory path argument for open_with_new_edit_layer.

## [1.3.35] - 2023-03-13
## Changed
- OM-60125: "Select Files to Save" window set (W) 600 x (H) 320 as the initial display size and elided long save file name

## [1.3.34] - 2023-03-07
## Changed
- Send file opened and file saved events to message stream.

## [1.3.33] - 2023-01-20
## Changed
- Fix ETM tests.

## [1.3.32] - 2023-01-13
## Changed
- Remove render settings save as it's driven by events already.

## [1.3.31] - 2023-01-04
## Changed
- skipping test_file_open_with_new_edit_layer_overwrites_existing_file which crashes when run in random order.

## [1.3.30] - 2022-11-04
## Added
- open stage complete callback register for the use of e.g. Activiy window

## [1.3.29] - 2022-10-28
## Changed
- When opening a stage, auto-connect to nucleus.

## [1.3.28] - 2022-10-01
## Changed
- Do not pass in a default filename for new stage for save-as;
- Explicitly set file exporter to validate filename for save-as;

## [1.3.27] - 2022-09-21
## Changed
- When saving a checkpoint or read-only file, use save_as instead.

## [1.3.26] - 2022-09-14
## Changed
- Pass in default file url to file exporter for save-as option.

## [1.3.25] - 2022-09-05
## Changed
- Supports to flatten stage without session layer.

## [1.3.24] - 2022-07-22
## Changed
- Fixed checkpoint comments with latet omni.usd_resolver.

## [1.3.23] - 2022-07-19
## Changed
- As menus no longer use contextual greying
- Improved error handing for actions & notifications

## [1.3.22] - 2022-07-19
## Changed
- Fixes comment field in save-as option

## [1.3.21] - 2022-06-27
## Changed
- Fixed save actions

## [1.3.20] - 2022-05-30
## Changed
- Added action "open_stage"
- Added action "save_with_options"
- Added action "save_as_flattened"
- Added action "add_payload"

## [1.3.19] - 2022-06-15
## Changed
- Updated unittests.

## [1.3.18] - 2022-05-30
## Changed
- "Select Files to Save" window expands with length of filenames
- Decoded URL in Opening URL popup window

## [1.3.17] - 2022-05-19
## Changed
- Fixed file export prompt when quitting an unsaved stage.

## [1.3.16] - 2022-05-05
## Changed
- Updated unittests.

## [1.3.15] - 2022-03-21
## Changed
- Disable checkpoint comments in save as dialog if server doesn't support checkpoints.

## [1.3.14] - 2022-03-21
## Changed
- Open payloads in file dialog.

## [1.3.13] - 2022-03-17
## Changed
- Fixed typo in the previous merge.

## [1.3.12] - 2022-03-17
## Changed
- Fixed UX flow for saving unsaved stage.

## [1.3.11] - 2022-03-08
## Changed
- Fixes Unsaved Layers dialog sometimes not enabling `Dont Save` flag.

## [1.3.10] - 2022-03-10
## Changed
- Pop up read only options dialog for read-only stage to keep consistent behavior as content browser.

## [1.3.9] - 2022-02-09
## Changed
- Refactor to use file_importer and file_exporter rather than FilePickerDialog.

## [1.3.8] - 2021-12-21
## Changed
- More fixes to `open_with_new_edit_layer` and tests added.
- Fix memory leak caused by prompt.

## [1.3.7] - 2021-12-17
## Changed
- Fixed `open_with_new_edit_layer` function

## [1.3.6] - 2021-11-10
## Changed
- Cleans up on shutdown, including releasing handle to FilePickerDialog.

## [1.3.5] - 2021-11-02
## Changed
- Add open stage callback register for the use of e.g. Activiy window

## [1.3.4] - 2021-10-20
## Changed
- Don't return windows slashes in paths

## [1.3.3] - 2021-08-04
## Changed
- Fixed leak in popup modal dialog

## [1.3.2] - 2021-07-29
## Changed
- Added LoadSet flags to open_file, open_stage
- Fixed Create Reference/Payload to use commands to they are undoable
- Create Reference/Payload now uses correct rotation when created

## [1.3.1] - 2021-06-25
## Changed
- "Would you like to save this stage?" is modal

## [1.3.0] - 2021-06-08
## Changed
- Added checkpoint description to `Save As` file picker

## [1.2.2] - 2021-05-05
## Changed
- Updated Save so can either have no UI or UI

## [1.2.1] - 2021-04-08
## Changed
= Removed versioning pane from `Save As` file picker

## [1.2.0] - 2021-03-22
## Changed
= Unified `Save` and `Save with Comment` user interface.

## [1.1.1] - 2021-03-02
- Added test
- Fixed leaks

## [1.1.0] - 2021-02-09
### Changes
- Changed checkpoint comment message:
  - When using Save As to save a new file and overwriting an existing file: "Replaced with new file"
  - When using Save As to save an existing file and overwriting an existing file: "Replaced with [the path of the file]"

## [1.0.2] - 2021-02-10
- Updated StyleUI handling

## [1.0.1] - 2020-08-28
### Changes
- added add_reference function

## [1.0.0] - 2020-08-28
### Changes
- converted to extension 2.0
