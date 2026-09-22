# Public API for module omni.kit.manipulator.transform:

## Classes

- class AbstractTransformManipulatorModel(sc.AbstractManipulatorModel)
  - class OperationItem(sc.AbstractManipulatorItem)
    - def __init__(self, op: Operation)
    - [property] def operation(self)
  - def __init__(self, **kwargs)
  - def get_as_floats(self, item: sc.AbstractManipulatorItem) -> List[float]
  - def get_as_floats(self, item: sc.AbstractManipulatorItem) -> List[int]
  - def get_item(self, name: str) -> sc.AbstractManipulatorItem
  - def widget_enabled(self)
  - def widget_disabled(self)
  - def set_floats(self, item: sc.AbstractManipulatorItem, value: List[float])
  - def set_ints(self, item: sc.AbstractManipulatorItem, value: List[int])
  - def get_operation(self) -> Operation
  - def get_snap(self, item: sc.AbstractManipulatorItem)

- class TransformManipulatorExt(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)

- class TransformChangedGesture(sc.ManipulatorGesture)
  - def __init__(self, **kwargs)
  - def process(self)
  - def on_began(self)
  - def on_changed(self)
  - def on_ended(self)
  - def on_canceled(self)

- class TranslateChangedGesture(TransformChangedGesture)

- class RotateChangedGesture(TransformChangedGesture)

- class ScaleChangedGesture(TransformChangedGesture)

- class RotateDragGesturePayload(TransformDragGesturePayload)
  - axis: Sequence[float]
  - angle_delta: float
  - angle: float
  - screen_space: bool
  - free_rotation: bool

- class ScaleDragGesturePayload(TransformDragGesturePayload)
  - axis: Sequence[float]
  - scale: Sequence[float]

- class TransformDragGesturePayload(sc.AbstractGesture.GesturePayload)
  - def __init__(self, base: sc.AbstractGesture.GesturePayload, changing_item: sc.AbstractManipulatorItem)

- class TranslateDragGesturePayload(TransformDragGesturePayload)
  - axis: Sequence[float]
  - moved_delta: Sequence[float]
  - moved: Sequence[float]

- class TransformManipulator(sc.Manipulator)
  - def __init__(self, size: float = 1.0, enabled: bool = True, axes: Axis = Axis.ALL, model: AbstractTransformManipulatorModel = None, style: Dict = {}, gestures: List[sc.ManipulatorGesture] = [], tool_registry: ToolbarRegistry = None, tool_button_additional_payload: Dict[str, Any] = {}, tools_default_collapsed: bool | None = None)
  - def destroy(self)
  - def on_build(self)
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value: bool)
  - [property] def size(self) -> float
  - [size.setter] def size(self, value: float)
  - [property] def axes(self) -> float
  - [axes.setter] def axes(self, value: float)
  - [property] def style(self) -> Dict
  - [style.setter] def style(self, value: Dict)
  - def model(self, model)
  - [property] def tool_registry(self) -> ToolbarRegistry
  - [tool_registry.setter] def tool_registry(self, value: ToolbarRegistry)
  - [property] def toolbar_visible(self) -> bool
  - [toolbar_visible.setter] def toolbar_visible(self, value: bool)
  - def refresh_toolbar(self)
  - def on_model_updated(self, item)

- class Axis(Flag)
  - X: Unknown
  - Y: Unknown
  - Z: Unknown
  - SCREEN: Unknown
  - ALL: Unknown

- class Operation(Enum)
  - TRANSLATE: Unknown
  - ROTATE: Unknown
  - SCALE: Unknown
  - NONE: Unknown
  - TRANSLATE_DELTA: Unknown
  - ROTATE_DELTA: Unknown
  - SCALE_DELTA: Unknown

- class Constants
  - TRANSFORM_MOVE_MODE_SETTING: str
  - TRANSFORM_ROTATE_MODE_SETTING: str
  - TRANSFORM_MODE_GLOBAL: str
  - TRANSFORM_MODE_LOCAL: str
  - TRANSFORM_OP_SETTING: str
  - TRANSFORM_OP_SELECT: str
  - TRANSFORM_OP_MOVE: str
  - TRANSFORM_OP_ROTATE: str
  - TRANSFORM_OP_SCALE: str
  - MANIPULATOR_SCALE_SETTING: str
  - FREE_ROTATION_ENABLED_SETTING: str
  - FREE_ROTATION_TYPE_SETTING: str
  - FREE_ROTATION_TYPE_CLAMPED: str
  - FREE_ROTATION_TYPE_CONTINUOUS: str
  - OMNI_SCALE_DIR_SETTING: str
  - INTERSECTION_THICKNESS_SETTING: str
  - TOOLS_DEFAULT_COLLAPSED_SETTING: str

- class OpSettingsListener(Listener)
  - class CallbackType(Enum)
    - OP_CHANGED: Unknown
    - TRANSLATION_MODE_CHANGED: Unknown
    - ROTATION_MODE_CHANGED: Unknown
  - def __init__(self)
  - def destroy(self)

- class SnapSettingsListener(Listener)
  - def __init__(self, enabled_setting_path: str = None, move_x_setting_path: str = None, move_y_setting_path: str = None, move_z_setting_path: str = None, rotate_setting_path: str = None, scale_setting_path: str = None, provider_setting_path: str = None)
  - def destroy(self)

- class ToolbarRegistry
  - class Subscription
    - def __init__(self, registry: ReferenceType[ToolbarRegistry], id: str)
    - def release(self)
  - def __init__(self)
  - [property] def tools(self) -> List[Type[ToolbarTool]]
  - def register_tool(self, tool_class: Type[ToolbarTool], id: str)
  - def unregister_tool(self, id: str)
  - def subscribe_to_registry_change(self, callback: Callable[[], None]) -> int
  - def unsubscribe_to_registry_change(self, id: int)
  - def set_sort_key_function(self, key: Callable[[Tuple[str, Type[ToolbarTool]]], Any])

- class SimpleToolButton(ToolbarTool)
  - def __init__(self, menu_delegate: ui.MenuDelegate = None, *args, **kwargs)
  - def destroy(self)

- class SimpleTransformModel(AbstractTransformManipulatorModel)
  - def __init__(self)
  - [property] def global_mode(self) -> bool
  - [global_mode.setter] def global_mode(self, value: bool)
  - def set_floats(self, item: AbstractTransformManipulatorModel.OperationItem, value: List[float])
  - def get_as_floats(self, item: AbstractTransformManipulatorModel.OperationItem) -> List[float]
  - def get_operation(self) -> Operation
  - def set_operation(self, op: Operation)

- class SimpleTranslateChangedGesture(TranslateChangedGesture)
  - def on_changed(self)

- class SimpleRotateChangedGesture(RotateChangedGesture)
  - def on_began(self)
  - def on_changed(self)

- class SimpleScaleChangedGesture(ScaleChangedGesture)
  - def on_began(self)
  - def on_changed(self)

## Functions

- def get_default_style()
- def abgr_to_color(abgr: int) -> cl

## Variables

- c: Constants
- COLOR_X: int
- COLOR_Y: int
- COLOR_Z: int
