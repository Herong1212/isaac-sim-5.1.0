# Public API for module omni.kit.pointclouds:

## Classes

- class OmniClientWrapper
  - static async def exists(path)
  - static def exists_sync(path)
  - static def parent(path: str) -> str
  - static def writeable(path: str)
  - static async def writeable_async(path: str) -> bool
  - static async def write(path: str, content)
  - static async def copy(src_path: str, dest_path: str)
  - static async def read(src_path: str)
  - static async def create_folder(path)

- class ConvertE57FilesCommand(omni.kit.commands.Command)
  - def __init__(self, paths: list, out_dir = '', combine_scans = True, center_pointcloud = False, to_usd = False)
  - def do(self)
  - def undo(self)

- class RunVdbTaskCommand(omni.kit.commands.Command)
  - def __init__(self, path: str, out_dir = '', local_farm = False, farm_worker_count = 0, neural_vdb = False, render_mode = '')
  - def do(self)
  - def undo(self)

- class E57Importer(ai.AbstractImporterDelegate)
  - def __init__(self, extension_path)
  - def destroy(self)
  - def reset(self)
  - [property] def name(self) -> str
  - [property] def filter_regexes(self) -> List[str]
  - [property] def filter_descriptions(self) -> List[str]
  - def get_cache_path(self, uri: str, import_method = ImportMethod.STREAM)
  - def build_options(self, paths: List[str])
  - async def get_asset_path(self, absolute_path)
  - async def convert_assets(self, paths: List[str]) -> Dict[str, Union[str, None]]
  - async def added_reference(self, assets)

- class LidarBINImporter(ai.AbstractImporterDelegate)
  - def __init__(self, extension_path)
  - def destroy(self)
  - [property] def name(self) -> str
  - [property] def filter_regexes(self) -> List[str]
  - [property] def filter_descriptions(self) -> List[str]
  - def build_options(self, paths: List[str])
  - async def convert_assets(self, paths: List[str]) -> Dict[str, Union[str, None]]

- class PTSImporter(ai.AbstractImporterDelegate)
  - def __init__(self, extension_path)
  - def destroy(self)
  - [property] def name(self) -> str
  - [property] def filter_regexes(self) -> List[str]
  - [property] def filter_descriptions(self) -> List[str]
  - def build_options(self, paths: List[str])
  - async def convert_assets(self, paths: List[str]) -> Dict[str, Union[str, None]]

- class PointCloudsExtension(omni.ext.IExt)
  - instance: NoneType
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

## Functions

- static def create_point_cloud_prim(src_path, render_mode = '', pointcloud_path = '')
- def submit_task(farm_uri: str, task_type: str, task_fn: str, fn_args: dict, task_name = 'point cloud', task_comment = '', next_fn: Callable = None)
- def get_pointclouds_instance()

## Variables

- CACHE_PATH_SETTINGS_KEY: str
- FARM_URI_SETTINGS_KEY: str

## Other

- asyncio: builtin module
- os: builtin module
- Path: unknown
- carb: public module
- omni.kit.commands: public module
- Sdf: unknown module
- Tf: unknown module
- omni.ext: public module
