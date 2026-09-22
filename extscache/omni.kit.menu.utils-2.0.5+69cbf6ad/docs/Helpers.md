# Menu Helpers

Requires omni.kit.menu.utils version 1.5.8 or above

## MenuHelperExtension
 - This helper assists with menu creation but minimal window creation help, adds menu_startup(), menu_shutdown() & menu_refresh() functions by MenuHelperExtension subclass. Allowing user to control window open/closing. But does require ui.Workspace.set_show_window_fn to be set as it uses this to open/close/get state for the window

NOTE: MenuHelperExtension only supports one window/menu item and no sub-menus, for these features use MenuHelperExtensionFull (see below for usage examples).

```python
from omni.kit.menu.utils import MenuHelperExtension

class ActionsExtension(omni.ext.IExt, MenuHelperExtension):
    def on_startup(self):
        self._actions_window = None
        ui.Workspace.set_show_window_fn(ActionsExtension.WINDOW_NAME, self.show_window)
        self.menu_startup(ActionsExtension.WINDOW_NAME, ActionsExtension.WINDOW_NAME, ActionsExtension.MENU_GROUP)
        ui.Workspace.show_window(ActionsExtension.WINDOW_NAME, False)

    def on_shutdown(self):
        self.menu_shutdown()
        ui.Workspace.set_show_window_fn(ActionsExtension.WINDOW_NAME, None)
        if self._actions_window:
            self._actions_window.destroy()
            self._actions_window = None

    def show_window(self, visible: bool):
        if visible:
            self._actions_window = ui.Window(ActionsExtension.WINDOW_NAME)
            self._actions_window.set_visibility_changed_fn(self._visiblity_changed_fn)
            self.menu_refresh()
        elif self._actions_window:
            self._actions_window.visible = False

    def _visiblity_changed_fn(self, visible):
        # tell omni.kit.menu.utils that actions window menu open/close state needs updating
        self.menu_refresh()
```

Building window widgets can be done by sub-classing _show function, although it's recommended that this should be done by sub-classing ui.Window and adding a frame build_fn via self.frame.set_build_fn(self._build_ui)
```python
    def _show(self):
        super()._show()

        if self._window:
            with self._window.frame:
                with ui.VStack(height=0, spacing=8):
                    with ui.HStack(height=460):
                        ui.Label("myWindow")
```

## MenuHelperExtensionFull

- This helper assists with menu creation and window creation, handles show/hide and menu state updating. Adds menu_startup(), menu_shutdown() & menu_refresh() functions by MenuHelperExtensionFull subclass, all user has-to provide a function call to create the window.

```python
from omni.kit.menu.utils import MenuHelperExtensionFull

class OscilloscopeWindowExtension(omni.ext.IExt, MenuHelperExtensionFull):
    def on_startup(self):
        self.menu_startup(lambda: ui.Window("Audio Oscilloscope", width=512, height=540), "Audio Oscilloscope", "Oscilloscope", "Window")
        ui.Workspace.show_window("Audio Oscilloscope", True)

    def on_shutdown(self):
        self.menu_shutdown()
```

or

```python
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow

class OscilloscopeWindowExtension(omni.ext.IExt, MenuHelperExtensionFull):
    def on_startup(self):
        self.menu_startup(lambda: MenuHelperWindow("Audio Oscilloscope", width=512, height=540), "Audio Oscilloscope", "Oscilloscope", "Window")
        ui.Workspace.show_window("Audio Oscilloscope", True)

    def on_shutdown(self):
        self.menu_shutdown()
```

## Example using sub-menu

```python
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow

class OscilloscopeWindowExtension(omni.ext.IExt, MenuHelperExtensionFull):
    def on_startup(self):
        self.menu_startup(lambda: MenuHelperWindow("Audio Oscilloscope", width=512, height=540), "Audio Oscilloscope", "Oscilloscope", "Window/Audio")
        ui.Workspace.show_window("Audio Oscilloscope", True)

    def on_shutdown(self):
        self.menu_shutdown()
```

## Example using sub-menus, multiple windows & menus

```python
import omni.ui as ui
import omni.ext
from omni.kit.menu.utils import MenuHelperExtensionFull, MenuHelperWindow

class OscilloscopeMultiWindowExtension(omni.ext.IExt, MenuHelperExtensionFull):
    class MyWindow(MenuHelperWindow):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.frame.set_build_fn(self.__build)

        def __build(self):
            with ui.VStack(height=0):
                with ui.HStack(height=20):
                    ui.Label(f"Hello world from {self.title}")

    def on_startup(self):
        for index in range(0,10):
            self.menu_startup(lambda i=index: OscilloscopeMultiWindowExtension.MyWindow(f"Audio Oscilloscope {i}", width=300, height=150),
                              f"Audio Oscilloscope {index}",
                              f"Audio Oscilloscope {index}",
                              "Window/Audio",
                              verbose=True)

        ui.Workspace.show_window(f"Audio Oscilloscope 0", True)

    def on_shutdown(self):
        self.menu_shutdown()
```
