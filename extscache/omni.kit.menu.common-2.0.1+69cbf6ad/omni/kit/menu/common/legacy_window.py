__all__ = ["WindowExtension"]

import carb
import carb.input
import carb.settings
import omni.appwindow
import omni.kit.app
import omni.kit.menu.utils
from carb.input import KeyboardInput as Key
from omni.kit.menu.utils import MenuItemDescription


# "Window" menus still uses editor_menu helper, so menu items have priority
class MenuItemPriDescription(MenuItemDescription):
    def __init__(self, *argv, **kwargs):
        priority = kwargs["priority"]
        del kwargs["priority"]

        super().__init__(*argv, **kwargs)
        self.priority = priority


class WindowExtension:
    """A class to manage window-related extensions and menu items.

    This class provides functionalities to handle window-specific menu items, including toggling UI visibility, fullscreen mode, and DPI scaling options.

    The window menu items are initialized upon instantiation and removed upon deletion of the object.
    """

    SHOW_DPI_SCALE_MENU_SETTING = "/app/window/showDpiScaleMenu"

    def __init__(self):
        """Initializes the WindowExtension with default settings and menu items."""
        self._legacy_window = None

        self._window_menu = [
            MenuItemPriDescription(
                name="UI Toggle Visibility",
                onclick_action=("omni.kit.ui.actions", "toggle_ui"),
                hotkey=(0, Key.F7),
                priority=51,
            ),
            MenuItemPriDescription(
                name="Fullscreen Mode",
                onclick_action=("omni.kit.ui.actions", "toggle_fullscreen"),
                hotkey=(0, Key.F11),
                priority=52,
            ),
        ]

        settings = carb.settings.get_settings()
        if settings.get_as_bool(WindowExtension.SHOW_DPI_SCALE_MENU_SETTING):
            dpi_menu = [
                MenuItemDescription(
                    name="Increase",
                    onclick_action=("omni.kit.ui.actions", "dpi_scale_increase"),
                    hotkey=(0, Key.EQUAL),
                ),
                MenuItemDescription(
                    name="Decrease",
                    onclick_action=("omni.kit.ui.actions", "dpi_scale_decrease"),
                    hotkey=(0, Key.MINUS),
                ),
                MenuItemDescription(
                    name="Reset",
                    onclick_action=("omni.kit.ui.actions", "dpi_scale_reset"),
                ),
            ]

            self._window_menu.append(MenuItemPriDescription(name="DPI Scale", sub_menu=dpi_menu, priority=-98))

        omni.kit.menu.utils.add_menu_items(self._window_menu, "Window", -6)

    def __del__(self):
        omni.kit.menu.utils.remove_menu_items(self._window_menu, "Window")
        self._window_menu = None
