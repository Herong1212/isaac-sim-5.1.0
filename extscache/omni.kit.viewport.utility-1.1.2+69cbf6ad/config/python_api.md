# Public API for module omni.kit.viewport.utility:

## Functions

- def frame_viewport_prims(viewport_api = None, prims: List[str] = None)
- def frame_viewport_selection(viewport_api = None, **kwargs)
- def get_viewport_from_window_name(window_name: str = None)
- def get_active_viewport(usd_context_name: str = '')
- def get_active_viewport_window(window_name: str = None, usd_context_name: str = '', **kwargs)
- def get_active_viewport_and_window(usd_context_name: str = '', window_name: str = None, **kwargs)
- def get_viewport_window_camera_path(window_name: str = None) -> Sdf.Path
- def get_viewport_window_camera_string(window_name: str = None) -> str
- def get_active_viewport_camera_path(usd_context_name: str = '') -> Sdf.Path
- def get_active_viewport_camera_string(usd_context_name: str = '') -> str
- def get_num_viewports(usd_context_name: str = None)
- def capture_viewport_to_file(viewport_api, file_path: str = None, is_hdr: bool = False, render_product_path: str = None, format_desc: dict = None, frame_to_capture = None)
- def capture_viewport_to_buffer(viewport_api, on_capture_fn: Callable, is_hdr: bool = False)
- def post_viewport_message(viewport_api_or_window, message: str, message_id: str = None)
- def toggle_global_visibility()
- def create_drop_helper(*args, **kwargs)
- def disable_selection(viewport_or_window, disable_click: bool = True)
- def get_ground_plane_info(viewport, ortho_special: bool = True) -> Tuple[Gf.Vec3d, List[str]]
