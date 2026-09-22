# pylint: disable=relative-beyond-top-level

__all__ = ["SearchBar"]
from typing import Optional, List
import omni.ui as ui
from omni.kit.actions.window import ACTIONS_WINDOW_STYLE
from omni.kit.widget.filter import FilterButton

from ..model.hotkeys_model import HotkeysModel
from .options_menu import OptionsMenu


class SearchBar:
    """
    Search bar, includes a search field and a filter button.

    Args:
        model (HotkeysModel): Hotkeys model.
    """

    def __init__(self, model: HotkeysModel):
        self.__model = model
        self.__container: Optional[ui.HStack] = None
        self.__filter_button: Optional[FilterButton] = None
        self.__options_menu: Optional[OptionsMenu] = None
        self.__build_ui()

    def destroy(self):
        if self.__filter_button:
            self.__filter_button.destroy()
            self.__filter_button = None

    @property
    def visible(self) -> bool:
        return self.__container.visible if self.__container else False

    @visible.setter
    def visible(self, value) -> None:
        if self.__container:
            self.__container.visible = False

    def __build_ui(self):
        try:
            from omni.kit.widget.searchfield import SearchField
            self.__container = ui.HStack(height=0)
            with self.__container:
                self._search_field = SearchField(
                    on_search_fn=self.__on_search,
                    subscribe_edit_changed=True,
                    style=ACTIONS_WINDOW_STYLE,
                    show_tokens=False,
                )
                self.__filter_button = FilterButton(self.__model.search_filter_flags, width=26, height=26)
                with ui.VStack(width=26):
                    self.__options_image = ui.ImageWithProvider(
                        width=26,
                        height=26,
                        mouse_pressed_fn=lambda x, y, b, f: self.__show_options(),
                        style_type_name_override="SearchBar.Options",
                    )
                    ui.Spacer()
        except ImportError:
            self._search_field = None

    def __on_search(self, search_words: Optional[List[str]]) -> None:
        self.__model.search(search_words)

    def __show_options(self):
        if self.__options_menu is None:
            self.__options_menu = OptionsMenu(self.__model, self.__options_image)

        self.__options_menu.show()
