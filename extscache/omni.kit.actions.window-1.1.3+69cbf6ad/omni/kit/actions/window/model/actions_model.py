__all__ = ["ActionsModel"]
from typing import List, Dict, Optional, Callable
from unittest.mock import NonCallableMagicMock

from .abstract_actions_model import AbstractActionsModel
from .actions_item import ActionDetailItem
from .actions_item import ActionExtItem
from ..column_registry import ColumnRegistry
from omni.kit.actions.core import Action, get_action_registry


class ActionsModel(AbstractActionsModel):
    """
    Data model for actions.

    Args:
        column_registey (ColumnRegistry): Registry to get column.
        on_search_action_fn (Callable[[Action, str], bool]): Callback to filter action with string. Default None.
    """
    def __init__(self, column_registry: ColumnRegistry, on_search_action_fn: Callable[[Action, str], bool] = None):
        self._action_registry = get_action_registry()
        self._actions_by_ext: Dict[str, List[Action]] = {}
        self._search_words = None
        self.__on_search_action_fn = on_search_action_fn

        super().__init__(column_registry)

    def get_ext_items(self) -> List[ActionExtItem]:
        all_actions = self._action_registry.get_all_actions()
        self._actions_by_ext: Dict[str, List[Action]] = {}

        for action in all_actions:
            if self._search_words and not self._filter_action(action):
                continue
            if action.requires_parameters:
                continue
            if action.extension_id not in self._actions_by_ext:
                self._actions_by_ext[action.extension_id] = []
            self._actions_by_ext[action.extension_id].append(action)

        return [ActionExtItem(id, highlight=self._search_words[0] if self._search_words else None) for id in self._actions_by_ext.keys()]

    def get_detail_items(self, item: ActionExtItem) -> List[ActionDetailItem]:
        if isinstance(item, ActionExtItem):
            details = [ActionDetailItem(action, highlight=self._search_words[0] if self._search_words else None) for action in self._actions_by_ext[item.id]]
            details.sort(key = lambda item: item.action.description)
            return details
        else:
            return []

    def search(self, search_words: Optional[List[str]]):
        # Now could highlight one word in HighlightLabel, so combine the search words back to a single string
        self._search_words = [" ".join(search_words)] if search_words else None
        self._item_changed(None)

    def execute(self, item: ActionDetailItem) -> None:
        if item is None or not isinstance(item, ActionDetailItem):
            return
        action = item.action
        action.execute()

    def _filter_action(self, action: Action) -> bool:
        for word in self._search_words:
            if self.__on_search_action_fn:
                if not self.__on_search_action_fn(action, word):
                    return False
            elif word.lower() not in action.extension_id.lower() \
                and word.lower() not in action.id.lower() \
                and word.lower() not in action.display_name.lower() \
                and word.lower() not in action.description.lower() \
                and word.lower() not in action.tag.lower() \
                and word.lower() not in action.icon_url.lower():
                return False

        return True
