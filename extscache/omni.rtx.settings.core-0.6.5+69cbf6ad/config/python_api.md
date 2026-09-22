# Public API for module omni.rtx.settings.core:

## Classes

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

- class CommonSettingStack(RTXSettingsStack)
  - def __init__(self)

- class PostSettingStack(RTXSettingsStack)
  - def __init__(self)

- class PTSettingStack(RTXSettingsStack)
  - def __init__(self)

- class RTSettingStack(RTXSettingsStack)
  - def __init__(self)

- class RTPTSettingStack(RTXSettingsStack)
  - def __init__(self)

- class RTXSettingsExtension(omni.ext.IExt)
  - MENU_PATH: str
  - rendererNames: List
  - stackNames: List
  - def on_startup(self)
  - def on_shutdown(self)

## Other

- omni.ext: public module
- carb.settings: public module
