# Scene

SceneUI is the framework built on top and tightly integrated with `omni.ui`. It
uses `omni.ui` inputs and basically supports everything `omni.ui` supports, like
Python bindings, properties, callbacks, and async workflow.

SceneView is the `omni.ui` widget that renders all the SceneUI items. It can be
a part of the `omni.ui` layout or an overlay of `omni.ui` interface. It's the
entry point of SceneUI.

## Camera

SceneView determines the position and configuration of the camera and has
projection and view matrices.

```execute
##
from omni.ui import scene as sc
##

# Projection matrix
proj = [1.7, 0, 0, 0, 0, 3, 0, 0, 0, 0, -1, -1, 0, 0, -2, 0]

# Move camera
rotation = sc.Matrix44.get_rotation_matrix(30, 50, 0, True)
transl = sc.Matrix44.get_translation_matrix(0, 0, -6)
view = transl * rotation

scene_view = sc.SceneView(
    sc.CameraModel(proj, view),
    aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_FIT,
    height=200
)

with scene_view.scene:
    # Edges of cube
    sc.Line([-1, -1, -1], [1, -1, -1])
    sc.Line([-1, 1, -1], [1, 1, -1])
    sc.Line([-1, -1, 1], [1, -1, 1])
    sc.Line([-1, 1, 1], [1, 1, 1])

    sc.Line([-1, -1, -1], [-1, 1, -1])
    sc.Line([1, -1, -1], [1, 1, -1])
    sc.Line([-1, -1, 1], [-1, 1, 1])
    sc.Line([1, -1, 1], [1, 1, 1])

    sc.Line([-1, -1, -1], [-1, -1, 1])
    sc.Line([-1, 1, -1], [-1, 1, 1])
    sc.Line([1, -1, -1], [1, -1, 1])
    sc.Line([1, 1, -1], [1, 1, 1])
```

## Screen

To get position and view matrices, SceneView queries the model component. It
represents either the data transferred from the external backend or the data
that the model holds. The user can reimplement the model to manage the user
input or get the camera directly from the renderer or any other back end.

The SceneView model is required to return two float arrays, `projection`
and `view` of size 16, which are the camera matrices.

`ui.Screen` is designed to simplify tracking the user input to control the
camera position. `ui.Screen` represents the rectangle always placed in the front
of the camera. It doesn't produce any visible shape, but it interacts with the
user input.

You can change the camera orientation in the example below by dragging the mouse
cursor left and right.

```execute 200
##
from omni.ui import scene as sc
##

class CameraModel(sc.AbstractManipulatorModel):
    def __init__(self):
        super().__init__()
        self._angle = 0

    def append_angle(self, delta: float):
        self._angle += delta * 100
        # Inform SceneView that view matrix is changed
        self._item_changed("view")

    def get_as_floats(self, item):
        """Called by SceneView to get projection and view matrices"""
        if item == self.get_item("projection"):
            # Projection matrix
            return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, -1, 0, 0, -2, 0]
        if item == self.get_item("view"):
            # Move camera
            rotation = sc.Matrix44.get_rotation_matrix(30, self._angle, 0, True)
            transl = sc.Matrix44.get_translation_matrix(0, 0, -8)
            view = transl * rotation
            return [view[i] for i in range(16)]

def on_mouse_dragged(sender):
    # Change the model's angle according to mouse x offset
    mouse_moved = sender.gesture_payload.mouse_moved[0]
    sender.scene_view.model.append_angle(mouse_moved)

with sc.SceneView(CameraModel(), height=200).scene:
    # Camera control
    sc.Screen(gesture=sc.DragGesture(on_changed_fn=on_mouse_dragged))

    # Edges of cube
    sc.Line([-1, -1, -1], [1, -1, -1])
    sc.Line([-1, 1, -1], [1, 1, -1])
    sc.Line([-1, -1, 1], [1, -1, 1])
    sc.Line([-1, 1, 1], [1, 1, 1])

    sc.Line([-1, -1, -1], [-1, 1, -1])
    sc.Line([1, -1, -1], [1, 1, -1])
    sc.Line([-1, -1, 1], [-1, 1, 1])
    sc.Line([1, -1, 1], [1, 1, 1])

    sc.Line([-1, -1, -1], [-1, -1, 1])
    sc.Line([-1, 1, -1], [-1, 1, 1])
    sc.Line([1, -1, -1], [1, -1, 1])
    sc.Line([1, 1, -1], [1, 1, 1])
```
