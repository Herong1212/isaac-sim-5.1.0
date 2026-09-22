# Public API for module omni.kit.xr.scene_view.utils:

## Classes

- class SceneViewUtils(Generic[_TSceneView])
  - class def find_scene_view(cls, element_path: str) -> _TSceneView | None
  - class def update_scene_views(cls, event: carb.events.IEvent)
  - class def update_scene_view_transforms(cls, event: carb.events.IEvent)
  - def __init__(self, scene_view_type: Type[_TSceneView], scene_view_args: dict = {}, attach_mode: SceneViewAttachMode = SceneViewAttachMode.ATTACH_TO_MAIN_VIEWPORT)
  - class def delete_later(cls, item: Any)
  - [property] def scene_view(self) -> _TSceneView

- class SceneViewAttachMode(Enum)
  - ATTACH_TO_MAIN_VIEWPORT: Unknown
  - DO_NOT_ATTACH_TO_MAIN_VIEWPORT: Unknown

- class SceneViewUtilsExtension(omni.ext.IExt)
  - static def on_startup(ext_id: str)
  - static def on_shutdown()

- class TransformableManipulator(ComposableManipulator)
  - def __init__(self)
  - def clear(self)
  - [property] def matrix(self) -> Gf.Matrix4d
  - [matrix.setter] def matrix(self, matrix: list[float] | Gf.Matrix4d)
  - [property] def scale(self) -> Float3
  - [scale.setter] def scale(self, scale: Float3)
  - [property] def rotation_radians(self) -> Float3
  - [rotation_radians.setter] def rotation_radians(self, rotation: Float3)
  - [property] def rotation_degrees(self) -> Float3
  - [rotation_degrees.setter] def rotation_degrees(self, rotation: Float3)
  - [property] def translation(self) -> Float3
  - [translation.setter] def translation(self, translation: Float3)
  - [property] def transform_model(self) -> TransformableManipulatorModel
  - def build_func(self)
  - def model_updated_func(self, item)

- class TranslationGestureHandler(sc.DragGesture)
  - def __init__(self, model: TransformableManipulatorModel, **kwargs)
  - def on_began(self)
  - def on_changed(self)
  - def on_ended(self)

- class RotationGestureHandler(sc.DragGesture)
  - def __init__(self, model: TransformableManipulatorModel, **kwargs)
  - def on_began(self)
  - def on_changed(self)

- class ScaleGestureHandler(sc.DragGesture)
  - def __init__(self, model: TransformableManipulatorModel, **kwargs)
  - def on_began(self)
  - def on_changed(self)
  - def on_ended(self)

- class PreventGestureOverlap(sc.GestureManager)
  - def can_be_prevented(self, arg0: sc.AbstractGesture) -> bool
  - def should_prevent(self, arg0: sc.AbstractGesture, arg1: sc.AbstractGesture) -> bool

- class WidgetComponent(Area2DComponent, Generic[_TWidget])
  - def __init__(self, widget_type: Type[_TWidget], width: float = 100, height: float = 100, resolution_scale: float = 1.0, unit_to_pixel_scale: float = 1.0, construct_callback: Callable[[_TWidget], None] | None = None, transform_args: Dict[str, Any] | None = None, update_policy: UpdatePolicy = UpdatePolicy.ON_MOUSE_HOVERED, color: List[float] | None = None, widget_args: Tuple[Any, ...] | List[Any] | Any | None = None, widget_kwargs: Dict[str, Any] | None = None, **kwargs)
  - [property] def resolution_scale(self) -> float
  - [resolution_scale.setter] def resolution_scale(self, scale)
  - [property] def unit_to_pixel_scale(self) -> float
  - [unit_to_pixel_scale.setter] def unit_to_pixel_scale(self, scale: float)
  - [property] def color(self) -> List[float] | None
  - [color.setter] def color(self, color: List[float] | None)
  - [property] def scene_widget(self) -> sc.Widget | None
  - [property] def widget(self) -> _TWidget | None

- class RotationHandleComponent(BaseTransformableComponent)

- class ScaleHandleComponent(BaseTransformableComponent)

- class TranslationHandleComponent(BaseTransformableComponent)

- class Resize2DHandleComponent(BaseTransformableComponent)
  - def __init__(self, target: Area2DComponent, *args, **kwargs)

- class Area2DComponent(ManipulatorComponent)
  - CENTER: Unknown
  - LEFT: Unknown
  - TOP_LEFT: Unknown
  - TOP: Unknown
  - TOP_RIGHT: Unknown
  - RIGHT: Unknown
  - BOTTOM_RIGHT: Unknown
  - BOTTOM: Unknown
  - BOTTOM_LEFT: Unknown
  - def __init__(self, width: float, height: float, origin: Float2 = CENTER, z_offset: float = 0.0, **kwargs)
  - [property] def width(self) -> float
  - [width.setter] def width(self, width: float)
  - [property] def height(self) -> float
  - [height.setter] def height(self, height: float)
  - [property] def transform(self) -> sc.Transform | None
  - [property] def owner(self) -> ProxyType[ComposableManipulator] | None
  - def add_child(self, child: Area2DComponent, placement: Float2 = CENTER)

- class UiContainer
  - def __init__(self, initial_component: ManipulatorComponent | None = None, space_stack: SpatialSource | list[SpatialSource] | None = None, scene_view_type: type[omni.ui.scene.SceneView] = XRSceneView, scene_view_args: dict = {}, attach_mode: SceneViewAttachMode = SceneViewAttachMode.ATTACH_TO_MAIN_VIEWPORT)
  - def show(self)
  - def hide(self)
  - [property] def root(self) -> omni.ui.scene.AbstractContainer
  - [property] def manipulator(self) -> TransformableManipulator
  - [property] def visible(self)
  - [visible.setter] def visible(self, should_be_visible: bool)
  - [property] def scene_view(self) -> omni.ui.scene.SceneView

- class UiInput(ABC)
  - def push_input(self, scene_view: omni.ui.scene.SceneView)

- class UiInputMotion(UiInput)
  - def __init__(self, origin: list[float], direction: list[float])
  - def push_input(self, scene_view: omni.ui.scene.SceneView)

- class UiInputToggle(UiInput)
  - def __init__(self, input_map: InputButtonMap, pressed: bool)
  - def push_input(self, scene_view: omni.ui.scene.SceneView)

- class ActionGraphNoCodeUiIntegration(ABC)
  - def __init__(self)
  - def send_to_scene(self, objects: dict, attributes: Dict[str, Any] = {})
  - def remove_from_scene(self, objects: dict) -> bool
  - def send_ui_to_scene(trigger: ot.execution, ui_frame_path: ot.string, parameters: ot.bundle) -> ot.execution
  - def remove_ui_from_scene(trigger: ot.execution, ui_frame_path: ot.string) -> ot.execution
