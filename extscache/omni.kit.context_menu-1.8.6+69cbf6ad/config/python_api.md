# Public API for module omni.kit.context_menu:

## Classes

- class ContextMenuExtension(omni.ext.IExt)
  - static def create_prim(objects: dict, prim_type: str, attributes: dict, create_group_xform: bool = False)
  - static def create_mesh_prim(objects: dict, prim_type: str)
  - def show_selected_prims_names(self, objects: dict, delegate = None)
  - def show_create_menu(self, objects: dict)
  - def build_create_menu(self, objects: dict, prim_list: list, custom_menu: dict = [], delegate = None)
  - def build_add_menu(self, objects: dict, prim_list: list, custom_menu: list = None, delegate = None)
  - def select_prims_using_material(self, objects: dict)
  - def find_in_browser(self, objects: dict)
  - def duplicate_prim(self, objects: dict)
  - def delete_prim(self, objects: dict, destructive = False)
  - def copy_prim_url(self, objects: dict)
  - def copy_prim_path(self, objects: dict)
  - def group_selected_prims(self, objects: dict)
  - def ungroup_selected_prims(self, objects: dict)
  - def refresh_payload_or_reference(self, objects: dict)
  - def convert_payload_to_reference(self, objects: dict)
  - def convert_reference_to_payload(self, objects: dict)
  - def refresh_reference_payload_name(self, objects: dict)
  - def get_prim_group(self, prim)
  - def is_one_prim_selected(self, objects: dict)
  - def is_material(self, objects: dict)
  - def has_payload_or_reference(self, objects: dict)
  - def can_convert_references_or_payloads(self, objects)
  - def has_payload(self, objects: dict)
  - def has_reference(self, objects: dict)
  - def can_be_copied(self, objects: dict)
  - def can_use_find_in_browser(self, objects: dict)
  - def can_show_find_in_browser(self, objects: dict)
  - def can_delete(self, objects: dict)
  - async def can_assign_material_async(self, objects: dict, menu_item: ui.Widget)
  - def is_prim_selected(self, objects: dict)
  - def is_prim_in_group(self, objects: dict)
  - def is_material_bindable(self, objects: dict)
  - def prim_is_type(self, objects: dict, type: Tf.Type) -> bool
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - [property] def name(self) -> str
  - [property] def menu_item_count(self) -> int
  - [menu_item_count.setter] def menu_item_count(self, value)
  - def close_menu(self)
  - def separator(self, name: str = '') -> bool
  - def menu(self, *args, **kwargs)
  - def menu_item(self, *args, **kwargs)
  - def show_context_menu(self, menu_name: str, objects: dict, menu_list: List[dict], min_menu_entries: int = 1, **kwargs)
  - [deprecated] def bind_material_to_prims_dialog(self, stage: Usd.Stage, prims: list)
  - def get_context_menu(self)

- class ViewportMenu
  - class ViewportMenuDelegate(DefaultMenuDelegate)
    - def get_style(self)
  - menu_delegate: Unknown
  - static def is_on_clipboard(objects, name)
  - static def is_prim_on_clipboard(objects)
  - static async def can_show_clear_clipboard(objects, menu_item)
  - static def is_material_bindable(objects)
  - static def bind_material_to_prim_dialog(objects)
  - static def set_prim_to_pos(path, new_pos)
  - static def copy_prim_to_clipboard(objects)
  - static def clear_clipboard(objects)
  - static def paste_prim_from_clipboard(objects)
  - static def show_create_menu(objects)
  - static def show_menu(usd_context_name: str, prim_path: str = None, world_pos: Sequence[float] = None, stage = None)

## Functions

- def get_instance()
- def get_instance()
- def close_menu()
- def reorder_menu_dict(menu_dict: List[dict])
- def post_notification(message: str, info: bool = False, duration: int = 3)
- def get_hovered_prim(objects)
- def add_menu(menu_dict, index: str = 'MENU', extension_id: str = '')
- def get_menu_dict(index: str = 'MENU', extension_id: str = '') -> List[dict]
- def get_menu_event_stream()

## Variables

- SETTING_HIDE_CREATE_MENU: str
