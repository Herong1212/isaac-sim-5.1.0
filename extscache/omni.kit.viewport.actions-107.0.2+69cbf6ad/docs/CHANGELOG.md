# CHANGELOG

This document records all notable changes to ``omni.kit.viewport.actions`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [107.0.2] - 2025-04-04
### Removed
- Legacy Viewport conditionals

## [107.0.2] - 2025-04-07
### Changed
- Updated to use omni.usd via eventdispatcher (Events 2.0) instead of EventStream (Events 1.0)

## [107.0.1] - 2024-12-24
### Changed
- OMPE-24967: Fix issue with toggling show by type not correctly resetting children type states.

## [107.0.0] - 2024-06-15
### Changed
- Updated documentation with AI agent.

## [106.0.1] - 2024-06-01
### Added
- OMPE-8596: Make camera visibility toggle remove the usd-mesh representation

## [106.0.0] - 2024-01-17
### Added
- OM-84741: Add action to toggle bounding box visibility

## [105.2.8] - 2023-12-11
### Added
- Move out UI relation actions into a new extension `omni.kit.ui.actions`.
- Break test into multiple sections according to their dependencies.

## [105.2.7] - 2023-11-27
### Added
- New process-memory key for HUD visibility action

## [105.2.6] - 2023-10-12
### Added
- More test coverage to bring coverage up to 85%

## [105.2.5] - 2023-09-27
### Added
- Add optional F7/F11/+/- hotkeys for alternative to omni.kit.menu.common

## [105.2.4] - 2023-09-18
### Added
- Add hotkey SHIFT+W to toggle wireframe

## [105.2.3] - 2023-08-28
### Changed
- Fixed toggle_ui to save/restore workspace

## [105.2.2] - 2023-08-15
### Added
- Added actions toggle_ui, toggle_fullscreen, dpi_scale_increase, dpi_scale_decrease, dpi_scale_reset

## [105.2.1] - 2023-07-31
### Added
- HUD visibility toggling actions
### Fixed
- Typo from merge conflict of 105.1

## [105.2.0] - 2023-07-31
### Added
- toggle_viewport_visibility action to batch custom group of visibility changes in one call.
- return codes for toggle_viewport_* actions to record state of what was toggled.

## [105.0.9] - 2023-06-27
### Added
- toggle_global_visibility action and setting to control what items it toggles.

## [105.0.8] - 2023-06-27
### Changed
- Full visibility testing against UsdRt.

## [105.0.7] - 2023-06-27
### Added
- /exts/omni.kit.viewport.actions/visibilityToggle/ignoreStageWindowHidden setting for visibility toggle action.
### Changed
- deregister_actions handles get_action_registry returning None

## [105.0.6] - 2023-04-07
### Added
- toggle_lock_navigation_height action.

## [105.0.5] - 2023-02-07
- deregister_actions handles get_action_registry returning None

## [105.0.4] - 2023-02-16
### Fixed
- Excessive calls responding to stage-open event.

## [105.0.3] - 2023-02-03
### Added
- Actions toggling grid, axis, and selection hilight.
- Actions hotkeys for toggling cameras and lights.
### Fixed
- Malfunctioning toggle_show_by_type_visibility and toggle_setting.

## [105.0.2] - 2022-12-05
### Added
- set_viewport_resolution action to set resolution by value or named costant.

## [105.0.1] - 2022-10-24
### Changed
- Add action to toggle between RealTime and PathTrace modes.

## [105.0.0] - 2022-10-17
### Changed
- Add actions for items known to be in "Show By Type" menu.
### Added
- Stage open handler to manage stickiness of "Show By Type" visibility.
- Setting to opt out inidividual "Show By Type" items from sticky behavior.

## [104.0.1] - 2022-10-10
### Changed
- Make Viewport's fillViewport setting persistent.

## [104.0.0] - 2022-09-30
### Added
- Initial version
