# Public API for module omni.kit.property.bundle:

## Classes

- class BundlePropertyWidgets(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class GeomPrimSchemeDelegate(PropertySchemeDelegate)
  - def get_widgets(self, payload)
  - def get_unwanted_widgets(self, payload)

- class MaterialPrimSchemeDelegate(PropertySchemeDelegate)
  - def get_widgets(self, payload)
  - def get_unwanted_widgets(self, payload)

- class PathPrimSchemeDelegate(PropertySchemeDelegate)
  - def get_widgets(self, payload)

- class ShaderPrimSchemeDelegate(PropertySchemeDelegate)
  - def get_widgets(self, payload)
  - def get_unwanted_widgets(self, payload)
