__all__ = ["RTXSettingsExtension", "RendererSettingsFactory"]

from typing import Callable, List

import carb.settings
import omni.ext
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperExtension

from .rtx_settings_window import RTXSettingsWindow


class RTXSettingsExtension(omni.ext.IExt, MenuHelperExtension):
    """The entry point for the extension"""

    WINDOW_NAME = "Render Settings"

    def __init__(self) -> None:
        super().__init__()
        RendererSettingsFactory.render_settings_extension_instance = self
        self._settings_window = RTXSettingsWindow()
        self._settings_window.set_visibility_changed_listener(self._visiblity_changed_fn)

    def on_startup(self):
        ui.Workspace.set_show_window_fn(self.WINDOW_NAME, self.show_window)
        menu_group = carb.settings.get_settings().get("exts/omni.rtx.window.settings/window_menu")

        self.menu_startup(RTXSettingsExtension.WINDOW_NAME, RTXSettingsExtension.WINDOW_NAME, menu_group)

    def on_shutdown(self):
        self.menu_shutdown()
        if self._settings_window:
            self._settings_window.set_visibility_changed_listener(None)
            self._settings_window.destroy()
        self._settings_window = None
        RendererSettingsFactory.render_settings_extension_instance = None

        ui.Workspace.set_show_window_fn(self.WINDOW_NAME, None)

    def _visiblity_changed_fn(self, visible):
        self.menu_refresh()
        if not visible:
            self.show_window(False)

    def show_window(self, value):
        self._settings_window.set_visible(value)

    def show_render_settings(self, hd_engine: str, render_mode: str, show_window: bool = True):
        self._settings_window.set_render_settings_to_viewport_renderer(hd_engine, render_mode)
        if not show_window:
            return

        self.show_window(True)

        async def focus_async():
            window = ui.Workspace.get_window(self.WINDOW_NAME)
            if window:
                window.focus()

        import asyncio

        asyncio.ensure_future(focus_async())


class RendererSettingsFactory:
    """
    entry point for other extensions to register renderers and settings stacks
    """

    render_settings_extension_instance = None

    @classmethod
    def _get_render_settings_extension(cls):
        if not cls.render_settings_extension_instance:
            cls.render_settings_extension_instance = RTXSettingsExtension()
        return cls.render_settings_extension_instance

    @classmethod
    def register_renderer(cls, name: str, stacks_list: List[str]):
        rs = cls._get_render_settings_extension()
        rs._settings_window.register_renderer(name, stacks_list)
        rs._settings_window._build_ui()

    @classmethod
    def unregister_renderer(cls, name):
        rs = cls._get_render_settings_extension()
        rs._settings_window.unregister_renderer(name)

    @classmethod
    def build_ui(cls):
        """
        This method may be called by either:
        + a dependent extension that's shutting down or starting up
        + when the app is shutting down
        We want to distinguish between them
        """
        if omni.kit.app.get_app().is_running():
            rs = cls._get_render_settings_extension()
            rs._settings_window._build_ui()
            rs._settings_window._build_stacks()

    @classmethod
    def set_current_renderer(cls, renderer_name: str) -> None:
        """
        sets the current stack and updates the UI model
        """
        rs = cls._get_render_settings_extension()
        rs._settings_window.set_current_renderer(renderer_name)

    @classmethod
    def get_current_renderer(cls):
        rs = cls._get_render_settings_extension()
        return rs._settings_window.get_current_renderer()

    @classmethod
    def register_stack(cls, name: str, stack_class: Callable):
        rs = cls._get_render_settings_extension()
        rs._settings_window.register_stack(name, stack_class)

    @classmethod
    def unregister_stack(cls, name) -> None:
        rs = cls._get_render_settings_extension()
        rs._settings_window.unregister_stack(name)

    @classmethod
    def set_current_stack(cls, name) -> None:
        """
        sets the current stack and updates the UI model
        """
        rs = cls._get_render_settings_extension()
        rs._settings_window.show_stack_from_name(name)

    @classmethod
    def get_current_stack(cls) -> str:
        rs = cls._get_render_settings_extension()
        return rs._settings_window.get_current_stack()

    @classmethod
    def get_registered_renderers(cls) -> list:
        rs = cls._get_render_settings_extension()
        return rs._settings_window.get_registered_renderers()

    @classmethod
    def get_renderer_stacks(cls, renderer) -> list:
        rs = cls._get_render_settings_extension()
        return rs._settings_window.get_renderer_stacks(renderer)
