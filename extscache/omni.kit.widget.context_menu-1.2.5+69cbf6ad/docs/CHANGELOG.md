# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2.5] - 2025-04-08
### Changed
- Renamed "Hide from camera" to "Invisible to Primary Ray"

## [1.2.4] - 2024-10-26
### Fixed
- OMPE-26036: Fix for nested menus could trigger merge warnings.

## [1.2.3] - 2024-07-30
### Changed
- OMPE-8922: Change default icon size and color

## [1.2.2] - 2024-05-29
### Removed
- Removed extraneous dependencies

## [1.2.1] - 2023-05-207
### Changed
- OM-124261: Only forward the accepted parameters to context menu action

## [1.2.0] - 2023-03-21
### Changed
- Update documentation

## [1.1.1] - 2023-03-14
### Changed
- OM-117551: Fix for startup warning due to nested classes.
- OM-117551: Fixed DefaultMenuDelegate to read correct defaults

## [1.1.0] - 2024-03-01
### Changed
- Added get_instance, close_menu, reorder_menu_dict, add_menu, get_menu_dict, get_menu_event_stream, ContextMenuEventType
- Can now be used a bare bones replacement of omni.kit.context_menu

## [1.0.4] - 2024-01-10
### Changed
- Fix for python 3.7 support

## [1.0.3] - 2023-12-11
### Changed
- Using omni.kit.menu.core for uiMenu* definitions & delegate

## [1.0.2] - 2023-12-07
### Updated
- Added documentation.

## [1.0.1] - 2023-12-05
### Fixed
- Fix for missing name property.

## [1.0.0] - 2023-11-15
### Created
- Split the core functionality to create menu from dictionary from `omni.kit.context_menu.`
