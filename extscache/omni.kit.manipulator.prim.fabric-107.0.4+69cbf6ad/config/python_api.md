# Public API for module omni.kit.manipulator.prim.fabric:

## Classes

- class ManipulatorPrim2FabricExt(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def register_data_accessor(self)
  - def unregister_data_accessor(self)

- class FabricDataAccessor
  - def __init__(self, usd_context_name: str = '', model = None)
  - def destroy(self)
  - def get_sdf_path_type(self) -> type
  - def get_data_tag(self) -> str
  - [property] def priority(self) -> int
  - [property] def priority_write(self) -> int
  - [property] def is_inited(self)
  - [property] def usd_context(self)
  - def is_transformation_affected_by_attr_named(self, sdf_path: usdrt.Sdf.Path) -> bool
  - def is_instance_proxy(self, prim: usdrt.Usd.Prim) -> bool
  - def get_stage_up_axis(self) -> str
  - def remove_descendent_paths(self, paths: List[usdrt.Sdf.Path]) -> List[usdrt.Sdf.Path]
  - def is_prim_active(self, prim: usdrt.Usd.Prim) -> bool
  - def get_sdf_path(self, path: usdrt.Sdf.Path) -> usdrt.Sdf.Path
  - def get_string_path(self, path: Union[usdrt.Sdf.Path, str]) -> str
  - def is_valid_path(self, path: Any) -> bool
  - def path_to_int(self, path: usdrt.Sdf.Path) -> int
  - def to_pxr_path(self, path: Union[usdrt.Sdf.Path, pxr.Sdf.Path]) -> pxr.Sdf.Path
  - def is_a_xformable(self, prim: usdrt.Usd.Prim) -> bool
  - def has_prim_at_path(self, path: usdrt.Sdf.Path) -> bool
  - def get_prim_at_path(self, path: usdrt.Sdf.Path) -> usdrt.Usd.Prim
  - def prim_has_prefix(self, path: usdrt.Sdf.Path, prim_path: usdrt.Sdf.Path) -> bool
  - def get_current_time_code(self, currentTime: float) -> usdrt.Usd.TimeCode
  - def get_local_transform_SRT(self, prim: usdrt.Usd.Prim, time: float = None) -> Tuple[usdrt.Gf.Vec3d, usdrt.Gf.Vec3d, usdrt.Gf.Vec3i, usdrt.Gf.Vec3d]
  - def get_local_to_world_transform(self, prim: usdrt.Usd.Prim) -> usdrt.Gf.Matrix4d
  - def get_parent_to_world_transform(self, prim: usdrt.Usd.Prim) -> usdrt.Gf.Matrix4d
  - def clear_xform_cache(self)
  - def free_xform_cache(self)
  - def xform_set_time(self)
  - def update_xform_cache(self)
  - def free_stage(self)
  - def get_stage(self) -> usdrt.Usd.Stage
  - def set_stage(self)
  - def setup_update_callback(self) -> usdrt.Rt.ChangeTracker
  - def remove_update_callback(self, listener: pxr.Tf.Listener = None) -> usdrt.Rt.ChangeTracker
  - def setup_update_callback_ref_prim_maker(self, func: Callable[[List, List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]], List[Union[usdrt.Sdf.Path, pxr.Sdf.Path]], str], None]) -> usdrt.Rt.ChangeTracker
  - def remove_update_callback_ref_prim_maker(self, listener: pxr.Tf.Listener = None) -> usdrt.Rt.ChangeTracker
  - def update_changes(self)
  - def do_transform_all_selected_prims_to_manipulator_pivot(self, paths: List[str], paths_c: List[int], new_translations: List[float], new_rotation_eulers: List[float], new_rotation_orders: List[int], new_scales: List[float])
  - def do_transform_selected_prims(self, paths: List[str], paths_c: List[int], new_translations: List[float], new_rotation_eulers: List[float], new_rotation_orders: List[int], new_scales: List[float])
  - def on_ended_transform(self, paths: List[str], paths_c: List[int], new_translations: List[float], new_rotation_eulers: List[float], new_rotation_orders: List[int], new_scales: List[float], old_translations: List[float], old_rotation_eulers: List[float], old_rotation_orders: List[int], old_scales: List[float])
  - def get_local_transform_pivot_inv(self, prim: usdrt.Usd.Prim, time: float = None) -> usdrt.Gf.Matrix4d

- class TransformMultiPrimsFabricSRT(omni.kit.commands.Command)
  - def __init__(self, paths: list[usdrt.Sdf._Sdf.Path], new_translations: List[usdrt.Gf.Vec3d] = None, new_rotation_eulers: List[usdrt.Gf.Vec3d] = None, new_rotation_orders: List[usdrt.Gf.Vec3i] = None, new_scales: List[usdrt.Gf.Vec3d] = None, old_translations: List[usdrt.Gf.Vec3d] = None, old_rotation_eulers: List[usdrt.Gf.Vec3d] = None, old_rotation_orders: List[usdrt.Gf.Vec3i] = None, old_scales: List[usdrt.Gf.Vec3d] = None, stage = None, time_code: usdrt.Usd.TimeCode = usdrt.Usd.TimeCode.Default(), write_to_stage: bool = False)
  - def do(self)
  - def undo(self)
