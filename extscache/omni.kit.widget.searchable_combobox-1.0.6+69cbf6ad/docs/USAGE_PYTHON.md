```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Create a Searchable ComboBox

```python
import omni.kit.app
import omni.ui as ui
import asyncio
from omni.kit.widget.searchable_combobox import build_searchable_combo_widget, ComboBoxListDelegate

# Create a searchable combo box widget
def create_searchable_combo_box():
    # Define a callback function to be called when an item is selected
    def on_combo_click_fn(model):
        selected_item = model.get_value_as_string()
        print(f"Selected item: {selected_item}")

    # Define the list of items for the combo box
    item_list = ["Item 1", "Item 2", "Item 3"]

    # Create the searchable combo box with the specified items and callback
    searchable_combo_widget = build_searchable_combo_widget(
        combo_list=item_list,
        combo_index=-1,  # Start with no item selected
        combo_click_fn=on_combo_click_fn,
        widget_height=18,
        default_value="Select an item",  # Placeholder text when no item is selected
        window_id="SearchableComboBoxWindow",
        delegate=ComboBoxListDelegate()  # Use the default delegate for item rendering
    )

    # Return the created widget
    return searchable_combo_widget

# Build UI and display the searchable combo box
async def build_ui():
    self._window = ui.Window("WidgetTest", width=300, height=100)
    with self._window.frame:
        # VBox is used to stack widgets vertically
        with ui.VStack(height=0, spacing=8, style={"margin_width": 2}):
            # Add the searchable combo box to the UI
            searchable_combo_box = create_searchable_combo_box()

# Run the build_ui function to display the UI
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.kit.widget.searchable_combobox", True)
asyncio.run(build_ui())
```
