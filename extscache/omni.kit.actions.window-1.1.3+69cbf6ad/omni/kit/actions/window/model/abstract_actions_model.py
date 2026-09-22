__all__ = ["AbstractActionsModel"]
import abc
from typing import Optional, List, Union, Dict
import omni.ui as ui
from ..column_registry import ColumnRegistry
from .actions_item import ActionExtItem, AbstractActionItem


class AbstractActionsModel(ui.AbstractItemModel):
    """
    General data model for actions.

    Args:
        column_registey (ColumnRegistry): Registry to get column.
    """
    def __init__(self, column_registry: ColumnRegistry):
        self._column_registry = column_registry
        self.__cached_items: Dict[Optional[ui.AbstractItem], List[ui.AbstractItem]] = {}
        super().__init__()

        self.add_item_changed_fn(lambda model, item: self.__remove_from_cache(None, item))

    def get_item_children(self, item: Optional[ActionExtItem]) -> List[ui.AbstractItem]:
        if item is None:
            if None not in self.__cached_items:
                self.__cached_items[None] = self.get_ext_items()
            return self.__cached_items[None]
        else:
            if item not in self.__cached_items:
                self.__cached_items[item] = self.get_detail_items(item)
            return self.__cached_items[item]

    @abc.abstractmethod
    def get_ext_items(self) -> List[ActionExtItem]:
        pass

    @abc.abstractmethod
    def get_detail_items(self, item: ActionExtItem) -> List[AbstractActionItem]:
        pass

    def get_item_value_model_count(self, item: ui.AbstractItem) -> int:
        return self._column_registry.max_column_id + 1

    def get_item_value_model(self, item: Optional[ui.AbstractItem] = None, index: int = 0) -> Optional[ui.AbstractValueModel]:
        return None

    def __remove_from_cache(self, _, item: Optional[AbstractActionItem]) -> None:
        children = self.__cached_items.pop(item, [])
        for c in children:
            self.__remove_from_cache(None, c)

    def clean(self) -> None:
        self.__cached_items = {}

    def _on_dirty(self):
        pass

    def _set_dirty(self):
        self._dirty = True
        self._on_dirty()
