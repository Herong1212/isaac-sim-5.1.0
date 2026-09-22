# Usage Examples

## Create a Basic Checkpoint Widget

```python
import omni.ui as ui
from omni.kit.widget.versioning import CheckpointWidget, LAYOUT_TABLE_VIEW, LAYOUT_SLIM_VIEW

# Create a window to host the checkpoint widget
window = ui.Window("Checkpoint Viewer", width=800, height=500)
with window.frame:
    with ui.VStack():
        ui.Label("File Checkpoints (Table View):", height=30)
        
        # Create a CheckpointWidget with table view layout
        url = "omniverse://server-name/path/to/file.usd"
        table_widget = CheckpointWidget(url, layout=LAYOUT_TABLE_VIEW)
        
        ui.Spacer(height=20)
        ui.Label("File Checkpoints (Slim View):", height=30)
        
        # Create a CheckpointWidget with slim view layout
        slim_widget = CheckpointWidget(url, layout=LAYOUT_SLIM_VIEW)
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.versioning/data/docs_images/usage_preview.png
---
align: center
---
```

---

## Using CheckpointCombobox for Checkpoint Selection

```python
import omni.ui as ui
from omni.kit.widget.versioning import CheckpointCombobox

# Create a window to host the checkpoint combobox
window = ui.Window("Checkpoint Selector", width=400, height=200)
with window.frame:
    with ui.VStack(spacing=5):
        ui.Label("Select a checkpoint version:", height=30)
        
        # Create a file URL to get checkpoints from
        url = "omniverse://server-name/path/to/file.usd"
        
        # Define a callback for when a checkpoint is selected
        def on_checkpoint_selection(checkpoint_item):
            if checkpoint_item:
                print(f"Selected checkpoint: {checkpoint_item.get_full_url()}")
                print(f"Checkpoint comment: {checkpoint_item.comment}")
        
        # Create the checkpoint combobox
        checkpoint_combobox = CheckpointCombobox(
            url,
            on_selection_changed_fn=on_checkpoint_selection,
            width=ui.Pixel(300),
            popup_width=450
        )
        
        # Add controls to demonstrate property access
        with ui.HStack(height=30, spacing=5):
            ui.Button("Toggle Visibility", clicked_fn=lambda: setattr(
                checkpoint_combobox, "visible", not checkpoint_combobox.visible))
```

---

## Using CheckpointHelper to Check Checkpoint Availability

```python
import asyncio
import omni.ui as ui
from omni.kit.widget.versioning import CheckpointHelper

# Create a window to display checkpoint status
window = ui.Window("Checkpoint Status", width=400, height=200)
with window.frame:
    with ui.VStack(spacing=5):
        status_label = ui.Label("Checking checkpoint status...")
        url_field = ui.StringField(height=30)
        url_field.model.set_value("omniverse://server-name/path/to/file.usd")
        
        # Status check using callback approach
        def check_with_callback():
            url = url_field.model.get_value_as_string()
            
            def on_checkpoint_status(server, enabled):
                status_label.text = f"Server: {server}\nCheckpoints enabled: {enabled}"
            
            # Extract server from URL and get checkpoint status
            CheckpointHelper.is_checkpoint_enabled_with_callback(url, on_checkpoint_status)
        
        # Status check using async approach
        async def check_async():
            url = url_field.model.get_value_as_string()
            server = CheckpointHelper.extract_server_from_url(url)
            status_label.text = f"Checking server: {server}..."
            
            # Check if checkpoint is enabled for this server
            is_enabled = await CheckpointHelper.is_checkpoint_enabled_async(url)
            status_label.text = f"Server: {server}\nCheckpoints enabled: {is_enabled}"
        
        with ui.HStack(height=30, spacing=5):
            ui.Button("Check (Callback)", clicked_fn=check_with_callback)
            ui.Button("Check (Async)", clicked_fn=lambda: asyncio.ensure_future(check_async()))
```

---

## Advanced CheckpointWidget with Context Menu and Events

```python
import omni.ui as ui
from omni.kit.widget.versioning import CheckpointWidget, CheckpointItem

# Create a window for advanced checkpoint widget demo
window = ui.Window("Advanced Checkpoint Widget", width=800, height=600)
with window.frame:
    with ui.VStack():
        url_field = ui.StringField(height=30)
        url_field.model.set_value("omniverse://server-name/path/to/file.usd")
        
        with ui.HStack(height=30, spacing=5):
            ui.Button("Load Checkpoints", clicked_fn=lambda: checkpoint_widget.set_url(
                url_field.model.get_value_as_string()))
            
            search_field = ui.StringField(placeholder="Search checkpoints...", height=30)
            search_field.model.subscribe_value_changed_fn(
                lambda model: checkpoint_widget.set_search(model.get_value_as_string()))
            
        # Create checkpoint widget with advanced features
        checkpoint_widget = CheckpointWidget(show_none_entry=True)
        
        # Add status label to show selection info
        status_label = ui.Label("No checkpoint selected")
        
        # Register selection change callback
        def on_selection_changed(checkpoint_item):
            if checkpoint_item:
                timestamp = CheckpointItem.datetime_to_string(checkpoint_item.entry.modified_time) 
                size = CheckpointItem.size_to_string(checkpoint_item.entry.size)
                status_label.text = f"Selected: {checkpoint_item.get_relative_path()}\nComment: {checkpoint_item.comment}\n" \
                                    f"Modified: {timestamp}, Size: {size}, By: {checkpoint_item.entry.modified_by}"
            else:
                status_label.text = "No checkpoint selected"
        
        checkpoint_widget.add_on_selection_changed_fn(on_selection_changed)
        
        # Add context menu items - use setattr() for assignment in lambdas
        checkpoint_widget.add_context_menu(
            "Apply Checkpoint",
            "refresh.svg",
            lambda name, item: setattr(status_label, "text", f"Applied checkpoint: {item.get_relative_path()}"),
            lambda name, item: True
        )
        
        checkpoint_widget.add_context_menu(
            "View Details",
            "info.svg",
            lambda name, item: setattr(status_label, "text", f"Details for: {item.get_relative_path()}\n"
                                                           f"Comment: {item.comment}\n"
                                                           f"Modified by: {item.entry.modified_by}"),
            lambda name, item: bool(item)
        )
        
        # Set event handlers for mouse interactions using proper functions
        def on_mouse_pressed(button, key_mod, item):
            if button == 0:
                status_label.text = f"Clicked checkpoint: {item.get_relative_path()}"
            
        checkpoint_widget.set_mouse_pressed_fn(on_mouse_pressed)
        
        def on_mouse_double_clicked(button, key_mod, item):
            status_label.text = f"Double-clicked checkpoint: {item.get_relative_path()}"
            
        checkpoint_widget.set_mouse_double_clicked_fn(on_mouse_double_clicked)
```

