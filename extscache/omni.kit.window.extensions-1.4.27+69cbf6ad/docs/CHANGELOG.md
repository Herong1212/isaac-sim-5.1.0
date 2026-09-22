# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.4.27] - 2025-06-21
### Fixed
- update menu window visibility in show_window, in case it is run in script.

## [1.4.26] - 2025-01-13
### Added
- Updated missing public API.

## [1.4.25] - 2024-11-28
### Fixed
- OMPE-14116: Added "default_search_words" setting to highlight featured extensions. Enable tokens for search widget.
- Added "kit_featured_exts" for additional extensions that should be in feature list.

## [1.4.24] - 2024-11-22
### Changed
- OMPE-27264: Updated categories

## [1.4.23] - 2024-10-29
### Fixed
- OMPE-21998: Readme handle markdown code blocks and other codes better

## [1.4.22] - 2024-10-25
### Changed
- OMPE-4125: An extension that fails to initialize will be disabled again.

## [1.4.21] - 2024-10-25
### Changed
- OMPE-18943: Removed mysterious blue line from list widget.

## [1.4.20] - 2024-10-16
### Changes
- Updated API and __all__ exports

## [1.4.19] - 2024-09-18
### Added
- OMPE-19510: Version locked extensions are not updatable

## [1.4.18] - 2024-09-09
### Changed
- OMPE-20916: Removed dependency graph as its being moved to omni.kit.widget.ext_win.dependency_graph
- Added workaround for "Container::addChild attempting to add a child during a draw callback" warning from `toggle_extension` function
- Added add_menu_to_info_widget & remove_menu_from_info_widget
- Updated so custom menus can be added

## [1.4.17] - 2024-08-20
### Changed
- OMPE-14116: Added setting "/exts/omni.kit.window.extensions/default_filter" which can be 'featured' or ['featured', 'enabled'] etc.

## [1.4.16] - 2024-08-19
### Changed
- OMPE-14120: Updated icons and added preview image when one isn't in toml.

## [1.4.15] - 2024-08-08
### Changed
- OMPE-16186: Updated icons and added preview image when one isn't in toml.

## [1.4.14] - 2024-08-08
### Changed
- OMPE-14114: When "/exts/omni.kit.window.extensions/featuredExts" setting is used, the feature=true in toml are ignored

## [1.4.13] - 2024-07-19
### Changed
- OMPE-14118: ExtSummaryItem prevent double call to get_ext_info_dict

## [1.4.12] - 2024-05-01
### Changed
- OM-124549 - update core label
- OM-123934: Changed support_level example to sample, both support_level or "example" or "sample" supported.
- OM-123934: Any support_level that is not "core", "internal", "example" or "sample" is now classed as "sample"
- OM-123934: Removed "others" category

## [1.4.11] - 2024-06-18
### Changed
- Updated documentation with AI agent.

## [1.4.10] - 2024-06-14
### Changed
- OMPE-12189: Groups are only expanded when window is opened.
- Fixed window re-opening, groups use expected defaults now.

## [1.4.9] - 2024-05-17
### Changed
- Updated flake8 linting overrides

## [1.4.8] - 2024-05-06
### Changed
- Fixed linting issues

## [1.4.7] - 2024-04-22
### Changed
- OM-123934: Changed support_level example to sample, both support_level or "example" or "sample" supported.
- OM-123934: Any support_level that is not "enterprise", "internal", "example" or "sample" is now classed as "sample"
- OM-123934: Removed "others" category

## [1.4.6] - 2024-04-15
### Changed
- OM-121637: Added tests

## [1.4.5] - 2024-04-14
### Changed
- OM-123551: Add button to copy extension id.

## [1.4.4] - 2024-04-10
### Changed
- OM-123378: Updated core list with extensions outside kit.

## [1.4.3] - 2024-04-09
### Changed
- OM-123322: Updated core/example/internal placeholder lists.
- OM-123322: Fixed filter so they can be disabled.

## [1.4.2] - 2024-03-14
### Changed
- OM-120798: Update how deprecation info is read

## [1.4.1] - 2024-03-08
### Changed
- OM-121904: Remove Test tab & omni.kit.test
- OM-121905: omni.kit.widget.graph is optional dependency

## [1.4.0] - 2024-03-01
### Changed
- OM-120783: Update with new styling
- Added core/example/internal/deprecated support

## [1.2.8] - 2024-02-28
### Changed
- OM-120233: Fixed leak breakage

## [1.2.7] - 2024-02-26
### Changed
- OM-120233: Fixed leaks

## [1.2.6] - 2024-02-19
### Changed
- OM-120427: Changed search field to be dependent on omni.kit.widget.searchfield.

## [1.2.5] - 2024-02-15
### Fixed
- Fixed unloading omni.kit.window.extensions

## [1.2.4] - 2024-02-08
### Fixed
- Fixed name property to handle finding the name of a port

## [1.2.3] - 2023-11-02
### Changed
- Updated menus to use omni.kit.menu.utils

## [1.2.2] - 2023-07-24
### Changed
- Fixed trash icon path

## [1.2.1] - 2023-07-14
### Changed
- Filter: do not hide popup menu when filter changed

## [1.2.0] - 2023-07-03
### Changed
- OM-98000: Apply new filter button

## [1.1.9] - 2023-05-29
### Fixed
- Added some safety checks for hot reloading

## [1.1.8] - 2023-05-12
### Updated
- Fixed Ascending spelling

## [1.1.7] - 2023-05-04
### Updated
- Removed "Featured" when not in use
- Filter button changes color when not default
- Sort By button changes color when not default

## [1.1.6] - 2023-04-28
### Updated
- Added tooltip for extension dependency solve failure

## [1.1.5] - 2023-04-24
### Updated
- Fixed OpenDoc button tooltip color
- Added Export button tooltip
- Added Sort Ascending/Descending

## [1.1.4] - 2022-11-17
### Updated
- Fixed filter list resetting after update

## [1.1.1] - 2022-11-17
### Updated
- Switched out pyperclip for linux-friendly copy & paste

## [1.1.0] - 2022-05-06
### Added
- Added support for truncated words in extension search window

## [1.0.2] - 2020-12-07
### Changed
- Fix path_is_parent exception with different drive paths

## [1.0.1] - 2020-07-09
### Changed
- Don't produce symlink for icons in the extension folder

## [1.0.0] - 2020-07-08
### Added
- The initial release with minimal support of loading/unloading extensions and access to the external extension registry.
