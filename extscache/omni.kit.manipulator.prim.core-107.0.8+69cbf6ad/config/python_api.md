# Public API for module omni.kit.manipulator.prim.core:

## Classes

- class PrimDataAccessorRegistry
  - def __init__(self)
  - def get_event_stream(self)
  - def register_data_accessor(self, func, data_tag)
  - def unregister_data_accessor(self, data_tag)
  - def get_data_accessors_func(self)
  - def destroy(self)

- class TransformManipulatorRegistry
  - def __init__(self)
  - def destroy(self)

- class PrimTransformManipulator(ManipulatorBase)
  - def __init__(self, usd_context_name: str = '', viewport_api = None, name = 'omni.kit.manipulator.prim.core', model: PrimTransformModel = None, size: float = 1.0)
  - def destroy(self)
  - [property] def model(self) -> PrimTransformModel
  - [property] def snap_manager(self) -> SnapProviderManager
  - [property] def enabled(self)
  - [enabled.setter] def enabled(self, value: bool)
  - def on_selection_changed(self, stage: Usd.Stage, selection: Union[List[Sdf.Path], None], *args, **kwargs) -> bool

- class PrimTransformModel(ViewportTransformModel)
  - def __init__(self, usd_context_name: str = '', viewport_api = None)
  - def update_selection(self)
  - def on_selection_changed(self, selection: List[pxr.Sdf.Path])
  - def get_da(self)
  - def destroy(self)
  - def set_pivot_prim_path(self, path0: self._data_accessor_selector.Sdf.Path) -> bool
  - def get_pivot_prim_path(self) -> self._data_accessor_selector.Sdf.Path
  - def on_began(self, payload)
  - def on_changed(self, payload)
  - def on_ended(self, payload)
  - def on_canceled(self, payload)
  - def widget_enabled(self)
  - def widget_disabled(self)
  - def set_floats(self, item: sc.AbstractManipulatorItem, value: Sequence[float])
  - def set_ints(self, item: sc.AbstractManipulatorItem, value: Sequence[int])
  - def get_as_floats(self, item: sc.AbstractManipulatorItem)
  - def get_as_ints(self, item: sc.AbstractManipulatorItem)
  - def get_operation(self) -> Operation
  - def get_snap(self, item: AbstractTransformManipulatorModel.OperationItem)
  - def on_objects_changed(self, resynced_paths, changed_info_only_paths, data_source = None)
  - def decompose_to_eulers(self, q: usdrt.Gf.Quatd, ro: usdrt.Gf.Vec3i) -> usdrt.Gf.Vec3d
  - [property] def custom_manipulator_enabled(self)
  - [property] def snap_settings_listener(self)
  - [property] def op_settings_listener(self)
  - [property] def usd_context(self) -> omni.usd.UsdContext
  - [property] def xformable_prim_paths(self) -> List[self._data_accessor_selector.Sdf.Path]

- class DataAccessorConstants
  - DATA_ACCESSOR_PRIORITY_FABRIC: str
  - DATA_ACCESSOR_PRIORITY_WRITE_FABRIC: str
  - DATA_ACCESSOR_PRIORITY_USD: str
  - DATA_ACCESSOR_PRIORITY_WRITE_USD: str

- class Constants
  - MANIPULATOR_PLACEMENT_SETTING: str
  - MANIPULATOR_PLACEMENT_LAST_PRIM_PIVOT: str
  - MANIPULATOR_PLACEMENT_SELECTION_CENTER: str
  - MANIPULATOR_PLACEMENT_BBOX_BASE: str
  - MANIPULATOR_PLACEMENT_BBOX_CENTER: str
  - MANIPULATOR_PLACEMENT_PICK_REF_PRIM: str

## Functions

- def get_prim_data_accessor_registry() -> PrimDataAccessorRegistry
- def get_toolbar_registry() -> ToolbarRegistry
