# QUICKLAYOUT CHANGELOG

## [1.0.8] - 2024-09-25
### Changes
- OMPE-16944: Warn user with instructions that loading a layout requires the user to first save a layout.

## [1.0.7] - 2024-05-22
### Changes
- OMPE-7476: Make omni.kit.window.filepicker dependency optional

## [1.0.6] - 2023-11-10
### Changes
- Updated to use omni.kit.menu.utils

## [1.0.5] - 2023-10-05
### Changed
- Added test
- Removed setting menu Window/Layout priority as it doesn't do anything in omni.kit.menu.utils

## [1.0.4] - 2023-06-27
### Changed
- Fixed `omni.client.combine_urls` calls to add trailing slash

## [1.0.3] - 2023-01-11
### Changed
- Removed python.module for tests, from extension.toml
- Fixed tests that broke when run in random order

## [1.0.2] - 2023-01-20
### Changed
- Fixed saving/loading using nucleus paths

## [1.0.1] - 2021-05-25
### Changed
- Using `omni.client` for saving and loading the workspace

## [1.0.0] - 2021-02-02
### Added
- Initial extension that saves/loads the layout to the userdirectory
