# Public API for module omni.kit.widget.options_menu:

## Classes

- class OptionCustom(AbstractOptionItem)
  - def __init__(self, build_fn: callable, model: Optional[ui.AbstractValueModel] = None, default: Optional[Any] = None)
  - def build_menu_item(self, **kwargs)
  - [property] def name(self) -> str
  - [property] def model(self) -> ui.SimpleBoolModel
  - [property] def dirty(self) -> bool
  - def reset(self)

- class OptionItem(AbstractOptionItem)
  - def __init__(self, name: Optional[str], text: Optional[str] = None, default: bool = False, on_value_changed_fn: Callable[[bool], None] = None, model: Optional[ui.SimpleBoolModel] = None, setting_path: Optional[str] = None, enabled: bool = True, checkable: bool = True, hide_on_click: bool = False)
  - def destroy(self)
  - def build_menu_item(self, **kwargs)
  - def build_custom_widget(self, item: ui.MenuItem)
  - def on_triggered(self)
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value: bool)
  - [property] def value(self) -> bool
  - [value.setter] def value(self, new_value: bool)
  - [property] def model(self) -> ui.SimpleBoolModel
  - [property] def dirty(self) -> bool
  - def reset(self)

- class OptionLabelMenuItemDelegate(ui.MenuDelegate)
  - def __init__(self, width: ui.Length = ui.Fraction(1))
  - def build_item(self, item: ui.MenuItem)
  - def build_widget(self, item: ui.MenuItem)

- class OptionRadios(AbstractOptionItem)
  - def __init__(self, radios: List[Union[str, Tuple[str]]], model: Optional[ui.SimpleStringModel] = None, setting_path: Optional[str] = None, default: Optional[str] = None, menu_text: Optional[str] = None, enabled: bool = True, tooltips: Optional[List[str]] = None, hide_on_click: bool = False)
  - def destroy(self)
  - def build_menu_item(self, **menu_item_kwargs: dict)
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value: bool)
  - [property] def model(self) -> ui.SimpleStringModel
  - [property] def dirty(self) -> bool
  - def reset(self)

- class OptionSeparator(AbstractOptionItem)
  - def __init__(self, title: str = None)
  - def build_menu_item(self, **menu_item_kwargs)
  - [property] def name(self) -> str

- class OptionsMenu(AbstractPopupMenu)
  - def __init__(self, model: OptionsModel, hide_on_click: bool = False, width: ui.Length = ui.Fraction(1), style: dict = {})
  - def destroy(self)
  - [property] def model(self) -> OptionsModel
  - def rebuild_items(self, items: List[AbstractOptionItem])
  - def build_menu_items(self)

- class OptionsModel(ui.AbstractItemModel)
  - def __init__(self, name: str, items: List[AbstractOptionItem])
  - def destroy(self)
  - [property] def dirty(self) -> bool
  - def rebuild_items(self, items: List[AbstractOptionItem])
  - def reset(self)
  - def get_item_children(self, item: Optional[AbstractOptionItem] = None) -> List[AbstractOptionItem]

- class RadioMenu(AbstractPopupMenu)
  - def __init__(self, title: str, radio_model: Union[RadioModel, List[RadioModel]])
  - def destroy(self)
  - def build_menu_items(self)

- class RadioModel(ui.AbstractItemModel)
  - def __init__(self, texts: List[str], default_index: int = 0)
  - [property] def dirty(self) -> bool
  - [property] def index_model(self) -> ui.SimpleIntModel
  - [property] def index(self) -> int
  - [index.setter] def index(self, value: int)
  - [property] def index_text(self) -> str
  - def reset(self)
  - def get_item_children(self, item: Optional[RadioItem] = None) -> List[RadioItem]
