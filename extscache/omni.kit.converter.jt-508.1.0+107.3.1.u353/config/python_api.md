# Public API for module omni.kit.converter.jt:

## Classes

- class JtConverter(ICadExtBase)
  - DELEGATE: JtConverterDelegate
  - FILTER_DATA: JT_CORE_FILTER_DATA
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class JtConverterDelegate(ai.AbstractImporterDelegate)
  - def __init__(self, name, filters, descriptions)
  - def destroy(self)
  - [property] def name(self)
  - [property] def filter_regexes(self)
  - [property] def filter_descriptions(self)
  - def build_options(self, paths)
  - def supports_usd_stage_cache(self)
  - def show_scene_optimizer_config_frame(self)
  - async def convert_assets(self, paths, **kargs)
  - def create_temp_json(self, import_path: str) -> str
  - async def launch_kit_app(self, file_path: str, output_path: str) -> tuple[int, str]

## Functions

- def get_instance() -> Optional[JtConverter]
