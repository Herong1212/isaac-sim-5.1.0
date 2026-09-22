# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.4.10] - 2025-04-14
### Changed
- Updated documentation with AI agent.

## [1.4.9] - 2024-10-22
### Changed
- OMPE-25686: Update public API

## [1.4.8] - 2024-07-30
### Changed
- OMPE-8922: Use omni.kit.widget.context_menu for context menu

## [1.4.7] - 2024-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.4.6] - 2023-11-14
### Fixed
- OMFP-3807: Update checkpoint list when server's file changed.

## [1.4.5] - 2023-10-16
### Changed
- OMFP-2270: Add tests and improve code coverage

## [1.4.4] - 2023-08-21
### Changed
- Use platform-agnostic omni.kit.clipboard instead of pyperclip

## [1.4.3] - 2023-05-18
### Changed
- Add back "head" dummy node for files with checkpoints

## [1.4.2] - 2023-03-08
### Changed
- Swapped a couple asyncio.ensure_future calls with run_coroutine

## [1.4.1] - 2023-03-07
### Added
- CheckpointCombobox could be used in Modal window with new argument "modal=true"

## [1.4.0] - 2023-02-23
### Added
- Add more arguments and properties for CheckpointCombobox to use in Welcome window

## [1.3.11] - 2023-02-02
### Changed
- Add checkpoint widget card selected style for card label for better visibility

## [1.3.10] - 2023-01-17
### Changed
- Added description for restored checkpoint

## [1.3.8] - 2022-04-27
### Changed
- Fixes unittests.

## [1.3.7] - 2022-04-18
### Changed
- Added CheckpointHelper.

## [1.3.6] - 2021-11-22
### Changed
- Fixed UI layout when imported into the filepicker detail view.

## [1.3.5] - 2021-08-12
### Changed
- Added method to retrieve comment from the Checkpoint item.

## [1.3.4] - 2021-07-20
### Changed
- Adds enable_fn to context menu

## [1.3.3] - 2021-07-20
### Changed
- Fixes checkpoint selection

## [1.3.2] - 2021-07-13
### Changed
- Fixed selection handling, particularly useful for the combo box

## [1.3.1] - 2021-07-12
### Changed
- Added compact view for checkpoint list
- Refactored the widget for incorporating into redesigned filepicker

## [1.2.1] - 2021-06-10
### Changed
- Added open checkpoint from checkpoint list

## [1.2.0] - 2021-06-10
### Changed
- Checkpoint window always shows when enabled

## [1.1.3] - 2021-06-07
### Changed
- Added `on_list_checkpoint_fn` to execute user callback when listing updated.

## [1.1.2] - 2021-05-04
### Changed
- Updated styling on checkpoint widget

## [1.1.1] - 2021-04-08
### Changed
- Right click on any column of a checkpoint entry now brings up the "Restore Checkpoint" context menu.

## [1.1.0] - 2021-03-25
### Added
- Added support `add_on_selection_changed_fn` to checkpoint widget.
- Added `CheckpointCombobox` widget for easy selection of checkpoint as a combobox.

## [1.0.0] - 2021-02-01
### Added
- Initial version.
