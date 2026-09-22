# Examples

## Simplified submenu creation with build_submenu_dict

- This creates a dictionary of lists from the `name` paths in MenuItemDescription, expanding the path and creating (multiple, if required) sub_menu lists. The last item on the path is assumed to be not a sub_menu item.

```python
menu_dict = omni.kit.menu.utils.build_submenu_dict([ MenuItemDescription(name="File/Open"),
                                                     MenuItemDescription(name="Edit/Select/Select by kind/Group"),
                                                     MenuItemDescription(name="Window/Viewport/Viewport 1"),
                                                     MenuItemDescription(name="Help/About"),
                                                    ])
```

### using add_menu_items
```python
for group in menu_dict:
    omni.kit.menu.utils.add_menu_items(menu_dict[group], group)
```

### using remove_menu_items
```python
for group in menu_dict:
    omni.kit.menu.utils.remove_menu_items(menu_dict[group], group)
```

## Another example: Adding a menu with submenu for your extension;

```
from omni.kit.menu.utils import MenuItemDescription

import carb.input

def on_startup(self, ext_id):
    self._file_menu_list = [
        MenuItemDescription(
            name="Sub Menu Example",
            glyph="file.svg",
            sub_menu=[
                MenuItemDescription(
                    name="Menu Example 1",
                    onclick_action=("omni.kit.menuext.extension", "menu_example_1"),
                ),
                MenuItemDescription(
                    name="Menu Example 2",
                    onclick_action=("omni.kit.menuext.extension", "menu_example_2"),
                )],
            )]
    omni.kit.menu.utils.add_menu_items(self._file_menu_list, "File")

def on_shutdown(self):
    omni.kit.menu.utils.remove_menu_items(self._file_menu_list, "File")
````

## Adding to create menu

```
self._create_menu_list = [
    MenuItemDescription(
        name="Scope",
        glyph="menu_scope.svg",
        appear_after="Camera",
        onclick_action=("omni.kit.menu.create", "create_prim_scope"),
    )
]

omni.kit.menu.utils.add_menu_items(self._create_menu_list, "Create")
```

## Menu example with ui.Window subclass

This is an example of how create a window with menu, without any helpers. Full working show/hide and subclass of ui.Window.
NOTE: This uses print only as an example allowing users to see how this works, and should be removed when used in real extension

### Extension class
```python
import carb
import asyncio
import omni.ext
import omni.ui as ui
import omni.kit.menu.utils
from omni.kit.menu.utils import MenuItemDescription
from .window import ExampleWindow

class TestMenu(omni.ext.IExt):
"""The entry point for Example Extension"""
    WINDOW_NAME = "Example"
    MENU_DESCRIPTION = "Example Window"
    MENU_GROUP = "TEST"

    def on_startup(self):
        print(f"[{self.__class__.__name__}] on_startup")
        ui.Workspace.set_show_window_fn(TestMenu.WINDOW_NAME, lambda v: self.show_window(None, v))
        self._menu_entry = [MenuItemDescription(
            name=TestMenu.MENU_DESCRIPTION,
            ticked=True, # menu item is ticked
            ticked_fn=self._is_visible, # gets called when the menu needs to get the state of the ticked menu
            onclick_fn=self._toggle_window
            )]
        omni.kit.menu.utils.add_menu_items(self._menu_entry, name=TestMenu.MENU_GROUP)
        ui.Workspace.show_window(TestMenu.WINDOW_NAME)

    def on_shutdown(self):
        print(f"[{self.__class__.__name__}] on_shutdown")
        omni.kit.menu.utils.remove_menu_items(self._menu_entry, name=TestMenu.MENU_GROUP)
        self._menu_entry = None
        ui.Workspace.set_show_window_fn(TestMenu.WINDOW_NAME, None)
        if self._window:
            self._window.destroy()
            self._window = None

    async def _destroy_window_async(self):
        print(f"[{self.__class__.__name__}] _destroy_window_async")
        # wait one frame, this is due to the one frame defer
        # in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None

    def _is_visible(self) -> bool:
        print(f"[{self.__class__.__name__}] _is_visible returning {False if self._window is None else self._window.visible}")
        return False if self._window is None else self._window.visible

    def _show(self):
        print(f"[{self.__class__.__name__}] _show")
        if self._window is None:
            self.show_window(None, True)

        if self._window and not self._window.visible:
            self.show_window(None, True)

    def _hide(self):
        print(f"[{self.__class__.__name__}] _hide")

        if self._window is not None:
            self.show_window(None, False)

    def _toggle_window(self):
        print(f"[{self.__class__.__name__}] _toggle_window")
        if self._is_visible():
            self._hide()
        else:
            self._show()

    def _visiblity_changed_fn(self, visible):
        print(f"[{self.__class__.__name__}] _visiblity_changed_fn")
        if not visible:
            # Destroy the window, since we are creating new window
            # in show_window
            asyncio.ensure_future(self._destroy_window_async())
            # this only tags test menu to update when menu is opening, so it
            # doesn't matter that is called before window has been destroyed
            omni.kit.menu.utils.refresh_menu_items(TestMenu.MENU_GROUP)

    def show_window(self, menu, value):
        print(f"[{self.__class__.__name__}] show_window menu:{menu} value:{value}")
        if value:
            self._window = ExampleWindow()
            self._window.set_visibility_changed_listener(self._visiblity_changed_fn)
        elif self._window:
            self._window.visible = False
```

### Window class
```python
import omni.ui as ui

class ExampleWindow(ui.Window):
"""The Example window"""

    def __init__(self, usd_context_name: str = ""):
        print(f"[{self.__class__.__name__}] __init__")
        super().__init__("Example Window", width=300, height=300)
        self._visiblity_changed_listener = None
        self.set_visibility_changed_fn(self._visibility_changed_fn)

def destroy(self):
    """
    Called by extension before destroying this object. It doesn't happen automatically.
    Without this hot reloading doesn't work.
    """
    print(f"[{self.__class__.__name__}] destroy")
    self._visiblity_changed_listener = None
    super().destroy()

    def _visibility_changed_fn(self, visible):
        print(f"[{self.__class__.__name__}] _visibility_changed_fn visible:{visible}")
        if self._visiblity_changed_listener:
            self._visiblity_changed_listener(visible)

    def set_visibility_changed_listener(self, listener):
        print(f"[{self.__class__.__name__}] set_visibility_changed_listener listener:{listener}")
        self._visiblity_changed_listener = listener
```

### Radio Buttons
```python
from omni.kit.menu.utils import MenuItemDescription

import carb.input
import omni.kit.actions.core

def on_startup(self, ext_id):
    self._radio_one_value = 1
    self._radio_two_value = 0

    # register actions
    def radio_one_func(value):
        print(f">> radio button one clicked {value}")
        self._radio_one_value = value

    def radio_two_func(value):
        print(f">> radio button two clicked {value}")
        self._radio_two_value = value

    action_registry = omni.kit.actions.core.get_action_registry()
    for index in range(10):
        action_registry.register_action(
            "test.radio.buttons", f"clicked_one_{index}", lambda v=index: radio_one_func(v)
        )
        action_registry.register_action(
            "test.radio.buttons", f"clicked_two_{index}", lambda v=index: radio_two_func(v)
        )

    # create menu
    self.__radiomenu_list = [
        MenuItemDescription(
            name=f"Radio One {index}",
            radio_group="test1",
            onclick_action=("test.radio.buttons", f"clicked_one_{index}"),
            ticked_value=index == 1,
        )
        for index in range(10)
    ]
    self.__radiomenu_list += [MenuItemDescription()]
    self.__radiomenu_list += [
        MenuItemDescription(
            name=f"Radio Two {index}",
            radio_group="test2",
            onclick_action=("test.radio.buttons", f"clicked_two_{index}"),
            ticked_value=index == 0,
        )
        for index in range(10)
    ]
    omni.kit.menu.utils.add_menu_items(self.__radiomenu_list, "Edit", 99)

def on_shutdown(self):
    omni.kit.menu.utils.remove_menu_items(self.__radiomenu_list, "Edit", 99)

    # free actions
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension("test.radio.buttons")

```
