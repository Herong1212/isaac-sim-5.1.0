# Public API for module omni.kit.viewport.menubar.core:

## Classes

- class ViewportMenuBarExtension(omni.ext.IExt)
  - def __init__(self)
  - def init_shades(self)
  - def on_startup(self)
  - def on_shutdown(self)
  - def get_menubars(self) -> List[AbstractViewportMenubarItem]
  - def get_menubar(self, name: str) -> Optional[AbstractViewportMenubarItem]

- class AbstractViewportMenubarItem(AbstractViewportMenuItem)
  - def build_fn(self, menu_items: List[AbstractViewportMenuItem], factory_args: Dict)

- class AbstractViewportMenuItem(ui.AbstractItem)
  - def __init__(self, name: str = '', visible_setting_path: Optional[str] = None, order_setting_path: Optional[str] = None, expand_setting_path: Optional[str] = None)
  - def destroy(self)
  - [property] def name(self)
  - [property] def parent(self)
  - def get_display_status(self, factory_args: dict) -> MenuDisplayStatus
  - def get_require_size(self, factory_args: dict, expand: bool = False) -> float
  - def expand(self, factory_args: dict)
  - def can_contract(self, factory_args: dict) -> bool
  - def contract(self, factory_args: dict)

- class MenuDisplayStatus
  - MIN: int
  - LABEL: int
  - EXPAND: int
  - MAX: int

- class CategoryStatus
  - EMPTY: str
  - ALL: str
  - MIXED: str

- class AbstractWidgetMenuDelegate(ui.MenuDelegate)
  - def __init__(self, model: Optional[ui.AbstractItemModel] = None, width: Optional[ui.Length] = None, height: Optional[ui.Length] = None, enabled: bool = True, has_reset: bool = False, reserve_status: bool = False, use_in_menubar: bool = False, content_clipping: bool = True, visible: bool = True)
  - def destroy(self)
  - def build_item(self, item: ui.MenuItem)
  - def build_widget(self, item: ui.MenuHelper)
  - [property] def visible(self) -> bool
  - [visible.setter] def visible(self, value: bool)
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value)

- class ViewportMenuDelegate(ui.MenuDelegate)
  - def __init__(self, icon_name: str = '', icon_width: int = 16, reserve_status: bool = True, force_checked: bool = False, icon_clicked_fn: Callable[[None], None] = None, build_custom_widgets: Callable[[ui.MenuDelegate, Union[ui.MenuItem, ui.Menu]], None] = None, show_hotkey_placeholder: bool = False)
  - def build_item(self, item: Union[ui.MenuItem, ui.Menu])
  - def get_selected(self) -> bool
  - def set_selected(self, value: bool) -> bool
  - def get_checked(self) -> bool
  - def set_checked(self, value: bool) -> bool
  - [property] def selected(self) -> bool
  - [selected.setter] def selected(self, value: bool)
  - [property] def checked(self) -> bool
  - [checked.setter] def checked(self, value: bool)

- class CategoryMenuDelegate(ViewportMenuDelegate)
  - def __init__(self, status: CategoryStatus, icon_clicked_fn: Callable[[None], None] = None)
  - def build_item(self, item: ui.MenuItem)
  - [property] def status(self) -> CategoryStatus
  - [status.setter] def status(self, value: CategoryStatus)

- class CheckboxMenuDelegate(AbstractWidgetMenuDelegate)
  - def __init__(self, model: Optional[ui.SimpleBoolModel] = None, tooltip: Optional[str] = None, width: ui.Length = 300, height: ui.Length = 0, enabled: bool = True, use_in_menubar: bool = False, has_reset: bool = False)
  - def destroy(self)
  - def build_widget(self, item: ui.MenuHelper)

- class ColorMenuDelegate(AbstractWidgetMenuDelegate)
  - def __init__(self, model: Optional[ColorModel] = None, tooltip: Optional[str] = None, has_reset: bool = False)
  - def destroy(self)
  - def build_widget(self, item: ui.MenuHelper)

- class ComboBoxMenuDelegate(AbstractWidgetMenuDelegate)
  - def __init__(self, model: Optional[ComboBoxModel] = None, height: ui.Length = 0, width: ui.Length = 300, enabled: bool = True, text: bool = True, icon_name: Optional[str] = None, icon_width: ui.Length = 30, icon_height: ui.Length = 30, tooltip: Optional[str] = None, use_in_menubar: bool = False, has_reset: bool = False)
  - def destroy(self)
  - def build_widget(self, item: ui.MenuHelper)

- class IconMenuDelegate(ui.MenuDelegate)
  - def __init__(self, name: str, text: bool = False, width: ui.Length = 30, height: ui.Length = 30, has_triangle: bool = True, triangle_size: float = 6, checked: bool = False, enabled: bool = True, triggered_fn: Callable[[None], None] = None, right_clicked_fn: Callable[[None], None] = None, tooltip: Optional[str] = None, build_custom_widgets: Callable[[ui.MenuItem], None] = None)
  - def build_item(self, item: ui.MenuItem)
  - [property] def text_size(self) -> float
  - [property] def text_visible(self) -> bool
  - [text_visible.setter] def text_visible(self, value: bool)
  - [property] def checked(self) -> bool
  - [checked.setter] def checked(self, value)
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value)
  - [property] def text(self) -> str
  - [text.setter] def text(self, txt: str)
  - def destroy(self)

- class LabelMenuDelegate(ui.MenuDelegate)
  - def __init__(self, enabled: bool = True, width: Optional[ui.Length] = None, height: ui.Length = 26, alignment: ui.Alignment = ui.Alignment.LEFT)
  - def build_item(self, item: ui.MenuItem)

- class SeparatorDelegate(ui.MenuDelegate)
  - def __init__(self)
  - def destroy(self)
  - def build_item(self, item: ui.MenuItem)

- class SliderMenuDelegate(AbstractWidgetMenuDelegate)
  - def __init__(self, model: Optional[ui.AbstractValueModel] = None, min: Union[float, int, None] = None, max: Union[float, int, None] = None, tooltip: Optional[str] = None, width: int = 300, slider_class: Union[ui.FloatSlider, ui.IntSlider] = ui.FloatSlider, show_checkbox_if_min: bool = False, default_value_on: Union[float, int, None] = None, enabled: bool = True, reserve_status: bool = False, has_reset: bool = False, step: Union[float, int, None] = None)
  - def destroy(self)
  - def build_widget(self, item: ui.MenuHelper)
  - [property] def min(self) -> Union[float, int]
  - [min.setter] def min(self, value: Union[float, int])
  - [property] def max(self) -> Union[float, int]
  - [max.setter] def max(self, value: Union[float, int])
  - def calculate_step(self, min: float, max: float, slider: ui.Widget) -> float
  - def set_range(self, min: float, max: float)

- class SpinnerMenuDelegate(ui.MenuDelegate)
  - def __init__(self, model: Optional[ui.AbstractValueModel] = None, tooltip: Optional[str] = None, width: Optional[ui.Length] = None, height: ui.Length = 0, min: Union[float, int, None] = None, max: Union[float, int, None] = None, step: Union[float, int] = 1, enabled: bool = True, text: bool = True, icon_name: Optional[str] = None, icon_width: ui.Length = 30, icon_height: ui.Length = 30, use_in_menubar: bool = False, precision: Optional[int] = 1)
  - def destroy(self)
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value)
  - def build_item(self, item: ui.MenuItem)

- class CategoryMenuCollection(ui.MenuItemCollection)
  - def __init__(self, model: SimpleCategoryModel, item: CategoryCollectionItem, identifier: Optional[str] = None, trigger_fns: Optional[Dict[str, Callable]] = None)
  - def destroy(self)

- class CategoryMenuContainer
  - def __init__(self, model: SimpleCategoryModel, identifier: Optional[str] = None, trigger_fns: Optional[Dict[str, Callable]] = None)
  - def build(self, trigger_fns: Optional[Dict[str, Callable]] = None)

- class AbstractColorMenuItem(ui.MenuItem)
  - def __init__(self, colors: List[float], name: str = '', default: Optional[List[float]] = None, has_reset: bool = False)
  - def destroy(self)
  - def on_color_changed(self, colors: List[float])
  - def reset(self)

- class FloatArraySettingColorMenuItem(AbstractColorMenuItem)
  - def __init__(self, setting_path: str, default: List[float], name: str = '', start_index: int = 0, has_reset: bool = False)
  - def destroy(self)
  - def on_color_changed(self, colors: List[float])
  - def reset(self)

- class RadioMenuCollection(ui.MenuItemCollection)
  - def __init__(self, text: str, model: ComboBoxModel, identifier: Optional[str] = None, hide_on_click: bool = False, can_toggle_off: bool = False, delegate: ui.MenuDelegate = None)
  - def destroy(self)
  - def build_menu_item(self, item: ui.AbstractItem) -> ui.MenuItem

- class SelectableMenuItem(ui.MenuItem)
  - def __init__(self, name: str, model: Optional[ui.AbstractValueModel] = None, delegate: Optional[ui.MenuDelegate] = None, hide_on_click: bool = False, toggle: bool = True, triggered_fn: Callable = None, trigger_will_set_model: bool = False, **kwargs)
  - def destroy(self)

- class ViewportButtonItem(AbstractViewportMenuItem)
  - def __init__(self, text: str = '', name: str = '', onclick_fn: Callable = None, build_menu_fn: Callable[[None], List[ui.MenuItem]] = None, build_window_fn: Callable[[None], ui.Window] = None, visible_setting_path: Optional[str] = None, order_setting_path: Optional[str] = None, expand_setting_path: Optional[str] = None, alignment: ui.Alignment = ui.Alignment.RIGHT_BOTTOM, enabled: bool = True, has_triangle: bool = False, triangle_size: float = 6, style: Optional[Dict] = None)
  - def destroy(self)
  - [property] def visible(self) -> bool
  - [visible.setter] def visible(self, value: bool)
  - [property] def button(self) -> Optional[ui.Button]
  - [property] def menu_item(self) -> ui.Menu
  - [property] def window(self) -> ui.Window
  - [property] def name(self) -> str
  - [name.setter] def name(self, value: str)
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value: bool)
  - [property] def selected(self) -> bool
  - [selected.setter] def selected(self, value: bool)
  - [property] def checked(self) -> bool
  - [checked.setter] def checked(self, value: bool)
  - def build_fn(self, factory: Dict)
  - def invalidate(self)
  - def on_right_clicked_fn(self)

- class ViewportMenuContainer(ViewportMenuItem)
  - def __init__(self, *args, **kwargs)
  - def destroy(self)
  - def build_fn(self, factory_args: Dict)

- class ViewportMenuItem(AbstractViewportMenuItem)
  - def __init__(self, name: str = '', icon: str = '', hide_on_click: bool = True, appear_after: str = '', onclick_fn: Optional[Callable] = None, delegate: Optional[ui.MenuDelegate] = None, visible_setting_path: Optional[str] = None, order_setting_path: Optional[str] = None, expand_setting_path: Optional[str] = None, style: Optional[Dict] = None, order: Optional[int] = None)
  - def destroy(self)
  - [property] def visible(self) -> bool
  - [visible.setter] def visible(self, value: bool)
  - [property] def menu_item(self) -> ui.MenuItem
  - def build_fn(self, factory_args: Dict)
  - def invalidate(self)

- class ViewportMenuSeparator(ViewportMenuItem)
  - def build_fn(self, factory_args: Dict)

- class ViewportMenuSpacer(ViewportMenuItem)
  - def __init__(self)
  - def build_fn(self, factory_args: Dict)
  - def get_computed_width(self, factory_args: Dict) -> float

- class ViewportMenubar(AbstractViewportMenubarItem)
  - def __init__(self, name: str = '', direction: ui.Direction = ui.Direction.LEFT_TO_RIGHT, spacing: ui.Length = 10, style: Optional[Dict] = None, background_visible: bool = False, visible_setting_path: Optional[str] = None)
  - [property] def visible(self) -> bool
  - [visible.setter] def visible(self, value: bool)
  - [property] def background_visible(self) -> bool
  - [background_visible.setter] def background_visible(self, visible: bool)
  - [property] def style(self) -> Dict
  - [property] def spacing(self) -> ui.Length
  - [spacing.setter] def spacing(self, value: ui.Length)
  - [property] def show_separator(self) -> bool
  - [show_separator.setter] def show_separator(self, visible: bool)
  - def destroy(self)
  - def build_fn(self, menu_items: List[AbstractViewportMenuItem], factory_args: Dict, content_clipping: bool = True)
  - def invalidate(self)

- class BaseCategoryItem(ui.AbstractItem)
  - def __init__(self, text: str)

- class CategoryCollectionItem(BaseCategoryItem)
  - def __init__(self, text: str, items: Optional[List[BaseCategoryItem]] = None, shown_changed_fn: Callable = None)
  - def destroy(self)
  - def add_item(self, item: BaseCategoryItem)
  - [property] def status(self) -> CategoryStatus
  - [status.setter] def status(self, value: CategoryStatus)

- class CategoryCustomItem(BaseCategoryItem)
  - def __init__(self, text: str, build_fn: Callable[[None], None])

- class CategoryStateItem(BaseCategoryItem)
  - def __init__(self, text: str, value_model: ui.SimpleBoolModel = None, setting_path: Optional[str] = None, hotkey_text: str = '', show_hotkey_placeholder: bool = False)
  - [property] def checked(self) -> bool
  - [checked.setter] def checked(self, value: bool)

- class SimpleCategoryModel(ui.AbstractItemModel)
  - def __init__(self, text: str, items: Optional[List[BaseCategoryItem]] = None, root: CategoryCollectionItem = None)
  - def destroy(self)
  - def get_item_children(self, item: Optional[BaseCategoryItem] = None) -> List[BaseCategoryItem]
  - def add_item(self, item: BaseCategoryItem, parent: BaseCategoryItem = None)

- class ComboBoxItem(ui.AbstractItem)
  - def __init__(self, text: str, value: Any)

- class ComboBoxModel(ui.AbstractItemModel)
  - def __init__(self, texts: List[str], values: Optional[List[Any]] = None, current_value: Any = None)
  - def destroy(self)
  - def get_item_children(self, item: Optional[ComboBoxItem]) -> List[ComboBoxItem]
  - def get_item_value_model(self, item: Optional[ComboBoxItem], column_id: int)
  - def on_current_changed(self)

- class SettingComboBoxModel(ComboBoxModel)
  - def __init__(self, setting_path: str, texts: List[str], values: Optional[List[Any]] = None, current_value: Any = None)
  - def destroy(self)

- class SimpleListItem(ui.AbstractItem)
  - def __init__(self, value: Union[float, int, str, ui.AbstractValueModel], text: Optional[str] = None)

- class SimpleListModel(ui.AbstractItemModel)
  - def __init__(self, values: List[float], texts: Optional[List[str]] = None)
  - def destroy(self)
  - def get_item_children(self, item: Optional[ui.AbstractItem] = None) -> List[ui.AbstractItem]
  - def get_item_value_model_count(self) -> int
  - def get_item_value_model(self, item: SimpleListItem, column_id: int)

- class SettingModel(ui.AbstractValueModel)
  - def __init__(self, setting_path: str, draggable: bool = False, min: Union[float, int, None] = None, max: Union[float, int, None] = None)
  - [property] def path(self) -> str
  - def begin_edit(self)
  - def end_edit(self)
  - def get_value_as_string(self) -> str
  - def get_value_as_float(self) -> float
  - def get_value_as_bool(self) -> bool
  - def get_value_as_int(self) -> int
  - def set_value(self, value: Any)
  - def on_value_changed(self)
  - def destroy(self)

- class SettingModelWithDefaultValue(AbstractSettingModelWithDefault)
  - def __init__(self, setting_path: str, default_value: Any, draggable: bool = False, min: Union[float, int, None] = None, max: Union[float, int, None] = None)
  - def get_default(self)
  - def restore_default(self)

- class USDAttributeModel(USDObjectModel)
  - def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str, prop_type: Sdf.ValueTypeNames = None, draggable: bool = False)
  - def get_type_name(self, value: Any) -> Optional[Sdf.ValueTypeNames]
  - def set_value(self, value: Any)

- class USDBoolAttributeModel(USDAttributeModel)
  - def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str)
  - def set_value(self, value: bool)

- class USDFloatAttributeModel(USDAttributeModel)
  - def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str, draggable: bool = False)
  - def set_value(self, value: float)

- class USDIntAttributeModel(USDAttributeModel)
  - def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str)
  - def set_value(self, value: int)

- class USDStringAttributeModel(USDAttributeModel)
  - def __init__(self, stage: Usd.Stage, path: Sdf.Path, prop_name: str)
  - def set_value(self, value: str)

- class USDMetadataModel(USDObjectModel)
  - def __init__(self, stage: Usd.Stage, path: Sdf.Path, md_key: str)
  - def set_value(self, value: Any)

- class ResetButton
  - def __init__(self, helpers: Optional[List[ResetHelper]] = None, on_reset_fn: Callable[[None], None] = None)
  - def add_setting_model(self, helper: ResetHelper)
  - def refresh(self)

- class ResetHelper
  - def __init__(self, reset_button: Optional[ResetButton] = None)
  - def get_default(self)
  - def restore_default(self)
  - def get_value(self)
  - def set_reset_button(self, button: ResetButton)

- class ViewportMenuModel(ui.AbstractItemModel)
  - def destroy(self)
  - def get_item_children(self, parent_item: Union[AbstractViewportMenuItem, AbstractViewportMenubarItem, None] = None) -> List[AbstractViewportMenuItem]
  - def get_item_value_model_count(self, item: AbstractViewportMenuItem)
  - def get_item_value_model(self, item: AbstractViewportMenuItem, column_id: int)
  - def get_drag_mime_data(self, item)
  - def drop_accepted(self, target_item, source, drop_location = -1)
  - def drop(self, target_item, source, drop_location = -1)

## Functions

- def get_instance() -> Optional[ViewportMenuBarExtension]

## Variables

- DEFAULT_MENUBAR_NAME: str
- VIEWPORT_MENUBAR_STYLE: dict
