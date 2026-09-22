# Public API for module omni.kit.search_core:

## Classes

- class AbstractSearchItem
  - [property] def path(self)
  - [property] def name(self)
  - [property] def date(self)
  - [property] def size(self)
  - [property] def icon(self)
  - [property] def is_folder(self)

- class AbstractSearchModel
  - def __init__(self)
  - [property] def items(self)
  - def destroy(self)
  - def subscribe_item_changed(self, fn)

- class SearchLifetimeObject
  - def __init__(self, callback)
  - def destroy(self)

- class SearchEngineRegistry
  - def __init__(self)
  - def register_search_model(self, name, model_type)
  - def get_search_names(self)
  - def get_available_search_names(self, server: str)
  - def get_search_model(self, name)
  - def subscribe_engines_changed(self, fn)
