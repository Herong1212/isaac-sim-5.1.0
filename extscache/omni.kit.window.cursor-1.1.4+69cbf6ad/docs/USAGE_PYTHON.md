# Usage Examples

## Managing cursor shapes

```python
from omni.kit.window.cursor import get_main_window_cursor
import carb.settings

# Override the current cursor shape with a custom extended shape
main_window_cursor = get_main_window_cursor()
if main_window_cursor:
    # Register a cursor
    settings = carb.settings.get_settings()
    cursors = settings.get_settings_dictionary("/exts/omni.kit.window.cursor/cursors")
    # via setting
    cursors["Rotate_object"] = "${omni.kit.window.cursor}/data/icons/usage/rotateObject.png"
    # or method
    main_window_cursor.register_cursor_shape_extend("Rotate_object", "${omni.kit.window.cursor}/data/icons/usage/rotateObject.png")

    # override the current cursor with cursors we registered
    main_window_cursor.override_cursor_shape_extend("Rotate_object")

    # do something....
    main_window_cursor.get_cursor_shape_override_extend() # should be "Rotate_object"

    # restore the cursor to default
    main_window_cursor.clear_overridden_cursor_shape()
    # unregister the cursor
    main_window_cursor.unregister_cursor_shape_extend("Rotate_object")
```

