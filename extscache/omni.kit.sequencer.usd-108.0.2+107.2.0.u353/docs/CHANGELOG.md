# Changelog

## [108.0.2] - 2025-05-22
- Added version lock on dependencies.

## [108.0.0] - 2025-02-11
- target kit 107.0 with abi=1
- Allow omni.usd.schema.sequence to have major change.
- remove unneeded test dependencies.

## [107.0.0] - 2024-12-04
- Update kit sdk to 107.

## [103.4.6] - 2024-09-06
- OMPE-20564: Fix extension startup warning of deprecated usage for pxr.OmniAudioSchema

## [103.4.5] - 2024-07-06
- Updated Kit SDK to 106.
- Fixed a bug that infinit error messages are printed when reopening a stage that contains a sequence.

## [103.4.4] - 2024-01-11

- Bump kit-sdk to `105.2`.
- Update curve dependency to use `omni.anim.curve.core`.

## [103.4.3] - 2023-12-19

- Remove exact dependencies.

## [103.4.2] - 2023-06-06

- Supports new format of animation curve.

## [103.4.1] - 2022-06-05

- Startup optimizations.

## [103.4.0] - 2022-09-06

### New

- Branched

## [103.3.0] - 2022-09-06

### New

- Supports new format of curve animation.

## [103.2.0] - 2022-07-15

# New

- OM-41985 - Sequence player now allows user to override camera even when camera sync is enabled. Viewport camera menu item added to be able to switch on and off the sequencer sync.

## [103.1.4] - 2022-04-22

- OM-48690 - Add function to test whether or not sequence schema is loaded and concrete.

## [103.1.3] - 2022-04-21

- OM-49312 - Could not find the stage update node index errors
- Getting audio length now returns the source asset length.

## [103.1.2] - 2022-04-20

- Automated tests added

## [103.1.1] - 2022-03-30

- Bump `kit-sdk` and `repo-tools`

## [103.1.0] - 2022-03-02

## Fixes

- OM-45217 - Sequencer - After using hold - Loop no longer works.

## [103.0.9] - 2022-02-23

- Made viewport dependencies optional.

## [103.0.8] - 2022-02-17

- Added support for new viewports.

## [103.0.7] - 2022-02-11

- Fixed kit-sdk version warning.

## [103.0.6] - 2022-01-06

- Unused functions removed from usd_sequencer.
- New functions for trim and split utils added.

## [103.0.5] - 2021-12-17

- Cleanup get_interface() usage.

## [103.0.3] - 2021-12-09

- Fix for rename of omni.kit.viewport

## [103.0.2] - 2021-11-19

- added get_clip_available_length().
- get_clip_source_length() returns None if playStart and playEnd are not set.

## [103.0.1] - 2021-11-15

- get_clip_source_length() returns 0 instead of None if not target or anim prim.

## [103.0.0] - 2021-10-22

- Update to kit-sdk 103

## [102.1.5] - 2021-10-04

### Fixes

- Viewport dependency issue

## [102.1.4] - 2021-10-04

### Fixes

- OM-38865 - Toggle sequencer camera button errors

## [102.1.3] - 2021-06-24

- Improvements to Player interface to allow suspend, resume, and async updates.

## [102.1.0] - 2021-06-24

- First version compatible with Kit 102
