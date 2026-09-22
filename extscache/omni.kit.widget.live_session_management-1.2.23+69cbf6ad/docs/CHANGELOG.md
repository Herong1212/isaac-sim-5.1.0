# Changelog

Omniverse Kit Shared Live Session Widgets

## [1.2.23] - 2025-04-14
### Changed
- Updated documentation with AI agent.

## [1.2.22] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [1.2.21] - 2024-12-03
- OMPE-25680: Update public API.

## [1.2.20] - 2024-03-27
- OMPRW-311: Fix some errors encountered during unit test.

## [1.2.19] - 2023-12-12
### Changes
- Improve API docs.

## [1.2.18] - 2023-11-16
### Changed
- Increase code coverage.
- OM-114885: Removed "Open Debug Window" menu item

## [1.2.17] - 2023-11-07
### Changed
- Renamed preference page from Live Session to Live.

## [1.2.16] - 2023-11-07
### Changed
- Changed quick live connect button to show dialog with a setting to configure previous vs new behavior.

## [1.2.15] - 2023-11-06
### Changed
- Possible fix for building user list when live users are over 10.

## [1.2.14] - 2023-07-27
### Changes
- Moved shareable components to omni.kit.widget.live_session_management.ui

## [1.2.13] - 2023-07-13
### Changes
- Improve layer events handling to only handle interested events.

## [1.2.12] - 2023-07-07
### Changes
- Check file ownership before merge.

## [1.2.11] - 2023-07-07
### Changes
- Batch reload and join.

## [1.2.10] - 2023-07-03
### Changes
- Don't follow myself.

## [1.2.9] - 2023-06-23
### Changes
- Fix cherry-pick issue.
- Filter event to handle events from interested sources only.

## [1.2.8] - 2023-06-19
### Changes
- Sort live session list by access time.

## [1.2.7] - 2023-06-09
### Changes
- Add setting to control live session management to be viewer only without merge menu.

## [1.2.6] - 2023-06-07
### Changes
- Fixed user limitation in overflow tooltip.

## [1.2.5] - 2023-06-02
### Changes
- UX fine-tune to report user-friendly error.
- Ensure session is selected in `Join Session` panel after switching from `Create Session` panel.

## [1.2.4] - 2023-05-17
### Changes
- Added right click menu to set timeline presenter.
- Changed user icon of the timeline presenter.

## [1.2.3] - 2023-04-28
### Changes
- Added support for global reload setting to affect the rest of UI.

## [1.2.2] - 2023-04-28
### Changed
- Improved handling for auto reloading prims while in live session.

## [1.2.1] - 2023-04-21
### Added
- Add maximum users control to LiveSessionUserList widget.

## [1.2.0] - 2023-04-11
### Added
- reload_outdated_layers function that respects a layers in_live_session state.

## [1.1.9] - 2023-03-28
### Changed
- Add widget LiveSessionUserList to track all users in a live session.
- Add widget LiveSessionCameraFollowerList to track all users that are following the camera in a live session.
- More utils.

## [1.1.8] - 2023-03-27
### Changed
- Add timeline session menu items.

## [1.1.7] - 2023-03-08
### Changed
- Add options to copy link of live session and open stage with live session joined.

## [1.1.6] - 2023-03-07
### Changed
- Supports to join live session for reference or payload prim.

## [1.1.5] - 2023-02-18
### Changed
- Simplified join live session prompt, enabled quick-join.

## [1.1.4] - 2023-02-17
### Changed
- Report error if target layer is not writable.

## [1.1.3] - 2022-11-21
### Changed
- Prompt if layer is outdate or dirty before live.

## [1.1.2] - 2022-10-27
### Changed
- Fix deprecated API warnings.

## [1.1.1] - 2022-10-15
### Changed
- Fix issue to refresh session list.

## [1.1.0] - 2022-09-29
### Changed
- Supports sublayer live session workflow.

## [1.0.6] - 2022-09-02
### Changed
- Add name validator for session name input.

## [1.0.5] - 2022-08-30
### Changed
- Show menu options for join.

## [1.0.4] - 2022-08-25
### Changed
- Notifications for read-only stage.

## [1.0.3] - 2022-08-09
### Changed
- Notify user before quitting application that session is live still.

## [1.0.2] - 2022-07-19
### Changed
- Shows menu still even session is empty when it's not forcely quit.

## [1.0.1] - 2022-06-29
### Changed
- Supports more options to control session menus.

## [1.0.0] - 2022-06-15
### Fixed
- Initialize extension.
