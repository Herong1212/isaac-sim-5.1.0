# Public API for module omni.kit.window.property:

## Classes

- class PropertyWindow
  - def __init__(self, window_kwargs = None, properties_frame_kwargs = None)
  - def destroy(self)
  - def set_visible(self, visible: bool)
  - def set_visibility_changed_listener(self, listener: callable)
  - def register_widget(self, scheme: str, name: str, property_widget: PropertyWidget, top_stack: bool = True)
  - def unregister_widget(self, scheme: str, name: str, top_stack: bool = True)
  - def register_scheme_delegate(self, scheme: str, name: str, delegate: PropertySchemeDelegate)
  - def unregister_scheme_delegate(self, scheme: str, name: str)
  - def set_scheme_delegate_layout(self, scheme: str, layout: List[str])
  - def reset_scheme_delegate_layout(self, scheme: str)
  - def notify(self, scheme: str, payload: Any)
  - def get_scheme(self)
  - def request_rebuild(self)
  - [property] def paused(self)
  - [paused.setter] def paused(self, to_pause: bool)
  - [property] def properties_frame(self)
  - def save_scroll_pos(self, reset = False)
  - def restore_scroll_pos(self)
  - def get_payload(self)

- class PropertyWidget
  - def __init__(self, title: str)
  - def clean(self)
  - def reset(self)
  - def build_impl(self)
  - def on_new_payload(self, payload) -> bool
  - def build(self, filter_cls: Optional[PropertyFilter] = None)

- class PropertySchemeDelegate
  - def get_widgets(self, payload) -> List[str]
  - def get_unwanted_widgets(self, payload) -> List[str]

- class PropertyFilter
  - def __init__(self)
  - def matches(self, name: str) -> bool
  - [property] def name_model(self)
  - [property] def name(self)
  - [name.setter] def name(self, name: str)

## Functions

- def get_window()
- def prep(frame: ui.CollapsableFrame, group_name: str)
- def set_collapsed_state(index_name: str, state: bool)
- def get_collapsed_state(index_name: str = None)
- def reset_collapsed_state()
- def build_frame_header(collapsed, text: str, group_id: str = None)
