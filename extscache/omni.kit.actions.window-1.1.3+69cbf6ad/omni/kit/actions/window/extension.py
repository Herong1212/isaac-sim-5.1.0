__all__ = ["ActionsExtension"]
import carb.settings
import omni.ext
import omni.ui as ui
from omni.kit.actions.core import get_action_registry
from omni.kit.menu.utils import MenuHelperExtension

from .window import ActionsWindow

SETTING_SHOW_STARTUP = "/exts/omni.kit.actions.window/showStartup"

class ActionsExtension(omni.ext.IExt, MenuHelperExtension):
    WINDOW_NAME = "Actions"
    MENU_GROUP = "Window"

    def on_startup(self):
        self._actions_window = None

        ui.Workspace.set_show_window_fn(
            ActionsExtension.WINDOW_NAME,
            self.show_window,
        )
        self.menu_startup(ActionsExtension.WINDOW_NAME, ActionsExtension.WINDOW_NAME, ActionsExtension.MENU_GROUP)

        show_startup = carb.settings.get_settings().get(SETTING_SHOW_STARTUP)
        if show_startup:
            ui.Workspace.show_window(ActionsExtension.WINDOW_NAME)
        
    def on_shutdown(self):
        self.menu_shutdown()
        if self._actions_window:
            self._actions_window.destroy()
            self._actions_window = None

        ui.Workspace.set_show_window_fn(ActionsExtension.WINDOW_NAME, None)

    def show_window(self, visible: bool):
        if visible:
            self._actions_window = ActionsWindow(ActionsExtension.WINDOW_NAME)
            self._actions_window.set_visibility_changed_fn(self._visibility_changed_fn)
        elif self._actions_window:
            self._actions_window.visible = False

    def _visibility_changed_fn(self, visible):
        self.menu_refresh()


