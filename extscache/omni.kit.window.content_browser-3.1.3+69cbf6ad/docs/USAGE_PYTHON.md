```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Cut and Paste Items
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# Assume we have a file we want to cut and paste
file_path_to_cut = "my_file_to_cut.usd"  # Replace with actual file path

# Perform the cut operation
content_browser_api.cut_selected_items()

# Assume we have a destination path to paste into
destination_path = "my_destination_folder/"  # Replace with actual destination path
content_browser_api.navigate_to(destination_path)
# Perform the paste operation
content_browser_api.paste_items()
```

## Copy and Paste Items
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# Perform the copy operation
content_browser_api.copy_selected_items()

# Assume we have a destination path to paste into
destination_path = "my_destination_folder/"  # Replace with actual destination path
content_browser_api.navigate_to(destination_path)
# Perform the paste operation
content_browser_api.paste_items()
```

## Delete Selected Items
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# Perform the delete operation
content_browser_api.delete_selected_items()
```

## Rename Selected Item
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# popup the rename dialog
content_browser_api.rename_selected_item()
```

## Navigate to a Directory
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# Path to navigate to
path_to_navigate = "/path/to/directory"  # Replace with the actual path

# Navigate to the given path
content_browser_api.navigate_to(path_to_navigate)
```

## Register File Open Handler
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# Define a file open handler function
def my_open_handler(file_path):
    print(f"Opening file: {file_path}")

# Register the file open handler
content_browser_api.add_file_open_handler("my_handler", my_open_handler, file_type=1)  # Corrected with a valid file type constant
```

## Deregister File Open Handler
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# Name of the previously registered handler
handler_name = "my_handler"

# Deregister the file open handler
content_browser_api.delete_file_open_handler(handler_name)
```

## Add Context Menu Item
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# Define a click callback function for the context menu item
def my_context_menu_click(item_name, item_path):
    print(f"Clicked on: {item_name} at {item_path}")

# Define a show callback function for the context menu item
def my_context_menu_show(item_path):
    return True  # Always show this menu item

# Name and glyph of the context menu item
menu_name = "My Context Menu"
menu_glyph = "my_glyph.svg"

# Add the context menu item
content_browser_api.add_checkpoint_menu(menu_name, menu_glyph, my_context_menu_click, my_context_menu_show)
```

## Delete Context Menu Item
```python
from omni.kit.window.content_browser.api import ContentBrowserAPI

# Instantiate the Content Browser API
content_browser_api = ContentBrowserAPI()

# Name of the previously added context menu item
menu_name = "My Context Menu"

# Delete the context menu item
content_browser_api.delete_checkpoint_menu(menu_name)
```