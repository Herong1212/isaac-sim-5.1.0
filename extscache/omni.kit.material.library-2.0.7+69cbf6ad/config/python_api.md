# Public API for module omni.kit.material.library:

## Classes

- class CreateAndBindMdlMaterialFromLibrary(omni.kit.commands.Command)
  - def __init__(self, mdl_name: str, mtl_name: str = '', mtl_created_list: list = None, bind_selected_prims: list = False, select_new_prim: bool = True, prim_name: str = '', on_created_fn: callable = None)
  - def do(self)
  - def undo(self)

- class CreateAndBindPreviewSurfaceFromLibrary(omni.kit.commands.Command)
  - def __init__(self, mtl_created_list: list = None, bind_selected_prims: list = False)
  - def do(self)
  - def undo(self)

- class CreateAndBindPreviewSurfaceTextureFromLibrary(omni.kit.commands.Command)
  - def __init__(self, mtl_created_list: list = None, bind_selected_prims: list = False)
  - def do(self)
  - def undo(self)

- class UpdateState(Enum)
  - UPDATE: int
  - UPDATE_COMPLETE: int
  - COMPLETE_LIST: int

- class MaterialUtils
  - def __init__(self, usd_context_name: [str | None] = None)
  - static def is_valid_material(prim, filter_funcs, ext_filter_func = None)
  - def stop(self)
  - def add_cache_changed_fn(self, cache_changed_fn: callable)
  - def remove_cache_changed_fn(self, cache_changed_fn: callable)
  - def destroy(self)
  - def flush_material_cache(self)
  - def get_materials_from_stage(self, ext_filter_func = None)
  - def get_materials_from_stage_async(self, update_func: callable, wait_frames: int, ext_filter_func: callable)
  - def add_materials_from_stage_filter_func(self, filter_fn: callable)
  - def remove_materials_from_stage_filter_func(self, filter_fn: callable)

- class SearchWidget
  - class WidgetFlags(IntFlag)
    - SHOW_OPEN_BUTTON: int
    - SHOW_GOTO_BUTTON: int
    - SHOW_ALL: Unknown
  - def __init__(self, theme: str, icon_path: str, modified_fn: callable = None)
  - def clean(self)
  - def destroy(self)
  - def update(self, filter_string: str)
  - def focus(self)
  - def build_ui(self, width: float, search_size: float)
  - def set_placeholder_text(self, msg: str)
  - def set_text(self, new_text: str)
  - def get_text(self)
  - def build_ui_popup(self, search_size: float, popup_text: str, index: int, update_fn: callable, widget_flags = WidgetFlags.SHOW_ALL, missing = False)

## Functions

- def multi_descendents_dialog(prim_paths: list, on_click_fn: callable)
- def drop_material(prim_path: str, model_path: str, apply_material_fn: callable)
- def bind_material_to_selected_prims(material_prim_path: Sdf.Path, paths: list)
- def get_material_prim_path(material_prim_name: str)
- def create_mdl_material(stage: Usd.Stage, mtl_url: str, mtl_name: str, on_create_fn: callable, mtl_real_name: str = '')
- def create_mtlx_material(stage: Usd.Stage, mtlx_url: str, on_create_fn: callable, base_name: str = '')
- def get_material_filename_from_prim(prim: Usd.Prim) -> str
- def get_mdl_lib_paths()
- def get_mdl_usd_source_asset_list()
- def get_material_hidden_list()
- async def get_mdl_list_async(use_hidden = False, wait_for_ready = True, get_private = False, expand_paths: bool = True)
- def get_mdl_list(use_hidden: bool = False, get_private: bool = False, expand_paths: bool = True)
- def add_material_list_refresh_callback(on_refresh_fn: callable)
- def remove_material_list_refresh_callback(on_refresh_fn: callable)
- async def delayed_material_list_refresh()
- def add_material_list_item(name: str, on_call_fn: callable, refresh: bool = True)
- def remove_material_list_item(name: str, refresh: bool = True)
- def material_list_refresh()
- def get_material_list()
- def custom_material_dialog(mdl_path: str, on_complete_fn: callable = None, bind_prim_paths: list = [])
- async def get_subidentifier_from_material(prim: Usd.Prim, on_complete_fn: callable, use_functions: bool = False, show_alert: bool = False)
- async def get_subidentifier_from_mdl(mdl_file: str, on_complete_fn: callable = None, use_functions: bool = False, show_alert: bool = False)
- def remove_mdl_from_cache(shader_prim_path: str)
- def get_material_enums()
- def bind_material_to_prims_dialog(stage: Usd.Stage, prims: list)
- def add_usd_source_asset_path_to_mtl_lib(source_asset_path: str, source_asset_subid: str, group_name: str, submenu_name: str = None, display_name: str = None)
- def remove_usd_source_asset_path_from_mtl_lib(source_asset_path: str, source_asset_subid: str)
- def add_to_mtl_lib(folder_paths: list[str], is_private: bool = False) -> list[str]
- def remove_from_mtl_lib(folder_paths: list[str]) -> list[str]
- def initalize_material_utils()
- def destroy_material_utils()
- def add_cache_changed_fn(cache_changed_fn: callable)
- def remove_cache_changed_fn(cache_changed_fn: callable)
- def get_materials_from_stage(none_string: str)
- def get_materials_from_stage_async(update_func: callable, wait_frames: int = 1, ext_filter_func: callable = None)
- def add_materials_from_stage_filter_func(filter_fn: callable)
- def remove_materials_from_stage_filter_func(filter_fn: callable)
- def get_prim_children_paths(prim_path: Sdf.Path)
- def get_cache_filename()
