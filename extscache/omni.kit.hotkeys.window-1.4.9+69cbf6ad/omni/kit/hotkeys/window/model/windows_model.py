__all__ = ["WindowItem", "WindowsModel"]
from typing import Optional, List
import uuid
import omni.ui as ui


IGNORE_WINDOW_TITLES = [
    "omni.ui.scene",
    "DockSpace",
    "Changing directory ...",
    "Add Attribute",
    "Select ",
    "###"
]


class WindowItem(ui.AbstractItem):
    def __init__(self, window_title: Optional[str]):
        self.window_title = window_title
        super().__init__()

    def get_value_model(self):
        return ui.SimpleStringModel(self.window_title if self.window_title else "")


class WindowsModel(ui.AbstractItemModel):
    """
    Model to represent all ui Windows and current selected in Hotkey.

    Args:
        window_title: selected window title in Hotkey.
    """
    def __init__(self, window_title: str):
        self.selected_window_title = window_title
        self.__items: List[WindowItem] = []
        self._current_index = ui.SimpleIntModel(-1)
        self._current_index.add_value_changed_fn(self.__on_current_index_changed)
        self._search_words = None
        super().__init__()

    @property
    def selected_windows(self) -> Optional[List[str]]:
        if self._current_index.as_int >= 0 and self._current_index.as_int < len(self.__items):
            return [self.__items[self._current_index.as_int].window_title]
        return None

    def get_item_value_model(self, item: Optional[WindowItem] = None, column_id: int = 0):
        if item is None:
            return ""
        return item.get_value_model()

    def get_item_children(self, item=None):
        """Returns all the children when the widget asks it."""
        if item is not None:
            return []

        # Window list may changed at runtime, so always refresh
        window_titles = []
        for window in ui.Workspace.get_windows():
            ignore = False
            for title in IGNORE_WINDOW_TITLES:
                if window.title.startswith(title):
                    ignore = True
                    break
            # Ignore window with GUID title
            try:
                uuid.UUID(str(window.title))
                continue
            except ValueError:
                pass

            if not self.__filter(window.title):
                continue
            if not ignore and window.title and window.title not in window_titles:
                window_titles.append(window.title)
        window_titles.sort()
        # Empty at top
        window_titles.insert(0, "")

        self.__items = [WindowItem(title) for title in window_titles]

        # Refresh current selected index
        selected_index = 0
        for index, window_item in enumerate(self.__items):
            if window_item.window_title == self.selected_window_title:
                selected_index = index
        self._current_index.set_value(selected_index)

        return self.__items

    def get_item_value_model_count(self, item=None):
        """The number of columns"""
        return 1

    def search(self, search_words: Optional[List[str]]):
        self._search_words = search_words
        self._item_changed(None)

    def __on_current_index_changed(self, value_model: ui.SimpleIntModel) -> None:
        # Save selected window title to make sure selection all right after refresh
        if value_model.as_int >= 0 and value_model.as_int < len(self.__items):
            self.selected_window_title = self.__items[value_model.as_int].window_title
        else:
            self.selected_window_title = ""
        self._item_changed(None)

    def __filter(self, title: str) -> bool:
        if not self._search_words:
            return True

        return all(not word.lower() not in title.lower() for word in self._search_words)
