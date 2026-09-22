# Usage Examples

## Initialize External Drag and Drop Support
```python
from omni.kit.window.drop_support import ExternalDragDrop

# Define a callback function to handle dropped files
def on_drop(external_drag_drop, dropped_paths):
    print(f"Dropped files: {dropped_paths}")

# Initialize ExternalDragDrop for a window named "MainWindow"
external_drag_drop = ExternalDragDrop("MainWindow", on_drop)
```
