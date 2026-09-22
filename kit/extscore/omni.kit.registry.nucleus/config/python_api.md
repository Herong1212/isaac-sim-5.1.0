# Public API for module omni.kit.registry.nucleus:

## Classes

- class RegistryProvider(omni.ext.IRegistryProvider)
  - def __init__(self, name: str, url: str, trusted: bool, optional: bool, registry_globals: RegistryGlobals)
  - def shutdown(self)
  - def get_urls(self) -> RegistryURLs
  - def refresh_index(self)
  - def sync_index(self)
  - def apply_index_changes_batch(self)
  - def publish_extension(self, ext_path: str, ext_item: carb.dictionary.Item) -> bool
  - def unpublish_extension(self, ext_id: str) -> bool
  - def pull_extension(self, ext_id: str, ext_folder: str) -> bool
  - def pull_extension_async(self, ext_id: str, ext_folder: str) -> omni.ext.DownloadState

- class PublishResult
  - OK: str
  - OK_EXISTS: str
  - FAIL: str
  - SKIP: str

## Functions

- def verify_extension_for_publishing(ext_dict: carb.dictionary.Item) -> Tuple[bool, str]
- def start_index_changes_batching()
- def apply_index_changes_batch()
- def get_publish_results() -> dict
- def get_registry_url_by_name(registry_name: str) -> str
- def get_registry_url_by_ext_dict(ext_dict: carb.dictionary.Item) -> str
- def get_package_resource_url_by_key(key: str, ext_dict: carb.dictionary.Item) -> str
- def get_preview_image_url(ext_dict: carb.dictionary.Item) -> str
- def get_icon_url(ext_dict: carb.dictionary.Item) -> str
- def get_extension_metadata_possible_urls(ext_dict: carb.dictionary.Item) -> List[str]
- def get_extension_metadata_url(ext_dict: carb.dictionary.Item) -> str
