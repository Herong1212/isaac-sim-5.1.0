# omni.kit.search_example

## Python Search Core

The example provides search model AbstractSearchModel and search registry
SearchEngineRegistry.

`AbstractSearchModel` represents the search results. It supports async mode. If
the search engine needs some time to process the request, it can return an
empty list and do a search in async mode. As soon as a result is ready, the
model should call `self._item_changed()`. It will make the view reload the
model. It's also possible to return the search result with portions.

`AbstractSearchModel.__init__` is usually called with the named arguments
search_text and current_dir.

`SearchEngineRegistry` keeps all the search engines. It's used to put custom
search engine to the content browser. It provides fast access to search
engines. Any extension that can use the objects derived from
`AbstractSearchModel` can use the search.
