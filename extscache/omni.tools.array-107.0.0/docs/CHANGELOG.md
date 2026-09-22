# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to Semantic Versioning <https://semver.org/>

## [107.0.0] - 2025-02-05
### Changed
- Updated for Kit 107.

## [105.0.4] - 2023-06-01
### Fixed
- The Array Tool will now work with objects who have additional unit resolve xform ops such as those added by the Metrics Assembler extension.

## [105.0.3] - 2023-03-22
### Changed
- Republish after USD/python update.

## [105.0.2] - 2023-03-22
### Changed
- Update test to tolerate small numerical differences.

## [105.0.1] - 2023-03-21
### Changed
- Republish after USD/python update.

## [105.0.0] - 2023-03-14

### Changed
- Republish after USD/python update.


## [104.0.12] - 2022-10-31

### Changed
- Updated button layout on tool UI

## [104.0.11] - 2022-10-18

### Changed
- Updated the functionality of the "Create Instances" UI option to automatically switch to "Create Copies" if invalid prims are selected. If a mix of valid and invalid instanceable prims are selected or provided via command, only the valid prims will be instanced and the invalid will be ignored.

### Fixed
- Fixed a bug where scale linking would not be remembered when "Remember Last Values" was set to true. Values and linking are now properly remembered.

## [104.0.10] - 2022-09-30

### Changed
- Incrementing extension version.

## [104.0.9] - 2022-09-02

### Fixed
- Fixed an issue where the Array Tool would error out if the user had instance proxies selected, or provided instance proxies to the CreateArrayCommand. This had the potential to put Create into a broken state requiring a restart.

## [104.0.8] - 2022-08-08

### Changed
- The default creation type for the Array Tool is now instances instead of copies. If invalid prims for instancing are selected, a warning will be displayed in the Array Tool UI. Select a valid instanceable prim or switch to copies to remove the warning.
- The CreateArrayCommand also now defaults to instances and expects the same input - valid instanceable prims.

## [104.0.7] - 2022-07-27

### Changed
- The Array Tool UI window can now be docked

## [104.0.6] - 2022-07-26

### Fixed
- Fixed a bug with the follow rotations option enabled where a source prim with pre-existing rotations would not be inherited by the array copies, so the copies would begin from an identity rotation.

## [104.0.5] - 2022-07-22

### Fixed
- Fixed a bug where moving multiple selected objects at once while they are being previewed with the array tool would cause all but one "array" to disappear.

## [104.0.4] - 2022-07-12

### Changed
- Updated Array Tool to use new tools menu

## [104.0.3] - 2022-06-29

### Fixed
- Removed lock that was preventing the Array Tool from being discoverable by kit versions prior to 104.

### Changed
- The Array Tool now appears as just "Array" in the Tools menu. Previously it appeared as "Array Tool"

## [104.0.2] - 2022-06-13

### Added
- Added an "x" button to the UI window to close the window. When clicked it acts like clicking "cancel".

## [104.0.1] - 2022-06-01

### Fixed
- Updated Copy Prim command used by array core to use the new version of the command.
- Updated name for Array Tool in the Tools menu

## [104.0.0] - 2022-05-05

### Added
- Initial release of array tool
