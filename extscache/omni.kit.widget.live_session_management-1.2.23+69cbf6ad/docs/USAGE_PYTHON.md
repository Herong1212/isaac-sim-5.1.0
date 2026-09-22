# Usage Examples

## Track Camera Followers with LiveSessionCameraFollowerList

```python
import omni.ui as ui
import omni.usd
from pxr import Sdf
from omni.kit.widget.live_session_management import LiveSessionCameraFollowerList

# Create a window to display camera followers
window = ui.Window("Camera Followers", width=400, height=200)

with window.frame:
    with ui.VStack():
        # Get the USD context
        usd_context = omni.usd.get_context()
        
        # Function to update the follower list when camera changes
        def update_follower_list(camera_path_str):
            # Clear previous content
            content_frame.clear()
            
            if camera_path_str:
                camera_path = Sdf.Path(camera_path_str)
                
                with content_frame:
                    # Create a camera follower list for the selected camera
                    follower_list = LiveSessionCameraFollowerList(
                        usd_context=usd_context,
                        camera_path=camera_path,
                        icon_size=24,
                        spacing=5,
                        maximum_users=5,
                        show_my_following_users=True
                    )
                    
                    # Add the follower list layout to our content frame
                    if not follower_list.empty():
                        follower_list.layout.height = ui.Pixel(40)
                    else:
                        ui.Label("No followers for this camera")
        
        # Create a combo box to select a camera
        camera_paths = []
        stage = usd_context.get_stage()
        if stage:
            # Find all cameras in the stage
            cameras = [prim for prim in stage.TraverseAll() if prim.IsA('Camera')]
            camera_paths = [str(camera.GetPath()) for camera in cameras]
        
        ui.Label("Select Camera:")
        camera_combo = ui.ComboBox(0, *camera_paths)
        camera_combo.model.add_item_changed_fn(
            lambda item_model, item: update_follower_list(camera_paths[item])
            if item and item < len(camera_paths) else None
        )
        ui.Label("Users following the camera:")
        
        # Content frame will contain the follower list
        content_frame = ui.Frame(height=60)
        
        # Initialize with the first camera if available
        if camera_paths:
            update_follower_list(camera_paths[0])
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.live_session_management/data/docs_images/camera_followers.png
---
align: center
---
```

---

## Reload Outdated Layers

```python
import omni.ui as ui
import omni.usd
from omni.kit.widget.live_session_management import reload_outdated_layers, is_viewer_only_mode

# Create a window with controls to reload layers
window = ui.Window("Layer Reload Example", width=600, height=300)

with window.frame:
    with ui.VStack(spacing=10):
        ui.Label("Layer Management")
        
        # Get USD context and stage
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        
        if stage:
            # Get all layers used in the stage
            layers = stage.GetUsedLayers()
            layer_paths = [layer.identifier for layer in layers]
            
            # Create a combo box to select a layer
            ui.Label("Select Layer:")
            selected_layer = ui.StringField()
            
            def set_selected_layer(model, item):
                current_index = model.get_item_value_model().as_int
                selected_layer.model.set_value(layer_paths[current_index])
            
            layer_combo = ui.ComboBox(0, *[layer.identifier.split('/')[-1] for layer in layers])
            layer_combo.model.add_item_changed_fn(set_selected_layer)
            
            if layers:
                selected_layer.model.set_value(layer_paths[0])
            
            # Show viewer mode status
            viewer_mode = is_viewer_only_mode()
            ui.Label(f"Viewer Only Mode: {'Enabled' if viewer_mode else 'Disabled'}")
            
            # Button to reload the selected layer
            def reload_layer():
                layer_path = selected_layer.model.get_value_as_string()
                if layer_path:
                    reload_outdated_layers(layer_path, usd_context)
            
            ui.Button("Reload Selected Layer", clicked_fn=reload_layer)
            
            # Button to reload all outdated layers
            def reload_all_outdated():
                reload_outdated_layers(layer_paths, usd_context)
            
            ui.Button("Reload All Outdated Layers", clicked_fn=reload_all_outdated)
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.live_session_management/data/docs_images/reload_outdated_layers.png
---
align: center
---
```

---

## Create and Manage Live Sessions with LiveSessionModel

```python
import omni.ui as ui
import omni.usd  # Added missing import
import omni.kit.usd.layers as layers
from omni.kit.widget.live_session_management import LiveSessionModel

# Create a window with controls for managing live sessions
window = ui.Window("Live Session Manager", width=400, height=200)

with window.frame:
    with ui.VStack(spacing=5):
        ui.Label("Live Session Management", height=20)
        
        # Get layers interface
        layers_interface = layers.get_layers()
        
        # Get the current stage's layer identifier
        layer_identifier = omni.usd.get_context().get_stage_url()
        
        # Create a LiveSessionModel for the current layer
        session_model = LiveSessionModel(layers_interface,layer_identifier)
        session_model.refresh_sessions(force=True)
        
        # Create a combo box to select from available sessions
        ui.Label("Select a session:")
        session_combo = ui.ComboBox(session_model)
        
        # Button to create a new session
        with ui.HStack(height=30, spacing=5):
            session_name = ui.StringField()
            session_name.model.set_value("My Session")
            
            def create_session():
                # Generate a new session name if needed
                if not session_name.model.get_value_as_string():
                    new_name = session_model.create_new_session_name()
                    session_name.model.set_value(new_name)
                
                # Create the session using layers interface
                live_syncing = layers_interface.get_live_syncing()
                live_syncing.create_live_session(
                    name=session_name.model.get_value_as_string(),
                    layer_identifier=layer_identifier
                )
            
            ui.Button("Create New Session", clicked_fn=create_session)
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.live_session_management/data/docs_images/live_session_model.png
---
align: center
---
```

---

## Build User Icons with User Layout Utility

```python
import omni.ui as ui
import omni.kit.usd.layers as layers
from omni.kit.widget.live_session_management import build_live_session_user_layout

# Create a window to display custom user icons
window = ui.Window("User Icons Example", width=400, height=100)

with window.frame:
    with ui.VStack():
        ui.Label("Custom User Icons:")
        
        with ui.HStack(height=50, spacing=10):
            # Create a sample user object
            # In a real scenario, this would come from a live session
            class SampleUser:
                def __init__(self, user_id, user_name, from_app):
                    self.user_id = user_id
                    self.user_name = user_name
                    self.from_app = from_app
                    # Adding user_color attribute required by the API
                    self.user_color = (0.2, 0.6, 0.8, 1.0)  # Blue with alpha=1
            
            # Create some sample users
            users = [
                SampleUser("user1", "John Doe", "Create"),
                SampleUser("user2", "Jane Smith", "View"),
                SampleUser("user3", "Bob Johnson", "Kit")
            ]
            
            # Function to handle double-click on a user icon
            def on_double_click(x, y, button, modifier, user):
                print(f"Double-clicked on user: {user.user_name}")
            
            # Function to handle single-click on a user icon
            def on_click(x, y, button, modifier, user):
                print(f"Clicked on user: {user.user_name}")
            
            # Create user icons for each sample user
            for user in users:
                # Build a custom tooltip
                tooltip = f"{user.user_name} ({user.from_app})"
                
                # Build the user icon layout
                user_layout = build_live_session_user_layout(
                    user_info=user,
                    size=32,
                    tooltip=tooltip,
                    on_double_click_fn=on_double_click,
                    on_mouse_click_fn=on_click
                )
```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.live_session_management/data/docs_images/build_user_icons.png
---
align: center
---
```

---

## Display Live Session Users

```python
import omni.ui as ui
import omni.usd
from omni.kit.widget.live_session_management import LiveSessionUserList

# Create a window to display the live session user list
window = ui.Window("Live Session Users", width=400, height=100)
with window.frame:
    with ui.VStack():
        ui.Label("Users in the current live session:", height=20)
        
        # Get the current USD context
        usd_context = omni.usd.get_context()
        
        # Get the base layer identifier (current stage URL)
        base_layer_identifier = usd_context.get_stage_url()
        
        # Create a user list widget with customized appearance
        user_list = LiveSessionUserList(
            usd_context=usd_context, 
            base_layer_identifier=base_layer_identifier,
            follow_user_with_double_click=True,
            icon_size=24,
            spacing=5,
            show_myself=True,
            show_myself_to_leftmost=True
        )

```
### Screenshot:
```{image} ../../../../source/extensions/omni.kit.widget.live_session_management/data/docs_images/display_live_session_users.png
---
align: center
---
```

