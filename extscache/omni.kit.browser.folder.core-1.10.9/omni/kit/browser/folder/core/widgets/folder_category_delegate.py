from typing import Optional, List
from omni.kit.browser.core import TreeCategoryDelegate
from .context_menu import ContextMenu
from ..models.folder_browser_item import FolderCategoryItem
from ..models.tree_folder_browser_model import TreeFolderBrowserModel


class FolderCategoryDelegate(TreeCategoryDelegate):
    def __init__(self, **kwargs):
        super().__init__(hide_zero_count=True)
        self._widget_model = None
        self._context_menu = None

    def get_count(self, item: FolderCategoryItem) -> str:
        if hasattr(item, "folder") and item.folder:
            if item.folder.has_timeout:
                return "TIMEOUT"
        return super().get_count(item)

    # To collect all items, we need to bind widget model to get all detail items
    def bind_model(self, model: TreeFolderBrowserModel):
        self._widget_model = model

    def _get_collect_urls(self, item: FolderCategoryItem) -> Optional[List[str]]:  # pragma: no cover - never called
        """
        Query folder category local collected urls.
        Args:
            item (FolderCategoryItem): category item to query
        Return:
            collected urls if found. Else None.
        """
        if not self._widget_model or not item:
            return None
        items = self._widget_model.get_detail_items(item)

        return [item.url for item in items]

    def _on_item_right_click(self, item: FolderCategoryItem):  # pragma: no cover - never called
        """Show category item's menu"""
        if self._context_menu is None:
            self._context_menu = ContextMenu()
        if self._context_menu:
            self._context_menu.urls = self._get_collect_urls(item)
            self._context_menu.folder_name = item.name
            self._context_menu.show_menu()
