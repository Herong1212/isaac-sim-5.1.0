# CHANGELOG

This document records all notable changes to ``omni.kit.widget.searchfield`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [1.1.8] - 2024-06-18
### Changed
- Updated documentation with AI agent.

## [1.1.7] - 2024-05-17
### Changed
OM-124244: Added public set_filter function

## [1.1.6] - 2024-02-19
### Added
- OM-120427: Allow changing the separator or disabling it.

## [1.1.5] - 2023-10-18
### Changed
- Increase code coverage to 91%

## [1.1.4] - 2023-10-05
### Changed
- Remove import of omni.kit.pipapi from test

## [1.1.3] - 2023-09-07
### Changed
- Updated test function emulate_search_field from double click to click & double click as 1st click gets focus

## [1.1.2] - 2023-09-06
### Changed
- OM-107704: Make sure text left aligned when double click
- OM-107724: double click to edit all words when suggestion enabled

## [1.1.1] - 2023-03-08
### Changed
- OM-81777: Buttons to show suggestions instead of Treeview

## [1.1.0] - 2023-02-07
### Added
- Add suggestion mode to show suggestion list when input in search field
- Add property "search_words" to preset search words in search field

## [1.0.12] - 2023-02-01
### Changed
- Move to kit repo

## [1.0.11] - 2023-01-31
### Changed
- Remove dependency of omni.kit.ui_test

## [1.0.10] - 2023-01-10
### Changed
- OM-77207: Increase test image threshold for ETM failure with kit 105

## [1.0.9] - 2023-01-03
### Changed
- OM-77207: Add "--no-window" otherwise test always failed in kit 105

## [1.0.8] - 2022-11-11
### Changed
- OM-70923: Focus keyboard back to search field if all search words cleared to exit the "searching" UI when it losts focus

## [1.0.7] - 2022-10-11
### Changed
- Fix issue if do not show tokens

## [1.0.6] - 2022-04-11
### Add
- Add tests for searchfield

## [1.0.5] - 2022-01-20
### Add
- API to clear search field

## [1.0.4] - 2021-05-10
### Changed
- Update ui to display well in View
### Added
- Example page for omni.kit.widget.examples

## [1.0.2] - 2021-04-28
### Added
- Option to show tokens
- Double click to convert tokens into full string

## [1.0.1] - 2021-04-27
### Added
- Show individual control for every search word

## [1.0.0] - 2021-04-27
### Added
- Initial version implementation
