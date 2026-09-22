# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.3.7] - 2025-06-21
### Fixed
- ui_test.find_all only returns windows which are not destroyed

## [1.3.6] - 2025-04-22
### Changed
- Added clear_before_input to function input as it can randomly append instead of replacing string.

## [1.3.5] - 2025-04-08
### Changed
- OMPE-43022: Handle the runtime exception when acquiring windowing interface on OVC2.

## [1.3.4] - 2025-01-30
### Changed
- menu_click(): Fixes including handling already shown menu

## [1.3.3] - 2024-11-15
### Changed
- emulate_mouse_move_and_click(): added human_delay_speed before click so mouse move as get processed

## [1.3.2] - 2024-06-06
### Changed
- Remove retry_until_success from this extension because a copy has been added to omni.kit.test.async_unittest.AsyncTestCase

## [1.3.1] - 2024-06-05
### Added
- Add comments in retry_until_success and raise TimeoutError when it exceeds the maximum number of retries.

## [1.3.0] - 2024-05-31
### Added
- Added function retry_until_success to reduce the waiting time and make the verification more reliable

## [1.2.20] - 2024-05-17
### Changed
- Restored human_delay in menu_click functions from 32 to the original 2
- Disabled INFO logging

## [1.2.19] - 2024-05-20
### Added
- Added function find_first to get the first matched widget for a query.

## [1.2.18] - 2024-05-21
- Updated `menu_click` to accept separator as argument to click menu options containing / in the text

## [1.2.17] - 2024-02-16
- Updated `menu_click` to mouse move before click as menu needs to update checked state before reading

## [1.2.16] - 2023-12-20
- Updated `emulate_mouse` method to use global modifiers down rather than clearing modifiers.
- Fix `emulate_keyboard` to correct arguments and types in `WidgetRef.input` method

## [1.2.15] - 2023-11-27
- Updated `select_context_menu` method to find the menu items with `/`

## [1.2.14] - 2023-11-22
- changed `menu_click` to be aware of ui.Menu states, preventing incorrect toggling of already open menus
- added `menu_click` optional parameter `show` to indicate clicks expected behavior. IE show or hide

## [1.2.13] - 2023-10-05
- added `select_context_menu` optional parameter `find_fn` for handling custom menus

## [1.2.12] - 2023-02-08
- Updated find_menu to have contains_path parameter

## [1.2.11] - 2023-01-27
- Updated get_context_menu to get all menu items & separator using get_all parameter

## [1.2.10] - 2022-10-31
- Added ui.IntDrag & ui.IntDrag support to `input`

## [1.2.9] - 2022-08-30
- Added modifier for `KeyDownScope`.

## [1.2.8] - 2022-08-12
- Added get_context_menu which gets current open context menu as dictionary

## [1.2.7] - 2022-07-19
- Restored human_delay change in emulate_keyboard_press

## [1.2.6] - 2022-07-19
- Incremented human_delay on emulate_keyboard_press & menu_click as now menus use async actions

## [1.2.5] - 2022-06-27
- Added `ignore_case` parameter to `find_menu`

## [1.2.4] - 2022-05-27
- Added parameter `key_end` to `input` function so you can use alternative key to KeyboardInput.ENTER like KeyboardInput.TAB
- Added support for `ui.FloatSlider` which requires CTRL pressed to start typing

## [1.2.3] - 2022-05-19
- Added `KeyDownScope`

## [1.2.2] - 2022-04-20
- Quiet human_delay spam in ui_test

## [1.2.1] - 2022-03-16
- Added `drag_drop` method to `WidgetRef`

## [1.2.0] - 2022-03-11
- Add `emulate_mouse_scroll` method

## [1.1.1] - 2022-03-11
- Add `emulate_mouse_drag_and_drop` added pause before drop to prevent failures on Linux

## [1.1.0] - 2022-02-23
- Add `emulate_key_combo` method

## [1.0.3] - 2021-12-10
### Updated
- Updated `emulate_mouse_move_and_click` to pass on double click
- Fixed `emulate_mouse_click` double click

## [1.0.2] - 2021-11-24
### Updated
- Added variable human_delay support in functions
- Added model accessor to `WidgetRef`
- Added compare function to `Vec2`
- Fix for viewport right-click

## [1.0.1] - 2021-11-16
### Updated
- Add more docs and types, cleanup API

## [1.0.0] - 2021-10-01
### Changes
- Created
