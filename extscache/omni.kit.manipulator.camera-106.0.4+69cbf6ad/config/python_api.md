# Public API for module omni.kit.manipulator.camera:

## Classes

- class SceneViewCameraManipulator(CameraManipulatorBase)
  - def __init__(self, center_of_interest, *args, **kwargs)
  - def on_model_updated(self, item)

- class CameraManipulatorBase(sc.Manipulator)
  - def __init__(self, bindings: dict = None, model: sc.AbstractManipulatorModel = None, *args, **kwargs)
  - def on_build(self)
  - def destroy(self)
  - [property] def gamepad_enabled(self) -> bool
  - [gamepad_enabled.setter] def gamepad_enabled(self, value: bool)

- class UsdCameraManipulator(CameraManipulatorBase)
  - def __init__(self, bindings: dict = None, usd_context_name: str = '', prim_path: Sdf.Path = None, *args, **kwargs)
  - def on_model_updated(self, item)

- class ViewportCameraManipulator(UsdCameraManipulator)
  - def __init__(self, viewport_api, bindings: dict = None, *args, **kwargs)
  - def destroy(self)

- class CameraGestureBase(sc.DragGesture)
  - def __init__(self, model: sc.AbstractManipulatorModel, configure_model: Callable = None, name: str = None, *args, **kwargs)
  - def destroy(self)
  - [property] def center_of_interest(self)
  - [property] def initial_transform(self)
  - [property] def last_transform(self)
  - [property] def projection(self)
  - [property] def orthographic(self)
  - [property] def disable_pan(self)
  - [property] def disable_tumble(self)
  - [property] def disable_look(self)
  - [property] def disable_zoom(self)
  - [property] def intertia(self)
  - [property] def up_axis(self)
  - def get_rotation_speed(self, secondary)
  - [property] def tumble_speed(self)
  - [property] def look_speed(self)
  - [property] def move_speed(self)
  - [property] def world_speed(self)
  - def on_began(self, mouse: Sequence[float] = None)
  - def on_changed(self, mouse: Sequence[float] = None)
  - def on_ended(self)
  - def dirty_items(self, model: sc.AbstractManipulatorModel)

- class LookGesture(CameraGestureBase)
  - def on_mouse_move(self, mouse_moved)

- class PanGesture(CameraGestureBase)
  - def on_mouse_move(self, mouse_moved)

- class TumbleGesture(CameraGestureBase)
  - def on_mouse_move(self, mouse_moved)

- class ZoomGesture(CameraGestureBase)
  - def dirty_items(self, model: sc.AbstractManipulatorModel)
  - def on_began(self, *args, **kwargs)
  - def on_mouse_move(self, mouse_moved)

## Functions

- def adjust_center_of_interest(model: CameraManipulatorModel, initial_transform: Gf.Matrix4d, final_transform: Gf.Matrix4d)
