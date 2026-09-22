from __future__ import annotations

import logging

from typing import List, Union, Optional

import carb
from omni import ui
from omni.ui_query import OmniUIQuery

from carb.input import KeyboardInput

from .input import emulate_mouse_move_and_click, emulate_char_press, emulate_keyboard_press, emulate_keyboard, emulate_mouse_drag_and_drop, emulate_mouse_move
from .common import wait_n_updates_internal
from .vec2 import Vec2

logger = logging.getLogger(__name__)

class WindowStub():
    """stub window class for use with WidgetRef & """
    def undock(_):
        pass

    def focus(_):
        pass

window_stub = WindowStub()

class WidgetRef:
    """Reference to `omni.ui.Widget` and a path it was found with."""

    def __init__(self, widget: ui.Widget, path: str, window: ui.Window = None):
        self._widget = widget
        self._path = path
        self._window = window if window else ui.Workspace.get_window(path.split("//")[0])

    @property
    def widget(self) -> ui.Widget:
        return self._widget

    @property
    def model(self):
        return self._widget.model

    @property
    def window(self) -> ui.Window:
        return self._window

    @property
    def path(self) -> str:
        """Path this widget was found with."""
        return self._path

    @property
    def realpath(self) -> str:
        """Actual unique path to this widget from the window."""
        return OmniUIQuery.get_widget_path(self.window, self.widget)

    def __str__(self) -> str:
        return f"WidgetRef({self.widget}, {self.path})"

    @property
    def position(self) -> Vec2:
        """Screen position of widget's top left corner."""
        return Vec2(self._widget.screen_position_x, self._widget.screen_position_y)

    @property
    def size(self) -> Vec2:
        """Computed size of the widget."""
        return Vec2(self._widget.computed_content_width, self._widget.computed_content_height)

    @property
    def center(self) -> Vec2:
        """Center of the widget."""
        return self.position + (self.size / 2)

    def offset(self, *kwargs) -> Vec2:
        if len(kwargs) == 2:
            return self.position + Vec2(kwargs[0], kwargs[1])
        if len(kwargs) == 1 and isinstance(kwargs[0], Vec2):
            return self.position + kwargs[0]
        return None

    async def _wait(self, update_count=2):
        await wait_n_updates_internal(update_count)

    async def focus(self):
        """Focus on a window this widget belongs to."""
        self.window.focus()
        await self._wait()

    async def undock(self):
        """Undock a window this widget belongs to."""
        self.window.undock()
        await self._wait()

    async def bring_to_front(self):
        """Bring window this widget belongs to on top. Currently this is implemented as undock() + focus()."""
        await self.undock()
        await self.focus()

    async def click(self, pos: Vec2 = None, right_click=False, double=False, human_delay_speed: int = 2):
        """Emulate mouse click on the widget."""
        logger.info(f"click on {str(self)} (right_click: {right_click}, double: {double})")
        await self.bring_to_front()
        if not pos:
            pos = self.center
        await emulate_mouse_move_and_click(
            pos, right_click=right_click, double=double, human_delay_speed=human_delay_speed
        )

    async def right_click(self, pos=None, human_delay_speed: int = 2):
        await self.click(pos=pos, right_click=True, human_delay_speed=human_delay_speed)

    async def double_click(self, pos=None, human_delay_speed: int = 2):
        await self.click(pos, double=True, human_delay_speed=human_delay_speed)

    async def input(self, text: str, end_key = KeyboardInput.ENTER, human_delay_speed: int = 2, clear_before_input: bool = False):
        """Emulate keyboard input of characters (text) into the widget.

        It is a helper function for the following sequence:

        1. Double click on the widget
        2. Input characters
        3. Press enter
        """
        if type(self.widget) == ui.FloatSlider or type(self.widget) == ui.FloatDrag or type(self.widget) == ui.IntSlider:
            from carb.input import MouseEventType, KeyboardEventType

            await self.click(human_delay_speed=human_delay_speed)
            await emulate_keyboard(KeyboardEventType.KEY_PRESS, KeyboardInput.LEFT_CONTROL, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL)
            # await wait_n_updates_internal()
            await self.click(human_delay_speed=human_delay_speed)
            await emulate_keyboard(KeyboardEventType.KEY_RELEASE, KeyboardInput.LEFT_CONTROL, 0)
            await self._wait()
        elif type(self.widget) == ui.IntDrag:
            await self._wait(20)
            await self.double_click(human_delay_speed=human_delay_speed)
        else:
            if clear_before_input:
                self.widget.model.set_value("")
            await self.double_click(human_delay_speed=human_delay_speed)

        await self._wait(human_delay_speed)
        await emulate_char_press(text)
        await emulate_keyboard_press(end_key)

    async def drag_and_drop(self, drop_target: Vec2, human_delay_speed: int = 4):
        """Drag/drop for widget.centre to `drop_target`"""
        await emulate_mouse_drag_and_drop(self.center, drop_target, human_delay_speed=human_delay_speed)

    def find(self, path: str) -> WidgetRef:
        """Find omni.ui Widget or Window by search query starting from this widget.

        .. code-block:: python

            stage_window = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
            label = stage_window.find("**/Label[*].text=='hello'")
            await label.right_click()


        Returns:
            Found Widget or Window wrapped into `WidgetRef` object.
        """
        return _find(path, self)

    def find_all(self, path: str) -> List[WidgetRef]:
        """Find all omni.ui Widget or Window by search query starting from this widget.

        .. code-block:: python

            stage_window = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
            labels = stage_window.find_all("**/Label[*]")
            for label in labels:
                await label.right_click()


        Returns:
            List of found Widget or Window wrapped into `WidgetRef` objects.
        """
        return _find_all(path, self)

    def find_first(self, path: str) -> WidgetRef:
        """Find the first omni.ui Widget or Window by search query starting from this widget.

        .. code-block:: python

            stage_window = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
            label = stage_window.find_first("**/Label[*]")
            await label.right_click()


        Returns:
            Widget or Window wrapped into `WidgetRef` object.
        """
        return _find_first(path, self)


class WindowRef(WidgetRef):
    """Reference to `omni.ui.WindowHandle`"""

    def __init__(self, widget: ui.WindowHandle, path: str):
        super().__init__(widget, path, window=widget)

    @property
    def position(self) -> Vec2:
        return Vec2(self._widget.position_x, self._widget.position_y)

    @property
    def size(self) -> Vec2:
        return Vec2(self._widget.width, self._widget.height)

def _build_window_ref(path: str) -> Optional[WindowRef]:
    window = ui.Workspace.get_window(path)
    if not window or window.visible is None:
        carb.log_warn(f"Can't find window at path: {path}")
        return None
    return WindowRef(window, path)

def _build_widget_ref(widget, path, root_widget) -> Union[WindowRef, WidgetRef]:
    fullpath = path
    window = None
    if root_widget:
        sep = "//" if isinstance(root_widget.widget, ui.WindowHandle) else "/"
        fullpath = f"{root_widget.path}{sep}{path}"
        window = root_widget.window

    if isinstance(widget, ui.WindowHandle):
        return WindowRef(widget, fullpath, window=window)
    else:
        return WidgetRef(widget, fullpath, window=window)

def _find_all(path: str, root_widget: WidgetRef = None) -> List[WidgetRef]:
    if "/" not in path and not root_widget:
        window_ref = _build_window_ref(path)
        return [window_ref] if window_ref else None

    root_widgets = [root_widget.widget] if root_widget else []
    widgets = OmniUIQuery.find_widgets(path, root_widgets=root_widgets)
    return [_build_widget_ref(widget, path, root_widget) for widget in widgets]

def _find_first(path: str, root_widget: WidgetRef = None) -> WidgetRef:
    if "/" not in path and not root_widget:
        return _build_window_ref(path)

    root_widgets = [root_widget.widget] if root_widget else []
    widget = OmniUIQuery.find_first_widget(path, root_widgets=root_widgets)

    return _build_widget_ref(widget, path, root_widget) if widget else None

def _find(path: str, root_widget: WidgetRef = None) -> WidgetRef:
    widgets = _find_all(path, root_widget)
    if not widgets or len(widgets) == 0:
        carb.log_warn(f"Can't find any widgets at path: {path}")
        return None

    MAX_OUTPUT = 10
    if len(widgets) > 1:
        carb.log_warn(f"Found {len(widgets)} widgets at path: {path} instead of one.")
        for i in range(len(widgets)):
            carb.log_warn(
                "[{0}] {1} name: '{2}', realpath: '{3}'".format(
                    i, widgets[i], widgets[i].widget.name, widgets[i].realpath
                )
            )
            if i > MAX_OUTPUT:
                carb.log_warn("...")
                break
        return None
    return widgets[0]


class MenuRef(WidgetRef):
    """Reference to `omni.ui.Menu`"""

    def __init__(self, widget: ui.Menu, path: str):
        super().__init__(widget, path, window=window_stub)

    @staticmethod
    async def menu_click(path, separator: str = "/", human_delay_speed: int = 4, show: bool = True):
        import omni.appwindow

        menu_widget = get_menubar()
        app_win = omni.appwindow.get_default_app_window()
        await emulate_mouse_move(Vec2(app_win.get_size().x-10, app_win.get_size().y-10))
        await wait_n_updates_internal(human_delay_speed)

        for idx, menu_name in enumerate(path.split(separator)):
            menu_widget = menu_widget.find_menu(menu_name)
            menu_pos = menu_widget.center
            if idx == 0:
                menu_pos += Vec2(10 * ui.Workspace.get_dpi_scale(), 5 * ui.Workspace.get_dpi_scale())
            await emulate_mouse_move(menu_pos)
            await wait_n_updates_internal(human_delay_speed)
            if isinstance(menu_widget.widget, ui.Menu):
                if menu_widget.widget.shown != show:
                    await menu_widget.click()
                elif menu_widget.widget.has_triggered_fn():
                    menu_widget.widget.call_triggered_fn()

                await wait_n_updates_internal(human_delay_speed)
                if menu_widget.widget.shown != show:
                    carb.log_error(f"ui.Menu item failed to become {'show' if show else 'hide'} for {menu_name} in {path}")
            elif show:
                await menu_widget.click()
                await wait_n_updates_internal(human_delay_speed)

        await wait_n_updates_internal(human_delay_speed)

    @property
    def center(self) -> Vec2:
        # Menu/MenuItem doesn't have width/height
        if isinstance(self._widget, ui.Menu):
            return self.position + Vec2(10, 5) * ui.Workspace.get_dpi_scale()
        return self.position + Vec2(25, 5) * ui.Workspace.get_dpi_scale()

    def find_menu(self, path: str, ignore_case: bool=False, contains_path: bool=False) -> MenuRef:
        for widget in self.find_all("**/"):
            if isinstance(widget.widget, ui.Menu) or isinstance(widget.widget, ui.MenuItem):
                menu_path = widget.widget.text.encode('ascii', 'ignore').decode().strip()
                if menu_path == path or \
                    (ignore_case and menu_path.lower() == path.lower()) or \
                    (contains_path and path in menu_path) or \
                    (ignore_case and contains_path and path.lower() in menu_path.lower()
                 ):
                    return MenuRef(widget=widget.widget, path=widget.path)
        return None


def find(path: str) -> WidgetRef:
    """Find omni.ui Widget or Window by search query. `omni.ui_query` is used under the hood.

    Returned object can be used to get actual found item or/and do UI test operations on it.

    .. code-block:: python

        stage_window = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        await stage_window.right_click()

        viewport = ui_test.find("Viewport")
        center = viewport.center
        print(center)


    Returns:
        Found Widget or Window wrapped into `WidgetRef` object.
    """
    return _find(path)


def find_all(path: str) -> List[WidgetRef]:
    """Find all omni.ui Widget or Window by search query.

    .. code-block:: python

        buttons = ui_test.find_all("Stage//Frame/**/Button[*]")
        for button in buttons:
            await button.click()


    Returns:
        List of found Widget or Window wrapped into `WidgetRef` objects.
    """
    return _find_all(path)

def find_first(path: str) -> List[WidgetRef]:
    """Find first omni.ui Widget or Window by search query.

    .. code-block:: python

        button = ui_test.find_first("Stage//Frame/**/Button[*]")
        await button.click()


    Returns:
        Widget or Window wrapped into `WidgetRef` objects.
    """
    return _find_first(path)


def get_menubar() -> MenuRef:
    from omni.kit.mainwindow import get_main_window

    window = get_main_window()
    return MenuRef(widget=window._ui_main_window.main_menu_bar, path="MainWindow//Frame/MenuBar")


async def menu_click(path, separator: str = "/", human_delay_speed: int = 2, show: bool = True) -> None:
    await MenuRef.menu_click(path, separator=separator, human_delay_speed=human_delay_speed, show=show)
