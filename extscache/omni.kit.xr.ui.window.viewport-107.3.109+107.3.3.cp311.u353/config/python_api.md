# Public API for module omni.kit.xr.ui.window.viewport:

## Classes

- class XRShutdown
  - class def add_shutdown_function(cls, fn: Callable[[], Any], module: str, description: str)
  - class def assert_object_deletion_upon_shutdown(cls, obj: Any)
  - class def run_shutdown_functions(cls, module: str)

- class XRViewportController(XRSingletonType)
  - def __init__(self)
  - def print_all_viewport_layers(viewport_window: ViewportWindow)

- class XRViewportLayer
  - def __init__(self, desc: dict)
  - def rebuild(self)
  - def build_ui(self)
  - def update_ui(self)
  - def destroy(self)
  - [property] def visible(self)
  - [visible.setter] def visible(self, value)
  - [property] def categories(self)
  - [property] def name(self)

- class XRUIViewportWindowExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

## Variables

- RegisterViewportLayer: Unknown

## Other

- Optional: unknown
- omni.ext: public module
