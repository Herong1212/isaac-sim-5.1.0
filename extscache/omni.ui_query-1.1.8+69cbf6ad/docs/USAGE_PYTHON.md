# Usage Examples

## Create UI and Find Widgets by Query Path

```python
import omni.ui as ui
from omni.ui_query import OmniUIQuery

# Create a sample window with widgets
window = ui.Window("Sample Window", width=300, height=200)
with window.frame:
    with ui.VStack():
        label = ui.Label("Hello World")
        with ui.HStack():
            button1 = ui.Button("Button 1")
            button2 = ui.Button("Button 2", name="action_button")
            
# Find a specific widget by exact path
found_button = OmniUIQuery.find_widget("Sample Window//Frame/VStack[0]/HStack[0]/Button[0]")
print(f"Found button1: {found_button == button1}")

# Find multiple widgets matching a pattern
all_buttons = OmniUIQuery.find_widgets("Sample Window//Frame/**/Button[*]")
print(f"Found {len(all_buttons)} buttons")

# Find the first widget matching a pattern
first_button = OmniUIQuery.find_first_widget("Sample Window//Frame/**/Button[*]")
print(f"First button found: {first_button == button1}")
```

---

## Get Widget Paths Within Window

```python
import omni.ui as ui
from omni.ui_query import OmniUIQuery

# Create a sample window with widgets
window = ui.Window("Path Example", width=300, height=200)
with window.frame:
    with ui.VStack():
        label = ui.Label("Hello World")
        with ui.HStack():
            button1 = ui.Button("Button 1")
            button2 = ui.Button("Button 2")

# Get path for a specific widget
button_path = OmniUIQuery.get_widget_path(window, button1)
print(f"Path to button1: {button_path}")

# Get paths for all child widgets of a parent widget
vstack = OmniUIQuery.find_widget("Path Example//Frame/VStack[0]")
if vstack:
    children_paths = OmniUIQuery.get_widget_children_with_path(vstack, "Path Example//Frame/VStack[0]")
    print("Children paths:")
    for widget, path in children_paths.items():
        print(f"- {path}")

# Get all widget paths in a window with custom attribute display
def get_widget_postfix(widget):
    try:
        text = getattr(widget, "text")
        return f".text=='{text}'"
    except:
        return ""

all_paths = OmniUIQuery.get_window_widget_paths(window, get_widget_postfix)
print("All widget paths in window:")
for path in all_paths:
    print(f"- {path}")
```

---

## Use Advanced Wildcards and Predicates for Querying

```python
import omni.ui as ui
from omni.ui_query import OmniUIQuery

# Create a more complex UI
window = ui.Window("Advanced Queries", width=300, height=200)
with window.frame:
    with ui.VStack():
        ui.Label("Parent Container")
        with ui.HStack():
            with ui.VStack():
                ui.Button("Action 1", name="action_btn")
                ui.Button("Action 2")
            with ui.VStack():
                ui.Label("Settings")
                ui.StringField(name="settings_field")

# Find all buttons using wildcards and recursion
all_buttons = OmniUIQuery.find_widgets("Advanced Queries//Frame/**/Button[*]")
print(f"Found {len(all_buttons)} buttons with wildcard query")

# Find elements with specific attributes using predicates
named_button = OmniUIQuery.find_widgets("Advanced Queries//Frame/**/Button[*].name=='action_btn'")
if named_button:
    print(f"Found button with name 'action_btn'")

# Find UI elements with specific text value
buttons_with_text = OmniUIQuery.find_widgets("Advanced Queries//Frame/**/Button[*].text=='Action 1'")
if buttons_with_text:
    print(f"Found button with text 'Action 1'")

# Find all direct children of a specific container
direct_children = OmniUIQuery.find_widgets("Advanced Queries//Frame/VStack[0]/HStack[0]/*")
print(f"Found {len(direct_children)} direct children in the HStack")
```

---

## Query Widgets Within Nested Frames

```python
import omni.ui as ui
from omni.ui_query import OmniUIQuery

# Create a window with nested frames
window = ui.Window("Frame Example", width=300, height=200)
with window.frame:
    with ui.HStack():
        frame1 = ui.Frame(name="LeftPanel")
        frame2 = ui.Frame(name="RightPanel")
        
        with frame1:
            ui.Label("Left Panel")
            ui.Button("Left Button")
            
        with frame2:
            ui.Label("Right Panel")
            ui.Button("Right Button")

# Find frames by name attribute
left_panel = OmniUIQuery.find_widgets("Frame Example//Frame/HStack[0]/Frame[*].name=='LeftPanel'")
if left_panel:
    print("Found left panel frame")

# Find widgets within specific frames
right_button = OmniUIQuery.find_widget("Frame Example//Frame/HStack[0]/Frame[1]/Button[0]")
print("Found right button" if right_button else "Right button not found")

# Find all buttons across all frames
all_frame_buttons = OmniUIQuery.find_widgets("Frame Example//Frame/HStack[0]/Frame[*]/Button[*]")
print(f"Found {len(all_frame_buttons)} buttons in frames")
```
