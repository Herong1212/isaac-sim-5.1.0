
import asyncio
import os
from itertools import chain
from typing import Dict, List, Optional, Union
from unicodedata import category

import carb
import carb.settings
import omni.kit.app
from omni.kit.browser.core import CategoryItem

from .folder_browser_data import AbstractBrowserFolder, BrowserFile, FileSystemFolder
from .folder_browser_item import FileDetailItem, FolderCategoryItem, FolderCollectionItem
from .folder_browser_model import FolderBrowserModel


class TreeFolderBrowserModel(FolderBrowserModel):
    def __init__(self, *args, **kwargs):
        self.__summary_item = None
        setting_folders_hide_in_category = kwargs.pop("setting_folders_hide_in_category", None)
        self.__folders_hide_in_category = carb.settings.get_settings().get(setting_folders_hide_in_category) if setting_folders_hide_in_category else []

        super().__init__(*args, **kwargs)

    def process_root_folder(self, root_folder: str, sync: bool=True) -> Optional[FileSystemFolder]:
        folder = super().process_root_folder(root_folder, sync=sync)

        # Hide root folder in category view only for default folders
        if folder and folder.name in self.__folders_hide_in_category:
            folder.hide_root_in_category = True
        return folder

    def remove_collection(self, item: FolderCollectionItem) -> bool:  # pragma: no cover
        # Only one default collection item and could not be removed
        pass

    def get_collection_items(self) -> List[FolderCollectionItem]:
        """Override to get list of collection items"""
        # Treeview mode, create a default collection item
        if self._root_collection_item is None:
            self._root_collection_item = FolderCollectionItem("TreeRoot", "", None)

        # Load folders from local cache
        self._load_data_from_json()

        return [self._root_collection_item]

    def get_category_items(self, item: FolderCollectionItem) -> List[FolderCategoryItem]:
        """
        Create category item for every root folder.
        Also create category items for sub folders as children of parent category item.
        Summary category item will be created if required.
        """
        category_items: List[FolderCategoryItem] = []

        for root_folder in self._root_folders:
            category_item = self._folder_cache.get(root_folder)

            if category_item is None:
                category_item = self._create_folder_category_item(root_folder)
                # Name contains sub categories, create full category item chain
                if len(root_folder.name.split("/")) > 1:
                    category_item = self._create_category_item_chain(root_folder, category_items)
                    if category_item:
                        self.sort_items(category_item.children)
            else:
                # Get root category item
                parent = category_item.parent
                while parent:
                    category_item = parent
                    parent = parent.parent

            if category_item and category_item not in category_items:
                if root_folder.hide_root_in_category and (root_folder.prepared or (hasattr(root_folder, "has_cache") and root_folder.has_cache)):
                    # When hide root in category view, only hide root item when prepared or laded from cache
                    category_items.extend(category_item.children)
                else:
                    category_items.append(category_item)
            if category_item:
                if not self._json_file or not hasattr(root_folder, "has_cache") or not root_folder.has_cache:
                    # Not in cache
                    if not root_folder.prepared:
                        # No traversed
                        self.start_traverse(root_folder)

        self.sort_items(category_items)

        if self._show_summary_folder:
            summary_count = sum([c.count for c in category_items])
            self.__summary_item = CategoryItem(self.SUMMARY_FOLDER_NAME, summary_count)
            category_items.insert(0, self.__summary_item)

        return category_items

    def get_detail_items(self, item: CategoryItem) -> List[FileDetailItem]:
        """Override to get list of detail items"""
        if item.name == self.SUMMARY_FOLDER_NAME:
            return self._get_summary_detail_items()
        elif isinstance(item, FolderCategoryItem):
            # List files in item folder
            if item.folder.hide_root_in_category:
                # For root folder that hidden in category view, get detail items from sub folders
                detail_items = []
                for sub_folder in item.folder.sub_folders:
                    detail_items += self._get_folder_detail_items(sub_folder)
                    if not self._show_category_subfolders:
                        for child in sub_folder.sub_folders:
                            detail_items += self._get_folder_detail_items(child)
            else:
                detail_items = self._get_folder_detail_items(item.folder)

                # In tree mode, for root folders, show items in sub folders
                if not detail_items:
                    if item.folder in self._root_folders:
                        for sub_folder in item.folder.sub_folders:
                            detail_items += self._get_folder_detail_items(sub_folder)
                    else:
                        pos = item.folder.url.rfind("/")
                        parent_url = item.folder.url[:pos]

                        for root_folder in self._root_folders:
                            if root_folder.hide_root_in_category:
                                if parent_url == root_folder.url:
                                    for sub_folder in item.folder.sub_folders:
                                        detail_items += self._get_folder_detail_items(sub_folder)
        else:
            detail_items = super().get_detail_items(item)

        self.sort_items(detail_items)
        return detail_items

    def folder_changed(self, item: Union[AbstractBrowserFolder, BrowserFile, None]) -> None:
        """
        Notify folder or file changed.
        Args:
            item (Union[AbstractBrowserFolder, BrowserFile]): Changed folder or file object.
        """
        def refresh_category_only():
            browser_item = self._folder_cache.get(item, None)
            if browser_item:
                self._item_changed(browser_item)

        if item is None:
            # Clean all folder cache and refresh the collection item
            self._folder_cache = {}
            self._item_changed(self._root_collection_item)
        elif item.hide_root_in_category:
            if item.prepared:
                if hasattr(item, "has_update") and not item.has_update and item.prepared:
                    # Folder traverse done without changes, only refresh category items for loading status
                    refresh_category_only()
                else:
                    # Folder traverse done, clean all folder cache and refresh the collection item
                    self._folder_cache = {}
                    self._item_changed(self._root_collection_item)

                    # Refresh cache
                    if isinstance(item, AbstractBrowserFolder):
                        for root in self._root_folders:
                            if item.url.startswith(root.url):
                                self._save_data_to_json(root)
                                break
            else:
                # Folder in traversing, refresh category item to show loading
                refresh_category_only()
        else:
            if hasattr(item, "has_update") and not item.has_update and item.prepared:
                refresh_category_only()
            else:
                # Remove cached browser item related to the item
                browser_item = self._folder_cache.get(item, None)
                if browser_item:
                    # Treeview mode, need to refresh category view to show sub folders
                    if self.on_refresh_categories:
                        self.on_refresh_categories()

                    # Category item updated, need to refresh
                    # For parent, refresh count, reset browser cache
                    old_count = browser_item.count
                    self.__refresh_category_item(browser_item)

                    # Update count in parent items
                    parent = browser_item.parent
                    while parent:
                        parent.count += browser_item.count - old_count
                        self._item_changed(parent)
                        parent = parent.parent

                    # Finally, need to update summary item
                    if self.__summary_item:
                        self.__summary_item.count += browser_item.count - old_count
                        self._item_changed(self.__summary_item)
                else:
                    # Either new root folder or root folder removed, just refresh the collection item
                    self._item_changed(self._root_collection_item)

    def __refresh_category_item(self, item: FolderCategoryItem) -> None:
        # Refresh category item
        # - For category itself, refresh count, reset browser cache
        # - For sub folders
        #     * if browser item already exists, refresh count
        #     * otherwise create a new browser item

        # Refresh children
        category_count = 0
        sub_category_items = []
        for sub in item.folder.sub_folders:
            sub_item = self._folder_cache.get(sub, None)
            if sub_item:
                if sub.has_update:
                    self.__refresh_category_item(sub_item)
            else:
                sub_item = self._create_folder_category_item(sub)
            if sub_item:
                sub_category_items.append(sub_item)
                category_count += sub_item.count
        category_count += item.folder.file_item_count

        # Reset count
        item.count = category_count

        # Reset children
        remove_children = [child for child in item.children if child not in sub_category_items]
        for child in remove_children:
            if child.folder:
                self._folder_cache.pop(child.folder, None)
        item.children = sub_category_items

        # Reset browser item cache
        self._item_changed(item)

    def _on_folder_traversed(self, folder: AbstractBrowserFolder, loading_completed=True, updated: bool=True) -> None:
        """
        Folder traversed,
        - Update category and detail widgets
        - Save data to cache
        """
        carb.log_info(f"Traverse completed: {folder.url}, {loading_completed}")

        if updated and folder in self._folder_cache:
            self.folder_changed(folder)
            self._save_data_to_json(folder)

    def _save_file_to_json(self, folder: AbstractBrowserFolder, file: BrowserFile) -> Dict:
        file_cache = {
            "url": os.path.relpath(file.url, folder.url),
            "thumbnail": os.path.relpath(file.thumbnail, folder.url).replace("\\", "/") if file.thumbnail else ""
        }
        return file_cache

    def _save_folder_to_json(self, folder: AbstractBrowserFolder, parent: Optional[AbstractBrowserFolder] = None) -> Dict:
        output = {
            "url": os.path.relpath(folder.url, parent.url) if parent else folder.url,
            "sub_folders": {},
            "files": {},
        }
        # sub folders
        for sub_folder in folder.sub_folders:
            output["sub_folders"][sub_folder.name] = self._save_folder_to_json(sub_folder, folder)

        # files
        for file in folder.files:
            dirs = file.url.split("/")
            name = dirs[-1]
            output["files"][name] = self._save_file_to_json(folder, file)

        return output

    def _load_file_from_json(self, data: Dict, folder: AbstractBrowserFolder) -> Optional[BrowserFile]:
        thumbnail = data["thumbnail"] if data["thumbnail"] else None
        if thumbnail:
            thumbnail = folder.url + "/" + thumbnail
        elif self._hide_file_without_thumbnails:
            return None
        return BrowserFile(folder.url + "/" + data["url"], thumbnail)

    def _load_folder_from_json(self, data: Dict, folder: AbstractBrowserFolder):
        files = data.get("files", {})
        if files:
            for file_data in files.values():
                file = self._load_file_from_json(file_data, folder)
                if file:
                    folder.files.append(file)

        if folder._ignore_sub_folder_with_files and folder.files:
            # This is already done when traverse folder now.
            # But in some test machiness, still cached with full data.
            # Could be removed later
            return

        sub_folders = data.get("sub_folders", {})
        if sub_folders:
            for name, sub in sub_folders.items():
                sub_folder_url = folder.url + "/" + sub["url"]
                sub_folder = self._create_folder_object_by_url(name, sub_folder_url)
                self._load_folder_from_json(sub_folders[name], sub_folder)
                folder.sub_folders.append(sub_folder)

        if folder.hide_root_in_category:
            # Refresh root folder to sync with new/deleted folder
            async def __refresh_root_folder():
                for _ in range(4):
                    await omni.kit.app.get_app().next_update_async()
                self.start_traverse(folder)

            asyncio.ensure_future(__refresh_root_folder())

    def _create_folder_category_item(self, folder: AbstractBrowserFolder) -> Optional[FolderCategoryItem]:
        """
        Create category item for a folder.
        Return None if no sub folder and files in folder.
        Otherwise return created category item.
        """
        # Count all sub folders and files
        category_count = 0
        sub_category_items = []
        for sub in folder.sub_folders:
            sub_category_item = self._create_folder_category_item(sub)
            if sub_category_item:
                sub_category_items.append(sub_category_item)
                category_count += sub_category_item.count
        category_count += folder.file_item_count

        # Create category item
        names = folder.name.split("/")
        if category_count > 0 or folder.has_timeout:
            category_item = FolderCategoryItem(names[-1], category_count, folder)
        elif folder in self._root_folders:
            # Empty, but since it is root folder, still show it with count = 0
            category_item = FolderCategoryItem(names[-1], 0, folder)
        else:
            return None
        category_item.children = sub_category_items
        for sub_item in sub_category_items:
            sub_item.parent = category_item
        self._folder_cache[folder] = category_item

        return category_item

    def __find_category_item_by_name(self, name: str, root_category_items: List[FolderCategoryItem]) -> Optional[FolderCategoryItem]:
        names = name.split("/")
        found = None
        for name in names:
            for item in root_category_items:
                if item.name.lower() == name.lower():
                    root_category_items = item.children
                    found = item
                    break
            else:
                return None

        return found

    def _create_category_item_chain(self, folder: AbstractBrowserFolder, root_category_items: List[FolderCategoryItem]) -> Optional[FolderCategoryItem]:
        # Folder name includs sub categories, create item one by one adding count of current folder
        exist_category_item = self.__find_category_item_by_name(folder.name, root_category_items)
        if exist_category_item:
            return None
        names = folder.name.split("/")
        folder_category_item = self._folder_cache[folder]
        last_name = ""
        parent_item: Optional[CategoryItem] = None
        for name in names:
            if name == names[-1]:
                item = folder_category_item
            else:
                fullname = f"{last_name}/{name}" if last_name else name
                item = self.__find_category_item_by_name(name, root_category_items)
                if item is None:
                    item = CategoryItem(fullname, 0)
                    self._folder_cache[fullname] = item
                item.count += folder_category_item.count
            if parent_item:
                if item not in parent_item.children:
                    parent_item.children.append(item)
                item.parent = parent_item
            parent_item = item
            last_name = name

        return self._folder_cache.get(names[0])

    def _get_summary_detail_items(self) -> List[FileDetailItem]:
        # Here not sort by all detail items but sort as:
        # - First sort by root folder order
        # - Then sort detail items in every root folder
        return list(
            chain.from_iterable(
                [self.get_detail_items(self._folder_cache[f]) for f in self._root_folders]
            )
        )
