# Changelog

This document records all notable changes to the **omni.kit.window.property** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.12.1] - 2025-02-21
### Changes
- OMPE-37362: Improved documentation for ButtonItem

## [1.12.0] - 2025-02-11
### Changes
- OMPE-33113: added "ButtonItem" & "build_frame_header_with_buttons"

## [1.11.6] - 2025-01-13
### Changes
- OMPE-27796, OMPE-27800: Updated public API

## [1.11.5] - 2024-10-11
### Changes
- Updated API and __all__ exports

## [1.11.4] - 2024-07-23
### Changed
- Fixed private class access (accessing functions/variables with _)

## [1.11.3] - 2025-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.11.2] - 2024-05-17
### Fixed
- Fixed linting issues

## [1.11.1] - 2024-04-17
### Updated
- Removed omni.usd dependency

## [1.11.0] - 2024-03-22
### Updated
- Updated documentation

## [1.10.0] - 2024-03-01
### Changed
- Updated to use omni.kit.widget.context_menu

## [1.9.10] - 2024-02-09
### Changed
- Moved on_collapsed_changed into SimplePropertyWidget so it can be sub-classed

## [1.9.9] - 2023-11-02
### Changed
- Updated menus to use omni.kit.menu.utils

## [1.9.8] - 2023-08-17
### Changed
- Property window becomes paused when its not visible

## [1.9.7] - 2023-07-07
### Changed
- Property panel can retain its scrolled position

## [1.9.6] - 2023-05-26
### Added
- Added style for `ComboBox::choices:disabled`.

## [1.9.5] - 2023-04-04
### Changed
- Clear widgets when property window is hidden to reduce background CPU usage.

## [1.9.4] - 2023-03-09
### Fixed
- Allow property widgets to rebuild after an exception is thrown from their build_fn

## [1.9.3] - 2023-03-09
### Fixed
- Fixed managed frame as wasn't keeping users state

## [1.9.2] - 2023-03-08
### Changed
- Swapped a couple asyncio.ensure_future calls with run_coroutine

## [1.9.1] - 2023-02-21
### Added
- Restore internal _window_frame variable that physics property tests were using
- Add public API to set Window and ScrollingFrame kwargs

## [1.9.0] - 2023-02-01
### Added
- Add property search/filter feature

## [1.8.3] - 2022-11-25
### Added
- Fixed `notify("", "")` as it didn't change the schema or payload

## [1.8.2] - 2022-08-08
### Added
- Added style for `Grab` color.

## [1.8.1] - 2021-04-26
### Changed
- Added `identifier` parameter to `add_item_with_model` to set StringField identifier

## [1.8.0] - 2021-03-17
### Changed
- Changed builder function to a class member to enable polymorphism

## [1.7.0] - 2022-02-14
### Added
- Added context menu for collapsible header
- Added `request_rebuild`

## [1.6.3] - 2021-06-29
### Changed
- Added Field::url style

## [1.6.2] - 2021-06-21
### Changed
- Fixed issue with layer metadata not showing sometimes

## [1.6.1] - 2021-05-18
### Added
- Updated Checkbox style

## [1.6.0] - 2021-04-28
### Added
- Added `paused` property to Property Window API to pause/resume handling `notify` function.

## [1.5.5] - 2021-04-23
### Changed
- Fixed exception when using different payload class

## [1.5.4] - 2021-04-21
### Changed
- Added warning if build_items takes too long to process

## [1.5.3] - 2021-02-02
### Changed
- Used PrimCompositionQuery to query references.
- Fixed removing reference from a layer that's under different directory than introducing layer.
- Fixed finding referenced assets in Content Window with relative paths.

## [1.5.2] - 2020-12-09
### Changed
- Added extension icon
- Added readme
- Updated preview image

## [1.5.1] - 2020-11-20
### Changed
- Prevented exception on shutdown in simple_property_widget function `_delayed_rebuild`

## [1.5.0] - 2020-11-18
### Added
- Added `top_stack` parameter to `PropertyWindow.register_widget` and `PropertyWindow.unregister_widget`. Set True to register the widget to "Top" stack which layouts widgets from top down. False to register the widget to "Button" stack which layouts widgets from bottom up and always below the "Top" stack. Default is True. Order only matters when no `PropertySchemeDelegate` applies on the widget.

## [1.4.0] - 2020-11-16
### Added
- Added `reset` function to `PropertyWidget`. It will be called when a widget is no longer applicable to build under new scheme/payload.

## [1.3.1] - 2020-10-22
### Added
- Changed style label text color

## [1.3.0] - 2020-10-19
### Added
- Added "request_rebuild" function to "SimplePropertyWidget". It collects rebuild requests and rebuild on next frame.

## [1.2.0] - 2020-10-19
### Added
- Added get_scheme to PropertyWindow class.

## [1.1.0] - 2020-10-02
### Changed
- Update to CollapsableFrame open by default setting.

## [1.0.0] - 2020-09-17
### Added
- Created.
