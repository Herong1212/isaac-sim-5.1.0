# Python Usage Examples

## Use the extension instance interface 
```python
from omni.kit.widget.layers import get_instance()

layer_instance = get_instance()

# set current focused layer
layer_instance.set_current_focused_layer_item(some_layer_path)

def on_layer_selection_changed(self, item):
    layer_item = layer_instance.get_current_focused_layer_item()
    if layer_item:
        # do something on layer selection changed
        pass

# subscribe layer item select change in layer widget 
layer_instance.add_layer_selection_changed_fn(on_layer_selection_changed)

# remve the subscribe function 
layer_instance.remove_layer_selection_changed_fn(on_layer_selection_changed)
```

## Add custom layers widget context menu
```python
import omni.kit.widget.layers as layers
menu_subscription = layers.ContextMenu.add_menu(
    [
        {"name": ""},
        {
            "name": "Edit...",
            "glyph": "menu_rename.svg",
            "show_fn": [
                layers.ContextMenu.is_layer_item,
                layers.ContextMenu.is_not_missing_layer,
                layers.ContextMenu.is_layer_writable,
                layers.ContextMenu.is_layer_not_locked_by_other,
                layers.ContextMenu.is_layer_and_parent_unmuted,
                LayersMenu.is_not_editing,
            ],
            "onclick_fn": LayersMenu.start_editing,
        },
    ])
```


