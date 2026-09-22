# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [107.0.0] - 2024-10-11
### Changed
- Use omni.kit.ui_test.emulate_mouse_move for test.

## [106.0.1] - 2024-10-11
### Fixed
- OMPE-22569: Update public API.

## [104.7.5] - 2024-08-07
### Changed
- OMPE-16870: Improve omni.kit.manipulator.transform startup time.

## [104.7.4] - 2024-04-22
### Added
- Documentations

## [104.7.3] - 2024-04-11
### Changed
- move the omni.kit.app.get_app() call to the method to avoid repo docs issue of failed to acquire interface: omni::kit::IApp

## [104.7.2] - 2023-10-10
### Changed
- Expanded the toolbar by default with a setting and an init arg to override such behavior.

## [104.7.1] - 2023-09-13
### Changed
Changed default omni scale to both horizontal and vertical.

## [104.7.0] - 2023-08-25
### Changed
- Changed how omni scale manipulation work. Default now is move up to scale up and down to scale down. It can also be configure to move right to scale up and left to scale down, or use both horizontal and vertical direction at the same time.

## [104.6.14] - 2023-06-14
### Changed
- Changed `SnapSettingsListener` to better handle array setting.

## [104.6.13] - 2023-01-12
### Added
- Made gesture payload classes dataclass and declared members and types.

## [104.6.12] - 2022-12-12
### Changed
- Removed manual DPI scaling for toolbar since sc.Widget now is DPI-aware.

## [104.6.11] - 2022-11-29
### Added
- Allow toolbar context menu to be trigger by pressing right mouse button on it.

## [104.6.10] - 2022-11-15
### Changed
- Implement OM-59447, move preference page to omni.kit.viewport.menubar.settings

## [104.6.9] - 2022-09-29
### Changed
- Allow tool button to have different tooltips on enabled/disabled state.

## [104.6.8] - 2022-09-01
### Changed
- Updated context menu to VP2 style.

## [104.6.7] - 2022-08-16
### Fixed
- Fixed error when changing the size of the manipulator.

## [104.6.6] - 2022-08-11
### Fixed
- Fixed typo of `SimpleScaleChangedGesture`'s base class to `ScaleChangedGesture`

## [104.6.5] - 2022-07-14
### Added
- Added tooltip support for manipulator toolbar items.

## [104.6.4] - 2022-07-07
### Changed
- Fixed incorrect toolbar width.
- Shrunk the click through prevention area of toolbar when it's collapsed.

## [104.6.3] - 2022-06-28
### Changed
- Do not prevent camera orbit when ALT is down and mouse hovering over manipulator.

## [104.6.2] - 2022-06-22
### Added
- Fixed toolbar clipping.

## [104.6.1] - 2022-06-01
### Added
- Exposed setting to change intersection thickness for lines and arcs.
- Exposed setting to enable/disable free rotation.

## [104.6.0] - 2022-05-19
### Added
- Allow additional payload to be passed into toolbar button context menu via `tool_button_additional_payload`
### Changed
- Adjusted toolbar icon size.
- Hide instead of collapse toolbar during manipulation.
- Other minor changes to accommodate snap changes.

## [104.5.0] - 2022-05-12
### Added
- Added a mini toolbar framework below the manipulator.

## [104.4.0] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.4.0] - 2022-04-18
### Added
- Added free rotation manipulator.
### Changed
- Rotation angle overlay now confined within [-180, 180) range to reduce visual obstruction.

## [1.3.12] - 2022-04-04
### Changed
- Do not trigger gestures when ALT is down (during camera manipulation).

## [1.3.11] - 2022-03-28
### Changed
- Improved scale manipulator.

## [1.3.10] - 2022-03-15
### Changed
- Increased the manipulator thickness

## [1.3.9] - 2022-03-15
### Changed
- Using different thickness and intersection thickness, so it's more handy to
  grab the manipulator

## [1.3.8] - 2022-03-11
### Fixed
- Don't prevent transform gesture in the middle of drag

## [1.3.7] - 2022-03-09
### Changed
- Added `order` for manipulator gesture and make the center "sphere" with higher selection priority than handles.

## [1.3.6] - 2022-03-08
### Changed
- Changed persistent setting path for manipulator scale to enforce the new default scale.

## [1.3.5] - 2022-03-07
### Changed
- Hovering on the center "ball" of scale manipulator now highlights the 3 quads.

## [1.3.4] - 2022-03-07
### Changed
- Set default manipulator scale to 1.4 and removed no longer needed manual DPI scaling.
- Moved quad translate gizmo out a bit for easier selection.

## [1.3.3] - 2022-02-28
### Changed
- Set default manipulator scale to 1.25
- Hovering on the center "ball" of translate manipulator now highlights the 3 quads.
- Fixed initial state of manipulator out of sync with model.

## [1.3.2] - 2022-02-22
### Changed
- Fixed out-of-sync highlighting state.
- Adjusted sizes of some manipulator components.
- Made hidden rotation Arc unselectable.

## [1.3.1] - 2022-02-08
### Changed
- The names of tests are shorter to make sure they fits to the line length
limitations.

## [1.3.0] - 2022-01-25
### Added
- Added highlighting when manipulator is hovered or dragged.

## [1.2.0] - 2021-12-06
### Changed
- A `canceled` event now calls `on_canceled` function on a `TransformChangedGesture` subclass.
- Added gesture preventer so only one transform operation can be performed at the same time.

## [1.1.2] - 2021-12-02
### Changed
- Fixed weakref on unsubscribe.

## [1.1.1] - 2021-12-01
### Removed
- Added prevention logic for fighting with selection-box in Viewport.

## [1.1.0] - 2021-11-29
### Added
- Added a global scaling factor for Transform Manipulator size.
- Supported DPI scaling (Won't change scale when drag across monitors with different DPI scaling).
### Changed
- Moved multi-select manipulator placement setting from omni.kit.manipulator.prim to omni.kit.manipulator.transform.
- Conformed to new omni.ui.scene API.

## [1.0.0] - 2021-09-23
### Added
- Init commit.
