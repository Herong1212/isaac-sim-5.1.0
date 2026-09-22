# Public API for module omni.kit.tool.collect:

## Classes

- class PublicExtension(omni.ext.IExt)
  - def on_startup(self)
  - def on_shutdown(self)
  - def collect(self, filepath: str, finish_callback: Callable[[], None] = None)
  - def get_content_window(self)
  - def get_content_folder(self)
  - def collect_multiple(self, filepaths: str, folder_name: str, target_folder: str = '', finish_callback: Callable[[], None] = None)
  - def collect_multiple_in_folder(self, folder: str, target_name: str = '', target_folder: str = '', finish_get_files_callback: Callable[[], None] = None, finish_collect_callback: Callable[[], None] = None)

- class Collector
  - def __init__(self, usd_path: str, collect_dir: str, usd_only: bool = False, flat_collection: bool = False, material_only: bool = False, failure_options = CollectorFailureOptions.SILENT, skip_existing: bool = False, max_concurrent_tasks = 32, texture_option = FlatCollectionTextureOptions.BY_MDL, force_non_read_only = True, exclusion_rules = {}, default_prim_only = False, **kwargs)
  - def destroy(self)
  - [property] def target_folder(self) -> str
  - [property] def source_stage_url(self) -> str
  - [property] def collect_mapping_file_url(self)
  - def get_target_url(self, source_url: str) -> str
  - def get_source_target_url_mapping(self) -> Dict[str, str]
  - def is_copy_skipped(self, source_url) -> bool
  - async def open_or_create_layer(self, layer_path, clear = True)
  - async def add_copy_task(self, source: str, target: str, skip_if_existed = False)
  - async def add_write_task(self, target: str, content: Union[str, bytes])
  - async def wait_all_unfinished_tasks(self, all_completed = False)
  - def get_status(self) -> CollectorStatus
  - def is_finished(self)
  - def is_cancelled(self)
  - def cancel(self)
  - async def collect(self, progress_callback: Callable[[int, int], None] = None, finish_callback: Callable[[], None] = None) -> Tuple[bool, str]

- class CollectorTaskType(Enum)
  - READ_TASK: int
  - WRITE_TASK: int
  - COPY_TASK: int
  - RESOLVE_TASK: int

- class CollectorException(Exception)
  - def __init__(self, error: str)

## Functions

- def get_instance()
