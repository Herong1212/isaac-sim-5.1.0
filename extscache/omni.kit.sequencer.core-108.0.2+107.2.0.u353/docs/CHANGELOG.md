# Changelog

## [108.0.2] - 2025-05-22
### Changed
- Added major and minor version lock on `omni.kit.sequencer.usd`.

## [108.0.0] - 2025-02-11
- target kit 107.0 with abi=1

## [107.0.0] - 2024-12-04
- Update kit sdk to 107.

## [103.4.1] - 2023-12-19

- Remove exact dependencies.

## [103.4.1] - 2023-06-05

- Startup optimizations.

## [103.4.0] - 2022-10-06

- Branched.

## [103.3.0] - 2022-10-06

- Minor fixes for Create 2022.3 release.

## [103.2.0] - 2022-05-05

- Fix issue with update_clip_time option in SequencerClipSetTargetCommand if no animation target.

## [103.1.2] - 2022-04-11

- `SequencerClipSetAnimationCommand` can now set animation to `None`.

## [103.1.1] - 2022-03-30

- Bump `kit-sdk` and `repo-tools`

## [103.1.0] - 2022-03-09

- Fix clip selection with split command.

## [103.0.6] - 2022-02-11

- Fixed kit-sdk version warning.

## [103.0.5] - 2022-01-06

- Add command to split clips.

## [103.0.4] - 2021-12-17

- Cleanup get_interface() usage.

## [103.0.3] - 2021-12-13

- Added SequencerClipUpdateTrimCommand to set playStart and playEnd.
- Setting a new target prim will update clip playStart and playEnd.

## [103.0.2] - 2021-12-09

- New clips set playStart and playEnd by default.

## [103.0.1] - 2021-11-19

- Extension cleanup.
- Moved command from window extension to core.

## [103.0.0] - 2021-10-22

- Update to kit-sdk 103

## [102.1.2] - 2021-10-22

- Fix errors with undo creation of prims when encountering unexpected children prims.

## [102.1.0] - 2021-06-24

- First version compatible with Kit 102
