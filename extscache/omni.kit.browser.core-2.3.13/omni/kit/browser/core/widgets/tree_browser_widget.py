import copy
from typing import Union
from ..models import CollectionItem, CategoryItem, DetailItem
from .browser_widget import BrowserWidget
from .tree_category_delegate import TreeCategoryDelegate
from .tree_style import TREE_UI_STYLES

class TreeBrowserWidget(BrowserWidget):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        category_delegate = kwargs.pop("category_delegate", TreeCategoryDelegate())
        show_collection = kwargs.pop("show_collection", False)
        extra_ui_style = kwargs.pop("style", {})
        extra_tree_style = copy.copy(TREE_UI_STYLES)
        extra_tree_style.update(extra_ui_style)

        super().__init__(
            *args,
            category_delegate=category_delegate,
            style=extra_tree_style,
            show_collection=show_collection,
            **kwargs
        )

    def _on_model_item_changed(self, item: Union[CollectionItem, CategoryItem, DetailItem]) -> None:
        if item and isinstance(item, CategoryItem):
            # Redraw item in category view
            self._category_view.model._item_changed(item)
            if item in self.category_selection:
                # Category selected, need to refresh details
                self._detail_view.model._item_changed(None)
        else:
            super()._on_model_item_changed(item)