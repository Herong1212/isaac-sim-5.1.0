# Public API for module omni.kit.converter.hoops:

## Classes

- class HoopsConverter(ICadExtBase)
  - DELEGATE: HoopsConverterDelegate
  - FILTER_DATA: HOOPS_CORE_FILTER_DATA
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class HoopsConverterDelegate(ai.AbstractImporterDelegate)
  - def __init__(self, name, filters, descriptions)
  - def destroy(self)
  - [property] def name(self)
  - [property] def filter_regexes(self)
  - [property] def filter_descriptions(self)
  - def build_options(self, paths)
  - def supports_usd_stage_cache(self)
  - def show_scene_optimizer_config_frame(self)
  - async def convert_assets(self, paths, **kargs) -> Dict[str, Union[str, None]]
  - def create_temp_json(self, import_path: str) -> str
  - async def launch_kit_app(self, file_path: str, output_path: str) -> tuple[int, str]

## Functions

- def get_instance() -> Optional[HoopsConverter]
