# Public API for module omni.kit.widget.live_session_management_ui:

## Classes

- class JoinWithSessionLinkWindow
  - def __init__(self, on_ok_button_cb: Callable[[str], None])
  - def destroy(self)
  - [property] def visible(self)
  - [visible.setter] def visible(self, value)
  - async def focus_field(self)
  - [property] def current_session_link(self)
  - [current_session_link.setter] def current_session_link(self, value)

- class LiveSessionInterface
  - [property] def name(self) -> str
  - [property] def url(self) -> str
  - [property] def owner(self) -> str
  - [property] def channel_url(self) -> str
  - [property] def base_layer_identifier(self) -> str
  - def get_last_modified_time(self) -> int
  - [property] def shared_link(self) -> str

- class LiveSessionComboBoxModel(ui.AbstractItemModel)
  - def __init__(self, layer_identifier: str, get_current_live_session_cb: Callable[[str], LiveSessionInterface], get_all_live_sessions_cb: Callable[[str], List[LiveSessionInterface]], update_users: bool = True)
  - [property] def base_layer_identifier(self)
  - [property] def all_users(self)
  - [property] def is_default_session_selected(self)
  - def set_user_update_callback(self, callback: Callable[[], None])
  - def set_model_reset_callback(self, callback: Callable[[], None])
  - def stop_channel(self)
  - def add_value_changed(self, fn)
  - def destroy(self)
  - def clear(self)
  - def empty(self)
  - def get_item_children(self, item)
  - [property] def current_session(self)
  - def refresh_sessions(self, force = False)
  - def get_item_value_model(self, item, column_id)
  - def select_default_session(self)
  - def create_new_session_name(self) -> str

- class LiveSessionEndWindow
  - def __init__(self, current_session, on_ok_button_cb: Callable[[], None], warn_root_prims = False)
  - def destroy(self)
  - [property] def visible(self)
  - [visible.setter] def visible(self, value)
  - def show_file_picker(self, file_handler, default_location = None, default_filename = None, new_os_window = False)
  - def set_error_msg(self, msg)

- class LiveSessionStartWindow
  - def __init__(self, session_model: LiveSessionComboBoxModel, prim_path: str, join_session_cb: Callable[[LiveSessionInterface, str, str], bool], create_live_session_cb: Callable[[str, str], LiveSessionInterface])
  - def destroy(self)
  - [property] def visible(self)
  - [visible.setter] def visible(self, value)
  - def select_default_session(self)
  - def set_focus(self, join_session)

- class ShareSessionLinkWindow
  - def __init__(self, session_model)
  - def destroy(self)
  - [property] def visible(self)
  - [visible.setter] def visible(self, value)
