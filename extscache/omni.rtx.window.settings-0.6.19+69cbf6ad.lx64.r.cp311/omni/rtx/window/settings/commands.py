__all__ = [
    "RestoreDefaultRenderSettingCommand",
    "RestoreDefaultRenderSettingSectionCommand",
    "SetCurrentRenderer",
    "SetCurrentStack",
]

import carb
import carb.dictionary
import carb.settings
import omni.kit.commands
from omni.rtx.window.settings import RendererSettingsFactory
from omni.rtx.window.settings.rendersettingsdefaults import RenderSettingsDefaults


class RestoreDefaultRenderSettingCommand(omni.kit.commands.Command):
    """
    Restore default setting for Renderer **Command**.

    Args:
        path: Path to the setting to be reset.
    """

    def __init__(self, path: str):
        self._path = path
        self._settings = carb.settings.get_settings()

    def do(self):
        self._value = self._settings.get(self._path)
        RenderSettingsDefaults().reset_setting_to_default(self._path)

    def undo(self):
        self._settings.set(self._path, self._value)


class RestoreDefaultRenderSettingSectionCommand(omni.kit.commands.Command):
    """
    Restore default settings for the whole section **Command**.

    Args:
        path: Path to the settings section to be reset.
    """

    def __init__(self, path: str):
        self._path = path
        self._settings = carb.settings.get_settings()

    def do(self):
        self._section_copy = self._settings.create_dictionary_from_settings(self._path)
        RenderSettingsDefaults().reset_setting_to_default(self._path)

    def undo(self):
        self._settings.destroy_item(self._path)
        self._settings.update(self._path, self._section_copy, "", carb.dictionary.UpdateAction.OVERWRITE)


class SetCurrentRenderer(omni.kit.commands.Command):
    """
    Sets the current renderer
    Args:
        renderer_name: name of the renderer
    """

    def __init__(self, renderer_name: str):
        self._renderer = renderer_name
        self._prev_renderer = None

    def do(self):
        self._prev_renderer = RendererSettingsFactory.get_current_renderer()
        RendererSettingsFactory.set_current_renderer(self._renderer)

    def undo(self):
        if self._prev_renderer:
            RendererSettingsFactory.set_current_renderer(self._prev_renderer)


class SetCurrentStack(omni.kit.commands.Command):
    """
    Sets the current stack (needs to be one which is valid for the current renderer)
    Args:
        stack_name: name of the stack
    """

    def __init__(self, stack_name: str):
        self._stack = stack_name
        self._prev_stack = None

    def do(self):
        self._prev_stack = RendererSettingsFactory.get_current_stack()
        RendererSettingsFactory.set_current_stack(self._stack)

    def undo(self):
        if self._prev_stack:
            RendererSettingsFactory.set_current_stack(self._prev_stack)


omni.kit.commands.register_all_commands_in_module(__name__)
