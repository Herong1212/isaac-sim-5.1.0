# Usage Examples

## Initialize and Set Path in PathField Widget

```python
from omni.kit.widget.path_field import PathField

# Initialize the PathField widget with custom handlers
def apply_path_handler(path):
    print(f"Path applied: {path}")

def branching_options_handler(path, callback):
    # Simulate branching options for a given path
    options = ["branch1", "branch2", "branch3"]
    callback(options)

path_field = PathField(
    apply_path_handler=apply_path_handler,
    branching_options_handler=branching_options_handler,
    separator="/"
)

# Set the initial path of the widget
path_field.set_path("/initial/path")
```

## Handling Branch Selection with Keyboard Interaction

```python
import omni.ui as ui
from omni.kit.widget.path_field import PathField

# Mock branching options handler to provide options based on the current path
def branching_handler(path, callback):
    if path == "/":
        callback(["folder1", "folder2"])
    elif path == "/folder1":
        callback(["subfolder1", "subfolder2"])
    else:
        callback([])

def apply_handler(path: str):
    print(f"Path: {path}")
    # do something with the path...

# Create a PathField widget with handlers
with ui.Window("PathField Example", width=300, height=100).frame:
    path_field = PathField(
        separator="/",
        branching_options_handler=branching_handler,
        apply_path_handler=apply_handler
    )

    path_field.set_path("/")
```

