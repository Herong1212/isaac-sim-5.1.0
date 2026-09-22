# pylint: disable=unused-private-member, relative-beyond-top-level, attribute-defined-outside-init

__all__ = ["HotkeysWindow"]
from typing import Optional
from omni.kit.actions.window import ColumnRegistry, ACTIONS_WINDOW_STYLE
import omni.ui as ui

from ..model.hotkeys_model import HotkeysModel
from ..column_delegate.hotkey_column_delegate import HotkeyColumnDelegate
from ..column_delegate.action_column_delegate import ActionColumnDelegate
from ..column_delegate.window_column_delegate import WindowColumnDelegate
from ..view.hotkeys_view import HotkeysView
from ..view.hotkeys_delegate import HotkeysDelegate
from ..style import HOTKEYS_WINDOW_STYLE
from .search_bar import SearchBar


class HotkeysWindow(ui.Window):
    def __init__(self, title):
        super().__init__(title, width=1000, height=600)

        self._hotkeys_model: Optional[HotkeysModel] = None
        self.__hotkey_column_delegate: Optional[HotkeyColumnDelegate] = None
        self._search_bar: Optional[SearchBar] = None
        self._column_registry: Optional[ColumnRegistry] = None
        self._hotkeys_view: Optional[HotkeysView] = None
        self._actions_delegate: Optional[HotkeysDelegate] = None
        self.__sub_model = None
        style = ACTIONS_WINDOW_STYLE.copy()
        style.update(HOTKEYS_WINDOW_STYLE)
        self.frame.set_style(style)
        self.frame.set_build_fn(self._build_ui)

    def destroy(self):
        self.visible = False
        self.__sub_model = None
        if self.__hotkey_column_delegate:
            self.__hotkey_column_delegate.destroy()
        if self._hotkeys_model:
            self._hotkeys_model.destroy()
            self._hotkeys_model = None

        super().destroy()

    def stop_key_capture(self):
        if self.__hotkey_column_delegate:
            self.__hotkey_column_delegate.stop_key_capture()

    def _build_ui(self):
        self.__hotkey_column_delegate = HotkeyColumnDelegate("Hotkey")

        self._column_registry = ColumnRegistry()
        self._column_registry.register_delegate(WindowColumnDelegate("Window", width=200))
        self._column_registry.register_delegate(ActionColumnDelegate("Action", width=400))
        self._column_registry.register_delegate(self.__hotkey_column_delegate)
        self._hotkeys_model = HotkeysModel(self._column_registry)
        self._actions_delegate = HotkeysDelegate(self._hotkeys_model, self._column_registry)

        self.__sub_model = self._hotkeys_model.subscribe_item_changed_fn(self.__on_model_changed)

        with self.frame:
            with ui.VStack(spacing=4):
                self._search_bar = SearchBar(self._hotkeys_model)
                with ui.ScrollingFrame(
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    style_type_name_override="ActionsView",
                ):
                    self._hotkeys_view = HotkeysView(self._hotkeys_model, self._actions_delegate)

    def __on_model_changed(self, model: HotkeysModel, item: ui.AbstractItem) -> None:
        if self.__hotkey_column_delegate:
            # Here need to clean key capture since the whole tree view is refreshed
            self.__hotkey_column_delegate.stop_key_capture()
