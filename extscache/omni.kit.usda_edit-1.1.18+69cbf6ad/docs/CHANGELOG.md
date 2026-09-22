# Changelog
This document records all notable changes to ``omni.kit.usda_edit``
extension.

## [1.1.18] - 2025-04-30
### Changed
- Updated documentation with AI agent.

## [1.1.17] - 2025-04-28
### Changed
- OMPE-44336: Fix the usda edit not works because of short tmp path.

## [1.1.16] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [1.1.15] - 2024-04-09
### Changed
- Restore unit test, and prevent failure on GitLab CI/CD.

## [1.1.14] - 2024-03-27
### Changed
- Revert changes made in 1.1.12.

## [1.1.13] - 2024-03-14
### Changed
- Add omni.kit.context_menu dependency to tests.

## [1.1.12] - 2023-12-13
### Changed
- Increase code coverage above 85%.

## [1.1.10] - 2022-02-02
### Changed
- Removed explicit pip dependency requirement on `watchdog`. It's now pre-bundled with Kit SDK.

## [1.1.9] - 2021-12-22
### Fixed
- content_browser context menu is now destroyed when content_browser unloaded first during kit exit

## [1.1.8] - 2021-02-23
### Changed
- The test waits for import instead of 15 frames

## [1.1.7] - 2021-02-17
### Added
- Support for the file format `usd_omni_wrapper` which is from Nucleus
### Changed
- The call of the editor is not blocking
### Fixed
- The path to editor can contain quotation marks

## [1.1.6] - 2020-12-08
### Added
- Preview image and description

## [1.1.5] - 2020-12-03
### Added
- Dependency on watchdog

## [1.1.4] - 2020-11-12
### Changed
- Fixed exception in Create

## [1.1.3] - 2020-11-11
### Changed
- Fixed the bug when the USD file destroyed when it's on the server and has the asset metadata
### Added
- Menu to `omni.kit.window.content_browser`

## [1.1.2] - 2020-07-09
### Changed
- Join the observer before destroy it. It should fix the exception when
exiting Kit.

## [1.1.1] - 2020-07-08
### Added
- Added dependency to `omni.kit.pipapi`

## [1.1.0] - 2020-07-06
### Added
- The editor executable is set using settings `/app/editor` or `EDITOR`
environment variable.

## [1.0.0] - 2020-07-06
### Added
- CHANGELOG.rst
- Added the context menu to Content Browser window to edit USDA files

## [0.1.0] - 2020-06-29
### Added
- Ability to edit USD layers as USDA files
- Added the context menu to Layers window to edit USDA files
