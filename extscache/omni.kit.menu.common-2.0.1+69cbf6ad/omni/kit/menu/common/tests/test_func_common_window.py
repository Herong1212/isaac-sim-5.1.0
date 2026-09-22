import carb
import omni.usd
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.test.async_unittest import AsyncTestCase

DPI_SCALE_OVERRIDE_SETTING = "/app/window/dpiScaleOverride"


def get_hide_ui():
    hide_ui = carb.settings.get_settings().get("/app/window/hideUi")
    if hide_ui is None:
        return False
    return hide_ui


async def common_test_func_window_ui_toggle_visibility(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertTrue(get_hide_ui() is False)

    # use menu
    await ui_test.menu_click("Window/UI Toggle Visibility")

    # verify state
    await tester.assertTrueWithRetry(lambda: get_hide_ui() is True)

    # cannot use menu so use hotkey instead
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify  state
    await tester.assertTrueWithRetry(lambda: get_hide_ui() is False)


async def common_test_hotkey_func_window_ui_toggle_visibility(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertTrue(get_hide_ui() is False)

    # hotkey
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify state
    await tester.assertTrueWithRetry(lambda: get_hide_ui() is True)

    # hotkey
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify  state
    await tester.assertTrueWithRetry(lambda: get_hide_ui() is False)


async def common_test_func_window_fullscreen_mode(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertTrue(omni.appwindow.get_default_app_window().is_fullscreen() is False)

    # use menu
    await ui_test.menu_click("Window/Fullscreen Mode")

    # verify state
    await tester.assertTrueWithRetry(lambda: omni.appwindow.get_default_app_window().is_fullscreen() is True)

    # cannot use menu so use hotkey instead
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify  state
    await tester.assertTrueWithRetry(lambda: omni.appwindow.get_default_app_window().is_fullscreen() is False)


async def common_test_hotkey_func_window_fullscreen_mode(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertTrue(omni.appwindow.get_default_app_window().is_fullscreen() is False)

    # hotkey
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify state
    await tester.assertTrueWithRetry(lambda: omni.appwindow.get_default_app_window().is_fullscreen() is True)

    # hotkey
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify  state
    await tester.assertTrueWithRetry(lambda: omni.appwindow.get_default_app_window().is_fullscreen() is False)


async def common_test_func_window_dpi_scale_increase(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)

    # use menu
    await ui_test.menu_click("Window/DPI Scale/Increase")

    # verify state
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.5)

    # cannot use menu so use hotkey instead
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify state
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), 2.0)

    # reset state
    carb.settings.get_settings().set(DPI_SCALE_OVERRIDE_SETTING, 1.0)
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)


async def common_test_hotkey_func_window_dpi_scale_increase(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)

    # hotkey
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify state
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.5)

    # hotkey
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify state
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), 2.0)

    # reset state
    carb.settings.get_settings().set(DPI_SCALE_OVERRIDE_SETTING, 1.0)
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)


async def common_test_func_window_dpi_scale_decrease(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)

    # use menu
    await ui_test.menu_click("Window/DPI Scale/Decrease")

    # verify state
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), 0.5)

    # cannot use menu so use hotkey instead
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify state - still 0.5 because it gets clamped to the min
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), 0.5)

    # reset state
    carb.settings.get_settings().set(DPI_SCALE_OVERRIDE_SETTING, 1.0)
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)


async def common_test_hotkey_func_window_dpi_scale_decrease(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)

    # hotkey
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify state
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), 0.5)

    # hotkey
    await ui_test.emulate_keyboard_press(menu_item.hotkey[1], menu_item.hotkey[0])

    # verify state - still 0.5 because it gets clamped to the min
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), 0.5)

    # reset state
    carb.settings.get_settings().set(DPI_SCALE_OVERRIDE_SETTING, 1.0)
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)


async def common_test_func_window_dpi_scale_reset(tester: AsyncTestCase, menu_item: MenuItemDescription):
    # verify default state
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)

    # use menu
    await ui_test.menu_click("Window/DPI Scale/Reset")

    # verify state
    await tester.assertEqualWithRetry(lambda: omni.appwindow.get_default_app_window().get_dpi_scale_override(), -1.0)

    # reset state
    carb.settings.get_settings().set(DPI_SCALE_OVERRIDE_SETTING, 1.0)
    tester.assertEqual(omni.appwindow.get_default_app_window().get_dpi_scale_override(), 1.0)
