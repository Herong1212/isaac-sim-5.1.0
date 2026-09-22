```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Register Custom Menu Item Type

```python
from omni.kit.viewport.menubar.render import get_instance, SingleRenderMenuItemBase

# Define a custom menu item type
def custom_single_render_menu_item(*args, **kwargs):
    class CustomSingleRenderMenuItem(SingleRenderMenuItemBase):
        def _option_clicked(self):
            # Do something when clicking the option icon on the right of this menu item
            return

    return CustomSingleRenderMenuItem(*args, **kwargs)

# Get the viewport render menu bar extension instance
extension = get_instance()

# Register the custom menu item type
extension.register_menu_item_type(custom_single_render_menu_item)
```
