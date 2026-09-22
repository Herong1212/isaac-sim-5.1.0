# Public API for module omni.ui_query:

## Classes

- class OmniUIQuery
  - def __init__(self)
  - class def get_widget_path(cls, window: ui.Window, widget: ui.Widget) -> Union[str, None]
  - class def get_widget_children_with_path(cls, widget: ui.Widget, path: str) -> Dict[ui.Widget, str]
  - class def get_window_widget_paths(cls, window: ui.Window, widget_postfix_fn: Optional[Callable[[ui.Widget], str]] = None) -> List[str]
  - class def find_menu_item(cls, query: str) -> Optional[ui.Widget]
  - class def find_widgets(cls, query: str, root_widgets = []) -> List[ui.Widget]
  - class def find_first_widget(cls, query: str, root_widgets = []) -> ui.Widget
  - class def find_widget(cls, query: str) -> Union[ui.Widget, None]
