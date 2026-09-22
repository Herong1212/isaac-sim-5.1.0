# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.2.11] - 2025-06-26
### Fixed
- OMPE-50278: Fix crash when dereferencing nullptr for stage in test test_open_stage_with_live_session_mock.

## [2.2.10] - 2025-05-30
### Changed
- OMPE-49021: Put open stage in a thread to avoid blocking the main thread on auth.

## [2.2.9] - 2025-05-01
### Changed
- Prepare for Python-3.12

## [2.2.8] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [2.2.7] - 2025-04-24
### Changed
- OMPE-43458: Fix test error in test_workflow_livesyncing.

## [2.2.6] - 2025-04-17
### Changed
- Refactor UsdNotice handling to target stages and handle Sdf.Layer mutedness for OpenUSd-25.02

## [2.2.5] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [2.2.4] - 2025-03-31
### Changed
- OMPE-37291: Improved error reporting for USD crate file version mismatch when creating layer reference.

## [2.2.3] - 2025-03-11
## Changed
- OMPE-24091: If underlying channel reports error, stop and remove live session.

## [2.2.2] - 2025-01-23
## Fixed
- OMPE-33230: Don't check availability for omni.kit.widget.versioning when creating checkpoint.

## [2.2.1] - 2025-01-22
## Fixed
- OMPE-30471: Change back LiveSession.modifiedTimestamp to seconds and fix issue with live session sort order.

## [2.2.0] - 2024-09-17
## Fixed
- OMPE-20299: Issue with invalid customStateDelegate

## [2.1.36] - 2024-09-05
## Added
- OMPE-12316: Add test for local path resolving.

## [2.1.35] - 2024-07-26
## Changed
- OMPE-14264: Fix issue with ETM test for omni.graph.test test_path_attribute.

## [2.1.34] - 2024-03-27
## Changed
- OMPRW-311: Fix some errors encountered during unit test.

## [2.1.33] - 2024-02-22
## Changed
- OMPRW-838: Improve locking to persist lock status.

## [2.1.32] - 2023-12-13
## Changed
- Copy all metas from stage after new layer creation.

## [2.1.31] - 2023-12-12
## Changed
- Add more docs.

## [2.1.30] - 2023-12-08
## Changed
- Improve mock utils to support live prim.

## [2.1.29] - 2023-11-30
## Changed
- In a live session, if a user is not the owner and tries to save the stage, show warning message in console.

## [2.1.28] - 2023-11-27
## Changed
- Fix crash that's caused by removing live session folder.

## [2.1.27] - 2023-11-13
## Changed
- Improve mock utils to create mocked live layers.

## [2.1.26] - 2023-10-27
## Changed
- Send out sublayer refresh event for layer reload.

## [2.1.25] - 2023-10-26
## Changed
- Add test util function for forbidding user merge.

## [2.1.24] - 2023-10-24
## Changed
- Mock user join/left with channel message.

## [2.1.23] - 2023-10-18
## Changed
- Add open stage callback register for the use of e.g. Activiy window

## [2.1.22] - 2023-10-18
- Add more tests to increase code coverage.
- Fix issues for mock utils.

## [2.1.21] - 2023-10-16
- Add mock utils for unittests that don't depend on real server states.

## [2.1.20] - 2023-10-13
- Fix crash caused by accessing released session handle.

## [2.1.19] - 2023-09-18
- Make omni.kit.collaboration.channel_manager optional.

## [2.1.18] - 2023-07-17
- Fix test on OVC

## [2.1.17] - 2023-07-13
- Improve layer event handling to only handle interested events.

## [2.1.16] - 2023-07-07
- Add API to get owner of layer.
- Fix ownership check.

## [2.1.15] - 2023-07-07
- Delays authoring target change if join live session is batched with Sdf.ChangeBlock.

## [2.1.14] - 2023-06-23
- Add API for LayerEventPayload to query influenced layers.

## [2.1.13] - 2023-06-19
- Add modified time for live session to support sorting by access time.

## [2.1.12] - 2023-06-13
- Fix possible crash that's caused by re-parenting live prims.

## [2.1.11] - 2023-05-26
- Creates default prim as over instead of def for live layer of live prim to instruct duplication logic.

## [2.1.10] - 2023-05-23
- Add settings to control display of outdate notifications.

## [2.1.9] - 2023-05-11
- Fix issue that live sessions cannot be found for several of them when multiple layers are in the same folder.

## [2.1.8] - 2023-04-30
- Tweaked auto reload behavior to work better with live sessions.

## [2.1.7] - 2023-04-28
- Extends LayerEventType to add AUTO_RELOAD_LAYERS_CHANGED event for notifying list change of auto reload layers.

## [2.1.6] - 2023-04-20
- Add API to add/remove auto-reload prims.

## [2.1.5] - 2023-04-11
- Respect in_live_session status when reloading layers.
- Added the ability to filter outdated layers by in_session status.

## [2.1.4] - 2023-04-10
- Improve live prim support to support joining live session for multiple prims with the same base layer.

## [2.1.3] - 2023-03-28
- Add utils to get short user name for live session user.

## [2.1.2] - 2023-03-22
- Ensure single leader in the live session.

## [2.1.1] - 2023-03-21
- Don't allow auto-authoring when stage is in any live session.
- Add interface to cancel session join.

## [2.1.0] - 2023-03-14
- Supports auto-reload interfaces to get/fetch outdated layers.

## [2.0.20] - 2023-03-15
- Add supports to follow user in a live session.

## [2.0.19] - 2023-03-08
- Add interface to open stage with live session joined.

## [2.0.18] - 2023-03-07
- More improvements to runtime performances of subscribing all layres except sublayers.

## [2.0.17] - 2023-03-07
- Fix issue to join session for prim to make sure default prim of live layer is the same as base layer.

## [2.0.16] - 2023-02-24
- More improvements to the performance of loading stage with thousands of layers.

## [2.0.15] - 2023-02-23
- Add supports to create live session for references/payloads.

## [2.0.14] - 2023-02-20
- Only copy interested layer meta into live layer when it's in a live session.

## [2.0.13] - 2023-02-17
- Fix performance regression of loading stage.

## [2.0.12] - 2023-02-14
- Save target layer after merging live session.
- Add support to refresh payloads and references if they are outdated.

## [2.0.11] - 2023-01-12
- Add user color support for live session user.

## [2.0.10] - 2022-11-30
- Fix permission issue for sublayer live session if root layer is anonymous.

## [2.0.9] - 2022-11-09
- Fix flaky specs_locking test

## [2.0.8] - 2022-11-02
- Add API for fetching logged-in user and id for layer.
- New events before/after merging live session.

## [2.0.7] - 2022-10-28
- Fix issue that session creates with different DNS alias cannot be found.

## [2.0.6] - 2022-10-27
- Fix UI issue that can show two sublayers as edit target.

## [2.0.5] - 2022-10-21
- Fix regression to merge live session to new layer.

## [2.0.4] - 2022-10-20
- Fix live session list refresh issue created by other connectors.

## [2.0.3] - 2022-10-15
- Fix issue to parse payload of LIVE_SESSION_LIST_CHANGED event.

## [2.0.2] - 2022-10-12
- Fix join live session by url that returns invalid session pointer.

## [2.0.1] - 2022-10-05
- Fix crash if a session is joined and it's removed from disk.
- Fix edit target switch issue after joining live session.
- Notification to remind saved session inside opened stage.

## [2.0.0] - 2022-09-29
- Re-work omni.kit.usd.layers to support sublayer live sesison.

## [1.1.8] - 2022-09-20
- Fix layer refresh if layer stack includes duplicate sublayer.
- Fix crash to switch muteness scope.

## [1.1.7] - 2022-09-13
- Ignore case for comparing session management message.
- Synchronize layer meta between root and live root layer in live session.

## [1.1.6] - 2022-08-09
- Fix layer version refresh

## [1.1.5] - 2022-08-05
- Add version safeguard for TOML file.

## [1.1.4] - 2022-07-25
- Fix duplicate outdate notification.
- Move outdate notification from layer view into this extension.

## [1.1.3] - 2022-07-20
- Add API to support link live layer to specific base layer for supporting projec workflow of other connectors.

## [1.1.2] - 2022-07-11
- Fix merge_changes_to_specific_layer and add tests.

## [1.1.1] - 2022-06-15
- Move channel management into this extension from layers view.

## [1.1.0] - 2022-05-31
- Supports new live workflow.

## [1.0.0] - 2022-03-31
- Initial extension.
- Refactoring omni.usd to move layers interface to this extension.
