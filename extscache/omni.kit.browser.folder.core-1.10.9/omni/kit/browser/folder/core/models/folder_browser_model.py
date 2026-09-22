__all__ = ["FolderBrowserModel"]

import asyncio
import json
import os
import time
import traceback
from itertools import chain
from typing import Callable, Dict, List, Optional, Set, Union

import carb
import carb.tokens
import omni.kit.app
from omni.kit.browser.core import AbstractBrowserModel, CategoryItem

from .folder_browser_data import AbstractBrowserFolder, BrowserFile, FileSystemFolder
from .folder_browser_item import FileDetailItem, FolderCategoryItem, FolderCollectionItem

REMOTE_FOLDER_PREFIX = "omniverse://"
PERSISTENT_SETTING_PREFIX = "/persistent"


class FolderBrowserModel(AbstractBrowserModel):
    """
    Represents the browser model for folders.

    Keyword Args:
        filter_file_suffixes (Optional[List[str]]): List of file suffixes. Files with suffix not in this list will be ignored. Default is None, means all file suffixes will appear.
        ignore_folder_names (Optional[List[str]]): List of folder names. Folder with name in this list will be ignored. Default is None, means all folders will appear.
        show_empty_folders (bool): If true, show empty folders (no files in the folder). Otherwise, hide empty folders. Default is False.
        show_summary_folder (bool): If true, show a summary folder (named "ALL") with all files in all folders. Otherwise, donot show such a folder. Default is True.
        setting_folders (Optional[str]): Setting path to save/load root folders
        create_file_object_fn (callable): Function called when creating a file object. Default is creating a BrowserFile. Function signature: Optional[BrowserFile] create_file_object_fn(url: str)
        timeout (Optional[float]): Number of seconds to wait for to list/reading from folder. If timeout is None, block until the future completes. Default is 5.
        category_tree_mode (bool): Show collections/categories in treeview mode
        local_cache_file(str):  Define the local cache file name for the model to be cached locally. If it is None, no local file cache will be stored.
        run_warmup (bool): If run in warmup. Default False.

    Overridden functions:
        bool filter_file(url: str): Determines a file will appear or not. Return true if appear, otherwise ingored. Default check file suffix with keyword args filter_file_suffixes.
            Args:
                url (str): Url of file.
        void execute(self, item: FileDetailItem): Execute a file.
            Args:
                item: File detail item to be executed.
        void sort_items(items: List[Union[FolderCollectionItem, FolderCollectionItem, DetailItem]]): Sort kinds of browser items. Default sort by name.
            Args:
                items (List[Union[FolderCollectionItem, FolderCollectionItem, DetailItem]]): List of browser items to be sorted.
        FolderCollectionItem create_collection_item(folder: AbstractBrowserFolder):  Create a collection item from a folder.
            Args:
                folder (AbstractBrowserFolder): Folder object to create collection item
        FolderCategoryItem create_category_item(folder: AbstractBrowserFolder): Create a category item from a folder.
            Args:
                folder (AbstractBrowserFolder): Folder object to create category item
        Union[FileDetailItem, List[FileDetailItem] create_detail_item(file: BrowserFile): Create detail item(s) from a file
            Args:
                file (BrowserFile): File object to create detail item
        AbstractBrowserFolder create_folder_object(*args, **kwargs): Create folder object when a root folder appended.
            Args and keyword args: please refer to FileSystemFolder

    """

    SUMMARY_FOLDER_NAME = "All"
    COUNT_LOADING = "..."
    COUNT_TIMEOUT = "Timeout"

    def __init__(
        self,
        filter_file_suffixes: Optional[List[str]] = None,
        ignore_folder_names: Optional[List[str]] = None,
        show_empty_folders: bool = False,
        show_summary_folder: bool = True,
        setting_folders: Optional[str] = None,
        create_file_object_fn: callable = None,
        hide_file_without_thumbnails: bool = False,
        show_category_subfolders: bool = False,
        timeout: Optional[float] = 5.0,
        category_tree_mode: bool = False,
        local_cache_file: str = None,
        run_warmup: bool = False,
        ignore_sub_folder_with_files: bool = False,
        custom_folders_setting: Optional[str] = None
    ):
        super().__init__()

        if category_tree_mode:  # pragma: no cover
            carb.log_warn("'category_tree_mode' deprecated in FolderBrowserModel. Use TreeFolderBrowserModel instead")
        self._root_collection_item: Optional[FolderCollectionItem] = None
        self._root_folders: List[AbstractBrowserFolder] = []
        self._filter_file_suffixes = filter_file_suffixes
        self._ignore_folder_names = ignore_folder_names
        self._show_empty_folders = show_empty_folders
        self._show_summary_folder = show_summary_folder
        self._create_file_object_fn = create_file_object_fn
        self._hide_file_without_thumbnails = hide_file_without_thumbnails
        self._show_category_subfolders = show_category_subfolders
        self._ignore_sub_folder_with_files = ignore_sub_folder_with_files
        self._timeout = timeout
        self._stop_event = asyncio.Event()
        self._work_queue = asyncio.Queue()
        self._traverse_in_queue: List[str] = []
        self._custom_folder_path: Optional[str] = custom_folders_setting
        self._custom_folder_sub: Optional[int] = None
        self._custom_folders: Set[str] = set()

        # Read alias from omniverse config to replace folder url if defined
        try:
            import toml

            global_config_path = carb.tokens.get_tokens_interface().resolve("${omni_global_config}")
            omniverse_config_path = os.path.join(global_config_path, "omniverse.toml").replace("\\", "/")
            omni_config = toml.load(omniverse_config_path)
            self.__alias_configs = omni_config.get("aliases", {})
        except:  # pragma: no cover
            self.__alias_configs = {}

        # If folder loading not completed, show category count with COUNT_LOADING instead of number
        self._loading_completed = True

        self._json_file = None
        if local_cache_file and local_cache_file.endswith(".json"):
            self._json_file = carb.tokens.get_tokens_interface().resolve(local_cache_file)

        # Cache of browser items
        self._folder_cache: Dict[
            Union[AbstractBrowserFolder, BrowserFile, str],
            Union[FolderCollectionItem, FolderCategoryItem, CategoryItem, FileDetailItem]
        ] = {}

        self._settings = carb.settings.get_settings()

        # Load root folders from settings
        if setting_folders is not None:
            if setting_folders.startswith(PERSISTENT_SETTING_PREFIX):
                self._setting_folders = setting_folders  # pragma: no cover
            else:
                self._setting_folders = PERSISTENT_SETTING_PREFIX + setting_folders

            # load root folders from setting
            root_folders = self._settings.get(self._setting_folders)
            if not root_folders:
                if self._setting_folders != setting_folders:
                    root_folders = self._settings.get(setting_folders)
            if root_folders:
                for root_folder in root_folders:
                    if root_folder:
                        self.process_root_folder(root_folder, sync=False)
        else:
            self._setting_folders = None

        # load root folders from additional folder settings. Add watcher on property to refresh on change
        if self._custom_folder_path:
            additional_root_folders = list(self._settings.get(self._custom_folder_path))
            for root_folder in additional_root_folders:
                self.process_root_folder(root_folder, sync=False)
                self._custom_folders.add(root_folder)
            self._custom_folder_sub = omni.kit.app.SettingChangeSubscription(
                self._custom_folder_path, self._on_custom_folders_changed
            )

        self.__traverse_future = asyncio.ensure_future(self._run())

        self.on_refresh_categories: Callable[[None], None] = None

        if run_warmup:
            self.__warmup()

    def process_root_folder(self, root_folder: str, sync: bool=True) -> Optional[FileSystemFolder]:
        """
        Process a root folder name and url and add it to the list of root folders.

        Args:
            root_folder: Name of root folder with optional prepended collection name.
        """
        fields = root_folder.split("::")
        if len(fields) == 1:
            return self.append_root_folder(root_folder, save=False, sync=sync)
        elif len(fields) == 2:
            return self.append_root_folder(fields[1], name=fields[0], save=False, sync=sync)
        else:
            carb.log_error(f"Unknown folder format: {root_folder}")
            return None

    def destroy(self):
        self._stop_event.set()
        self._work_queue.put_nowait(None)
        self.__traverse_future.cancel()
        self.on_refresh_categories = None

        for root_folder in self._root_folders:
            for sub_folder in root_folder.sub_folders:
                sub_folder.destroy()
            root_folder.destroy()

        self._custom_folder_sub = None

    def register_folder(self, url: str, name: Optional[str] = None) -> None:   # pragma: no cover - never called
        """
        Register a folder path with the model.
        Args:
            url (str): Url of folder
            name (Optional[str]): Name of folder. Default is None.
        """
        if name:
            url = f"{name}::{url}"
        carb.log_info(f"Registering root folder: {url}")
        self.process_root_folder(url)

    def unregister_folder(self, url: str) -> None:   # pragma: no cover - never called
        """
        Unregister a folder path with the model when finished with it.
        Args:
            url (str): Url of folder
        """
        self.remove_root_folder(url)

    def append_root_folder(self, url: str, name: Optional[str] = None, save: bool = True, sync: bool=True) -> Optional[FileSystemFolder]:
        """
        Append a root folder.
        Return FileSystemFolder object is appended, otherwise None means url already exists.
        Args:
            url (str): Url of folder
            name (Optional[str]): Name of folder. Default is None, means use last directory name as collection name.
            save (bool): True to save current root folder to settings if setting path defined. False means nothing saved.
        """
        url = carb.tokens.get_tokens_interface().resolve(url)
        url = url.replace("\\", "/")
        if url.endswith("/"):
            url = url[:-1]

        if self.get_root_folder(url):
            return None  # pragma: no cover

        if name is None:
            name = url.split("/")[-1]

        def __is_name_valid(name) -> bool:
            if self._root_folders:
                for root_folder in self._root_folders:
                    if root_folder.name == name:
                        return False
            return True

        def __get_next_valid_name(name) -> str:
            if __is_name_valid(name):
                return name

            for index in range(1, 100):
                next = f"{name}_{index}"
                if __is_name_valid(next):
                    return next
            else:
                return name

        name = __get_next_valid_name(name)
        folder = self._create_folder_object_by_url(
            name,
            url,
            on_traversed_fn=self._on_folder_traversed,
            root=True,
        )
        self._root_folders.append(folder)

        if save:
            self._save_root_folders()

        if sync:
            self.folder_changed(folder)
        return folder

    def remove_root_folder(self, url: str) -> bool:
        """
        Remove a root folder
        Return True if succeeded, otherwise False.
        Args:
            url (str): Url of root folder to be removed.
        """
        url = carb.tokens.get_tokens_interface().resolve(url)
        url = url.replace("\\", "/")
        root_folder = self.get_root_folder(url)
        if root_folder:
            if root_folder in self._folder_cache:
                # Some root_folders can be lower in the hierarchy
                item = self._folder_cache[root_folder]
                if hasattr(item, "parent"):
                    if item.parent:
                        item.parent.children.remove(item)
                        parent = item.parent
                        # Decrement item counts for ancestors of the removed folder
                        while parent is not None:
                            parent.count -= item.count
                            self._item_changed(parent)
                            parent = parent.parent
                self._folder_cache.pop(root_folder)
            self._root_folders.remove(root_folder)
            if root_folder.url in self._traverse_in_queue:
                self._traverse_in_queue.remove(root_folder.url)

            self._save_root_folders()
            self.folder_changed(root_folder)
            return True
        else:  # pragma: no cover
            carb.log_error(f"Folder {url} does not exist!")
            return False

    def get_root_folder(self, url: str) -> Optional[AbstractBrowserFolder]:
        """
        Find a root folder
        Return folder object if succeeded, otherwise False.
        Args:
            url (str): Url of root folder to find.
        """
        url = url.replace("\\", "/")
        if url.endswith("/"):
            url = url[:-1]
        for root_folder in self._root_folders:
            if root_folder.url == url:
                return root_folder
        return None

    def folder_changed(self, item: Union[AbstractBrowserFolder, BrowserFile, None]) -> None:
        """
        Notify folder or file changed.
        Args:
            item (Union[AbstractBrowserFolder, BrowserFile]): Changed folder or file object.
        """
        if item is None:
            self._item_changed(None)
        else:
            # Remove cached browser item related to the item
            self.__clear_folder_cache(item)
            browser_item = self._folder_cache.get(item, None)
            if browser_item:
                self._item_changed(browser_item)
            else:
                # New folder
                self._item_changed(None)

    def _on_custom_folders_changed(self, item, event):
        """
        Remove and Add folders that change between updates
        """
        if event == carb.settings.ChangeEventType.CHANGED:
            custom_folder_raw = self._settings.get(self._custom_folder_path) or []  # In the case the property is None
            new_folders, old_folders = set(custom_folder_raw), set(self._custom_folders)
            added, deleted = new_folders - old_folders, old_folders - new_folders

            for folder in deleted:
                self.remove_root_folder(folder)

            for folder in added:
                self.process_root_folder(folder, sync=True)

            self._custom_folders = new_folders

    def start_traverse(self, folder: FileSystemFolder, force: bool=False):
        if folder.url not in self._traverse_in_queue or force:
            carb.log_info(f"Add folder to queue: {folder.url}")
            self._traverse_in_queue.append(folder.url)
            self._work_queue.put_nowait(folder)

    def get_collection_items(self) -> List[FolderCollectionItem]:
        """Override to get list of collection items"""
        collection_items = []

        for root_folder in self._root_folders:
            if root_folder not in self._folder_cache:
                self._folder_cache[root_folder] = self.create_collection_item(root_folder)
            collection_items.append(self._folder_cache[root_folder])

        # fill self._root_folders with local cache
        self._load_data_from_json()

        # For collections, keep the order of settings
        # self.sort_items(collection_items)

        return collection_items

    def get_category_items(self, item: FolderCollectionItem) -> List[FolderCategoryItem]:
        """Override to get list of category items"""

        root_folder = item.folder
        if root_folder is None:
            return []

        if not root_folder.prepared:
            # Traverse folder to update all sub folders and files now
            self.start_traverse(root_folder)

        category_items = []
        summary_count = 0
        has_timeout = root_folder.has_timeout
        for sub_folder in root_folder.sub_folders:
            if sub_folder not in self._folder_cache:
                self._folder_cache[sub_folder] = self.create_category_item(sub_folder)
            category_item = self._folder_cache[sub_folder]
            if sub_folder.has_timeout:
                category_items.append(category_item)
            elif category_item.count > 0:
                category_items.append(category_item)
                summary_count += category_item.count
            elif self._show_empty_folders:  # pragma: no cover
                category_items.append(category_item)

            # If loading not completed, do not show category number
            if not self._loading_completed:
                category_item.count = self.COUNT_LOADING

        self.sort_items(category_items)
        if self._show_summary_folder:
            if has_timeout:
                summary_count = self.COUNT_TIMEOUT
            elif not self._loading_completed:
                summary_count = self.COUNT_LOADING
            category_items.insert(0, FolderCategoryItem(self.SUMMARY_FOLDER_NAME, summary_count, item.folder))

        return category_items

    def get_detail_items(self, item: CategoryItem) -> List[FileDetailItem]:
        """Override to get list of detail items"""
        detail_items = []

        if item.name == self.SUMMARY_FOLDER_NAME:
            # List all files in sub folders
            for sub_folder in item.folder.sub_folders:
                detail_items += self._get_folder_detail_items(sub_folder)
        elif isinstance(item, FolderCategoryItem):
            # List files in item folder
            detail_items = self._get_folder_detail_items(item.folder)
        else:  # CategoryItem
            return list(chain.from_iterable([self.get_detail_items(c) for c in item.children]))

        self.sort_items(detail_items)
        return detail_items

    def remove_collection(self, item: FolderCollectionItem) -> bool:
        url = item.folder.url
        return self.remove_root_folder(url)

    def get_folder_item(self, folder: FileSystemFolder) -> FolderCategoryItem:
        return self._folder_cache.get(folder, None)

    def _get_folder_detail_items(self, folder: AbstractBrowserFolder) -> List[FileDetailItem]:
        """Get list of detail items from a folder"""
        detail_items = []
        for file in folder.files:
            # with that option files that don't have thumbnails are hidden
            if self._hide_file_without_thumbnails and not file.thumbnail:
                continue

            if file not in self._folder_cache:
                self._folder_cache[file] = self.create_detail_item(file)

            if isinstance(self._folder_cache[file], list):
                detail_items.extend(self._folder_cache[file])
            else:
                detail_items.append(self._folder_cache[file])

        # we will have some means to make it configured by the user right now it is fixed at the
        # browser level
        if self._show_category_subfolders:
            for sub_folder in folder.sub_folders:
                detail_items = detail_items + self._get_folder_detail_items(sub_folder)

        return detail_items

    def _on_folder_traversed(self, folder: AbstractBrowserFolder, loading_completed=True, updated: bool=True) -> None:
        """Callback when folder traverse done"""
        carb.log_info(f"Traverse completed: {folder.url}, {loading_completed}")
        self._loading_completed = loading_completed

        if folder in self._root_folders:
            self.folder_changed(folder)
            self._save_data_to_json(folder)

    def filter_file(self, url: str) -> bool:
        """
        Check a file if valid or not.
        Return true if valid, otherwise false.
        If filter_file_suffixes not defined, always valid. Otherwise only valid if in valid_file_suffixed.
        Args:
            url (str): Url of file.
        """
        if self._filter_file_suffixes is not None:
            for ext in self._filter_file_suffixes:
                if url.lower().endswith(ext.lower()):
                    return True
            else:
                return False
        else:
            return True

    def sort_items(self, items: List[Union[FolderCollectionItem, FolderCollectionItem, FileDetailItem]]) -> None:
        """
        Sort kinds of browser items by name.
        Args:
            items (List[Union[FolderCollectionItem, FolderCollectionItem, FileDetailItem]]): List of browser items to be sorted.
        """
        items.sort(key=lambda item: item.name)

    def create_collection_item(self, folder: AbstractBrowserFolder) -> FolderCollectionItem:
        """
        Create a collection item from a folder.
        Args:
            folder (AbstractBrowserFolder): Folder object to create collection item
        """
        return FolderCollectionItem(folder.name, folder.url, folder)

    def create_category_item(self, folder: AbstractBrowserFolder,
                             parent: Optional[CategoryItem] = None) -> FolderCategoryItem:
        """
        Create a category item from a folder.
        Args:
            folder (AbstractBrowserFolder): Folder object to create category item
        """
        if folder.has_timeout:
            count = self.COUNT_TIMEOUT
        else:
            count = self.__get_folder_count(folder)

            if self._show_category_subfolders:

                def recursive_count(current_count, folder: AbstractBrowserFolder) -> int:
                    for sub_folder in folder.sub_folders:
                        if self._hide_file_without_thumbnails:
                            for file in sub_folder.files:
                                if file.thumbnail:
                                    current_count += 1
                        else:
                            current_count += len(sub_folder.files)
                        current_count = recursive_count(current_count, sub_folder)

                    return current_count

                count = recursive_count(count, folder)

        return FolderCategoryItem(folder.name, count, folder, parent)

    def create_detail_item(self, file: BrowserFile) -> Union[FileDetailItem, List[FileDetailItem]]:
        """
        Create detail item(s) from a file.
        A file may includs multi detail items.
        Args:
            file (BrowserFile): File object to create detail item(s)
        """
        dirs = file.url.split("/")
        name = dirs[-1]

        return FileDetailItem(name, file.url, file, file.thumbnail)

    def create_folder_object(self, *args, **kwargs) -> AbstractBrowserFolder:
        """
        Create a folder object when a root folder appended. Default using FileSystemFolder.
        User could overridden to create own folder object for special usage.
        Args and keyword args please reference to FileSystemFolder.
        """
        return FileSystemFolder(*args, **kwargs)

    def _save_root_folders(self):
        # save to settings
        if not self._setting_folders:
            return
        folder_settings = []
        for root_folder in self._root_folders:
            folder_settings.append(f"{root_folder.name}::{root_folder.url}")
        self._settings.set(self._setting_folders, folder_settings)

    def _save_folder_to_json(self, folder: AbstractBrowserFolder, parent: Optional[AbstractBrowserFolder] = None) -> Dict:
        # collection
        folder_url = folder.url
        output = {"url": folder_url, "sub_folders": {}}
        # category
        for sub_folder in folder.sub_folders:
            sub_folder_url = sub_folder.url
            category_item = {"url": os.path.relpath(sub_folder_url, folder_url), "files": {}}
            output["sub_folders"][sub_folder.name] = category_item
            # detail
            for file in sub_folder.files:
                thumbnail = file.thumbnail
                if thumbnail:
                    thumbnail = os.path.relpath(thumbnail, sub_folder_url)
                detail_item = {
                    "url": os.path.relpath(file.url, sub_folder_url),
                    "thumbnail": thumbnail
                }

                name = file.url.split("/")[-1]
                output["sub_folders"][sub_folder.name]["files"][name] = detail_item
        return output

    def _load_folder_from_json(self, data: Dict, folder: AbstractBrowserFolder):
        # category
        sub_folders = data["sub_folders"]
        for category_item in sub_folders:
            category_data = sub_folders[category_item]
            folder_url = folder.url + "/" + category_data["url"]
            category_folder = self._create_folder_object_by_url(category_item, folder_url)
            # files
            files = category_data["files"]
            for file_item in files:
                file_data = files[file_item]
                thumbnail = file_data["thumbnail"]
                if thumbnail:
                    thumbnail = folder_url + "/" + thumbnail
                file = BrowserFile(folder_url + "/" + file_data["url"], thumbnail)
                category_folder.files.append(file)
            folder.sub_folders.append(category_folder)

    def _save_data_to_json(self, folder: AbstractBrowserFolder):
        if not self._json_file:
            return

        start = time.time()
        try:
            with open(self._json_file) as json_file:
                json_decoded = json.load(json_file)
        except FileNotFoundError:
            json_decoded = {}
        except PermissionError:
            carb.log_error(f"Cannot write to {self._json_file}: permission denied!")
            return
        except Exception as exc:
            carb.log_error(f"Unknown failure to save to {self._json_file}: {exc}")
            return

        json_decoded[folder.name] = self._save_folder_to_json(folder, None)

        with open(self._json_file, 'w') as json_file:
            json.dump(json_decoded, json_file, indent=4)
            if json_file:
                json_file.close()

        carb.log_info(f"Save folder {folder.url} to cache: {time.time() - start:.2f} seconds")

    def _load_data_from_json(self, check_only: bool=False):
        if not self._json_file:
            return

        start = time.time()
        asset_json = None
        try:
            with open(self._json_file, "r") as json_file:
                asset_json = json.load(json_file)
        except FileNotFoundError:
            carb.log_info(f"Failed to open {self._json_file}!")
            return
        except PermissionError:
            carb.log_error(f"Cannot read {self._json_file}: permission denied!")
            return
        except Exception as exc:
            carb.log_error(f"Unknown failure to read {self._json_file}: {exc}")
            return

        if asset_json is None:
            return
        # collection
        for root_folder in self._root_folders:
            if not root_folder.prepared and root_folder.name in asset_json:
                saved_url = asset_json[root_folder.name]["url"]
                # OM-75630: If folder url redirected, do not load from cache
                saved_url = saved_url.replace("\\", "/")
                if saved_url == root_folder.url:
                    if not check_only:
                        self._load_folder_from_json(asset_json[root_folder.name], root_folder)
                    root_folder.has_cache = True
                else:
                    carb.log_warn(f"Do not load cache for {root_folder.name} because url changed:")
                    carb.log_warn(f" - from {saved_url}")
                    carb.log_warn(f" -   to {root_folder.url}")
                    root_folder.has_cache = False

        carb.log_info(f"Load folders from cache: {time.time() - start:.5f} seconds")

    def __get_folder_count(self, folder: AbstractBrowserFolder) -> int:
        if self._hide_file_without_thumbnails:
            return len([file for file in folder.files if file.thumbnail])
        else:
            return len(folder.files)

    async def _run(self):
        while not self._stop_event.is_set():
            folder: AbstractBrowserFolder = await self._work_queue.get()
            if folder is None:
                break
            else:
                try:
                    start_time = time.time()
                    carb.log_info(f"Start traverse from queue: {folder.url}")
                    category_item = self._folder_cache.get(folder, None)
                    if category_item:
                        category_item.loading = True
                        # only need to update loading status
                        self._item_changed(category_item)
                    done = await folder.start_traverse(on_connected_fn=self.__on_server_connected)
                    if done:
                        carb.log_info(f"[{time.time() - start_time:.2f} s] End traverse {folder.url}")
                        if category_item:
                            category_item.loading = False
                        self.folder_changed(folder)

                except Exception as e:
                    carb.log_error(f"Exception when traverse: {folder.url}, {e}")
                    exc = traceback.format_exc()
                    carb.log_error(f"[omni.ui.tests.compare] Traceback:\n{exc}")

    def __warmup(self):

        async def __cache_all_folders_async():
            self._load_data_from_json(check_only=True)
            for folder in self._root_folders:
                try:
                    if hasattr(folder, "has_cache") and folder.has_cache:
                        carb.log_info(f"Already has cache for {folder.url}, ignore.")
                    else:
                        carb.log_info(f"Caching {folder.url}")
                        # Do not try connecting to nucleus server during warmup
                        await folder.start_traverse(try_connect_nucleus=False)
                        self._save_data_to_json(folder)
                        carb.log_info(f"Cached {folder.url}")
                except Exception as e:
                    carb.log_info(f"Exception when caching: {folder.url}, {e}")

        loop = asyncio.events.new_event_loop()
        loop.run_until_complete(__cache_all_folders_async())
        loop.close()

    def _create_folder_object_by_url(self, name: str, url: str, **kwargs) -> FileSystemFolder:
        # OM-75623: Replace url if alias defined in omniverse.toml
        url = url.replace("\\", "/")
        for alias, value in self.__alias_configs.items():
            alias = alias.replace("\\", "/")
            value = value.replace("\\", "/")
            if alias.endswith("/"):
                alias = alias[:-1]
            if url.startswith(alias):
                carb.log_info(f"Replace url with alias:")
                carb.log_info(f"  from: {url}")
                url = url.replace(alias, value)
                carb.log_info(f"  to: {url}")
                break

        return self.create_folder_object(
            name,
            url,
            ignore_file_without_thumbnail=self._hide_file_without_thumbnails,
            ignore_empty_folder=not self._show_empty_folders,
            ignore_folder_names=self._ignore_folder_names,
            ignore_sub_folder_with_files=self._ignore_sub_folder_with_files,
            filter_file_fn=self.filter_file,
            timeout=self._timeout,
            **kwargs
        )

    def __clear_folder_cache(self, folder: AbstractBrowserFolder) -> None:
        for sub_folder in folder.sub_folders:
            self._folder_cache.pop(sub_folder, None)
            for file in sub_folder.files:
                self._folder_cache.pop(file, None)
            self.__clear_folder_cache(sub_folder)

    def __on_server_connected(self, folder: AbstractBrowserFolder, result: bool) -> None:
        if result:
            # Server connected, traverse folder again
            carb.log_info(f"Connected to {folder.url}!")
            # Remove from traverse queue and add it back
            self._traverse_in_queue.remove(folder.url)
            self.start_traverse(folder)
        else:
            carb.log_error(f"Invalid URL: {folder.url}!")
