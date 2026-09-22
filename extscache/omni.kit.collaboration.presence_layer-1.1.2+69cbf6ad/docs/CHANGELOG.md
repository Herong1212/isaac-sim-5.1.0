# Changelog

## [1.1.2] - 2025-04-26
### Changed
- OMPE-39146: Remove hard code for "omnverse".

## [1.1.1] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [1.1.0] - 2025-02-10
### Changed
- OMPE-25657: Update public API

## [1.0.10] - 2024-12-20
### Changed
- OMPE-31903: Use omni.usd.make_valid_identifier instead of Tf.MakeValidIdentifier to support unicode characters.

## [1.0.9] - 2023-12-12
### Changed
- Add docs for presence layer.

## [1.0.8] - 2023-10-16
### Changed
- Increase code coverage with mock api of live syncing.

## [1.0.7] - 2023-08-16
### Changed
- Order of layer event handler.

## [1.0.6] - 2023-08-14
### Changed
- Don't follow user when the user has no valid bound camera shared.

## [1.0.5] - 2023-07-13
### Changed
- Improve layer events handling to only handle interested events.

## [1.0.4] - 2023-07-03
### Changed
- Report warning when it's to follow myself.

## [1.0.3] - 2023-06-23
### Changed
- Only handle live sync events from root layer session.

## [1.0.2] - 2023-05-16
### Changed
- API exposes the shared stage.

## [1.0.1] - 2023-04-10
### Changed
- Add more tests and improve API to enter follow mode.

## [1.0.0] - 2023-03-28
### Changed
- Initial extension.
