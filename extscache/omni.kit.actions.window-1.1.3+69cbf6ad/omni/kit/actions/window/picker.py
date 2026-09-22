__all__ = ["ActionColumnDelegate", "ActionsPicker"]
import omni.ui as ui
from typing import List, Callable
from omni.kit.actions.core import Action
from .window import ActionsWindow
from .model.actions_item import AbstractActionItem, ActionDetailItem
from .delegate.string_column_delegate import StringColumnDelegate

class ActionColumnDelegate(StringColumnDelegate):
    """
    A simple delegate to display a action in column.

    Kwargs:
        get_value_fn (Callable[[ui.AbstractItem], str]): Callback function to get item display string. Default using item.id
        width (ui.Length): Column width. Default ui.Fraction(1).
    """
    def get_value(self, item: ActionDetailItem):
        if self._get_value_fn:
            return self._get_value_fn(item)
        else:
            if isinstance(item, ActionDetailItem):
                # Show action display name instead action id
                return item.action.display_name
            else:
                return item.id


class ActionsPicker(ActionsWindow):
    def __init__(self,
        width=0,
        height=600,
        on_selected_fn: Callable[[Action],None]=None,
        expand_all: bool=True,
        focus_search: bool=True
    ):
        super().__init__("###ACTION_PICKER", width=width, height=height)
        self.flags = ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_POPUP
        self.__on_selected_fn = on_selected_fn
        self.__expand_all = expand_all
        self.__focus_search = focus_search

    def _register_column_delegates(self):
        self._column_registry.register_delegate(ActionColumnDelegate("Action", width=200))

    def _build_ui(self):
        super()._build_ui()

        self._actions_view.set_selection_changed_fn(self._on_selection_changed)
        if self.__expand_all:
            self._actions_view.set_expanded(None, True, True)
        if self.__focus_search and self._search_field:
            self._search_field._search_field.focus_keyboard()

    def _on_selection_changed(self, selections: List[AbstractActionItem]):
        for item in selections:
            if isinstance(item, ActionDetailItem):
                if self.__on_selected_fn:
                    self.__on_selected_fn(item.action)

    def _on_search_action(self, action: Action, word: str) -> bool:
        # In pick mode, only display extension id and display name
        # So we only search in these two fields
        if word.lower() in action.extension_id.lower() \
            or word.lower() in action.display_name.lower():
                return True

        return False