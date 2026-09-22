```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

omni.kit.menu.utils allows users to add/remove/update menus for the top bar of the window.

## Adding a menu for your extension

```
from omni.kit.menu.utils import MenuItemDescription

import carb.input

def on_startup(self, ext_id):
    self._file_menu_list = [
        MenuItemDescription(
            name="Menu Example",
            glyph="file.svg",
            onclick_action=("omni.kit.menuext.extension", "menu_example"),
            hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.T),
        )]

    omni.kit.menu.utils.add_menu_items(self._file_menu_list, "File")

def on_shutdown(self):
    omni.kit.menu.utils.remove_menu_items(self._file_menu_list, "File")
```

What does this do?
- Adds a menu item "Menu Example" in "File" menu using icon file.svg and when clicked executes action "omni.kit.menuext.extension" / "menu_example".

NOTES:
- You need to keep a copy of your file menu list to prevent python from garbage collecting it.
- Although kit uses fastexit and on_shutdown is never called, a user can still disable your extension and on_shutdown will be called, so you need to cleanup your menus otherwise you will get leaks and menu will still be shown.

## MenuItemDescription parameters

### glyphs
- Name/path of an icon/image. Can either be a full path to extension or just an "cog.svg" which are loaded from kit/_build/resources/glyphs

### onclick_action / unclick_action
- tuple containing extension & action name

### onclick/unclick
- As menus use carb.input for hotkeys and carb.input also supports joypad buttons, joypad buttons can be bound to menus
- onclick is called when menu item selected / input button is pressed
- unclick is called when input button is released
    - This can be used for long-press processing

### appear_after
- Example: appear_after=["Mesh", MenuItemOrder.FIRST]
    - This can be used to have your menu item appear after other menu items, list is used for multiple items to try.
    - EG "Mesh" would only exist if omni.kit.primitive.mesh is enabled

### sub_menu
- Used for submenu, like "File" "Recent" and is a list of MenuItemDescription’s

### name/name_fn
- Value "name" is  menu item name
- Function "name_fn" is function that returns string used for name

### show_fn
- Function that returns True/False, if item is False, then menu item is not shown (hidden)

### enabled/enable_fn
- Value enabled is True/False
- Function enabled_fn is functions that returns True/False
    - When False the menu item is greyed out but still shown

### ticked/ticked_value/ticked_fn
- Value ticked. When True Menu item is tickable
- Value ticked_value True/False. When True white tick is shown otherwise greyed tick is shown
    - Function ticked_fn function returns True/False. When True white tick is shown otherwise greyed tick is shown

### radio_group (requires omni.kit.menu.utils version 1.6.1 or above)
- Changes the ticked items into radio buttons. When a radio group item is clicked all ticked items with the same group will have ticks set to false.
- NOTE: This doesn't write back to variables and only clears the menu item values. So its upto the author to handle clearing/setting variables using the onclick_action callback.

### user
- dictionary
- Can be used to pass information into delegate functions or build_item function or onclick function etc.
NOTE: menus also add information to this dictionary

## Delegates
You can have a delegate associated with your menu

Currently supported functions are:
- build_item(item: ui.Menu)
    - created ui for menu items, be careful overriding this function as IconMenuDelegate has a custom build_item
- get_elided_length(menu_name: str)
    - returns max string length & any menu text over this length will be elided
- get_menu_alignment() returns MenuAlignment.LEFT or MenuAlignment.RIGHT
    - used by "Live" and "Cache" button on top right. These are right aligned menu items with custom build_item function
- update_menu_item(menu_item: Union[ui.Menu, ui.MenuItem], menu_refresh: bool)
    - allows modification of ui.Menu/ui.MenuItem. `menu_refresh` indicates its updating state during ui triggered_fn

Example
```python
from omni.kit.menu.utils import MenuItemDescription, IconMenuDelegate

class FileMenuDelegate(IconMenuDelegate):
    def build_item(item: ui.Menu):
        super().build_item(item)
        ui.Label("<<>>")

    def get_menu_alignment(self):
        return MenuAlignment.RIGHT

    def update_menu_item(self, menu_item: Union[ui.Menu, ui.MenuItem], menu_refresh: bool):
        if isinstance(menu_item, ui.MenuItem):
            menu_item.visible = False

    def get_elided_length(self, menu_name):
        if menu_name == "Open Recent":
            return 160
        return 0


self._file_delegate = FileMenuDelegate()
self._file_menu_list = [
    MenuItemDescription(
        name="Menu Example",
        glyph="file.svg",
        onclick_action=("omni.kit.menuext.extension", "menu_example"),
        hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.T),
    )]

omni.kit.menu.utils.add_menu_items(self._file_menu_list, "File", -10, delegate=self._file_delegate)
