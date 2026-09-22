# Public API for module omni.kit.converter.dgn:

## Classes

- class DgnConverter(ICadExtBase)
  - DELEGATE: DgnConverterDelegate
  - FILTER_DATA: DGN_CORE_FILTER_DATA
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class DgnConverterDelegate(ai.AbstractImporterDelegate)
  - def __init__(self, name, filters, descriptions)
  - def destroy(self)
  - [property] def name(self) -> str
  - [property] def filter_regexes(self) -> List[str]
  - [property] def filter_descriptions(self) -> List[str]
  - def build_options(self, paths)
  - def supports_usd_stage_cache(self) -> bool
  - def show_scene_optimizer_config_frame(self)
  - async def convert_assets(self, paths, **kargs) -> Dict[str, Union[str, None]]
  - def create_temp_json(self, import_path: str) -> str
  - async def launch_kit_app(self, file_path: str, output_path: str) -> tuple[int, str]

## Functions

- def get_instance() -> Optional[DgnConverter]
