# Public API for module rtx.settings:

## Functions

- def get_associated_setting_flags_path(arg0: str) -> str
- def get_internal_setting_string(arg0: str) -> str

## Variables

- SETTING_FLAGS_NONE: int
- SETTING_FLAGS_RESET_DISABLED: int
- SETTING_FLAGS_TRANSIENT: int

# Public API for module omni.rtx.window.settings:

## Classes

- class RTXSettingsWindow
  - def __init__(self, usd_context_name = '')
  - def register_renderer(self, name: str, stacks_list: List[str])
  - def get_registered_renderers(self)
  - def get_current_renderer(self)
  - def set_current_renderer(self, renderer_name: str)
  - def register_stack(self, name: str, stack_class: Callable)
  - def show_stack_from_name(self, name: str)
  - def get_renderer_stacks(self, renderer_name)
  - def get_current_stack(self) -> str
  - def unregister_renderer(self, name)
  - def unregister_stack(self, name)
  - def set_visibility_changed_listener(self, listener)
  - def set_render_settings_to_viewport_renderer(self, *args, **kwargs)
  - def set_visible(self, value: bool)
  - def destroy(self)

- class RTXSettingsExtension(omni.ext.IExt, MenuHelperExtension)
  - WINDOW_NAME: str
  - def __init__(self)
  - def on_startup(self)
  - def on_shutdown(self)
  - def show_window(self, value)
  - def show_render_settings(self, hd_engine: str, render_mode: str, show_window: bool = True)

- class RendererSettingsFactory
  - render_settings_extension_instance: NoneType
  - class def register_renderer(cls, name: str, stacks_list: List[str])
  - class def unregister_renderer(cls, name)
  - class def build_ui(cls)
  - class def set_current_renderer(cls, renderer_name: str)
  - class def get_current_renderer(cls)
  - class def register_stack(cls, name: str, stack_class: Callable)
  - class def unregister_stack(cls, name)
  - class def set_current_stack(cls, name)
  - class def get_current_stack(cls) -> str
  - class def get_registered_renderers(cls) -> list
  - class def get_renderer_stacks(cls, renderer) -> list

- class RestoreDefaultRenderSettingCommand(omni.kit.commands.Command)
  - def __init__(self, path: str)
  - def do(self)
  - def undo(self)

- class RestoreDefaultRenderSettingSectionCommand(omni.kit.commands.Command)
  - def __init__(self, path: str)
  - def do(self)
  - def undo(self)

- class SetCurrentRenderer(omni.kit.commands.Command)
  - def __init__(self, renderer_name: str)
  - def do(self)
  - def undo(self)

- class SetCurrentStack(omni.kit.commands.Command)
  - def __init__(self, stack_name: str)
  - def do(self)
  - def undo(self)
