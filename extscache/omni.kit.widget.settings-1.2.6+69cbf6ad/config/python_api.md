# Public API for module omni.kit.widget.settings:

## Classes

- class SettingType(Enum)
  - FLOAT: int
  - INT: int
  - COLOR3: int
  - BOOL: int
  - STRING: int
  - DOUBLE3: int
  - INT2: int
  - DOUBLE2: int
  - ASSET: int

- class SettingsSearchableCombo
  - def __init__(self, setting_path: str, key_value_pairs: dict, default_key: str)
  - def destroy(self)
  - def get_key_from_value(self, value)
  - def get_current_key(self)

- class SettingWidgetType(Enum)
  - FLOAT: int
  - INT: int
  - COLOR3: int
  - BOOL: int
  - STRING: int
  - DOUBLE3: int
  - INT2: int
  - DOUBLE2: int
  - ASSET: int
  - COMBOBOX: int
  - RADIOBUTTON: int
  - VECTOR3: int

- class SettingsWidgetBuilder
  - class def get_checkbox_alignment(cls)
  - class def get_label_alignment(cls)
  - class def createColorWidget(cls, model, comp_count = 3, additional_widget_kwargs: Optional[dict] = None) -> ui.HStack
  - class def createVecWidget(cls, model, range_min, range_max, comp_count = 3, additional_widget_kwargs: Optional[dict] = None)
  - class def createDoubleArrayWidget(cls, model, range_min, range_max, comp_count = 3, additional_widget_kwargs: Optional[dict] = None)
  - class def createIntArrayWidget(cls, model, range_min, range_max, comp_count = 3, additional_widget_kwargs: Optional[dict] = None)
  - class def createBoolWidget(cls, model, additional_widget_kwargs: Optional[dict] = None)
  - class def createFloatWidget(cls, model, range_min, range_max, additional_widget_kwargs: Optional[dict] = None)
  - class def createIntWidget(cls, model, range_min, range_max, additional_widget_kwargs: Optional[dict] = None)
  - class def createAssetWidget(cls, model, additional_widget_kwargs: Optional[dict] = None)
  - class def createRadiobuttonWidget(cls, model: RadioButtonSettingModel, setting_path: str = '', additional_widget_kwargs: Optional[dict] = None) -> omni.ui.RadioCollection
  - class def createComboboxWidget(cls, setting_path: str, items: Union[list, dict, None] = None, setting_is_index: Optional[bool] = None, allow_non_items: Optional[bool] = False, additional_widget_kwargs: Optional[dict] = None) -> Tuple[SettingsComboItemModel, ui.ComboBox]

## Functions

- def get_style()
- def get_ui_style_name()
- def create_setting_widget(setting_path: str, setting_type: SettingType, range_from = 0, range_to = 0, speed = 1, **kwargs) -> Tuple[ui.Widget, ui.AbstractValueModel]
- def create_setting_widget_combo(setting_path: str, items: Union[list, dict], setting_is_index: Optional[bool] = None, allow_non_items: bool = False, **kwargs) -> Tuple[SettingsComboItemModel, ui.ComboBox]
