# CHANGELOG

This document records all notable changes to ``omni.kit.viewport.menubar.core`` extension.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

## [107.2.1] - 2025-07-17
### Changed
- OMPE-54320: Breaking reference cycles to clear memory leak.

## [107.1.5] - 2025-03-16
### Changed
- OMPE-39716: Update goldens since "/exts/omni.ui/Image/syncTextureLoad" is True by default in UI tests.

## [107.1.4] - 2025-01-13
### Added
- Updated missing `ViewportMenuModel` public API.

## [107.1.3] - 2024-11-02
### Fixed
- Issue with shutdown on Python-3.11

## [107.1.2] - 2024-06-24
### Changed
- Updated documentation with AI agent.

## [107.1.1] - 2024-06-04
### Changed
- Preferences page golden image

## [107.1.0] - 2024-06-26
### Changed
- Update version so it is unique across Kit SDK versions

## [107.0.2] - 2024-05-24
### Changed
- OMPE-5286: Use FloatDrag instead of FloatSlider if no min/max in SpinnerMenuDelegate when omni.kit.widget.spinner not imported

## [107.0.1] - 2024-05-17
### Changed
- Linting

## [107.0.0] - 2024-03-13
### Changed
- Made omni.kit.widget.spinner optional

## [105.2.1] - 2024-02-28
### Changed
- Remove unused imports

## [105.2.0] - 2023-10-18
### Changed
- Increase code coverage to 86.8%

## [105.1.1] - 2023-10-12
### Changed
- Exposed content_clipping for _build_menubar, build_fn of ViewportMenubar

## [105.1.0] - 2023-09-12
### Added
- Able to show hotkey in menu item delegate
- Able to Watch hotkeys in ViewportMenuContainer

## [105.0.18] - 2023-08-28
### Changed
- OM-106699: SliderMenuDelegate should return actual max value

## [105.0.17] - 2023-05-31
### Changed
- Fix for "Render Resolution" submenu not always showing when hovered

## [105.0.16] - 2023-05-23
### Changed
- SettingModel values now properly converted between int and bool

## [105.0.15] - 2023-05-10
### Added
- Be able to change the `viewport_menubar_border_radius`

## [105.0.14] - 2023-05-10
### Changed
- OM-90924, OM-94089, OM-70794: Get correct label size with spacer width for IconMenuDelegate

## [105.0.13] - 2023-04-21
### Changed
- Fixes for slider menu item precision, stepping, and range defaults.

## [105.0.12] - 2023-03-28
### Changed
- Open API to append more layout for IconMenuDelegate.

## [105.0.11] - 2023-03-07
### Changed
- Update test golden image.

## [105.0.10] - 2023-02-26
### Changed
- Replaced asyncio.ensure_future calls in usd_watch.py with omni.kit.async_engine.run_coroutine function.

## [105.0.9] - 2023-02-24
### Fixed
- Added img compare threshold for flaky test.

## [105.0.8] - 2023-02-06
### Fixed
- Add settings for look, tumble, and zoom movements.

## [105.0.7] - 2023-02-03
### Fixed
- Issue with usage of ChangePropertyCommand and custom omni.usd.UsdContext.

## [105.0.6] - 2023-01-04
### Changed
- OM-77174: Update preference page when viewport menubar item enabled/disabled

## [105.0.5] - 2022-11-15
### Added
- Add inteface: menubar.visible
### Changed
- Fix variable name typo

## [105.0.4] - 2022-11-05
### Updated
- Cherry-picked changes from v104.3.6 and merged with latest v105

## [105.0.3] - 2022-10-25
### Changed
- OM-64798: Listen menu expand status to refresh spacer width

## [105.0.2] - 2022-10-17
### Changed
- Added possibility to set triggered_fn on items created that are otherwise unreachable.

## [105.0.1] - 2022-10-03
### Added
- API to customize RadioMenuCollection

## [104.3.6] - 2022-10-26
### Added
- Optional shown_changed_fn callback can now be set on CategoryCollectionItem menus

## [104.3.5] - 2022-10-11
### Fixed
- Issues with SettingComboBoxModel using an array setting.

## [105.0.0] - 2022-10-02
### Changed
- Make omni.kit.window.cursor an optional dependency.
### Added
- Common icon for settings option.
- Ability to specify toggle for SelectableMenuItem.
### Fixed
- Issues with model destruction

## [104.3.2] - 2022-08-23
### Added
- Multiple VP support

## [104.3.1] - 2022-08-19
### Fixed
- Issue with deregistration and using an already destroyed weakref.proxy object

## [104.3.0] - 2022-08-15
### Added
- Conform root frame to internal ViewportWindow API so that it can be shown and hidden by name.
- More properties for menu bar item to customize in View.
- Separator line in category menu collection for custom items.
- Way for menu-entry to watch for ui.Widget size changes.
### Changed
- Update background color of viewport menu title bar.
- Show border when hovering on menu header bar.

## [104.2.6] - 2022-08-02
### Fixed
- Spinner/Attribute value to float number value conversion.
- Issue with SettingModel setting carb-setting to a string value causing type loss.
- Typo of AbstractSettingModelWidthDefault instead of AbstractSettingModelWithDefault.
### Changed
- Make RadioCollection items not toggle check state when selected and clicked again.

## [104.2.5] - 2022-07-28
### Changed
- Show border when hovering on menu header bar

## [104.2.4] - 2022-07-25
### Changed
- OM-55152: Re-adjust viewport dashboard and icons for VP2
- OM-56499: Change the UI Background transparency to 1.0
- Hotfix on menubar styles: bigger icon, hover background, preference page, etc.
- Auto resize menubar when width changed
- Add reset box for menu delegates

## [104.2.3] - 2022-07-13
### Changed
- Optimized color changes through carb settings, particularly when located within in large arrays.
- Re-enable tearoff for all Viewport menus now that position is correct.
### Fixed
- FloatArraySettingColorMenuItem.destroy leaving a carb.settings subscription
- Use Icon computed_XXX methods instead of computed_content_XXX
- Issue where user is locked out from Viewport interaction if all menubar items are hidden.
### Added
- hide_on_click argument to RadioMenuCollection constructor
### Removed
- Extra copy incoming factory arguments dictionary.

## [104.2.2] - 2022-07-11
### Fixed
- Use Icon computed_XXX methods instead of computed_content_XXX

## [104.2.1] - 2022-07-08
### Added
- Add menu_is_tearable function, and force it to always return False
- Let IconMenuDelegate change label text.
- hide_on_clicked argument to SelectableMenuItem constructor
### Changed
- Trigger icon-clicked function only inside Icon and forward arguments to callback.
- Limit check / un-check icon clicking to left mouse button.
- Rename RatioMenuCollection to RadioMenuCollection.
### Removed
- Pruned some unused imports.
### Fixed
- Trigger icon-clicked function only inside Icon and forward arguments to callback.
- Limit check / un-check icon clicking to left mouse button.
- Rename RatioMenuCollection to RadioMenuCollection.

## [104.2.0] - 2022-07-05
### Added
- Support multiple menubars in viewport
## [104.1.15] - 2022-06-23
### Changed
- Add option_box option to ViewportDelegate

## [104.1.14] - 2022-06-19
### Added
- ViewportButtonItem for button in viewport menubar
### Changed
- SliderMenuDelegate to align with other general menu items

## [104.1.13] - 2022-05-25
### Changed
- Change base class of color menu item to ui.MenuItem

## [104.1.12] - 2022-05-04
### Changed
- Imported to kit repro and bump version to match Kit SDK

## [1.1.12] - 2022-04-108
### Changed
- Donot update widget if model in edit mode except draggable
- For float value model, if input invalid, set value to 0.0

## [1.1.11] - 2022-04-1
### Changed
- Change flyaway carats

## [1.1.10] - 2022-04-1
### Fixed
- Broken menu insertion from external extensions because of interface change

## [1.1.9] - 2022-03-31
### Added
- Preference page for menubar

## [1.1.8] - 2022-03-29
### Fixed
- OM-47088: Prevent expanding of viewport when the toolbar is big

## [1.1.7] - 2022-03-28
### Changed
- Setting menu default width
- Only update setting when value Changed

## [1.1.6] - 2022-03-27
### Fixed
- Issue with Usd notice of re-synch on paths not being picked up by model

## [1.1.5] - 2022-03-25
### Changed
- OM-46246: Add explicit casts for all SettingsModel.get_value_as_X methods

## [1.1.4] - 2022-03-24
- Minor title style improvements

## [1.1.3] - 2022-03-24
### Changed
- Made Usd edits through models undoable
### Added
- Typed Usd attribute models
- Usd metadata model
- Tests

## [1.1.2] - 2022-03-16
### Fixed
- OM-46220: menu-bar click causes selection to be lost.
- OM-46246: SettingsModel.get_value_as_int must return an int if possible

## [1.1.1] - 2022-03-16
### Fixed
- OM-46211: selected may be called before build_item on ViewportMenuDelegate.

## [1.1.0] - 2022-03-11
### Changed
- Refactor the exts

## [1.0.10] - 2022-02-22
### Changed
- Move from pxr TraceFunction to carb.profiler decorators

## [1.0.9] - 2022-02-17
### Changed
- Make AOV menu display selected AOV's name
- Remove change of anti-aliasing mode

## [1.0.8] - 2022-02-16
### Fixed
- Issue with delayed startup and camera-menu

## [1.0.7] - 2022-02-10
### Added
- Simple AOV menu for RTX rendering
### Changed
- Disable debug tool menu.

## [1.0.6] - 2022-02-07
### Changed
- Rename Iray Photoreal to RTX Ground Truth in Renderer menu.

## [1.0.5] - 2022-01-31
### Fixed
- Fix issues with current menu-bar blocking mouse-events in dead space.

## [1.0.3]
### Added
- Add simple settings menu to set resolution.
- Basic ability to style menu bar for prototype. (to be deprecated with omni.ui.menu)

## [1.0.2]
### Changed
- Fix some destruction and cleanup issues.

## [1.0.1]
### Changed
- Better menu-state and switching when the Viewport owns the omni.hydra.pxr engine
- Inset menu-bar with a margin
- Order implicit cameras as Viewport-1 does

## [1.0.0]
### Changed
- Check renderer-change has succeeded and adjust menu state accordingly

## [0.9.5]
### Changed
- Remove all omni.scene.ui inheritance

## [0.9.0]
### Changed
- Move to omni.kit.viewport namespace

## [0.8.1] -
### Changed
- Scan Stage for cameras when extension loaded into a running session

## [0.8.0] - unrelease
### Changed
- first release
