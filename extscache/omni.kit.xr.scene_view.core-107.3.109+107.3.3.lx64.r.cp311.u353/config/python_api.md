# Public API for module omni.kit.xr.scene_view.core:

## Classes

- class InputButtonMap
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - BackButton: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - Button0: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - Button1: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - Button2: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - Button3: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - Button4: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - ForwardButton: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - LeftButton: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - MiddleButton: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap
  - RightButton: omni.kit.xr.scene_view.core._xr_scene_view.InputButtonMap

- class InputType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - ScreenSpaceMovement: omni.kit.xr.scene_view.core._xr_scene_view.InputType
  - ToggleActivated: omni.kit.xr.scene_view.core._xr_scene_view.InputType
  - ToggleDeactivated: omni.kit.xr.scene_view.core._xr_scene_view.InputType
  - WorldSpaceMovement: omni.kit.xr.scene_view.core._xr_scene_view.InputType

- class XRPrimPathTransformBasis(omni.ui_scene._scene.TransformBasis)
  - def __init__(self, arg0: str)

- class XRSceneView(omni.ui_scene._scene.SceneView, omni.ui._ui.Widget)
  - def __init__(self, model: omni.ui_scene._scene.AbstractManipulatorModel = None, custom_base_path: str = '', **kwargs)
  - static def get_base_path() -> str
  - def run_update(self)
  - def update_transforms(self)
  - [property] def input_event_stream(self) -> carb.events._events.IEventStream
  - [property] def system_path(self) -> str
  - FLAG_WANT_CAPTURE_KEYBOARD: int
