from typing import Optional
from omni.kit.browser.core import TreeBrowserWidget
from .folder_browser_widget import FolderBrowserWidget
from .folder_category_delegate import FolderCategoryDelegate
from ..models import FolderCategoryItem, FileSystemFolder


class TreeFolderBrowserWidget(FolderBrowserWidget):
    def __init__(
        self,
        *args,
        category_delegate: Optional[FolderCategoryDelegate] = None,
        **kwargs
    ):
        category_delegate = category_delegate or FolderCategoryDelegate()
        category_width = kwargs.pop("category_width", 190)
        splitter_extra_width = kwargs.pop("splitter_extra_width", 0)
        show_category_splitter=kwargs.pop("show_category_splitter", True)

        super().__init__(
            *args,
            category_delegate=category_delegate,
            category_width=category_width,
            show_category_splitter=show_category_splitter,
            splitter_extra_width=splitter_extra_width,
            **kwargs
        )
        if isinstance(category_delegate, FolderCategoryDelegate):
            category_delegate.bind_model(self._browser_model)

    def _build_browser_widget_internal(self, *args, **kwargs) -> TreeBrowserWidget:
        browser_widget = TreeBrowserWidget(*args, **kwargs)
        browser_widget._on_category_selection_changed_fn = self._on_category_selection_changed
        return browser_widget

    def _on_category_selection_changed(self, category_item: FolderCategoryItem) -> None:
        # Traverse a category folder when selected and not synced
        if category_item and hasattr(category_item, "folder") and not category_item.folder.prepared:
            self._browser_model.start_traverse(category_item.folder)

    def _on_new_collection_added(self, folder: FileSystemFolder) -> None:
        # Tree mode, collection is a root category item
        pass
