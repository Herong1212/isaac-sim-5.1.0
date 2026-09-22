# Public API for module omni.vdb_timesample_editor:

## Classes

- class TimeSampleEditor
  - def __init__(self)
  - def show(self, attr_path: Sdf.Path)
  - def close(self)
  - static def get_asset(value)
  - static def get_time_code(value)
  - def load_time_samples(self)

- class TimeSamplePropertiesWidget(BasePropertiesWidget)
  - def __init__(self, element_type, attribute_names)
  - def build_properties(self)

- class PublicExtension(omni.ext.IExt)
  - def on_startup(self)
  - def on_shutdown(self)

## Other

- omni.ext: public module
