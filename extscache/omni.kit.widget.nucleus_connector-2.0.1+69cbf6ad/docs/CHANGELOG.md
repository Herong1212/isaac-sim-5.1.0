# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.1] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [2.0.0] - 2024-01-20
### Changed
- Update public API, remove deprecated API.

## [1.1.11] - 2024-12-03
### Fixed
- OMPE-29317: Fix unable to reconnect to a nucleus server after cancelling the first connection attempt.

## [1.1.10] - 2024-10-28
### Changed
- Updated documentation with AI agent.
- Update public API.

## [1.1.9] - 2024-06-19
### Changed
- OMPE-8355: Updated documentation.

## [1.1.8] - 2024-06-14
### Changed
- OMPE-8355: Updated documentation with AI agent for omni.kit.widget.nucleus_connector.

## [1.1.7] - 2024-06-04
### Fixed
- Safeguard ui elements accessing when showing/hiding when it's None

## [1.1.6] - 2024-04-30
### Changed
- OM-122760: Reduce the retry time for omni client connecting.

## [1.1.5] - 2024-03-20
### Changed
- Make pip_archive optional for qrcode support

## [1.1.4] - 2023-10-19
### Changed
- Increase code coverage to 93.2%

## [1.1.3] - 2023-10-12
### Changed
- OMFP-2249: [John Han] Dont show the loading bar (do nothing) when user clicked "OK" without a name/url present

## [1.1.2] - 2023-09-20
### Changed
- OM-109813: Removed pip install for qrcode package if it cannot be imported and add pip_archive as dependency to use
  the package that comes with pip_prebundle.

## [1.1.1] - 2023-09-05
### Changed
- Changed url in device auth flow dialog to be a read-only string field so it can be copied by user

## [1.1.0] - 2023-07-19
### Added
- Added device auth flow for cases when kit is running headless or in OVC environment

## [1.0.11] - 2023-07-03
### Fixed
- Fixed issue with indented AlertPane display, fixed error in reconnect

## [1.0.10] - 2023-06-02
### Fixed
- Fixed issue with adding new connection, don't destroy auth dialogs on end flow and leave destroy process to gc

## [1.0.9] - 2023-05-25
### Changed
- Create connector dialog on demand so it shows up correctly in detached window

## [1.0.8] - 2023-05-23
### Fixed
- Fixed issue with canceling

## [1.0.7] - 2023-03-23
### Changed
- Add width to AlertPane, fix issue with connector dialog randomly resized to a thin long window

## [1.0.6] - 2023-02-17
### Added
- Adds authentication mode to ConnectorDialog, shows a simplified UI with only login info and cancel button
- Connecting to named server/reconnect/auth will now use authentication mode of ConnectorDialog

## [1.0.5] - 2023-02-01
### Changed
- Update ui to focus fields on show

## [1.0.4] - 2023-01-30
### Changed
- Make the url field to be focused for keyboard input

## [1.0.3] - 2023-01-25
### Changed
- Fixed tests to be able to run in random order

## [1.0.2] - 2022-12-08
### Added
- No longer cancels unaccounted authentication
- Emits event upon successful connection

## [1.0.1] - 2022-09-23
### Added
- Fixes hang on browser login page.

## [1.0.0] - 2022-07-20
### Added
- Initial commit to master.
