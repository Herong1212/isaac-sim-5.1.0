# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Next Version]

## [1.1.8] - 2025-04-30
### Changed
- Updated documentation with AI agent.

## [1.1.7] - 2024-11-07
### Changes
- OMPE-22724: Fix ui query get the same path for different widget issue.

## [1.1.6] - 2024-10-28
### Changes
- Updated API and __all__ exports

## [1.1.5] - 2024-07-18
### Added
- OMPE-15065: Add function get_widget_children_with_path to get all child widgets with path for given widget and path

## [1.1.4] - 2024-05-29
### Added
- Fix find_first_widget's attribute error.

## [1.1.3] - 2024-05-20
### Added
- Added function find_first_widget to get the first matched widget for a query.

## [1.1.2] - 2024-01-29
### Added
- OM-119448: Added function get_window_widget_paths to get all widget paths of a window.

## [1.1.1] - 2022-01-10
- support for widgets under Treeviews (i.e those created by the treeview delegate)

## [1.1.0] - 2021-11-09
- (breaking!) Remove add to omni.ui namespace magic as it breaks intellisense
- Add support for starting search from a set of root widgets
- Fix few query search bugs

## [1.0.1] - 2021-10-29
### Added
- When multiple windows with the same name are found, use the 1st visible one.

## [1.0.0] - 2021-09-08
### Added
- The initial release
