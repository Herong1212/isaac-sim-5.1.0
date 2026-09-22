# Usage Examples

## Use a Read-Only Dictionary

```python
from omni.kit.menu.core import DictReadOnly

# Create a read-only dictionary
data = {
    "Window": {
        "background_color": 0xFF000000,
        "border_color": 0x0,
        "border_radius": 0
    }
}
read_only_dict = DictReadOnly(data)

# Attempting to modify the dictionary will raise an exception
try:
    read_only_dict["new_key"] = "new_value"
except Exception as e:
    print(f"Modification attempt failed: {e}")

# Accessing the dictionary elements
print(read_only_dict["Window"]["background_color"])

# Copy the read-only dictionary
new_dict = read_only_dict.copy()
print(new_dict)

# Perform a union operation
merged_dict = read_only_dict | {"additional_key": "additional_value"}
print(merged_dict)
```
---


## Handle Menu Activation Events

```python
from omni.kit.menu.core import MenuEventType

# Example usage of MenuEventType
def handle_menu_event(event_type):
    if event_type == MenuEventType.ACTIVATE:
        print("Menu item activated!")

# Simulate menu activation event
handle_menu_event(MenuEventType.ACTIVATE)
```
---


## Create and Show a Custom Menu

```python
import carb
import omni.ui as ui
import omni.kit.app
from omni.kit.menu.core import uiMenu, uiMenuItem, IconMenuBaseDelegate

# Ensure the required extension is enabled
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.kit.menu.core", True)

# Create a custom menu delegate
class CustomMenuDelegate(IconMenuBaseDelegate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_settings("omni.kit.menu.utils")

# Instantiate the custom delegate
custom_delegate = CustomMenuDelegate()

# Create the root menu
menu_root = uiMenu(
    "Custom Menu",
    enabled=True,
    delegate=custom_delegate,
    tearable=False,
    glyph="menu_prim.svg",
    menu_checkable=True,
    menu_hotkey_text="Hotkey Text",
    submenu=False,
)

# Add menu items to the root menu
# Created items need retained to prevent auto garbage collection
holder = []
icon_path1 = carb.tokens.get_tokens_interface().resolve("${omni.ui}/data/icons/RenderCheckMark.svg")
icon_path2 = carb.tokens.get_tokens_interface().resolve("${kit}/resources/glyphs/cog.svg")
icon_path3 = carb.tokens.get_tokens_interface().resolve("${kit}/resources/icons/lights/distant_light.png")
with menu_root:
    holder.append(uiMenuItem("Menu Item 1", enabled=True, glyph="cog.svg", menu_checkable=True))
    holder.append(uiMenuItem("Menu Item 2", enabled=True, glyph=icon_path1, menu_hotkey_text="Ctrl+M"))
    holder.append(uiMenuItem("Menu Item 3", enabled=True, glyph=icon_path2))
    holder.append(uiMenuItem("Menu Item 4", enabled=True, glyph=icon_path3))

# Show the menu at a specific position
menu_root.show_at(100, 100)
```
