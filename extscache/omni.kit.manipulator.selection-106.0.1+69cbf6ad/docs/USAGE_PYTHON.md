```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Initialize Selection Manipulator with Custom Style

```python
from omni.kit.manipulator.selection import SelectionManipulator

# Initialize a selection manipulator with custom styling
custom_style = {
    "thickness": 5.0,
    "color": (0.2, 0.2, 0.8, 0.8),
    "inner_color": (0.2, 0.6, 0.8, 0.4)
}
selection_manipulator = SelectionManipulator(style=custom_style)
```

## Create and Update SelectionShapeModel

```python
from omni.kit.manipulator.selection import SelectionShapeModel

# Create a selection shape model
selection_model = SelectionShapeModel()

# Set normalized device coordinate start and current points
ndc_start_point = [1, 2]
ndc_current_point = [3, 4]
selection_model.set_floats('ndc_start', ndc_start_point)
selection_model.set_floats('ndc_current', ndc_current_point)

# Get the normalized device coordinate rectangle
ndc_rect = selection_model.get_as_floats('ndc_rect')
print("NDC Rectangle:", ndc_rect)
```

## Respond to Selection Changes in Manipulator Model

```python
from omni.kit.manipulator.selection import SelectionManipulator

# Create a selection manipulator
selection_manipulator = SelectionManipulator()

# Define a callback function to respond to selection changes
def on_selection_changed(model, item):
    if item == model.get_item('ndc_rect'):
        ndc_rect = model.get_as_floats(item)
        print("Selection Changed:", ndc_rect)

# Subscribe to selection changes
subscription = selection_manipulator.model.subscribe_item_changed_fn(on_selection_changed)

# Later, to unsubscribe
selection_manipulator.model.unsubscribe_item_changed_fn(subscription)
```

## Perform Selection with Mouse Dragging (Test Simulation)

```python
from omni.kit.manipulator.selection import SelectionManipulator
from omni.kit.manipulator.selection import SelectionShapeModel

# This function simulates a selection test
def perform_selection_test():
    # Create a model and manipulator for the test
    selection_model = SelectionShapeModel()
    selection_manipulator = SelectionManipulator(model=selection_model)

    # Simulate setting normalized device coordinate start and current points
    ndc_start_point = [0.1, 0.1]
    ndc_current_point = [0.9, 0.9]
    selection_model.set_floats('ndc_start', ndc_start_point)
    selection_model.set_floats('ndc_current', ndc_current_point)

    # Trigger the manipulator's model update callback
    selection_manipulator.on_model_updated(selection_model.get_item('ndc_rect'))

    # Get the resulting selection rectangle
    ndc_rect = selection_model.get_as_floats('ndc_rect')
    print("Selection Rectangle:", ndc_rect)

# Call the function to simulate the test
perform_selection_test()
```

Please note that the final example was corrected to properly simulate the selection process programmatically. The updated version sets the normalized device coordinate start and current points and triggers the manipulator's model update callback to reflect a mouse drag gesture. This provides a complete standalone example that does not rely on asynchronous operations or a test framework.