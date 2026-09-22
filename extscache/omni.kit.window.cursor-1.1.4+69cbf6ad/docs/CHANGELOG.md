# CHANGELOG

This document records all notable changes to ``omni.kit.window.cursor`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`.

## [1.1.4] - 2024-10-21
### Fixed
- Remove main window cursor variable and log_warn from public API.

## [1.1.3] - 2024-07-26
### Changed
- Avoid hardcoding extra cursors by providing them as default settings.
- Wrap more IMGUI renderer functions.
- Updated documentation with AI agent.
### Fixed
- Fix for extra cursors not being registered after hot reloading.

## [1.1.2] - 2023-10-10
### Changed
- Added grab_open/grap_clode cursor shapes.

## [1.1.1] - 2022-09-26
### Changed
- Store weakly referenced proxy to extension object.
- Handle possiblity of lower level API failure better.
- Return value of success for changing / restoring the cursor.

## [1.1.0] - 2022-05-06
### Changed
- Using `IImGuiRenderer` to override the mouse cursor

## [1.0.1] - 2021-03-01
### Added

- Added tests.


## [1.0.0] - 2020-11-06
### Added

- Initial extensions.
