# Public API for module omni.kit.helper.file_utils:

## Classes

- class FileEventModel
  - url: str
  - asset_type: Optional[str]
  - is_folder: Optional[bool]
  - event_type: Optional[int]
  - event_name: Optional[str]
  - tag: Optional[str]
  - datetime: Optional[datetime]
  - def dict(self)

## Functions

- def get_latest_urls_from_event_queue(num_latest: int = 1, asset_type: str = None, event_type: int = 0, event_name: str = None, tag: str = None) -> List[str]
- def get_last_url_visited(asset_type: str = None, tag: str = None) -> str
- def get_last_url_opened(asset_type: str = None, tag: str = None) -> str
- def get_last_url_saved(asset_type: str = None, tag: str = None) -> str
- def reset_file_event_queue()

## Variables

- FILE_OPENED_GLOBAL_EVENT: str
- FILE_OPENED_EVENT: int
- FILE_SAVED_GLOBAL_EVENT: str
- FILE_SAVED_EVENT: int
- FILE_EVENT_QUEUE_UPDATED_GLOBAL_EVENT: str
- FILE_EVENT_QUEUE_UPDATED: int

## Other



# Public API for module omni.kit.helper.file_utils.asset_types:

## Functions

- def init_asset_types()
- def known_asset_types()
- def clear_asset_types()
- def register_file_extensions(asset_type: str, exts: [str], replace: bool = False)
- def asset_type_exts(asset_type: str) -> List[str]
- def is_asset_type(filename: str, asset_type: str) -> bool
- def is_udim_sequence(filename: str)
- def get_asset_type(filename: str) -> str
- def get_icon(filename: str) -> str
- def get_thumbnail(filename: str) -> str

## Variables

- AssetTypeDef: Unknown
- ASSET_TYPE_ANIM_USD: str
- ASSET_TYPE_CACHE_USD: str
- ASSET_TYPE_CURVE_ANIM_USD: str
- ASSET_TYPE_GEO_USD: str
- ASSET_TYPE_MATERIAL_USD: str
- ASSET_TYPE_PROJECT_USD: str
- ASSET_TYPE_SEQ_USD: str
- ASSET_TYPE_SKEL_USD: str
- ASSET_TYPE_SKEL_ANIM_USD: str
- ASSET_TYPE_USD_SETTINGS: str
- ASSET_TYPE_USD: str
- ASSET_TYPE_FBX: str
- ASSET_TYPE_OBJ: str
- ASSET_TYPE_MATERIAL: str
- ASSET_TYPE_IMAGE: str
- ASSET_TYPE_SOUND: str
- ASSET_TYPE_SCRIPT: str
- ASSET_TYPE_VOLUME: str
- ASSET_TYPE_FOLDER: str
- ASSET_TYPE_ICON: str
- ASSET_TYPE_HIDDEN: str
- ASSET_TYPE_UNKNOWN: str
