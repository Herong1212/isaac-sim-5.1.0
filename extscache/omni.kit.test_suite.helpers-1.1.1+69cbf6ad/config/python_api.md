# Public API for module omni.kit.test_suite.helpers:

## Classes

- class StageEventHandler
  - def __init__(self, ext_name)
  - async def reset_stage_event(self, stage_event)
  - async def wait_for_stage_event(self, timeout = 30.0)

- class TestSuiteHelpers(omni.ext.IExt)
  - stage_event_debug: bool
  - stage_loading_debug: bool
  - stage_debug: Dict
  - stage_state: Dict
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

## Functions

- def get_test_data_path(module: str, subpath: str = '') -> str
- async def wait()
- async def wait_stage_loading(wait_frames: int = 2, usd_context = None, timeout = 1000, timeout_error = True)
- async def open_stage(path: str, usd_context = omni.usd.get_context())
- async def select_prims(paths, usd_context = omni.usd.get_context())
- def get_prims(stage, exclude_list = [])
- async def wait_for_window(window_name: str)
- async def handle_assign_material_dialog(index, strength_index = 0)
- async def handle_create_material_dialog(mdl_path: str, mtl_name: str)
- async def delete_prim_path_children(prim_path: str)
- async def build_sdf_asset_frame_dictonary()
- def push_window_height(cls, window_name, new_height = None)
- def pop_window_height(cls, window_name)
- async def handle_multiple_descendents_dialog(stage, prim_path: str, target_prim: str)
- async def arrange_windows(topleft_window = 'Stage', topleft_height = 421.0, topleft_width = 436.0, hide_viewport = False, topleft_position_x = 0)
- async def wait_for_viewport_ready(usd_context = omni.usd.get_context())
- async def get_random_material_list(max_items = 5, use_hidden = False)
