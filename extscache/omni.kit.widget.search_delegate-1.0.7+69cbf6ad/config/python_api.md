# Public API for module omni.kit.widget.search_delegate:

## Classes

- class SearchField(SearchDelegate)
  - SEARCH_IMAGE_SIZE: int
  - CLOSE_IMAGE_SIZE: int
  - def __init__(self, callback: Callable, **kwargs)
  - [property] def visible(self)
  - [visible.setter] def visible(self, value)
  - [property] def enabled(self)
  - [enabled.setter] def enabled(self, value)
  - [property] def search_dir(self)
  - [search_dir.setter] def search_dir(self, search_dir: str)
  - def build_ui(self)
  - def destroy(self)
  - def search(self, search_words: List[str])

- class SearchDelegate
  - def __init__(self)
  - [property] def visible(self)
  - [property] def enabled(self)
  - [property] def search_dir(self)
  - [search_dir.setter] def search_dir(self, search_dir: str)
  - def build_ui(self)
  - def destroy(self)

- class SearchResultsModel(FileBrowserModel)
  - def __init__(self, search_model: AbstractSearchModel, **kwargs)
  - def destroy(self)
  - def get_item_children(self, item: SearchResultsItem) -> [SearchResultsItem]

- class SearchResultsItem(FileBrowserItem)
  - def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = False)
  - async def get_custom_thumbnails_for_folder_async(self) -> Dict
