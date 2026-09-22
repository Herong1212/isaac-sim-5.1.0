# Public API for module omni.kit.usd.collect:

## Classes

- class CollectorStatus(Enum)
  - NOT_STARTED: int
  - IN_PROGRESS: int
  - FINISHED: int
  - CANCELLED: int

- class CollectorFailureOptions(IntFlag)
  - SILENT: int
  - EXTERNAL_USD_REFERENCES: int
  - OTHER_EXTERNAL_REFERENCES: int

- class CollectorTaskType(Enum)
  - READ_TASK: int
  - WRITE_TASK: int
  - COPY_TASK: int
  - RESOLVE_TASK: int

- class CollectorException(Exception)
  - def __init__(self, error: str)

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

- class DefaultPrimOnlyOptions(Enum)
  - ROOT_LAYER_ONLY: int
  - ALL_LAYERS: int

- class FlatCollectionTextureOptions(Enum)
  - BY_MDL: int
  - BY_USD: int
  - FLAT: int

## Variables

- COLLECT_MAPPING_FILE_NAME: str
