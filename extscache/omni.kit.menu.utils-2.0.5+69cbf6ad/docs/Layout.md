# Layouts & Hooks

- Hooks – This is low level function that modifies the menu dictionary directly. Its recommend to use Layout method below
    - For an example of this in action see omni.example.menu_hook
- Layout – This allows the menus to be moved/removed and renamed
    - This is meant for apps to change how menus are presented

## Example layout

```
from omni.kit.menu.utils import MenuLayout

self._menu_layout = [
    MenuLayout.Menu("Window", [
        MenuLayout.Item("Viewport", source="Window/Viewport/Viewport 1"),
        MenuLayout.Item("Playlist", remove=True),
        MenuLayout.Item("Layout", remove=True),
        MenuLayout.Sort(exclude_items=["Extensions"], sort_submenus=True),
    ])
]

omni.kit.menu.utils.add_layout(self._menu_layout)
```

What does this do?
- Menu item "Window" menu is changed;
- Menu item "Window/Viewport/Viewport 1" is moved to "Window/Viewport"
- Menu item "Window/Playlist" is removed
- Menu item "Window/Layout" is removed
- Menu item "Window" menu is then alphabetically sorted except "Extensions" which is not moved

## Another Example Layout

```
from omni.kit.menu.utils import MenuLayout

self._menu_file_layout = [
    MenuLayout.Menu(
        "File",
        [
            MenuLayout.Item("New"),
            MenuLayout.Item("New From Stage Template"),
            MenuLayout.Item("Open"),
            MenuLayout.Item("Open Recent"),
            MenuLayout.Seperator(),
            MenuLayout.Item("Re-open with New Edit Layer"),
            MenuLayout.Seperator(),
            MenuLayout.Item("Share"),
            MenuLayout.Seperator(),
            MenuLayout.Item("Save"),
            MenuLayout.Item("Save As..."),
            MenuLayout.Item("Save With Options"),
            MenuLayout.Item("Save Selected"),
            MenuLayout.Item("Save Flattened As...", remove=True),
            MenuLayout.Seperator(),
            MenuLayout.Item("Collect As..."),
            MenuLayout.Item("Export"),
            MenuLayout.Seperator(),
            MenuLayout.Item("Import"),
            MenuLayout.Item("Add Reference"),
            MenuLayout.Item("Add Payload"),
            MenuLayout.Seperator(),
            MenuLayout.Item("Exit"),
        ]
    )
]

omni.kit.menu.utils.add_layout(self._menu_file_layout)
```

What does this do?
- Menu item "File" menu is changed;
- Menu is now in order listed above
- Menu item "Save Flattened As" is removed

NOTES:

- Any other File menu items not covered in list, like "Export" will appear after layout list
- You can include items that get added only when specific extension is enabled, and missing items will be ignored
- You cannot add menu items, this will have to be done 1st by omni.kit.menu.utils.add_menu_items
