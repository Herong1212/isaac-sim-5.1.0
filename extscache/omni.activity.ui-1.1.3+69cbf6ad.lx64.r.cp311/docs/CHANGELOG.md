# Changelog

This document records all notable changes to the **omni.activity.ui** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.1.3] - 2025-04-24
### Changed
- Updated icon image

## [1.1.2] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.1.1] - 2025-10-22
### Changed
- Update the public API for the extension

## [1.1.0] - 2025-09-81
### Fixed
- Made dependency on omni.kit.usd.layers explicit and optional

## [1.0.29] - 2024-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.0.28] - 2023-11-13
### Fixed
- OMFP-3811: Fixed float division by zero issue

## [1.0.27] - 2023-10-04
### Fixed
- Ignore nodes with more than 512 events at once. It saves 15s of FE startup.

## [1.0.26] - 2023-10-24
### Fixed
- OMFP-3078: Fixed activity item name which has space was replaced by %

## [1.0.25] - 2023-09-25
### Fixed
- Fixed another issue with updating before `progress_stack()` is called

## [1.0.24] - 2023-10-18
### Added
- Added addon widget to the stage open event subscription for live session

## [1.0.23] - 2023-10-05
### Added
- Adds test coverage, to get to 85%

## [1.0.22] - 2023-07-18
### Fixed
- OM-76599: Show a load asset activity prompt window when drag and drop asset into stage window.

## [1.0.21] - 2023-04-24
### Fixed
- UI update with Omni UI rasterization optimization enabled

## [1.0.20] - 2023-04-11
### Fixed
- Fixed issue with updating before `progress_stack()` is called

## [1.0.19] - 2023-02-08
### Fixed
- total duration not correct in progress window
- sync loading activity files between Timeline and Progress windows

## [1.0.18] - 2022-12-08
### Changed
- Don't use usd_resolver python callbacks

## [1.0.17] - 2022-12-08
### Fixed
- try to open non-exsited URL, the spinner is always rotating by using OPEN_FAILED event (OM-73934)

## [1.0.16] - 2022-11-30
### Fixed
- Updated to use omni.kit.menu.utils

## [1.0.15] - 2022-12-05
### Changed
- Fixed pinwheel slightly offset from loading bar (OM-74619)
- Added padding on the tree view header (OM-74828)

## [1.0.14] - 2022-11-28
### Fixed
- when new stage is created or new stage is loading, the previous stage data should be cleared

## [1.0.13] - 2022-11-24
### Fixed
- try to open non-exsited URL, the spinner is always rotationg (OM-73934)
- force loading completion in the model rather than in the widget in case widget is not available (OM-73085)

## [1.0.12] - 2022-11-22
### Changed
- Make the pinwheel invisible when it's not loading

## [1.0.11] - 2022-11-22
### Changed
- Fixed the performance issue when ASSETS_LOADED is triggered by selection change
- Changed visibility of the progress bar window, instead of poping up when the prompt window is done we show the window when user clicks the status bar's progress area

## [1.0.10] - 2022-11-18
### Changed
- fixed performance issue caused by __extend_unfinished
- create ActivityModelStageOpenForProgress model for progress bar window to solve the performance issue of progress bar

## [1.0.9] - 2022-11-14
### Added
- informative text on the total progress bar showing the activity event happening (OM-72502)
- docs for the extension (OM-52478)

## [1.0.8] - 2022-11-10
### Changed
- also clear the status bar when the stage is loaded so it's not stuck at 100%

## [1.0.7] - 2022-11-10
### Changed
- clear the status bar instead of sending progress as 0% when new stage is created

## [1.0.6] - 2022-11-07
### Changed
- using spinner instead of the ping-pong rectangle for the floating window

## [1.0.5] - 2022-11-07
### Changed
- make sure the activity progress window is shown and on focus when open stage is triggered

## [1.0.4] - 2022-10-26
### Changed
- Stop the timeline view when asset_loaded
- Move the Activity Window menu item under Utilities
- Disable the menu button in the floating window
- Rename windows to Activity Progress and Activity Timeline
- Removed Timeline window menu entry and only make accessible through main Activity window
- Fixed resizing issue in the Activity Progress Treeview - resizing second column resizer breaks the view
- Make the spinner active during opening stage
- Remove the material progress bar size and speed for now
- Set the Activty window invisible by default (fix OM-67358)
- Update the preview image

## [1.0.3] - 2022-10-20
### Changed
- create ActivityModelStageOpen which inherits from ActivityModelRealtime, so to move the stage_path and _flattened_children out from the ActivityModelRealtime mode

## [1.0.2] - 2022-10-18
### Changed
- Fix the auto save to be window irrelevant (when progress bar window or timeline window is closed, still working), save to "${cache}/activities", and auto delete the old files, at the moment we keep 20 of them
- Add file numbers to timeline view when necessary
- Add size to the parent time range in the tooltip of timeline view when make sense
- Force progress to 1 when assets loaded
- Fix the issue of middle and right clicked is triggered unnecessarily, e.g., mouse movement in viewport
- Add timeline view selection callback to usd stage prim selection

## [1.0.1] - 2022-10-13
### Fixed
- test failure due to self._addon is None

## [1.0.0] - 2022-06-05
### Added
- Initial window
