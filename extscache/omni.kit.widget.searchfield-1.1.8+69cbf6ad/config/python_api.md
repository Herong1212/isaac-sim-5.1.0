# Public API for module omni.kit.widget.searchfield:

## Classes

- class SearchField
  - SEARCH_IMAGE_SIZE: int
  - CLOSE_IMAGE_SIZE: int
  - def __init__(self, width: Optional[ui.Length] = None, height: Optional[ui.Length] = ui.Pixel(26), on_search_fn: Callable[[Optional[List[str]]], None] = None, subscribe_edit_changed: bool = False, show_tokens: bool = True, style: Dict = None, suggestions: Optional[List[str]] = None, max_suggestions: int = 10, separator = ' ')
  - def destroy(self)
  - [property] def visible(self) -> bool
  - [visible.setter] def visible(self, value)
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value)
  - [property] def search_words(self) -> Optional[List[str]]
  - [search_words.setter] def search_words(self, words: List[str])
  - [property] def suggestions(self) -> Optional[List[str]]
  - [suggestions.setter] def suggestions(self, words: List[str])
  - [property] def max_suggestions(self) -> int
  - [max_suggestions.setter] def max_suggestions(self, count: int)
  - def set_filter(self, filter_cls)
  - [property] def text(self) -> str
  - [text.setter] def text(self, text: str)
  - def clear(self)
