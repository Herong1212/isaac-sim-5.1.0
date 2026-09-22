# pylint: disable=relative-beyond-top-level

__all__ = ["WindowsPicker"]
from typing import List, Callable, Optional
import omni.ui as ui
from omni.kit.actions.window import ACTIONS_WINDOW_STYLE
from ..model.windows_model import WindowsModel, WindowItem
from ..style import WINDOW_PICK_STYLE


class WindowsPicker(ui.Window):
    def __init__(
        self,
        width=0,
        height=600,
        on_selected_fn: Callable[[str], None] = None,
        expand_all: bool = True,
        focus_search: bool = True,
    ):
        super().__init__("###WINDOW_PICKER", width=width, height=height)
        self.flags = ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_POPUP
        self.__on_selected_fn = on_selected_fn
        self.__expand_all = expand_all
        self.__focus_search = focus_search
        self._actions_view: Optional[ui.TreeView] = None
        self._search_field = None
        self._windows_model: Optional[WindowsModel] = None

        style = ACTIONS_WINDOW_STYLE.copy()
        style.update(WINDOW_PICK_STYLE)
        self.frame.set_style(style)
        self.frame.set_build_fn(self._build_ui)

    def _build_ui(self):
        self._windows_model = WindowsModel("")

        with self.frame:
            with ui.VStack(spacing=4):
                try:
                    from omni.kit.widget.searchfield import SearchField
                    self._search_field = SearchField(
                        on_search_fn=self._on_search,
                        subscribe_edit_changed=True,
                        style=ACTIONS_WINDOW_STYLE,
                    )
                except ImportError:
                    self._search_field = None
                with ui.ScrollingFrame(
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    style_type_name_override="ActionsView",
                ):
                    self._actions_view = ui.TreeView(
                        self._windows_model, root_visible=False, header_visible=False,
                    )

        self._actions_view.set_selection_changed_fn(self._on_selection_changed)
        if self.__expand_all:
            self._actions_view.set_expanded(None, True, True)
        if self.__focus_search and self._search_field:
            self._search_field._search_field.focus_keyboard()  # pylint: disable=protected-access

    def _on_search(self, search_words: Optional[List[str]]) -> None:
        self._windows_model.search(search_words)
        # Auto expand on searching
        self._actions_view.set_expanded(None, True, True)

    def _on_selection_changed(self, selections: List[WindowItem]):
        for item in selections:
            if isinstance(item, WindowItem) and self.__on_selected_fn:
                self.__on_selected_fn(item.window_title)
