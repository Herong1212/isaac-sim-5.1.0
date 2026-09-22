"""UI Toolkit

Starting with the release 2020.1, Omniverse Kit UI Toolkit has been replaced by the alternative UI toolkit :mod:`Omni::UI <omni.ui>`. Currently the Omniverse Kit UI Toolkit is deprecated.

Omniverse Kit UI Toolkit is retained mode UI library which enables extending and changing Omniverse Kit look and feel in any direction.

It contains fundamental building primitives, like windows, containers, layouts, widgets. As well as additional API (built on top of it) to create widgets for USD attributes and omni.kit settings.

Typical example to create a window with a drag slider widget:

.. code-block::

    import omni.kit.ui
    window = omni.kit.ui.Window('My Window')
    d = omni.kit.ui.DragDouble()
    d.width = omni.kit.ui.Percent(30)
    window.layout.add_child(d)

All objects are python-friendly reference counted object. You don't need to explicitly release or control lifetime. In the code example above `window` will be kept alive until `window` is released.

Core:
------

* :class:`.Window`
* :class:`.Popup`
* :class:`.Container`
* :class:`.Value`
* :class:`.Length`
* :class:`.UnitType`
* :class:`.Widget`

Widgets:
--------

* :class:`.Label`
* :class:`.Button`
* :class:`.Spacer`
* :class:`.CheckBox`
* :class:`.ComboBox`
* :class:`.ComboBoxInt`
* :class:`.ListBox`
* :class:`.SliderInt`
* :class:`.SliderDouble`
* :class:`.DragInt`
* :class:`.DragInt2`
* :class:`.DragDouble`
* :class:`.DragDouble2`
* :class:`.DragDouble3`
* :class:`.DragDouble4`
* :class:`.Transform`
* :class:`.FieldInt`
* :class:`.FieldDouble`
* :class:`.TextBox`
* :class:`.ColorRgb`
* :class:`.ColorRgba`
* :class:`.Image`

Containers:
-----------

* :class:`.ColumnLayout`
* :class:`.RowLayout`
* :class:`.RowColumnLayout`
* :class:`.CollapsingFrame`
* :class:`.ScrollingFrame`




"""

# This module depends on other modules. VSCode python language server scrapes modules in an isolated environment
# (ignoring PYTHONPATH set). import fails and for that we have separate code path to explicitly add it's folder to
# sys.path and import again.
try:
    import weakref
    import carb
    import carb.dictionary
    import omni.ui
except:
    import os, sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..")))
    import weakref
    import carb
    import carb.dictionary
    import omni.ui

from ._ui import *
from .editor_menu import EditorMenu

legacy_mode = False


def add_item_attached(self: _ui.Menu, *args, **kwargs):
    subscription = self.add_item(*args, **kwargs)
    self.user_data.setdefault("items", []).append(subscription)
    return subscription


def create_window_hook(self, title:str, *args, **kwargs):
    menu_path = None
    add_to_menu = True
    if "menu_path" in kwargs:
        menu_path = kwargs["menu_path"]
        kwargs["menu_path"] = ""
    if "add_to_menu" in kwargs:
        add_to_menu = kwargs["add_to_menu"]
    kwargs["add_to_menu"] = False

    Window.create_window_hook(self, title, *args, **kwargs)

    if add_to_menu and not menu_path:
        menu_path = f"Window/{title}"

    if menu_path:
        def on_window_click(visible, weak_window):
            window = weak_window()
            if window:
                if visible:
                    window.show()
                else:
                    window.hide()
                # This is a pretty terrible hack to fix OM-123471 but we can't rely
                # on `omni.kit.ui.Window`'s show/hide methods alone, as they can be
                # out of sync from the incoming `visible` state of the menu.
                # For reasons I don't entirely understand, `ui.Workspace.show_window`
                # is able to work around this issue and get the two back in sync.
                omni.ui.Workspace.show_window(window.title(), visible)

        def on_window_showhide(visible, weak_window):
            window = weak_window()
            if window:
                Menu.static_class.set_value(menu_path, visible)

        EditorMenu.window_handler[title] = omni.kit.ui.get_editor_menu().add_item(menu_path, on_click=lambda m, v, w=weakref.ref(self): on_window_click(v, w), toggle=True, value=self.is_visible())
        self.set_visibility_changed_fn(lambda v, w=weakref.ref(self): on_window_showhide(v, w))


def get_editor_menu():
    if legacy_mode:
        return get_editor_menu_legacy()
    elif Menu.static_class == None:
        Menu.static_class = EditorMenu()

    return Menu.static_class


def using_legacy_mode():
    carb.log_warn(f"using_legacy_mode: function is deprecated as it always return False")
    return legacy_mode


def init_ui():
    import carb.settings
    import carb

    # Avoid calling code below at documentation building time with try/catch
    try:
        settings = carb.settings.get_settings()
    except RuntimeError:
        return

    if not legacy_mode:
        if hasattr(Window, "create_window_hook"):
            carb.log_warn(f"init_ui window hook already initialized")
        else:
            # hook into omni.kit.ui.window to override menu creation
            Window.create_window_hook = Window.__init__
            Window.__init__ = create_window_hook


Menu.static_class = None
Menu.add_item_attached = add_item_attached
Menu.get_editor_menu = get_editor_menu
Menu.using_legacy_mode = using_legacy_mode

init_ui()
