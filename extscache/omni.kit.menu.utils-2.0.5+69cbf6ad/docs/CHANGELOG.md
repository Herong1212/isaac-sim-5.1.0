# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.5] - 2025-06-13
### Fixed
- Fixed refreshing a submenu that only has separators as it should not be visible.

## [2.0.3] - 2025-04-15
### Fixed
- OMPE-43816: ensured some extension enable/disable hook objects are cleaned up.

## [2.0.2] - 2025-03-19
### Changes
- OMPE-40698: Fixed issue with MenuHelperExtensionFull not updating menu items when layout is loaded
- Prevent duplicate registration of windows in MenuHelperExtension & MenuHelperExtensionFull

## [2.0.1] - 2025-01-30
### Changes
- OMPE-34904: Fixed flaky tests

## [2.0.0] - 2025-01-16
### Changes
- OMPE-34006: Bump major version after removal of deprecated APIs

## [1.7.8] - 2025-12-12
### Changes
- OMPE-31521: Remove deprecated APIs from omni.kit.menu.utils

## [1.7.7] - 2025-11-29
### Changes
- Fixed issue with missing icons in layout
- Fixed issue with copying menu with separators

## [1.7.6] - 2025-10-30
### Changes
- OMPE-25887: added duplicate to MenuLayoutItem.Item so the menus can be in multiple places
- Fixed issue with MenuLayout.Item on a submenu item as it would break refresh_menu_items()
- Added optional 3rd value to separator_size for spacing after text
- Added "menu_headfoot_spacing" for spacing at top & bottom of menus
- Added glyph override to MenuLayout.Item
- Fixed MenuHelperExtensionFull logging without verbose enabled

## [1.7.5] - 2025-10-29
### Fixed
- Fixed MenuLayout.Sort key error

## [1.7.4] - 2025-10-16
### Changes
- OMPE-25351: Stopped MenuLayout.SubMenu finding non-submenu items
- Improve startup time by preventing unnecessary rebuilding
- MenuLayout.Item clears item header (ui.Separator) as can cause random extra separators
- Fixed issue with MenuLayout.Item source not handling "\\" correctly
- Fixed issue with submenu names not changing occasionally

## [1.7.3] - 2025-10-04
### Fixed
- OMPE-24162: Fixed menu separators not showing after submenu

## [1.7.2] - 2024-09-25
### Changes
- Updated API and __all__ exports

## [1.7.1] - 2025-09-06
### Changed
- Removed the extra spaces in submenu titles

## [1.7.0] - 2024-09-05
### Changed
- Move some functions from utils to AppMenu and export AppMenu to be used for other menu bars in other windows
- Add hotkey_window in MenuItemDescription to define hotkey for special window only when build menu item
- Add destroy in MenuItemDescription to release resources by user (especially hotkey bind to the menu item)

## [1.6.1] - 2025-08-16
### Fixed
- Updated to support new settings and radio groups.

## [1.6.0] - 2024-07-27
### Fixed
- Updated MenuHelperExtensionFull to support subgroups and multiple menu items

## [1.5.27] - 2024-06-27
### Fixed
- Fix menu remapping into submenus

## [1.5.26] - 2024-05-29
### Fixed
- Removed usage of omni.kit.ui

## [1.5.25] - 2024-05-29
### Removed
- Removed extraneous dependencies

## [1.5.24] - 2024-05-17
### Fixed
- Updated flake8 linting overrides

## [1.5.23] - 2024-05-06
### Fixed
- Fixed linting issues

## [1.5.22] - 2024-02-26
### Fixed
- OM-120233: Fixed leaks in MenuHelperExtension when registering actions

## [1.5.21] - 2024-02-15
### Fixed
- Fixed torn-off menus so ticks get refreshed when `refresh_menu_items` is called

## [1.5.20] - 2024-01-11
### Changed
- Error when default IAppWindow is not available

## [1.5.19] - 2024-01-08
### Fixed
- OM-116648: Fix for appear_after multi-choice item list using FIRST/LAST

## [1.5.18] - 2023-12-29
### Fixed
- OM-116648: Fix for appear_after multi-choice item list but 1st choice hasn't been added yet

## [1.5.17] - 2023-12-29
### Fixed
- random order test fixes
- rebuild_menus clears pending refresh updates
- added `clear_menu_data` function

## [1.5.16] - 2023-12-20
### Fixed
- Typo

## [1.5.15] - 2023-11-28
### Changed
- Using omni.kit.menu.core for uiMenu* definitions & delegate

## [1.5.14] - 2023-11-28
### Changed
- added documentation

## [1.5.13] - 2023-11-14
### Changed
- improved deprecation message

## [1.5.12] - 2023-11-17
### Added
- use refresh_menu_items to update menu item hotkey text

## [1.5.11] - 2023-11-14
### Changed
- added `build_submenu_dict` function

## [1.5.9] - 2023-11-08
### Added
- refresh_menu_items now supports individual item paths

## [1.5.8] - 2023-11-02
### Changed
- Fixed header so it adds menu item and separator
- added helper class MenuHelperExtension
- added helper class MenuHelperExtensionFull

## [1.5.7] - 2023-11-03
### Added
- Overrode [] and get for dict-like read-only access MenuItemDescription so it can be used as an entry for omni.kit.context_menu

## [1.5.6] - 2023-10-19
### Added
- Improved deprecated warnings
- fix for recursive appear_after using wrong appear_after item on rebuild
- added `replace_menu_items(new_menu, old_menu, name)`

## [1.5.5] - 2023-08-28
### Changed
- OM-106118: Fix crash in `hotkey_changed` due to using Destroyed keys

## [1.5.4] - 2023-08-28
### Changed
- OM-105932: Use carb.dictionary.get in subscription of setting changed

## [1.5.3] - 2023-08-09
### Changes
- Changed `add_menu_items` message "cannot change delegate" to only show if original/new are both valid
- Added `parent_menu` to `uiMenu` and `uiMenuItem`
- Added `get_elided_length` to `IconMenuDelegate`
- Menu names can now be elided

## [1.5.2] - 2023-07-27
### Changes
- Adjust submenu arrow size/spacing
- Adjust tick size/spacing

## [1.5.1] - 2023-07-17
### Changes
- Adjust root menu spacing
- Added more spacing overrides

## [1.5.0] - 2023-06-14
### Changes
- Support icons/glyphs with paths

## [1.4.13] - 2023-05-15
### Changes
- layout improvement. Added `MenuLayoutItem.source_search` which can be LayoutSourceSearch.EVERYWHERE or LayoutSourceSearch.LOCAL_ONLY.
-    EVERYWHERE as before
-    LOCAL_ONLY will only search for menu items in current menu

## [1.4.12] - 2023-02-23
### Changes
- remove_menu_items() now checks to ensure the requested menu item exists before remove() is called on it.

## [1.4.11] - 2023-02-09
### Changes
- Added optional user_style styling dictionary to MenuItemDescription user dictionary

## [1.4.10] - 2023-01-30
### Changes
- fixed missing import

## [1.4.9] - 2022-11-07
### Changes
- Added debug window activated with SHIFT+CTRL+ATL+M (requires omni.kit.hotkeys.core extension)
- Removed is_shutting_down on omni.kit.app.POST_QUIT_EVENT_TYPE event
- Added json save support for menus/layout

## [1.4.8] - 2022-11-14
### Changes
- optimized menu rebuilds during app startup

## [1.4.7] - 2022-10-24
### Changes
- Strip off USD dependencies.

## [1.4.6] - 2022-09-22
### Changes
- Added "exts.omni.kit.menu.utils.logDeprecated" setting so deprecated warnings can be silenced

## [1.4.5] - 2022-09-22
### Changes
- When omni.kit.hotkeys.core enabled, register hotkey with hotkey registry. Otherwise, same as before

## [1.4.4] - 2022-09-09
### Changes
- Register hotkey with omni.kit.hotkeys.core

## [1.4.3] - 2022-09-02
### Changes
- Fixed issue with non-ticked items being tickable

## [1.4.1] - 2022-08-29
### Changes
- MenuLayout.Group now supports source for submenu copying
- MenuLayout.Sort now whole current menu not just non-ordered items
- MenuLayout.Sort now supports sort_submenus for ordering submenus too

## [1.4.0] - 2022-08-16
### Changes
- Fixed issue with refresh_menu_items & items moved via layout
- Menus now refresh on ui.Menu on_triggered. refresh_menu_items now only set dirty state

## [1.3.2] - 2022-08-17
### Changes
- Fix menubar disappearing issue

## [1.3.1] - 2022-06-07
### Changes
- Added support for menu delegate
- Added support for right aligned menus

## [1.3.0] - 2022-06-07
### Changes
- Added `onclick_action` and `unclick_action`
- Deprecated `onclick_fn`
- Deprecated `unclick_fn`
- Deprecated `original_svg_color`
- Deprecated `onclick_right_fn`

## [1.2.11] - 2022-05-19
### Changes
- Added info logs to rebuild_menus & refresh_menu_items
- Added `get_debug_stats` function to get dictionary of functions called

## [1.2.10] - 2022-04-13
### Changes
- Optimized rebuild_menus usage during startup

## [1.2.9] - 2022-04-11
### Changes
- Fixed layout ordering issue in Submenu/Submenu

## [1.2.8] - 2022-03-10
### Changes
- Fixed missing layout menu issue after multiple `remove_menu_items`

## [1.2.7] - 2022-03-09
### Changes
- Fixed missing layout menu issue

## [1.2.6] - 2022-02-23
### Changes
- Added `get_merged_menus` function
- Added warning for SubMenu without Menu
- Added warning for Menu using non-existing menu name
- Fixed omni.kit.mainwindow load order problems. Will now work if omni.kit.mainwindow is loaded after omni.kit.menu.utils
- Added tests
- Fixed visibility issues
- Fixed layout issues

## [1.2.5] - 2022-02-14
### Changes
- Fixed issue with refresh_menu_items refreshing all menus to just named one
- Fixed issue with sub_menus and show_fn. If show_fn was False sub_menu wasn't built and refresh_menu_items couldn't show sub_menu when show_fn became True.

## [1.2.4] - 2022-02-02
### Changes
- MenuLayout.Sort has submenu items above others

## [1.2.3] - 2022-02-03
### Changes
- Added support for hotkeys press/release callbacks

## [1.2.2] - 2022-02-02
### Changes
- Silenced layout warning spam

## [1.2.1] - 2022-01-28
### Changes
- Added support for hotkeys using carb.input.GamepadInput

## [1.2.0] - 2022-01-21
### Changes
- Added menu layout templates

## [1.1.5] - 2022-01-14
### Changes
- Handle external deletion of action mapping

## [1.1.4] - 2021-11-23
### Changes
- Fixed leak from async `refresh_menu_items`

## [1.1.3] - 2021-10-25
### Changes
- Added `set_default_menu_priority` so extensions cannot change order of existing menus
- Updated `refresh_menu_items` to support "immediately" parameter

## [1.1.2] - 2021-09-29
### Changes
- Fix for menu of sub_menus being now shown

## [1.1.1] - 2021-09-23
### Changes
- Handled removal exceptions. Reported as warnings

## [1.1.0] - 2021-08-18
### Changes
- Removed editor_menu support
- Menus require omni.kit.mainwindow loaded but not dependent
- Fixed leaks

## [1.0.4] - 2021-08-11
### Changes
- Added action mapping for menu hotkeys

## [1.0.3] - 2021-08-04
### Changes
- Added `ticked_value` to `MenuItemDescription`
- Added `set_hotkey` function to  `MenuItemDescription`

## [1.0.2] - 2021-06-03
### Changes
- refresh_menu_items now accumulates requests and refreshes each menu at most once a frame. Can be overridden to refresh immediately.

## [1.0.1] - 2021-02-02
### Changes
- Fixed leak in hotkeys
- Fixed issues with ticked menus
- Fixed issues with duplicate menus with omni.ui
- Added hotkey info to menus with omni.ui

## [1.0.0] - 2020-08-17
### Changes
- Created
