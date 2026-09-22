# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.11] - 2024-08-13
### Changed
- OMPE-18535: Force update tips after paste+Enter.

## [2.0.10] - 2024-07-11
### Changed
- Updated documentation with AI agent.

## [2.0.9] - 2023-11-08
### Added
- OM-75838: Don't auto select tooltips item when subfolder exists with the filename in it.

## [2.0.8] - 2023-10-17
### Added
- Tests to increase the code coverage.

## [2.0.7] - 2023-06-18
### Added
- # By John Han <johan@nvidia.com>, fix OM-93524, OM-93228, OM-93015
- Move the widgets down in the path field to make it align center by 4 pixels.
- Re-place the popup window according to main window resized.

## [2.0.6] - 2023-05-23
### Added
- Added begin edit subscription for path field string field and apply specified handler.

## [2.0.5] - 2023-05-03
### Changes
- OM-93184: Able to use in modal window

## [2.0.4] - 2022-11-09
### Changes
- Fix to toml file

## [2.0.3] - 2021-06-16
### Changes
- Fixes double "//" at the end of the path string.

## [2.0.2] - 2021-04-23
### Changes
- Fix to breadcrumbs on Linux returning incorrect paths resulting in Connection Errors.

## [2.0.1] - 2021-02-10
### Changes
- Updated StyleUI handling

## [2.0.0] - 2020-01-03
### Updated
- Refactored for async directory listing to improve overall stability in case of network delays.
### Added
- Keyword Arg: 'branching_options_handler'
### Deleted
- Keyword Arg: 'branching_options_provider'

## [0.1.6] - 2020-11-20
### Added
- Don't Execute "apply path" on directory changes, only when user hits Esc or Enter key.

## [0.1.5] - 2020-11-20
### Added
- Fixes occasionally jumbled-up breadcrumbs.

## [0.1.4] - 2020-09-18
### Added
- Initial commit to master.
