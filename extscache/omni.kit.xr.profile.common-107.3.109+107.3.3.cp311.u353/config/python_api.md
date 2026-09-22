# Public API for module omni.kit.xr.profile.common:

## Classes

- class XRDisableSave(XRSingletonType)
  - def __init__(self)
  - def destroy(self)
  - def add_profile(self, name: str)
  - def remove_profile(self, name: str)

- class XRShutdown
  - class def add_shutdown_function(cls, fn: Callable[[], Any], module: str, description: str)
  - class def assert_object_deletion_upon_shutdown(cls, obj: Any)
  - class def run_shutdown_functions(cls, module: str)

- class XRCommonProfileExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class XRProfileCommon
  - def __init__(self)
  - def on_profile_startup(self)
  - def on_profile_shutdown(self)
  - def on_startup(self)
  - def on_shutdown(self)
  - def setup_settings_window(self, components: Any, icons: Union[None, List[str]] = None, show_message: bool = False) -> XRProfileSettingsWindow
  - def setup_zero_conf(self)
  - def set_ar_mode(self, ar_mode)
  - def disable_saving(self)
  - def get_default_render_quality_items(self) -> dict
  - def get_name(self) -> str
  - def get_extension_name(self) -> str
  - def get_profile_name(self) -> str
  - def get_profile_path(self) -> str
  - def get_persistent_path(self) -> str
  - def get_non_persistent_path(self) -> str
  - def get_scene_persistent_path(self) -> str
  - def get_profile(self) -> XRProfile
  - def get_window_name(self) -> str
  - def destroy(self)
  - def on_activate_profile(self)
  - def on_deactivate_profile(self)
  - def on_open_file(self)

## Other

- omni.ext: public module
