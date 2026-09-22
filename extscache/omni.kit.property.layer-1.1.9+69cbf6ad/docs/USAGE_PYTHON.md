# Usage Examples

## Modify Stage Up Axis

```python
# This snippet is correct and does not require changes.
from pxr import UsdGeom
from omni.kit.property.layer.commands import ModifyStageAxisCommand

# Assuming we have a valid USD stage reference called `stage`
# For demonstration, let's create a temporary USD stage
from pxr import Usd
stage = Usd.Stage.CreateInMemory()

# Change the up axis to 'Z'
modify_stage_axis_cmd = ModifyStageAxisCommand(stage=stage, axis='Z')
modify_stage_axis_cmd.do()

# Confirm the up axis is now 'Z'
assert UsdGeom.GetStageUpAxis(stage) == 'Z'

# Undo the modification to revert the up axis to its original state
modify_stage_axis_cmd.undo()
```

## Modify Layer Metadata

```python
# This snippet is correct and does not require changes.
from omni.kit.property.layer.commands import ModifyLayerMetadataCommand
from omni.kit.property.layer.types import LayerMetaType
from pxr import Sdf

# Assuming we have identifiers for layer and parent layer
layer_identifier = 'layer.usd'
parent_layer_identifier = 'parent_layer.usd'

# Create a temporary layer for demonstration
layer = Sdf.Layer.CreateNew(layer_identifier)

# Modify layer's start time code metadata to 101.0
modify_layer_metadata_cmd = ModifyLayerMetadataCommand(
    layer_identifier=layer_identifier,
    parent_layer_identifier=parent_layer_identifier,
    meta_index=LayerMetaType.START_TIME,
    value=101.0
)
modify_layer_metadata_cmd.do()

# Verify the start time code is updated
layer = Sdf.Find(layer_identifier)
assert layer.startTimeCode == 101.0

# Undo the metadata modification
modify_layer_metadata_cmd.undo()
```

## Set Custom File Picker Functions

```python
# This snippet is correct and does not require changes.
from omni.kit.property.layer.file_picker import FilePicker, FileBrowserSelectionType

# Create a file picker for selecting USD files
file_picker = FilePicker(
    title="Select USD File",
    apply_button_name="Select",
    selection_type=FileBrowserSelectionType.FILE_ONLY,
    item_filter_options=[(r'.*\.usd', 'USD Files (*.usd)')]
)

# Custom function to call when a file is selected
def on_file_selected(file_path):
    print(f"Selected file: {file_path}")

# Custom function to call when the file picker is canceled
def on_cancel():
    print("File selection canceled")

# Set custom functions for the file picker
file_picker.set_custom_fn(on_file_selected, on_cancel)

# Show the file picker dialog
file_picker.show_dialog()
```

## Replace Layer in USD Stage

```python
from omni.kit.property.layer.layer_property_models import LayerPathModel
from omni.kit.commands import execute
import weakref

class MockLayerItem:
    def __init__(self, identifier, parent=None, reserved=False):
        self._identifier = identifier
        self._parent = parent
        self._reserved = reserved

    @property
    def identifier(self):
        return self._identifier

    @property
    def parent(self):
        return self._parent

    @property
    def reserved(self):
        return self._reserved

# Mocking layer items for demonstration
parent_layer_item = MockLayerItem('parent_layer.usd')
layer_item = MockLayerItem('layer.usd', parent=parent_layer_item)
# Replace the layer with a new path "new_layer_path.usd"
layer_path_model = LayerPathModel(weakref.ref(layer_item))
layer_path_model.replace_layer("new_layer_path.usd")

# Execute the replacement command
execute("ReplaceSublayer",
    layer_identifier=layer_item.parent.identifier,
    sublayer_position=0,  # Assuming the layer is at position 0
    new_layer_path="new_layer_path.usd"
)
```

## Update Layer Metadata in Property Widget

```python
from omni.kit.property.layer.layer_property_widgets import LayerMetaWiget
from omni.kit.property.layer.layer_property_models import LayerMetaModel
from omni.kit.property.layer.types import LayerMetaType
import weakref

class MockLayerItem:
    def __init__(self, identifier, parent=None, reserved=False, layer=None):
        self._identifier = identifier
        self._parent = parent
        self._reserved = reserved
        self._layer = layer

    @property
    def identifier(self):
        return self._identifier

    @property
    def parent(self):
        return self._parent

    @property
    def reserved(self):
        return self._reserved

    @property
    def layer(self):
        return self._layer

# Mocking a layer item for demonstration
layer_item = MockLayerItem('layer.usd')

# Create a metadata widget for layer comments
meta_widget = LayerMetaWiget(icon_path="path/to/icon")

# Create a metadata model for comments
meta_model = LayerMetaModel(weakref.ref(layer_item), LayerMetaType.COMMENT)

# Set a new value for the comment metadata
meta_model.set_value("This is a new comment")

# End editing to apply the change
meta_model.end_edit()

# Build the metadata widget UI with the new model
meta_widget.build_items()
```