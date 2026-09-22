# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.1.11] - 2025-04-14
### Changed
- Updated documentation with AI agent.

## [2.1.10] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [2.1.9] - 2024-12-03
- OMPE-25680: Update public API.

## [2.1.8] - 2024-08-26
- Fixed error when updating tooltips.

## [2.1.7] - 2024-05-29
- Removed extraneous test flags

## [2.1.6] - 2023-10-18
- More code coverage.

## [2.1.5] - 2023-10-16
- Increase code coverage with mock api of live syncing.

## [2.1.4] - 2023-10-12
### Added
- /app/liveSession/enableMenuFollowUser settings to enable/disable follow user UI

## [2.1.3] - 2023-07-13
- Improve layer events handling to only handle interested events.

## [2.1.2] - 2023-06-23
- Only handle live syncing events from root layer session.

## [2.1.1] - 2023-05-17
- Add right click menu to user icon.

## [2.1.0] - 2023-05-04
- Separate cache indicator from live widget into omni.kit.widget.cache_indicator.

## [2.0.8] - 2023-04-20
- Fix cache indicator when Hub is not being used (bug introduced in previous version).

## [2.0.7] - 2023-04-06
- Show "HUB" in the cache indicator if Hub is enabled.

## [2.0.6] - 2023-03-28
- Replace widgets with omni.kit.live_session_management.LiveSessionUserList

## [2.0.5] - 2023-03-01
- More unittests for live button.

## [2.0.4] - 2023-01-12
- Change user icon style.
- Add local user to the user list.

## [2.0.3] - 2022-09-29
- Use new omni.kit.usd.layers interfaces.

## [2.0.2] - 2022-08-30
### Changes
- Show menu options for join.

## [2.0.1] - 2022-07-19
### Changes
- Show app name for user in the live session.

## [2.0.0] - 2022-06-29
### Changes
- Refactoring live widget to move all code into python.

## [1.0.0] - 2022-06-13
### Changes
- Initialize live widget changelog.