__all__ = ["BrowserFile", "AbstractBrowserFolder", "FileSystemFile", "FileSystemFolder"]

import abc
import asyncio
import os
import re
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import carb
import omni.client
_legacy_nucleus_connector = False
try:
    from omni.kit.widget.nucleus_connector import connect
except ImportError:
    _legacy_nucleus_connector = True
    from omni.kit.widget.nucleus_connector import get_connector_instance

THUMBNAIL_PATH = ".thumbs"
THUMBNAIL_SIZE = 256
THUMBNAIL_FULL_PATH = f"/{THUMBNAIL_PATH}/{THUMBNAIL_SIZE}x{THUMBNAIL_SIZE}"
MAX_RETRY_COUNT = 3


class BrowserFile:
    """
    Represents a single file.
    Args:
        url (str): file url.
        thumbnail (Optional[str]): thumbnail url of file. Default is None.
    """

    def __init__(self, url: str, thumbnail: Optional[str] = None):
        self._url: str = url
        self._thumbnail: str = thumbnail

        # Use prepared to check status of file in folder
        # False means this file in cache and not found in last traverse
        # True means this file was found in last traverse
        self.prepared = True

    def __eq__(self, other: "BrowserFile") -> bool:
        return self.equals(other)

    def __hash__(self):
        return hash((self.url, self.thumbnail))

    def equals(self, other: "BrowserFile") -> bool:
        """
        Check if two file objects are same.
        Returns True means same otherwise False.
        """
        return (self.url == other.url and self.thumbnail == other.thumbnail)

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value

    @property
    def thumbnail(self) -> str:
        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, value: str):
        try:
            if not self.set_thumbnail(value):
                carb.log_warn(f"Thumbnail is still set to {value}")
                # We still set the thumbnail to the given value. This is for backward compatibility.
                self._thumbnail = value
        except Exception as e:
            carb.log_warn(f"Error when setting thumbnail. {e}. Thumbnail is still set to {value}, but it may not belong to this file {self.url}.")
            self._thumbnail = value

    def set_thumbnail(self, thumbnail_url: str) -> bool:
        """
        Check and set thumbnail.
        Args:
            thumbnail (str): Url of thumbnail.
        Return True if the thumbnail belongs to this file, otherwise False.
        """
        thumbnail_name = Path(thumbnail_url).stem
        file_name = self.url.split("/")[-1]

        if thumbnail_name == file_name or thumbnail_name == file_name + ".auto":
            self._thumbnail = thumbnail_url
            return True
        else:
            carb.log_warn(f"Thumbnail {thumbnail_url} does not belong to file {self.url}")
            return False

    def get_default_thumbnail_url(self) -> str:
        """
        Get default thumbnail url.
        """
        output_path = os.path.dirname(self.url) + THUMBNAIL_FULL_PATH
        output_file_name = self.url.split("/")[-1]
        return f"{output_path}/{output_file_name}.png"

class AbstractBrowserFolder:
    """
    Represents the abstract folder. Following functions need to be reimplemented:
        void start_traverse(): Start traverse folder to get sub folders and files

    Args:
        name (str): Folder name
        url (str): Folder url

    Keyword Args:
        ignore_folder_names (Optional[List[str]]): List of folder names. Sub folder with name in this list will be ignored.
            Default is None, means all folders will appear.
        filter_file_fn (callable): Determines a file will appear or not. Return true if appear, otherwise ingored. Default is None. Function signature:
            bool filter_file(url: str)
        on_traversed_fn (callable): Function to notify folder traverse done. Default is None. Function signature:
            void on_traversed_fn(folder: AbstractBrowserFolder)
        list_entry (Optional[omni.client.ListEntry]): folder list entry information. It is read while traversing, save for future usage. Default is None.
        timeout (Optional[float]): Number of seconds to wait for to list/reading from folder. If timeout is None, block until the future completes. Default is 5.

    Overridden functions:
        void start_traverse(): Start travserse to get all sub folders and filess in this folder.
            If traverse done, must set prepared = True and call on_traversed_fn to notify model.
    """

    def __init__(
        self,
        name: str,
        url: str,
        ignore_folder_names: Optional[List[str]] = None,
        filter_file_fn: callable = None,
        on_traversed_fn: callable = None,
        list_entry: Optional[omni.client.ListEntry] = None,
        timeout: Optional[float] = 5.0,
    ):
        self.name = name
        self.url = url
        self.list_entry = list_entry
        self._timeout = timeout

        self._ignore_folder_names = ignore_folder_names
        self._filter_file_fn = filter_file_fn
        self._on_traverse_done_fn = on_traversed_fn

        self.hide_root_in_category = False

        self._init_data()

    def destroy(self):
        pass

    @property
    def file_item_count(self) -> int:
        """Count of file items in this folder displayed in detail view"""
        return len(self.files)

    @abc.abstractmethod
    def start_traverse(self) -> None:
        """Start traverse folder to get sub folders and files"""
        self._init_data()

    def create_file_object(self, url: str) -> BrowserFile:
        """
        Create file object.
        Args:
            url: File Url.
        Return file object.
        """
        return BrowserFile(url)

    def _filter_folder(self, folder_name: str) -> bool:
        """
        Filter folder by name.
        Args:
            folder_name: Name of folder.
        Returns True if valid. Otherwise return False.
        """
        if self._ignore_folder_names is None:
            return True
        else:
            for ignore in self._ignore_folder_names:
                # Convert wild char "." and "*" to regex
                if "?" in ignore:
                    ignore = ignore.replace("?", ".")
                if "*" in ignore:
                    ignore = ignore.replace("*", ".+")
                if re.search(ignore, folder_name):
                    return False

            return True

    async def _on_file_found_async(self, url: str) -> Optional[BrowserFile]:
        """Function when a new file found during traversing."""
        if self._filter_file_fn and not self._filter_file_fn(url):
            return None

        return self.create_file_object(url)

    async def _on_sub_folder_found_async(self, url: str, entry) -> Optional["AbstractBrowserFolder"]:
        """Function when a new sub folder found during traversing."""
        sub_folder = self.create_folder_object(
            url.split("/")[-1],
            url,
            list_entry=entry,
            filter_file_fn=self._filter_file_fn,
            ignore_folder_names=self._ignore_folder_names,
            ignore_file_without_thumbnail=self._ignore_file_without_thumbnail,
            ignore_sub_folder_with_files=self._ignore_sub_folder_with_files,
            ignore_empty_folder=self._ignore_empty_folder,
            timeout=self._timeout,
        )
        self.sub_folders.append(sub_folder)
        return sub_folder

    def _init_data(self) -> None:
        self.prepared: bool = False
        self.has_timeout = False
        self.sub_folders: List[AbstractBrowserFolder] = []
        self.files: List[BrowserFile] = []


class FileSystemFile(BrowserFile):
    """
    Represents a single file system file.
    Args:
        url (str): file url.
        list_entry (Optional[omni.client.ListEntry]): file list entry information. It is read while traversing, save for future usage. Default is None.
        thumbnail (Optional[str]): thumbnail url of file. Default is None.
        thumbnail_list_entry ((Optional[omni.client.ListEntry]): thumbnail list entry information. It is read while traversing, save for future usage. Default is None.
    """

    def __init__(
        self,
        url: str,
        list_entry: Optional[omni.client.ListEntry] = None,
        thumbnail: Optional[str] = None,
        thumbnail_list_entry: Optional[omni.client.ListEntry] = None,
    ):
        super().__init__(url, thumbnail)
        self.list_entry = list_entry
        self.thumbnail_list_entry = thumbnail_list_entry


class FileSystemFolder(AbstractBrowserFolder):
    """
    Represents a folder in file system. Could be local folder or folder on omniverse server.
    Keyword Args:
        root (bool): If a root folder need to check connection status. Default False
        ignore_empty_folder (bool): Ignore empty folder. Default False
        ignore_file_without_thumbnail (bool): Ignore file without thumbnail. Default False

    Overridden functions:
        async bool start_traverse(): Start travserse to get all sub folders and filess in this folder.
            Notices: This is a coroutine and needs to be called in the correct way.
            for example, use await in other coroutine,or use asyncio.ensure_furture.

    Other args and Keyword args: Please refer to AbstractBrowserFolder.
    """

    def __init__(self, *args, **kwargs):
        root = kwargs.pop("root", False)
        self._ignore_empty_folder = kwargs.pop("ignore_empty_folder", False)
        self._ignore_file_without_thumbnail = kwargs.pop("ignore_file_without_thumbnail", False)
        self._ignore_sub_folder_with_files = kwargs.pop("ignore_sub_folder_with_files", False)
        self._cached_file_count = 0
        self._cached_sub_folder_count = 0
        self.has_update = False
        super().__init__(*args, **kwargs)
        if root:
            # If root folder, need to check connection status when list contents
            self._connection_status: Optional[omni.client.ConnectionStatus] = None
            self._subscription = omni.client.register_connection_status_callback(self._on_server_status_changed)
        else:
            # If not root folder, assume connected since checked in root folder
            self._connection_status = omni.client.ConnectionStatus.CONNECTED

    def _on_server_status_changed(self, url, status):
        if self.url.startswith(url):
            carb.log_info(f"[{self.url}] {url}: {status}")
            self._connection_status = status

    def destroy(self) -> None:
        super().destroy()

    async def start_traverse(
        self,
        try_connect_nucleus: bool=True,
        on_connected_fn: Callable[[AbstractBrowserFolder, bool], None] = None
    ) -> bool:
        """
        Start traverse folder to get sub folders and files
        Keyword Args:
            try_connect_nucleus (bool): Try connection to nucleus if not connected. Default True.
            on_connected_fn (Callable): Callback function on connection result.
        Return True if traverse done. Otherwise False means waiting for connection result.
        """
        self.prepared: bool = False
        self.has_timeout = False

        # Now donot clean sub folders and files
        # Instead, let's keep them to check if something changed
        for sub_folder in self.sub_folders:
            sub_folder.prepared = False
        for file in self.files:
            file.prepared = False
        self._cached_sub_folder_count = len(self.sub_folders)
        self._cached_file_count = len(self.files)
        self.has_update = False

        # Verify URL
        result, _ = await omni.client.stat_async(self.url)
        if result == omni.client.Result.OK:
            await self._traverse_folder_async(self.url)
            return True

        if self._connection_status is not None and self._connection_status == omni.client.ConnectionStatus.CONNECTED:
            # Already connected
            carb.log_error(f"Invalid URL: {self.url} with error code {result}")
            return True

        if not try_connect_nucleus:
            carb.log_info(f"Do not try connecting to {self.url}")
            return True

        # Attempt to connect to nucleus server
        broken_url = omni.client.break_url(self.url)
        if broken_url.scheme == 'omniverse':
            server_url = omni.client.make_url(scheme='omniverse', host=broken_url.host)
            def __on_connect_result(result: bool):
                if on_connected_fn:
                    on_connected_fn(self, result)
            # OMPE-31528: Make it compatible with different nucleus connector API
            if _legacy_nucleus_connector:
                nucleus_connector = get_connector_instance()
                if nucleus_connector:
                    carb.log_info(f"Trying to connect {server_url}")
                    nucleus_connector.connect(broken_url.host, server_url,
                        on_success_fn=lambda *_: __on_connect_result(True),
                        on_failed_fn=lambda *_: __on_connect_result(False)
                    )
                    return False
            else:
                carb.log_info(f"Trying to connect {server_url}")
                connect(broken_url.host, server_url,
                    on_success_fn=lambda *_: __on_connect_result(True),
                    on_failed_fn=lambda *_: __on_connect_result(False)
                )
                return False
        else:
            # OM-75623: Without internet connection, url will be invalid
            # But with alias, it may be redirect to a valid url
            # So still try traversing for now.
            carb.log_warn(f"Invalid URL: {self.url}")
            await self._traverse_folder_async(self.url)

        return True

    def create_file_object(self, url: str) -> FileSystemFile:
        """
        Create file object.
        Args:
            url: File Url.
        Return file object.
        """
        return FileSystemFile(url)

    def create_folder_object(self, name: str, url: str, **kwargs) -> AbstractBrowserFolder:
        """
        Create a folder object when a sub folder found. Default using FileSystemFolder.
        User could overridden to create own folder object for special usage.
        Args and keyword args please reference to FileSystemFolder.
        """
        return FileSystemFolder(name, url, **kwargs)

    async def _traverse_folder_async(self, url: str, recurse: bool = True):
        """
        Traverse folder to list files with thumbnail and sub folders
        """
        if not url.endswith("/"):
            url += "/"

        entries = await self._list_folder_async(url)
        if entries:
            thumbnail_paths = []
            files: List[BrowserFile] = []
            sub_folders: List[str] = []
            for entry in entries:
                path = omni.client.combine_urls(url, entry.relative_path)
                #  "\" used in local path, convert to "/"
                path = path.replace("\\", "/")
                if entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
                    if recurse:
                        dirs = path.split("/")
                        sub_folder_name = dirs[-1]
                        if sub_folder_name == THUMBNAIL_PATH:
                            thunmnail_path = url + THUMBNAIL_FULL_PATH
                            # For thumbnail, list it later to make sure files are loaded first
                            thumbnail_paths.append(thunmnail_path)
                        else:
                            if self._filter_folder(sub_folder_name):
                                sub_folders.append(path)
                else:
                    file = await self._on_file_found_async(path)
                    if file:
                        file.list_entry = entry
                        files.append(file)

            # Find thumbnails
            for thumbnail_path in thumbnail_paths:
                await self.__traverse_thumbnail(thumbnail_path, files)

            # Filter valid files
            if self._ignore_file_without_thumbnail:
                files = [file for file in files if file.thumbnail]

            # Compare to cache files and update
            for file in files:
                for cached_file in self.files:
                    if file.equals(cached_file):
                        # Already in cache
                        cached_file.prepared = True
                        if hasattr(cached_file, "list_entry") and hasattr(file, "list_entry") and cached_file.list_entry != file.list_entry:
                            # Update file list entry if different (may be None in cached_file)
                            cached_file.list_entry = file.list_entry
                        break
                else:
                    # Not in cache, either new or thumbnail changed
                    self.files.append(file)

            if not self._ignore_sub_folder_with_files or not self.files:
                # Donot list sub folder if files found in this folder
                for path in sub_folders:
                    for sub_folder in self.sub_folders:
                        if sub_folder.url == path:
                            sub_folder.prepared = True
                            break
                    else:
                        sub_folder = await self._on_sub_folder_found_async(path, entry)
                    if sub_folder:
                        await sub_folder.start_traverse()

            if self._ignore_empty_folder:
                self.sub_folders = [folder for folder in self.sub_folders if folder.files or folder.sub_folders or folder.has_timeout]

            # Timeout
            if not self.has_timeout:
                for sub_folder in self.sub_folders:
                    if sub_folder.has_timeout:
                        self.has_timeout = True
                        break

        self._on_traverse_async_done()

    async def __traverse_thumbnail(self, url: str, files: List[BrowserFile]):
        """
        List all thumbnails and assign to file
        """
        if not url.endswith("/"):
            url += "/"

        entries = await self._list_folder_async(url)
        if entries:
            for entry in entries:
                path = omni.client.combine_urls(url, entry.relative_path)
                if not path.endswith(".png"):
                    continue
                #  "\" used in local path, convert to "/"
                path = path.replace("\\", "/")

                # Assign to related file
                for file in files:
                    if file.set_thumbnail(path):
                        file.thumbnail_list_entry = entry
                        break

    async def _list_folder_async(self, url: str) -> Optional[Tuple[omni.client.ListEntry]]:
        """List files on a omniverse server folder"""
        retry_count = 0
        while retry_count < MAX_RETRY_COUNT:
            if self._connection_status and self._connection_status == omni.client.ConnectionStatus.CONNECTING:
                # Wait for connected
                await asyncio.sleep(1)
            else:
                try:
                    (result, entries) = await asyncio.wait_for(omni.client.list_async(url), timeout=self._timeout)
                    if result == omni.client.Result.OK:
                        return entries
                    else:
                        carb.log_warn(f"Cannot list {url}, error code: {result}.")
                        return None
                except Exception:  # MM-CHANGE: change to always retry, this also handles asyncio.CancelledError
                    if (
                        self._connection_status is None
                        or self._connection_status == omni.client.ConnectionStatus.CONNECTED
                    ):
                        retry_count += 1
                    else:
                        # Not connected, try later
                        carb.log_info(f"[{url}] Not connected, try later")
        else:
            self.has_timeout = True
            carb.log_error(
                f"Timeout {self._timeout} seconds when listing {url}. Please check your network and connection to the url. Otherwise increase the timeout."
            )

    def _on_traverse_async_done(self, loading_completed=True) -> None:
        """Callback when folder traverse done"""
        self.has_update = self._is_folder_updated()
        if self.has_update:
            carb.log_info(f"{self.name} updated")
        self.prepared = True
        if self._on_traverse_done_fn is not None:
            self._on_traverse_done_fn(self, loading_completed=loading_completed, updated=self.has_update)

    def _is_folder_updated(self):
        """
        Check if folder udpated after traverse.
        Changes in either files or sub folder means updated.
        """
        file_update = False
        if len(self.files) != self._cached_file_count:
            file_update = True

        # Files in cache but not in traverse result
        remove_files = [file for file in self.files if not file.prepared]
        if remove_files:
            for remove in remove_files:
                self.files.remove(remove)
            file_update = True

        if file_update:
            self.files.sort(key=lambda item: item.url)

        folder_updated = False
        if len(self.sub_folders) != self._cached_sub_folder_count:
            folder_updated = True

        # Sub folders in cache but not in traverse result
        remove_sub_folders = [folder for folder in self.sub_folders if not folder.prepared]
        if remove_sub_folders:
            for remove in remove_sub_folders:
                self.sub_folders.remove(remove)
            folder_updated = True

        if folder_updated:
            self.sub_folders.sort(key=lambda item: item.name)

        # Still need to look into sub folder to make sure all items in order
        for sub_folder in self.sub_folders:
            # Sub folder already check update status, just read
            if sub_folder.has_update:
                folder_updated = True
                break

        return file_update or folder_updated
