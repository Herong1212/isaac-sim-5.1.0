# Public API for module omni.syntheticdata:

## Classes

- class SyntheticDataException(Exception)
  - def __init__(self, message = 'error')

- class SyntheticDataStage
  - AUTO: Unknown
  - SIMULATION: int
  - PRE_RENDER: int
  - POST_RENDER: int
  - ON_DEMAND: int

- class SyntheticData
  - class NodeConnectionTemplate
    - node_template_id: str
    - render_product_idxs: tuple
    - attributes_mapping: dict
  - class NodeTemplate
    - pipeline_stage: int
    - node_type_id: str
    - connections: list
    - attributes: dict
  - static def post_process_graph_tick_order() -> int
  - static def renderer_template_name() -> str
  - static def rendervar_host_to_disk_trigger_template_name() -> str
  - static def register_display_rendervar_templates()
  - static def register_combine_rendervar_templates()
  - static def register_combine_rendervar_template(template_name: str)
  - static def register_device_rendervar_to_host_templates(rendervars: list)
  - static def register_device_rendervar_tex_to_buff_templates(rendervars: list)
  - static def register_export_rendervar_ptr_templates(rendervars: list)
  - static def register_export_rendervar_array_templates(rendervars: list)
  - static def register_host_rendervar_to_disk_templates(rendervars: list)
  - static def convert_sensor_type_to_rendervar(legacy_type_name: str)
  - static def disable_async_rendering()
  - static def get_registered_visualization_template_names() -> list
  - static def get_registered_visualization_template_names_for_display() -> list
  - static def get_visualization_template_name_default_activation(template_name: str) -> bool
  - static def reset_visualization_template_name_default_activation()
  - static def set_visualization_template_name_default_activation(template_name: str, activation: bool) -> bool
  - static def Initialize()
  - static def Get()
  - static def Reset()
  - static def register_node_template(node_template: NodeTemplate, rendervars: list = None, template_name: str = None) -> str
  - static def is_node_template_registered(template_name: str) -> bool
  - static def unregister_node_template(template_name: str)
  - def __init__(self)
  - def reset(self, usd = True, remove_activated_render_vars = False)
  - def get_graph(self, stage: int = SyntheticDataStage.ON_DEMAND, renderProductPath: str = None) -> object
  - def activate_node_template(self, template_name: str, render_product_path_index: int = -1, render_product_paths: list = None, attributes: dict = None, stage: Usd.Stage = None, activate_render_vars: bool = True)
  - def is_node_template_activated(self, template_name: str, render_product_path: str = None, only_manually_activated: bool = False)
  - def deactivate_node_template(self, template_name: str, render_product_path_index: int = -1, render_product_paths: list = [], stage: Usd.Stage = None, deactivate_render_vars: bool = False, recurse_only_automatically_activated: bool = True)
  - def connect_node_template(self, src_template_name: str, dst_template_name: str, render_product_path: str = None, connection_map: dict = None)
  - def disconnect_node_template(self, src_template_name: str, dst_template_name: str, render_product_path: str = None, connection_map: dict = None)
  - def request_node_execution(self, template_name: str, render_product_path: str = None)
  - def set_node_attributes(self, template_name: str, attributes: dict, render_product_path: str = None)
  - def get_node_attributes(self, template_name: str, attribute_names: list, render_product_path = None, gpu = False) -> dict
  - def set_instance_mapping_semantic_filter(self, predicate = '*:*')
  - def get_instance_mapping_semantic_filter(self)
  - def set_default_semantic_filter(self, predicate = '*:*', hierarchical_labels = False, matching_labels = True)
  - def get_default_semantic_filter(self)
  - def get_semantic_filter_label_template_name(self, filter_name: str, post_render_stage: bool = True)
  - def set_semantic_filter(self, filter_name: str, predicate: str, hierarchical_labels = False, matching_labels = True)
  - def get_semantic_filter(self, filter_name: str)
  - def enable_rendervar(self, render_product_path: str, render_var: str, usd_stage: Usd.Stage = None)
  - def disable_rendervar(self, render_product_path: str, render_var: str, usd_stage: Usd.Stage = None)
  - def is_rendervar_used(self, render_product_path: str, render_var: str)
  - def is_rendervar_enabled(self, render_product_path: str, render_var: str, only_sdg_activated: bool = False, usd_stage: Usd.Stage = None)

- class Extension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def get_name(self)
  - static def get_instance()

## Variables

- EXTENSION_NAME: str

## Other

- Tf: unknown module
- Trace: unknown
- Usd: unknown module
- carb.settings: public module
- carb.eventdispatcher: public module
- omni.kit: unknown module
- omni.ext: public module
- Sdf: unknown module
- carb: public module
- omni.graph.core: public module
- omni.usd: public module
- dataclass: unknown
- field: unknown
- lru_cache: unknown
- numpy: unknown module
- UNKNOWN_MODULE_DEFS: unknown


# Public API for module omni.syntheticdata.scripts.helpers:

## Functions

- def get_bbox_3d_corners(extents)
- def reduce_bboxes_2d(bboxes, instance_mappings)
- def reduce_bboxes_3d(bboxes, instance_mappings)
- def merge_sensors(bounding_box_2d_tight = None, bounding_box_2d_loose = None, bounding_box_3d = None, occlusion_quadrants = None)
- def get_projection_matrix(fov, aspect_ratio, z_near, z_far)
- def get_view_proj_mat(view_params)
- def project_pinhole(points, view_params)
- def get_instance_mappings()
- def reduce_occlusion(occlusion_data, instance_mappings)
- def project_fish_eye_map_to_sphere(direction)
- def fish_eye_polynomial(ndc, view_params)
- def project_fish_eye_polynomial(points, view_params)
- def get_view_params(viewport)
- def image_to_world(image_coordinates, view_params)
- def world_to_image(points, viewport, view_params = None)
- def ftheta_distortion(ftheta, x)
- def ftheta_distortion_prime(ftheta, x)

## Variables

- EPS: float

## Other

- math: builtin module
- lru_cache: unknown
- numpy.lib.recfunctions: unknown module
- carb: public module
- numpy: unknown module
- omni.usd: public module
- UsdGeom: unknown module
- UsdShade: unknown
- Semantics: public module


# Public API for module omni.syntheticdata.scripts.visualize:

## Functions

- def colorize_distance(image_data)
- def colorize_segmentation(segmentation_image)
- def colorize_bboxes(bboxes_2d_data, bboxes_2d_rgb)
- def colorize_bboxes_3d(bboxes_3d_corners, rgb)
- def random_colours(N)
- def get_bbox2d_tight(viewport)
- def get_bbox2d_loose(viewport)
- def get_normals(viewport)
- def get_motion_vector(viewport)
- def get_cross_correspondence(viewport)
- def get_instance_segmentation(viewport, mode = None)
- def get_semantic_segmentation(viewport, mode = '')
- def get_bbox3d(viewport, mode = 'parsed')
- def get_depth(viewport, mode = 'linear')
- def get_distance(viewport, mode = 'image_plane')

## Other

- random: builtin module
- colorsys: builtin module
- numpy: unknown module
- carb: public module
- Image: unknown
- ImageDraw: unknown




# Public API for module omni.syntheticdata.scripts.sensors:

## Classes

- class SyntheticDataException(Exception)
  - def __init__(self, message = 'error')

- class SyntheticDataStage
  - AUTO: Unknown
  - SIMULATION: int
  - PRE_RENDER: int
  - POST_RENDER: int
  - ON_DEMAND: int

- class SyntheticData
  - class NodeConnectionTemplate
    - node_template_id: str
    - render_product_idxs: tuple
    - attributes_mapping: dict
  - class NodeTemplate
    - pipeline_stage: int
    - node_type_id: str
    - connections: list
    - attributes: dict
  - static def post_process_graph_tick_order() -> int
  - static def renderer_template_name() -> str
  - static def rendervar_host_to_disk_trigger_template_name() -> str
  - static def register_display_rendervar_templates()
  - static def register_combine_rendervar_templates()
  - static def register_combine_rendervar_template(template_name: str)
  - static def register_device_rendervar_to_host_templates(rendervars: list)
  - static def register_device_rendervar_tex_to_buff_templates(rendervars: list)
  - static def register_export_rendervar_ptr_templates(rendervars: list)
  - static def register_export_rendervar_array_templates(rendervars: list)
  - static def register_host_rendervar_to_disk_templates(rendervars: list)
  - static def convert_sensor_type_to_rendervar(legacy_type_name: str)
  - static def disable_async_rendering()
  - static def get_registered_visualization_template_names() -> list
  - static def get_registered_visualization_template_names_for_display() -> list
  - static def get_visualization_template_name_default_activation(template_name: str) -> bool
  - static def reset_visualization_template_name_default_activation()
  - static def set_visualization_template_name_default_activation(template_name: str, activation: bool) -> bool
  - static def Initialize()
  - static def Get()
  - static def Reset()
  - static def register_node_template(node_template: NodeTemplate, rendervars: list = None, template_name: str = None) -> str
  - static def is_node_template_registered(template_name: str) -> bool
  - static def unregister_node_template(template_name: str)
  - def __init__(self)
  - def reset(self, usd = True, remove_activated_render_vars = False)
  - def get_graph(self, stage: int = SyntheticDataStage.ON_DEMAND, renderProductPath: str = None) -> object
  - def activate_node_template(self, template_name: str, render_product_path_index: int = -1, render_product_paths: list = None, attributes: dict = None, stage: Usd.Stage = None, activate_render_vars: bool = True)
  - def is_node_template_activated(self, template_name: str, render_product_path: str = None, only_manually_activated: bool = False)
  - def deactivate_node_template(self, template_name: str, render_product_path_index: int = -1, render_product_paths: list = [], stage: Usd.Stage = None, deactivate_render_vars: bool = False, recurse_only_automatically_activated: bool = True)
  - def connect_node_template(self, src_template_name: str, dst_template_name: str, render_product_path: str = None, connection_map: dict = None)
  - def disconnect_node_template(self, src_template_name: str, dst_template_name: str, render_product_path: str = None, connection_map: dict = None)
  - def request_node_execution(self, template_name: str, render_product_path: str = None)
  - def set_node_attributes(self, template_name: str, attributes: dict, render_product_path: str = None)
  - def get_node_attributes(self, template_name: str, attribute_names: list, render_product_path = None, gpu = False) -> dict
  - def set_instance_mapping_semantic_filter(self, predicate = '*:*')
  - def get_instance_mapping_semantic_filter(self)
  - def set_default_semantic_filter(self, predicate = '*:*', hierarchical_labels = False, matching_labels = True)
  - def get_default_semantic_filter(self)
  - def get_semantic_filter_label_template_name(self, filter_name: str, post_render_stage: bool = True)
  - def set_semantic_filter(self, filter_name: str, predicate: str, hierarchical_labels = False, matching_labels = True)
  - def get_semantic_filter(self, filter_name: str)
  - def enable_rendervar(self, render_product_path: str, render_var: str, usd_stage: Usd.Stage = None)
  - def disable_rendervar(self, render_product_path: str, render_var: str, usd_stage: Usd.Stage = None)
  - def is_rendervar_used(self, render_product_path: str, render_var: str)
  - def is_rendervar_enabled(self, render_product_path: str, render_var: str, only_sdg_activated: bool = False, usd_stage: Usd.Stage = None)

## Functions

- def get_synthetic_data()
- async def next_render_simulation_async(render_product_path, num_simulation_frames_offset = 0)
- async def next_sensor_data_async(viewport = None, waitSimFrame: bool = False, inViewportId: int = None)
- def enable_sensors(viewport, sensor_types)
- def disable_sensors(viewport, sensor_types)
- def create_or_retrieve_sensor(viewport, sensor_type)
- async def create_or_retrieve_sensor_async(viewport, sensor_type)
- async def initialize_async(viewport, sensor_types)
- def get_sensor_array(viewport, sensor_type, elemType, elemCount, is2DArray)
- def get_rgb(viewport)
- def get_depth(viewport)
- def get_depth_linear(viewport)
- def get_distance_to_image_plane(viewport)
- def get_distance_to_camera(viewport)
- def get_camera_3d_position(viewport)
- def get_bounding_box_3d(viewport, parsed = False, return_corners = False, camera_frame = False, instance_mappings = None)
- def get_bounding_box_2d_tight(viewport, instance_mappings = None)
- def get_bounding_box_2d_loose(viewport, instance_mappings = None)
- def get_semantic_segmentation(viewport, parsed = False, return_mapping = False, instance_mappings = None)
- def get_instance_segmentation(viewport, parsed = False, return_mapping = False, instance_mappings = None)
- def get_normals(viewport)
- def get_motion_vector(viewport)
- def get_cross_correspondence(viewport)
- def get_occlusion(viewport, parsed = False, instance_mappings = None)
- def get_semantic_data(instance_mappings = None)
- def get_occlusion_quadrant(viewport, return_bounding_boxes = False)

## Other

- carb: public module
- carb.eventdispatcher: public module
- omni.usd: public module
- omni.kit: unknown module
- UsdGeom: unknown module
- numpy: unknown module
- asyncio: builtin module
- Sdf: unknown module
- Usd: unknown module
- omni.graph.core: public module
- dataclass: unknown
- field: unknown
- lru_cache: unknown




