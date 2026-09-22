# Changelog

This document records all notable changes to the **omni.kit.viewport.utility** extension.

The format is based on [Keep a Changelog](https://keepachangelog.com). The project adheres to [Semantic Versioning](https://semver.org).

## [1.1.2] - 2025-04-04
### Removed
- Legacy Viewport wrappers, arguments, and conditionals

## [1.1.1] - 2025-04-02
### Fixed
- add_aov_to_viewport function to target current or session layer based on whether render settings are transient or not.

## [1.1.0] - 2025-02-21
### Added
- Viewport capture support for capturing a specific SWH frame number.
### Changed
- capture_viewport_and_wait now waits for the capture object to start capturing before starting its 3 frame wait count.

## [1.0.19] - 2025-01-13
### Changed
- next_viewport_frame_async to new API

## [1.0.18] - 2024-11-21
### Added
- Updated missing `get_active_viewport_window` public API

## [1.0.17] - 2024-04-22
### Added
- Documentations

## [1.0.16] - 2023-07-05
### Fixed
- Typo in create_viewport_window

## [1.0.15] - 2023-05-10
### Changed
- Make toggle_global_visibility call through to new action.

## [1.0.14] - 2023-01-25
### Added
- get_ground_plane_info API call.

## [1.0.13] - 2022-12-09
### Added
- Be able to pass a prim path to focus on

## [1.0.12] - 2022-10-17
### Added
- disable_context_menu API to disable contet menu for single or all Viewport.
- Support legacy global disabling of context-menu by carb-setting.
- Ability to also disable object-click (or not) when disabling selection-rect.
### Fixed
- A few typos.

## [1.0.11] - 2022-09-27
### Added
- Use new ViewportWindow.active_window API.
### Fixed
- Possibly import error from omni.usd.editor

## [1.0.10] - 2022-09-10
### Added
- disable_selection API to disable Viewport selection.

## [1.0.9] - 2022-08-25
### Fixed
- Convert to Gf.Camera at Viewport time.

## [1.0.8] - 2022-08-22
### Added
- Re-enable possibility of more than one Viewport.

## [1.0.7] - 2022-08-10
### Added
- Ability to specify format_desc dictionary to new capture-file API.

## [1.0.6] - 2022-07-28
### Added
- Accept a ViewportWindow or ViewportAPI for toast-message API.
- Add _post_toast_message method to LegacyViewportWindow

## [1.0.5] - 2022-07-06
### Added
- Add resolution and scaling API to mirror new Viewport

## [1.0.4] - 2022-06-22
### Added
- Add capture_viewport_to_buffer function
### Changed
- Return an object from capture_viewport_to_file and capture_viewport_to_buffer.
- Get test-suite coverage above 70%.
### Fixed
- Query of fill_frame atribute after toggling with legacy Viewport

## [1.0.3] - 2022-06-16
### Added
- Add create_drop_helper function

## [1.0.2] - 2022-05-25
### Added
- Add framing and toggle-visibility function for edit menu.

## [1.0.1] - 2022-05-25
### Added
- Fix issue with usage durring startup with only Legacy viewport

## [1.0.0] - 2022-04-29
### Added
- Initial release
