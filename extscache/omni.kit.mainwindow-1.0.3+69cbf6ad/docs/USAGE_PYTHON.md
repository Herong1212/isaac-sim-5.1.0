```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Check MainWindow Initialization

```python
from omni.kit.mainwindow import get_main_window

# Check if the main window has been properly initialized
main_window = get_main_window()
assert main_window is not None
```

## Toggle Main Menu and Status Bar Visibility

```python
from omni.kit.mainwindow import get_main_window

main_window = get_main_window()
if main_window:
    # Toggle the visibility of the main menu bar in the main window
    main_window.show_hide_menu()
    # Toggle the visibility of the status bar in the main window
    main_window.show_hide_status_bar()
```

## Access Main Menu Bar and Status Bar Frame Object

```python
from omni.kit.mainwindow import get_main_window

main_window = get_main_window()
if main_window:
    # Get the main menu bar object from the main window
    menu_bar = main_window.get_main_menu_bar()
    # Get the status bar frame object from the main window
    status_bar_frame = main_window.get_status_bar_frame()
```

## Validate DockSpace Window

```python
import omni.ui as ui
import omni.kit.app
import asyncio

# Validate the existence of the DockSpace window
async def check_dockspace():
    await omni.kit.app.get_app().next_update_async()
    main_dockspace = ui.Workspace.get_window("DockSpace")
    assert main_dockspace is not None

# Example usage (this needs to be run inside an async context)
asyncio.ensure_future(check_dockspace())
```