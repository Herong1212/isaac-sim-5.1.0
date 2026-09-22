# pylint: disable=attribute-defined-outside-init

__all__ = ["HotkeysExtension"]
import carb.settings
import omni.ext
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperExtension
from .window.hotkeys_window import HotkeysWindow

SETTING_SHOW_STARTUP = "/exts/omni.kit.hotkeys.window/showStartup"


class HotkeysExtension(omni.ext.IExt, MenuHelperExtension):
    WINDOW_NAME = "Hotkeys"
    MENU_GROUP = "Window"

    def on_startup(self):
        self._window = None

        ui.Workspace.set_show_window_fn(
            HotkeysExtension.WINDOW_NAME,
            self.show_window,
        )

        self.menu_startup(HotkeysExtension.WINDOW_NAME, HotkeysExtension.WINDOW_NAME, HotkeysExtension.MENU_GROUP)

        show_startup = carb.settings.get_settings().get(SETTING_SHOW_STARTUP)
        if show_startup:
            ui.Workspace.show_window(HotkeysExtension.WINDOW_NAME)

    def on_shutdown(self):
        self.menu_shutdown()
        ui.Workspace.set_show_window_fn(HotkeysExtension.WINDOW_NAME, None)
        if self._window:
            self._window.destroy()
            self._window = None

    def show_window(self, visible: bool):
        if visible:
            self._window = HotkeysWindow(HotkeysExtension.WINDOW_NAME)
            self._window.set_visibility_changed_fn(self._visibility_changed_fn)
        elif self._window:
            self._window.visible = False

    def _visibility_changed_fn(self, visible):
        self.menu_refresh()
        if self._window and not visible:
            self._window.stop_key_capture()
