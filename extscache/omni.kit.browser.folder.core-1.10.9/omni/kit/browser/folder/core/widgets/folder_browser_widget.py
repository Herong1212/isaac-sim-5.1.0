__all__ = ["FolderBrowserWidget"]
import asyncio
from typing import Callable, Dict, List, Optional

import omni.kit.app
from omni import ui
from omni.kit.browser.core import BrowserSearchBar, BrowserWidget, CategoryDelegate, DetailItem, OptionsMenu
from omni.kit.window.filepicker import FilePickerDialog

from ..models import FileSystemFolder, FolderBrowserModel, FolderCategoryItem
from .folder_category_delegate import FolderCategoryDelegate
from .folder_detail_delegate import FolderDetailDelegate
from .options_menu import FolderOptionsMenu


class FolderBrowserWidget:
    """
    Represent a widget for folders.
    Args:
        browser_model (FolderBrowserModel): Folder browser model used in the widget.
    Keyword args:
        detail_delegate (Optional[FolderDetailDelegate]): Detail delegate used in the widget. Default None means using standard folder detail delegate.
        options_menu (Optional[OptionsMenu]): Options menu used in the widget. Default None means using default (Add/Remove collection) in the widget.
        style (dict): Extra ui style. Default empty.
        min_thumbnail_size (int): min thumbnail size used in zoom bar. Default 32.
        max_thumbnail_size (int): max thumbnail size used in zoom bar. Default 512.
        detail_thumbnail_size (int): size of detail item thumbnail, in pixel. Default 128.
        thumbnail_aspect (float): Aspect ratio of thumbnail. Default 1.0 (width / height).
        extra_filter_fn (callable): Extra filter function called to filter items. Return True to show item otherwise hide.
            Default None. Function signure: bool extra_filter_fn(item: DetailItem)
        predownload_folder (Optional[str]): Folder to predownload files and sub folders. Predownload is used to download items from remote folder to local when startup.
            Default None means no predowndload.
        category_tree_mode (Optional[bool]): Show categories in tree mode rather than flat mode.
        show_category_splitter (Optional[bool]): Show adjustable splitter bar between category and detail views.
        category_width (Optional[float]): Set starting width of category view.
        splitter_extra_width (int): Width added to vertical splitter between category view and detail view.
        multiple_drag (bool): True to allow drag multiple items. Default False.
    """

    def __init__(
        self,
        browser_model: FolderBrowserModel,
        category_delegate: Optional[CategoryDelegate] = None,
        detail_delegate: Optional[FolderDetailDelegate] = None,
        options_menu: Optional[OptionsMenu] = None,
        min_thumbnail_size: int = 32,
        max_thumbnail_size: int = 512,
        detail_thumbnail_size: int = 128,
        thumbnail_aspect: float = 1.0,
        predownload_folder: Optional[str] = None,
        style: Dict = {},
        extra_filter_fn: callable = None,
        category_tree_mode=False,
        show_category_splitter=False,
        category_width: float = 120,
        splitter_extra_width: int = 4,
        always_select_category: bool = True,
        multiple_drag: bool = False,
    ):
        self._browser_model = browser_model
        self._delegate = detail_delegate or FolderDetailDelegate(browser_model)
        self._options_menu = options_menu or FolderOptionsMenu(predownload_folder)
        self._min_thumbnail_size = min_thumbnail_size
        self._max_thumbnail_size = max_thumbnail_size
        self._detail_thumbnail_size = detail_thumbnail_size
        self._thumbnail_aspect = thumbnail_aspect
        self._extra_ui_style = style
        self._splitter_extra_width = splitter_extra_width
        self._pick_folder_dialog: Optional[FilePickerDialog] = None
        self._extra_filter_fn = extra_filter_fn
        self._category_tree_mode = category_tree_mode
        self._show_category_splitter = show_category_splitter
        self._category_width = category_width
        self._category_delegate = category_delegate or CategoryDelegate()
        self._always_select_category = always_select_category
        self._last_selected_folder: Optional[str] = None
        self._last_selected_file: Optional[str] = None
        self._multiple_drag = multiple_drag
        self._build_ui()

        self.__sub_model = self._browser_model.subscribe_item_changed_fn(self.__on_browser_model_changed)
        def __on_refresh_categories():
            # Save last selected category so that we can recover the category selection after categories refreshed
            if self._browser_widget.category_selection:
                if isinstance(self._browser_widget.category_selection[0], FolderCategoryItem):
                    self._last_selected_folder = self._browser_widget.category_selection[0].folder.url
            if self._browser_widget.detail_selection:
                self._last_selected_file = self._browser_widget.detail_selection[0].file.url

        self._browser_model.on_refresh_categories = __on_refresh_categories

    def destroy(self) -> None:
        """Clean up"""
        self.__sub_model = None
        if self._pick_folder_dialog is not None:
            self._pick_folder_dialog.destroy()
            self._pick_folder_dialog = None
        self._search_bar.destroy()
        self._delegate = None
        self._browser_model.destroy()
        self._browser_widget.remove_thumbnail_size_changed_fn(self._thumbnail_sub_id)
        self._browser_widget.destroy()

    @property
    def category_selection(self) -> List[FolderCategoryItem]:
        return self._browser_widget.category_selection

    @category_selection.setter
    def category_selection(self, selection: List[FolderCategoryItem]) -> None:
        self._browser_widget.category_selection = selection

    @property
    def detail_selection(self) -> List[DetailItem]:
        return self._browser_widget.detail_selection

    @detail_selection.setter
    def detail_selection(self, selection: List[DetailItem]) -> None:
        self._browser_widget.detail_selection = selection

    def build_widgets(self):
        with ui.VStack(spacing=4):
            self._build_search_bar()
            self._build_browser_widget()

    def _build_ui(self):
        self.build_widgets()

        self._options_menu.set_add_collection_fn(self._on_add_collection)
        self._search_bar.bind_browser_widget(self._browser_widget)
        self._thumbnail_sub_id = self._browser_widget.add_thumbnail_size_changed_fn(self._on_thumbnail_size_changed)
        self._browser_widget.collection_index = 0

    def select_folder(self, folder: FileSystemFolder, expand: bool=False):
        folder_item = self._browser_model.get_folder_item(folder)
        if folder_item:
            self._browser_widget.category_selection = [folder_item]
            if expand:
                self._browser_widget._category_view.set_expanded(folder_item, True, True)

    def _build_search_bar(self):
        self._search_bar = BrowserSearchBar(options_menu=self._options_menu, style=self._extra_ui_style)

    def _build_browser_widget(self):
        self._browser_widget = self._build_browser_widget_internal(
            self._browser_model,
            detail_delegate=self._delegate,
            category_delegate=self._category_delegate,
            min_thumbnail_size=self._min_thumbnail_size,
            max_thumbnail_size=self._max_thumbnail_size,
            detail_thumbnail_size=self._detail_thumbnail_size,
            thumbnail_aspect=self._thumbnail_aspect,
            style=self._extra_ui_style,
            extra_filter_fn=self._extra_filter_fn,
            category_tree_mode=self._category_tree_mode,
            category_width=self._category_width,
            show_category_splitter=self._show_category_splitter,
            splitter_extra_width=self._splitter_extra_width,
            always_select_category=self._always_select_category,
            multiple_drag=self._multiple_drag,
        )

    def _build_browser_widget_internal(self, *args, **kwargs):
        return BrowserWidget(*args, **kwargs)

    def _on_thumbnail_size_changed(self, thumbnail_size: int) -> None:
        # Hide detail lable if thumbnail size it smaller than 128
        self._delegate.hide_label = thumbnail_size < 128
        self._delegate.item_changed(None, None)

    def _on_add_collection(self) -> None:
        if self._pick_folder_dialog is None:
            self._pick_folder_dialog = self._create_filepicker(
                "Select Collection Directory", click_apply_fn=self._on_folder_picked, dir_only=True
            )
        self._pick_folder_dialog.show()

    def _on_remove_collection(self) -> None:
        if self._browser_widget.collection_index < 0:
            return
        else:
            collection_items = self._browser_model.get_collection_items()
            url = collection_items[self._browser_widget.collection_index].folder.url
            if self._browser_model.remove_root_folder(url):
                # Update collection combobox and default none selected
                self._browser_model._item_changed(None)
                self._browser_widget.collection_index = -1

    def _create_filepicker(
        self,
        title: str,
        filters: list = ["All Files (*)"],
        click_apply_fn: Callable = None,
        error_fn: Callable = None,
        dir_only: bool = False,
    ) -> FilePickerDialog:
        async def on_click_handler(
            filename: str, dirname: str, dialog: FilePickerDialog, click_fn: Callable, dir_only: bool
        ):
            fullpath = None
            if dir_only:
                fullpath = dirname
            else:
                if dirname:
                    fullpath = f"{dirname}/{filename}"
                elif filename:
                    fullpath = filename
            if click_fn:
                click_fn(fullpath)
            dialog.hide()

        dialog = FilePickerDialog(
            title,
            allow_multi_selection=False,
            apply_button_label="Select",
            click_apply_handler=lambda filename, dirname: asyncio.ensure_future(
                on_click_handler(filename, dirname, dialog, click_apply_fn, dir_only)
            ),
            click_cancel_handler=lambda filename, dirname: dialog.hide(),
            item_filter_options=filters,
            error_handler=error_fn,
        )
        dialog.hide()
        return dialog

    def _on_folder_picked(self, url: Optional[str]) -> None:
        if url is not None:
            if url[-1] == "/":
                url = url[:-1]
            folder = self._browser_model.append_root_folder(url)
            if folder:
                self._on_new_collection_added(folder)

    def _on_new_collection_added(self, folder: FileSystemFolder) -> None:
        # Update collection combobox if appended
        self._browser_widget._collection_model._item_changed(None)

        # Select the new collection
        collection_items = self._browser_model.get_collection_items()
        for index, item in enumerate(collection_items):
            if item.folder.url == folder.url:
                if self._browser_widget.collection_index == index:
                    # If index is same, change to -1 first to force update categories.
                    self._browser_widget.collection_index = -1
                self._browser_widget.collection_index = index
                break
        else:
            self._browser_widget.collection_index = -1

    def __on_browser_model_changed(self, model: FolderBrowserModel, item: ui.AbstractItem):
        if self._last_selected_folder:
            # Select expect folder
            async def __force_select_folder_async(select_folder, select_file):
                await omni.kit.app.get_app().next_update_async()
                for collection_item in self._browser_model.get_item_children(None):
                    for category_item in self._browser_model.get_item_children(collection_item):
                        found = self.__find_category_item_by_url(select_folder, category_item)
                        if found:
                            self._browser_widget.category_selection = [found]
                            if select_file:
                                details = self._browser_model.get_item_children(found)
                                for detail in details:
                                    if detail.file.url == select_file:
                                        await omni.kit.app.get_app().next_update_async()
                                        self._browser_widget.detail_selection = [detail]
                            return

            (saved_select_folder, self._last_selected_folder) = (self._last_selected_folder, None)
            (saved_select_file, self._last_selected_file) = (self._last_selected_file, None)
            asyncio.ensure_future(__force_select_folder_async(saved_select_folder, saved_select_file))

    def __find_category_item_by_url(self, url: str, parent_item: FolderCategoryItem) -> Optional[FolderCategoryItem]:
        if not hasattr(parent_item, "folder"):
            return None
        if parent_item.folder.url == url:
            return parent_item
        elif url.startswith(parent_item.folder.url):
            for child in parent_item.children:
                result = self.__find_category_item_by_url(url, child)
                if result:
                    return result
            return None
