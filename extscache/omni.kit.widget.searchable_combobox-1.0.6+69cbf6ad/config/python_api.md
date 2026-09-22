# Public API for module omni.kit.widget.searchable_combobox:

## Classes

- class SearchModel(ui.AbstractValueModel)
  - def __init__(self, modified_fn)
  - def is_in_string(self, string: str)
  - def set_value(self, value)
  - def get_value_as_string(self)

- class SearchWidget
  - def __init__(self, theme: str, icon_path: str, modified_fn: callable = None)
  - def clean(self)
  - def destroy(self)
  - def update(self, string)
  - def focus(self)
  - def build_ui(self, width, search_size)
  - def set_placeholder_text(self, msg: str)
  - def set_text(self, new_text: str)
  - def get_text(self)
  - def build_ui_popup(self, search_size: float, default_value: str, popup_text: str, index: int, update_fn: callable)

- class ComboBoxListItem(ui.AbstractItem)
  - def __init__(self, text)
  - def prefilter(self, filter_name_text: str)

- class ComboBoxListModel(ui.AbstractItemModel)
  - def __init__(self, item_list)
  - def clean(self)
  - def get_item_children(self, item)
  - def get_item_value_model_count(self, item)
  - def get_drag_mime_data(self, item)
  - def get_item_value_model(self, item, column_id)
  - def filter_by_text(self, filter_name_text: str)
  - def get_index_for_item(self, item_text: str)

- class ComboBoxListDelegate(ui.AbstractItemDelegate)
  - def __init__(self, flat = False)
  - def clean(self)
  - def build_branch(self, model, item, column_id, level, expanded)
  - def build_widget(self, model, item, column_id, level, expanded)

- class ComboListBoxWidget
  - def __init__(self, search_widget: SearchWidget, item_list: list, theme: str, window_id: str = 'SearchableComboBoxWindow', delegate: ui.AbstractItemDelegate = ComboBoxListDelegate())
  - def set_parent(self, parent)
  - def clean(self)
  - def destroy_ui(self, visible)
  - def build_ui(self)
  - def destroy(self)

## Functions

- def build_searchable_combo_widget(combo_list: List[str], combo_index: int, combo_click_fn: callable, widget_height: int, default_value: str, window_id: str = 'SearchableComboBoxWindow', delegate: ui.AbstractItemDelegate = ComboBoxListDelegate()) -> SearchWidget
