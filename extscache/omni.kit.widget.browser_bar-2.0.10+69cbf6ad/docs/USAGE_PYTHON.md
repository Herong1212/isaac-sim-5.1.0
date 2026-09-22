# Usage Examples

## Initialize BrowserBar and Set Path

```python
from omni.kit.widget.browser_bar import BrowserBar

# Initialize the BrowserBar with custom handlers
browser_bar = BrowserBar(
    visited_history_size=20,
    apply_path_handler=lambda path: print(f"Path applied: {path}"),
    branching_options_handler=lambda path, callback: ["Option1", "Option2"]
)

# Set a path and add it to the history
browser_bar.set_path("/path/to/directory")
```

## Navigate to Previous Path

```python
from omni.kit.widget.browser_bar import BrowserBar

# Initialize the BrowserBar for demonstration
browser_bar = BrowserBar(
    visited_history_size=20,
    apply_path_handler=lambda path: print(f"Path applied: {path}"),
    branching_options_handler=lambda path, callback: ["Option1", "Option2"]
)

# Adding dummy paths to history for demonstration
browser_bar.set_path("path_one")
browser_bar.set_path("path_two")

# Navigate to the previous path in history
browser_bar._on_prev_button_pressed()

# The path field will be updated to the previous path
current_path = browser_bar.path
print(f"Current Path after navigating back: {current_path}")
# Expected outputs
# Path applied: path_one
# Current Path after navigating back: path_one/
```

## Navigate to Next Path

```python
from omni.kit.widget.browser_bar import BrowserBar

# Initialize the BrowserBar for demonstration
browser_bar = BrowserBar(
    visited_history_size=20,
    apply_path_handler=lambda path: print(f"Path applied: {path}"),
    branching_options_handler=lambda path, callback: ["Option1", "Option2"]
)

# Adding dummy paths to history for demonstration
browser_bar.set_path("path_one")
browser_bar.set_path("path_two")
browser_bar._on_prev_button_pressed()  # Navigate back to add history

# Navigate to the next path in history
browser_bar._on_next_button_pressed()

# The path field will be updated to the next path
current_path = browser_bar.path
print(f"Current Path after navigating forward: {current_path}")
# Expected outputs
# Path applied: path_one
# Path applied: path_two
# Current Path after navigating forward: path_two/
```

## Selecting an Item from the Navigation Menu

```python
from omni.kit.widget.browser_bar import BrowserBar

# Initialize the BrowserBar for demonstration
browser_bar = BrowserBar(
    visited_history_size=20,
    apply_path_handler=lambda path: print(f"Path applied: {path}"),
    branching_options_handler=lambda path, callback: ["Option1", "Option2"]
)

# Adding dummy paths to history for demonstration
browser_bar.set_path("path_one")
browser_bar.set_path("path_two")
browser_bar.set_path("path_three")

# Simulate selecting an item from the navigation menu
menu_item_index = 1  # Index of the item to select from the navigation menu
browser_bar._visited_menu.model.selected_index = menu_item_index

# The path field will be updated to the selected path
selected_path = browser_bar.path
print(f"Selected Path from navigation menu: {selected_path}")
# Expected outputs
# Path applied: path_two
# Current Path after navigating back: path_two/
```

## Clean Up BrowserBar Resources

```python
from omni.kit.widget.browser_bar import BrowserBar

# Initialize the BrowserBar for demonstration
browser_bar = BrowserBar(
    visited_history_size=20,
    apply_path_handler=lambda path: print(f"Path applied: {path}"),
    branching_options_handler=lambda path, callback: ["Option1", "Option2"]
)

# Assuming 'browser_bar' has already been initialized
# Destroy the BrowserBar to clean up resources
browser_bar.destroy()
```