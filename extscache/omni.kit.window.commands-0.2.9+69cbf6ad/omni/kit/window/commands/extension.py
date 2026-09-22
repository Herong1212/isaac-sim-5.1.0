import carb.settings
import omni.ext
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperExtensionFull
from .main import Window

WINDOW_NAME = "Commands"


class Extension(omni.ext.IExt, MenuHelperExtensionFull):
    def on_startup(self):
        self.menu_startup(lambda: Window(WINDOW_NAME), WINDOW_NAME, WINDOW_NAME, "Window", window_attr_name="_win_history")
        open_by_default = carb.settings.get_settings().get("exts/omni.kit.window.commands/windowOpenByDefault")
        ui.Workspace.show_window(WINDOW_NAME, open_by_default)

    def on_shutdown(self):
        self.menu_shutdown()
