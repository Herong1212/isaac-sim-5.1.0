# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui as ui
from omni.ui import scene as sc

from .manipulator import Axis, TransformManipulator
from .simple_transform_model import (
    SimpleRotateChangedGesture,
    SimpleScaleChangedGesture,
    SimpleTranslateChangedGesture,
)
from .types import Operation


class Select(sc.ClickGesture):
    """A gesture class for handling selection in a scene.

    This class extends the omni.ui.scene ClickGesture to provide a custom selection
    mechanism for objects in a scene. When the gesture ends, it triggers an action
    on the associated SimpleManipulatorExample instance.

    Args:
        example (SimpleManipulatorExample): The example instance this gesture is associated with."""

    def __init__(self, example):
        """Initialize the Select gesture with a reference to the example.

        Args:
            example (SimpleManipulatorExample): The example instance that created the gesture."""
        super().__init__()
        self._example = example

    def on_ended(self):
        """Callback for when the click gesture has ended, triggering the point clicked handler.

        This method is called automatically when the click gesture ends. It will then call the `on_point_clicked`
        method of the `SimpleManipulatorExample` instance that was provided during the `Select` instantiation."""
        self._example.on_point_clicked(self.sender)


class SimpleManipulatorExample:
    """A simple example class that demonstrates the use of TransformManipulator for object manipulation in a scene.

    This class creates a UI window and a scene with points that, when clicked, activate a manipulator allowing for the translation, rotation, and scaling of the selected point.
    """

    def __init__(self):
        """Initializes a simple manipulator example with a predefined projection and view matrix, setting up the UI and scene."""
        projection = [0.011730205278592375, 0.0, 0.0, 0.0]
        projection += [0.0, 0.02055498458376156, 0.0, 0.0]
        projection += [0.0, 0.0, 2.00000020000002e-07, 0.0]
        projection += [-0.0, -0.0, 1.00000020000002, 1.0]
        view = [1.0, 0.0, 0.0, 0.0]
        view += [0.0, 1.0, 0.0, 0.0]
        view += [0.0, 0.0, 1.0, 0.0]
        view += [-2.2368736267089844, 13.669827461242786, -5.0, 1.0]

        self._selected_shape = None

        self._window = ui.Window("Simple Manipulator Example")
        with self._window.frame:
            scene_view = sc.SceneView(projection=projection, view=view)
            with scene_view.scene:
                self._ma = TransformManipulator(
                    size=1,
                    axes=Axis.ALL & ~Axis.Z & ~Axis.SCREEN,
                    enabled=False,
                    gestures=[
                        SimpleTranslateChangedGesture(),
                        SimpleRotateChangedGesture(),
                        SimpleScaleChangedGesture(),
                    ],
                )

                self._sub = self._ma.model.subscribe_item_changed_fn(self._on_item_changed)

                sc.Points([[0, 0, 0]], colors=[ui.color.white], sizes=[10], gestures=[Select(self)])
                sc.Points([[50, 0, 0]], colors=[ui.color.white], sizes=[10], gestures=[Select(self)])
                sc.Points([[50, -50, 0]], colors=[ui.color.white], sizes=[10], gestures=[Select(self)])
                sc.Points([[0, -50, 0]], colors=[ui.color.white], sizes=[10], gestures=[Select(self)])

    def __del__(self):
        """Delegates to the `destroy` method to clean up resources when the instance is being deleted."""
        self.destroy()

    def destroy(self):
        """Cleans up the window resource by setting it to None."""
        self._window = None

    def on_point_clicked(self, shape):
        """Activates the manipulator and sets its position to the selected shape when a point in the scene is clicked.

        Args:
            shape (sc.Shape): The shape that was clicked in the scene."""
        self._selected_shape = shape
        self._ma.enabled = True

        model = self._ma.model
        model.set_floats(
            model.get_item("translate"),
            [
                self._selected_shape.positions[0][0],
                self._selected_shape.positions[0][1],
                self._selected_shape.positions[0][2],
            ],
        )

    def _on_item_changed(self, model, item):
        """Updates the position of the selected shape based on the manipulator's model item changes.

        Args:
            model (SimpleTransformModel): The model associated with the manipulator.
            item (Item): The item that was changed in the model."""
        if self._selected_shape is not None:
            if item.operation == Operation.TRANSLATE:
                self._selected_shape.positions = model.get_as_floats(item)
