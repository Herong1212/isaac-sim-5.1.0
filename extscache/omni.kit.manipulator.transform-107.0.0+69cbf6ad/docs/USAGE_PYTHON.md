```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Transform Manipulator Usage Example

```python
import omni.kit.app
import omni.ui as ui
from omni.kit.manipulator.transform import (
    TransformManipulator,
    Axis,
    SimpleRotateChangedGesture,
    SimpleScaleChangedGesture,
    SimpleTranslateChangedGesture,
)
from omni.ui import scene as sc

# Initialize a simple manipulator example with predefined projection and view matrices
projection = [
    0.011730205278592375, 0.0, 0.0, 0.0, 0.0, 0.02055498458376156, 0.0, 0.0,
    0.0, 0.0, 2.00000020000002e-07, 0.0, -0.0, -0.0, 1.00000020000002, 1.0
]
view = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -2.2368736267089844, 13.669827461242786, -5.0, 1.0]

# Create a window and a scene with a TransformManipulator
window = ui.Window("Simple Manipulator Example")

class Select(sc.ClickGesture):
    """A gesture class for handling selection in a scene."""
    def __init__(self, example):
        super().__init__()
        self._example = example

    def on_ended(self):
        self._example.on_point_clicked(self.sender)

class SimpleManipulatorExample:
    def __init__(self):
        with window.frame:
            scene_view = sc.SceneView(projection=projection, view=view)
            with scene_view.scene:
                # Instantiate the TransformManipulator with gestures for translation, rotation, and scaling
                self._manipulator = TransformManipulator(
                    size=1,
                    axes=Axis.ALL & ~Axis.Z & ~Axis.SCREEN,
                    enabled=False,
                    gestures=[
                        SimpleTranslateChangedGesture(),
                        SimpleRotateChangedGesture(),
                        SimpleScaleChangedGesture(),
                    ],
                )

                # Placeholder for selected shape
                self._selected_shape = None

                # Subscribe to manipulator model item changes
                self._sub = self._manipulator.model.subscribe_item_changed_fn(self._on_item_changed)

                # Create points in the scene and attach a selection gesture to each
                points = [
                    ([0, 0, 0], ui.color.white),
                    ([50, 0, 0], ui.color.white),
                    ([50, -50, 0], ui.color.white),
                    ([0, -50, 0], ui.color.white)
                ]
                for position, color in points:
                    sc.Points(positions=[position], colors=[color], sizes=[10], gestures=[Select(self)])

    def on_point_clicked(self, shape):
        self._selected_shape = shape
        self._manipulator.enabled = True

        model = self._manipulator.model
        model.set_floats(
            model.get_item("translate"),
            [
                self._selected_shape.positions[0][0],
                self._selected_shape.positions[0][1],
                self._selected_shape.positions[0][2],
            ],
        )

    def _on_item_changed(self, model, item):
        if self._selected_shape is not None:
            if item.operation == Operation.TRANSLATE:
                self._selected_shape.positions = model.get_as_floats(item)

# Create an instance to show the manipulator
example = SimpleManipulatorExample()

# Display the window
window.visible = True
```