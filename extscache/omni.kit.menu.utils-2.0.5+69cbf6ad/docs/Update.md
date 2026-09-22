# Update menus

## Rebuild
- omni.kit.menu.utils.rebuild_menus()
    - This completely rebuilds all the menus

## Refresh
- omni.kit.menu.utils.refresh_menu_items("File") - This refreshes the "File" menu group.
- omni.kit.menu.utils.refresh_menu_items("File/New") - Is now supported to only refresh a single item in the group.
    - Refreshing only sets a flag, which is used when the menu is opening. Then it will update enabled/tick status updated etc.

## Updating menu items

Menus added to "File" group
```python
self._file_menu_list = [
        MenuItemDescription(name="Menu Example 1", onclick_action=("omni.kit.menuext.extension", "menu_example_1")),
        MenuItemDescription(name="Menu Example 2", onclick_action=("omni.kit.menuext.extension", "menu_example_2")),
]

omni.kit.menu.utils.add_menu_items(self._file_menu_list, "File")
```

To add an additional menu item to the previously created menus.

### New method
Requires version 1.5.6 or above

```python
file_menu_list = self._file_menu_list.copy()

file_menu_list.append(
        MenuItemDescription(name="Menu Example 3", onclick_action=("omni.kit.menuext.extension", "menu_example_3"))
        )

omni.kit.menu.utils.replace_menu_items(file_menu_list, self._file_menu_list, "File")
self._file_menu_list = file_menu_list
```

### Old method

```python
omni.kit.menu.utils.remove_menu_items(self._file_menu_list, "File")

self._file_menu_list.append(
        MenuItemDescription(name="Menu Example 3", onclick_action=("omni.kit.menuext.extension", "menu_example_3"))
        )

omni.kit.menu.utils.add_menu_items(file_menu_list, self._file_menu_list, "File")
```
