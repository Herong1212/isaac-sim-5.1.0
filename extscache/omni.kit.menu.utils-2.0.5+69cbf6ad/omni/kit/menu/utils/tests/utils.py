# pylint: disable=broad-exception-raised
import carb
import omni.ui as ui
from omni.kit import ui_test


def verify_menu_items(cls, verify_list, use_menu_spacers: bool = False):
    menu_widget = ui_test.get_menubar()
    menu_widgets = []

    def show_debug():  # pragma: no cover
        nonlocal verify_list, use_menu_spacers

        debug_info = ""
        for w in menu_widgets:
            if isinstance(w.widget, (ui.Menu, ui.MenuItem, ui.Separator)):
                debug_info += f"(ui.{w.widget.__class__.__name__.replace('uiMenu','Menu')}, \"{w.widget.text.strip()}\", {w.widget.visible}), "
            elif isinstance(w.widget, ui.Spacer) and use_menu_spacers:
                debug_info += f"(ui.{w.widget.__class__.__name__.replace('uiMenu','Menu')}, {w.widget.visible}), "

        verify_list = str(verify_list).replace("<class 'omni.ui._ui.MenuItem'>", "ui.uiMenuItem")
        verify_list = verify_list.replace("<class 'omni.ui._ui.Menu'>", "ui.uiMenu")
        carb.log_error(f"verify_menu_items [{debug_info[:-2]}] vs {verify_list}")

    for w in menu_widget.find_all("**/"):
        if isinstance(w.widget, (ui.Menu, ui.MenuItem, ui.Separator)) or (
            isinstance(w.widget, ui.Spacer)
            and use_menu_spacers
            and w.widget.identifier in ["right_aligned_menus", "right_padding"]
        ):
            menu_widgets.append(w)

    try:
        cls.assertEqual(len(menu_widgets), len(verify_list))
        for index, item in enumerate(verify_list):
            widget = menu_widgets[index]
            if isinstance(widget.widget, (ui.Menu, ui.MenuItem, ui.Separator)):
                cls.assertTrue(
                    isinstance(widget.widget, item[0]),
                    f'menu type error {widget.widget} vs {item[0]} on "{widget.widget.text.strip()}"',
                )
                cls.assertEqual(
                    widget.widget.text.strip(),
                    item[1],
                    f'Menu item {index} text value is wrong ("{widget.widget.text.strip()}" vs "{item[1]})"',
                )
                cls.assertEqual(
                    widget.widget.visible,
                    item[2],
                    f'Menu item {index} visible value is wrong on "{widget.widget.text.strip()}" ({widget.widget.visible} vs {item[2]})',
                )
            elif (
                isinstance(widget.widget, ui.Spacer)
                and use_menu_spacers
                and widget.widget.identifier in ["right_aligned_menus", "right_padding"]
            ):
                cls.assertTrue(isinstance(widget.widget, item[0]), f"menu type error {widget.widget} vs {item[0]}")
                cls.assertEqual(widget.widget.visible, item[1], "Menu item spacer value is wrong")
    except Exception as exc:  # pragma: no cover
        show_debug()
        raise Exception(exc) from exc


def verify_menu_checked_items(cls, verify_list):
    menu_widget = ui_test.get_menubar()
    menu_widgets = []

    def show_debug():  # pragma: no cover
        nonlocal verify_list

        debug_info = ""
        for w in menu_widgets:
            if isinstance(w.widget, (ui.Menu, ui.MenuItem)) and w.widget.text.strip() != "placeholder":
                debug_info += f'(ui.{w.widget.__class__.__name__}, "{w.widget.text.strip()}", {w.widget.visible}, {w.widget.checkable}, {w.widget.checked}), '

        verify_list = str(verify_list).replace("<class 'omni.ui._ui.MenuItem'>", "ui.uiMenuItem")
        verify_list = verify_list.replace("<class 'omni.ui._ui.Menu'>", "ui.uiMenu")
        carb.log_error(f"verify_menu_items [{debug_info[:-2]}] vs {verify_list}")

    for w in menu_widget.find_all("**/"):
        if isinstance(w.widget, (ui.Menu, ui.MenuItem)) and w.widget.text.strip() != "placeholder":
            menu_widgets.append(w)

    try:
        cls.assertEqual(len(menu_widgets), len(verify_list))
        for index, item in enumerate(verify_list):
            widget = menu_widgets[index]
            cls.assertTrue(isinstance(widget.widget, item[0]), f"menu type error {widget.widget} vs {item[0]}")
            cls.assertEqual(
                widget.widget.text.strip(),
                item[1],
                f'Menu item {index} text value is wrong ("{widget.widget.text.strip()}" vs "{item[1]})"',
            )
            cls.assertEqual(
                widget.widget.visible,
                item[2],
                f'Menu item {index} visible value is wrong on "{widget.widget.text.strip()}" ({widget.widget.visible} vs {item[2]})',
            )
            cls.assertEqual(
                widget.widget.checkable,
                item[3],
                f'Menu item checkable value is wrong on "{widget.widget.text.strip()}"',
            )
            cls.assertEqual(
                widget.widget.checked, item[4], f'Menu item checked value is wrong on "{widget.widget.text.strip()}"'
            )
    except Exception as exc:  # pragma: no cover
        show_debug()
        raise Exception(exc) from exc


async def refresh_menus(menu: str, menu_click: str = ""):
    import omni.kit.menu.utils

    omni.kit.menu.utils.refresh_menu_items(menu)
    if menu_click:
        await ui_test.menu_click(menu_click, human_delay_speed=4, show=True)
        await ui_test.menu_click(menu_click.split("/")[0], human_delay_speed=4, show=False)
    else:
        await ui_test.menu_click(menu, human_delay_speed=4, show=True)
        await ui_test.menu_click(menu.split("/")[0], human_delay_speed=4, show=False)

    await ui_test.human_delay(10)
