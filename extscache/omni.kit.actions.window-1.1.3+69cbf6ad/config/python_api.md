# Public API for module omni.kit.actions.window:

## Classes

- class AbstractActionItem(ui.AbstractItem)
  - def __init__(self, id: str, highlight: str = None)

- class ActionExtItem(AbstractActionItem)
  - def __init__(self, ext_id: str, highlight: str = None)

- class AbstractActionsModel(ui.AbstractItemModel)
  - def __init__(self, column_registry: ColumnRegistry)
  - def get_item_children(self, item: Optional[ActionExtItem]) -> List[ui.AbstractItem]
  - def get_ext_items(self) -> List[ActionExtItem]
  - def get_detail_items(self, item: ActionExtItem) -> List[AbstractActionItem]
  - def get_item_value_model_count(self, item: ui.AbstractItem) -> int
  - def get_item_value_model(self, item: Optional[ui.AbstractItem] = None, index: int = 0) -> Optional[ui.AbstractValueModel]
  - def clean(self)

- class ColumnRegistry
  - def __init__(self)
  - [property] def max_column_id(self) -> int
  - def register_delegate(self, delegate: AbstractColumnDelegate, column_id: int = -1, overwrite_if_exists: bool = True) -> bool
  - def unregister_delegate(self, column_id: int) -> bool
  - def get_delegate(self, column_id: int) -> Optional[AbstractColumnDelegate]

- class ActionsView(ui.TreeView)
  - def __init__(self, model: AbstractActionsModel, delegate: ActionsDelegate)

- class AbstractColumnDelegate
  - def __init__(self, name: str, width: ui.Length = ui.Fraction(1))
  - [property] def width(self) -> ui.Length
  - def execute(self, item: ui.AbstractItem)
  - def build_widget(self, model: ui.AbstractItemModel, item: ui.AbstractItem, level: int, expand: bool) -> ui.Widget
  - def build_header(self)

- class StringColumnDelegate(AbstractColumnDelegate)
  - def __init__(self, name: str, get_value_fn: Callable[[AbstractActionItem], str] = None, width: ui.Length = ui.Fraction(1))
  - def build_widget(self, model: AbstractActionsModel, item: AbstractActionItem, level: int, expand: bool)
  - def get_value(self, item: AbstractActionItem)

- class ActionsDelegate(ui.AbstractItemDelegate)
  - def __init__(self, model: AbstractActionsModel, column_registry: ColumnRegistry)
  - [property] def column_widths(self) -> List[ui.Length]
  - def build_branch(self, model: ui.AbstractItemModel, item: ui.AbstractItem, column_id: int = 0, level: int = 0, expanded: bool = False)
  - def build_widget(self, model: ui.AbstractItemModel, item: ui.AbstractItem, column_id: int = 0, level: int = 0, expanded: bool = False)
  - def build_header(self, column_id)
  - def on_mouse_double_click(self, button: int, item: ui.AbstractItem, column_delegate: AbstractColumnDelegate)
  - def on_mouse_pressed(self, button: int, item: ui.AbstractItem, column_delegate: AbstractColumnDelegate)

- class ActionsPicker(ActionsWindow)
  - def __init__(self, width = 0, height = 600, on_selected_fn: Callable[[Action], None] = None, expand_all: bool = True, focus_search: bool = True)

- class ActionDetailItem(AbstractActionItem)
  - def __init__(self, action: Action, highlight: str = None)

- class ActionsModel(AbstractActionsModel)
  - def __init__(self, column_registry: ColumnRegistry, on_search_action_fn: Callable[[Action, str], bool] = None)
  - def get_ext_items(self) -> List[ActionExtItem]
  - def get_detail_items(self, item: ActionExtItem) -> List[ActionDetailItem]
  - def search(self, search_words: Optional[List[str]])
  - def execute(self, item: ActionDetailItem)

## Variables

- ACTIONS_WINDOW_STYLE: Dict
