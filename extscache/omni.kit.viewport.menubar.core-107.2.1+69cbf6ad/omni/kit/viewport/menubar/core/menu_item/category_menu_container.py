from typing import Callable, Dict, Optional

from ..model.category_model import CategoryCustomItem, SimpleCategoryModel, CategoryStateItem, CategoryCollectionItem
from .category_menu_collection import CategoryMenuCollection
from .selectable_menu_item import SelectableMenuItem


__all__ = ["CategoryMenuContainer"]


class CategoryMenuContainer:
    """A menu container for category menu items."""
    def __init__(
        self,
        model: SimpleCategoryModel,
        identifier: Optional[str] = None,
        trigger_fns: Optional[Dict[str, Callable]] = None
    ):
        """
        Constructor.

        Args:
            model (SimpleCategoryModel): Category data model.

        Keyword Args:
            identifier (Optional[str]): Widget identifier, defaults to None.
            trigger_fns (Optional[Dict[str, Callable]]): Callbacks when menu item clicked, defaults to None.
        """
        self._model = model
        self.__identifier = identifier
        self.build(trigger_fns)

    def build(self, trigger_fns: Optional[Dict[str, Callable]] = None):
        """
        Build category menu items.

        Keyword Args:
            trigger_fns (Optional[Dict[str, Callable]]): Callbacks when menu item clicked by item text, defaults to None
        """
        # XXX: trigger_fns is a workaround for omni.kit.viewport.menubar.display
        # do not expect it will always exists!

        for item in self._model.get_item_children():
            name: str = getattr(item, "text", "")
            if isinstance(item, CategoryCollectionItem):
                identifier = f"{self.__identifier}.{name}" if self.__identifier else None
                item = CategoryMenuCollection(self._model, item, identifier=identifier, trigger_fns=trigger_fns)
            elif isinstance(item, CategoryStateItem):
                item = SelectableMenuItem(name=name, model=item.value_model)
            elif isinstance(item, CategoryCustomItem):
                item = item.build_fn()

            # Try to pull a triggered_fn from the ones provided
            if trigger_fns and item and name:
                trigger_fn = trigger_fns.get(name)
                if trigger_fn:
                    item.set_triggered_fn(trigger_fn)
