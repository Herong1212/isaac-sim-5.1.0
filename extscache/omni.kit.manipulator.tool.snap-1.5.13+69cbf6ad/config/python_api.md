# Public API for module omni.kit.manipulator.tool.snap:

## Classes

- class SnapToolExt(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class SnapProvider(ABC)
  - def __init__(self, viewport_api)
  - def destroy(self)
  - def on_began(self, excluded_paths: List[Union[str, Sdf.Path]], **kwargs)
  - def on_ended(self, **kwargs)
  - def on_snap(self, xform: Gf.Matrix4d, ndc_location: Sequence[float], scene_view: sc.SceneView, want_orient: bool, want_keep_spacing: bool, on_snapped: Callable, conform_up_axis: str, enabled_providers: List[SnapProvider], *args, **kwargs) -> bool
  - static def get_name() -> str
  - class def get_display_name(cls) -> str
  - static def can_orient() -> bool
  - class def can_show_menu(cls, object: dict) -> bool
  - static def can_enable_menu(object: dict) -> bool
  - static def require_viewport_api() -> bool
  - static def get_order() -> float

- class SnapProviderRegistry
  - class def get_instance(cls) -> SnapProviderRegistry
  - def __init__(self)
  - def destroy(self)
  - [property] def providers(self) -> Dict[str, Type[SnapProvider]]
  - def get_provider_class_by_name(self, name: str) -> Type[SnapProvider]
  - def register_provider(self, provider_class: Type[SnapProvider])
  - def unregister_provider(self, provider_class: Type[SnapProvider])
  - def subscribe_to_registry_change(self, callback: Callable[[], None]) -> int
  - def unsubscribe_to_registry_change(self, id: int)

- class RegistrationHelper
  - def __init__(self, module_name: str, base_class: Type)
  - def destroy(self)

- class SnapToolButton(SimpleToolButton)
  - def __init__(self, *args, **kwargs)
  - def destroy(self)
  - class def can_build(cls, manipulator: TransformManipulator, operation: Operation) -> bool

- class SnapProviderManager
  - def __init__(self, viewport_api)
  - def destroy(self)
  - def on_began(self, excluded_paths: List[Union[str, Sdf.Path]], **kwargs)
  - def on_ended(self, **kwargs)
  - def get_snap_pos(self, xform: Gf.Matrix4d, ndc_location: Sequence[float], scene_view: sc.SceneView, on_snapped: Callable) -> bool

## Variables

- PRIM_SNAP_NAME: str
- SURFACE_SNAP_NAME: str
- GRID_SNAP_NAME: str

## Other



# Public API for module omni.kit.manipulator.tool.snap.settings_constants:

## Variables

- SNAP_PROVIDER_NAME_SETTING_PATH: str
- CONFORM_TO_TARGET_SETTING_PATH: str
- CONFORM_UP_AXIS_SETTING_PATH: str
- KEEP_SPACING_SETTING_PATH: str
- SNAP_SETTING_PREFIX: str
- SNAP_TRANSLATE_SETTING_PATH: Unknown
- SNAP_ROTATE_SETTING_PATH: Unknown
- SNAP_SCALE_SETTING_PATH: Unknown
- SNAP_ENABLED_SETTING: str
