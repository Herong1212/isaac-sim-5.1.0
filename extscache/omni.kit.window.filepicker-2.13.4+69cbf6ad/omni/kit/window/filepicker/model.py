# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["FilePickerModel"]
import asyncio
import re
import urllib
import omni.client

from carb import log_warn
from typing import Callable, List, Tuple
from omni.kit.helper.file_utils import asset_types
from omni.kit.widget.filebrowser import FileBrowserItem
from .style import ICON_PATH, THUMBNAIL_PATH


class FilePickerModel:
    """The model class for :obj:`FilePickerWidget`."""
    def __init__(self, **kwargs):
        self._collections = {}

    @property
    def collections(self) -> dict:
        """[:obj:`FileBrowseItem`]: The collections loaded for this widget"""
        return self._collections

    @collections.setter
    def collections(self, collections: dict):
        self._collections = collections

    def get_icon(self, item: FileBrowserItem, expanded: bool) -> str:
        """
        Returns fullpath to icon for given item. Override this method to implement custom icons.

        Args:
            item (:obj:`FileBrowseritem`): Item in question.
            expanded (bool): True if item is expanded.

        Returns:
            str

        """
        if not item or item.is_folder:
            return None
        return asset_types.get_icon(item.path)

    def get_thumbnail(self, item: FileBrowserItem) -> str:
        """
        Returns fullpath to thumbnail for given item.

        Args:
            item (:obj:`FileBrowseritem`): Item in question.

        Returns:
            str: Fullpath to the thumbnail file, None if not found.

        """
        thumbnail = None
        if not item:
            return None
        parent = item.parent
        # TODO: It's collection name here, don't need to change?
        if parent in self._collections.values() and parent.path.startswith("omniverse"):
            if item.icon.endswith("hdd_plus.svg"):
                # Add connection item
                thumbnail = f"{THUMBNAIL_PATH}/add_mount_drive_256.png"
            else:
                thumbnail = f"{THUMBNAIL_PATH}/mount_drive_256.png"
        elif parent in self._collections.values() and parent.path.startswith("my-computer"):
            thumbnail = f"{THUMBNAIL_PATH}/local_drive_256.png"
        elif item.is_folder:
            thumbnail = f"{THUMBNAIL_PATH}/folder_256.png"
        else:
            thumbnail = asset_types.get_thumbnail(item.path)

        return thumbnail or f"{THUMBNAIL_PATH}/unknown_file_256.png"

    def get_badges(self, item: FileBrowserItem) -> List[Tuple[str, str]]:
        """
        Returns fullpaths to badges for given item. Override this method to implement custom badges.

        Args:
            item (:obj:`FileBrowseritem`): Item in question.

        Returns:
            List[Tuple[str, str]]: Where each tuple is an (icon path, tooltip string) pair.

        """
        if not item:
            return None
        badges = []
        if not item.writeable:
            badges.append((f"{ICON_PATH}/lock.svg", ""))
        if item.is_deleted:
            badges.append((f"{ICON_PATH}/trash_grey.svg", ""))
        return badges

    def find_item_with_callback(self, url: str, callback: Callable = None):
        """
        Searches filebrowser model for the item with the given url. Executes callback on found item.

        Args:
            url (str): Url of item to search for.
            callback (Callable):  Invokes this callback on found item or None if not found. Function signature is
                void callback(item: FileBrowserItem)

        """
        asyncio.ensure_future(self.find_item_async(url, callback))

    async def find_item_async(self, url: str, callback: Callable = None) -> FileBrowserItem:
        """
        Searches model for the given path and executes callback on found item.

        Args:
            url (str): Url of item to search for.
            callback (Callable):  Invokes this callback on found item or None if not found. Function signature is
                void callback(item: FileBrowserItem)

        """
        if not url:
            return None
        url = omni.client.normalize_url(url)
        broken_url = omni.client.break_url(url)

        # OM-103188: First check if it's a collection root
        for col in self._collections.values():
            if col.path == url:
                return col

        path, collection = None, None
        for collection_item in self._collections.values():
            if collection_item.accept_url(url):
                collection = collection_item
                break

        if broken_url.scheme in ['file', None]:
            path = self.sanitize_path(broken_url.path).rstrip('/')
        else:
            path = self.sanitize_path(broken_url.path).strip('/')
            if path:
                path = f"{broken_url.host}/{path}"
            else:
                path = broken_url.host

        item = None
        if path:
            try:
                item = await self.find_item_in_subtree_async(collection, path)
            except asyncio.CancelledError:
                raise
            except Exception:
                pass

            if not item and broken_url.scheme not in ['file', None] and collection:
                # Haven't found the item but we need to try again for connection names that are aliased; for example, a connection
                # with the url "omniverse://ov-content" but renamed to "my-server".
                server = None
                for _, child in collection.children.items():
                    if (broken_url.scheme + "://" + path).startswith(child.path):
                        server = child
                        break
                if server:
                    splits = path.split("/", 1)
                    sub_path = splits[1] if len(splits) > 1 else ""
                    try:
                        item = await self.find_item_in_subtree_async(server, sub_path)
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        pass
        else:
            item = collection

        if item is None:
            log_warn(f"Failed to find item at '{url}'")

        if callback:
            callback(item)

        return item

    async def find_item_in_subtree_async(self, root: FileBrowserItem, path: str) -> FileBrowserItem:
        """
        Finds the given item in the current model recursively asynchronously.

        Args:
            root (:obj: 'FileBrowserItem'): The root item to search.
            path (str): Path of item to search for.

        Returns:
            :obj: 'FileBrowserItem': item that has the path and under the root item.
        """
        if not root:
            # Item not found!
            raise RuntimeWarning(f"Path not found: '{path}'")
        if not path:
            return root

        item = root
        while item:
            # Populate current folder before searching it
            try:
                result = await item.populate_async(item.on_populated_async)
            except asyncio.CancelledError:
                raise

            if isinstance(result, Exception):
                raise result

            for child in item.children.values():
                child_path = child.path[len(root.path):] if child.path.startswith(root.path) else child.path
                if path.startswith(child_path):
                    if child_path == path:
                        # Item found
                        return child
                    elif child_path.endswith("/") or path[len(child_path)] == "/":
                        # Make sure compare the full folder path
                        item = child
                        break
            else:
                # Item not found!
                raise RuntimeWarning(f"Path not found: '{path}'")


    @staticmethod
    def is_local_path(path: str) -> bool:
        """Returns True if given path is a local path"""
        return omni.client.is_local_url(path)

    def _correct_filename_case(self, file: str) -> str:
        """
        Helper function to workaround problem of windows paths getting lowercased

        Args:
            path (str): Raw path

        Returns:
            str

        """
        try:
            import platform, glob, re

            if platform.system().lower() == "windows":
                # get correct case filename
                ondisk = glob.glob(re.sub(r'([^:/\\])(?=[/\\]|$)|\[', r'[\g<0>]', file))[0].replace("\\", "/")
                # correct drive letter case
                if ondisk[0].islower() and ondisk[1] == ":":
                    ondisk = ondisk[0].upper() + ondisk[1:]
                # has only case changed
                if ondisk.lower() == file.lower():
                    return ondisk
        except Exception as exc:
            pass
        return file

    def sanitize_path(self, path: str) -> str:
        """
        Helper function for normalizing a path that may have been copied and pasted int to browser
        bar. This makes the tool more resiliant to user inputs from other apps.

        Args:
            path (str): Raw path

        Returns:
            str

        """
        # Strip out surrounding white spaces
        path = path.strip() if path else ""
        if not path:
            return path
        path = omni.client.normalize_url(path)
        path = urllib.parse.unquote(path).replace("\\", "/")
        return self._correct_filename_case(path)

    def destroy(self):
        """ Destructor """
        self._collections = None
