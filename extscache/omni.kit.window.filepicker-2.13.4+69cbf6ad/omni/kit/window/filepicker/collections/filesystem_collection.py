import asyncio
from datetime import datetime
import os
import platform
import traceback
from typing import Callable, Any, Optional, Dict

import carb
import omni.client
from omni.kit.widget.filebrowser import FileSystemItem, FileBrowserItemFields
import omni.ui as ui
from .collection_item import CollectionItem
from ..style import ICON_PATH
from ..utils import get_user_folders_dict


class FileSystemCollectionItem(CollectionItem):
    def __init__(self):
        """
        Collection for local drives and mounted folders.
        """
        super().__init__("my-computer", "My Computer", f"{ICON_PATH}/my_computer.svg", populated=False, order=30)

    def create_child_item(self, name: str, path: str, is_folder: bool = True) -> Optional[FileSystemItem]:
        """
        Create a connection item.

        Args:
            name (str): Name of the connection.
            path (str): Path of the connection.
            is_folder (bool): Whether the connection is a folder.

        Returns:
            :obj:`FileSystemItem`: The created connection item.
        """
        if not path.endswith("/"):
            path += "/"
        access = omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE
        fields = FileBrowserItemFields(name, datetime.now(), 0, access)
        item = FileSystemItem(path, fields, is_folder=True)
        item._models = (ui.SimpleStringModel(item.name), datetime.now(), ui.SimpleStringModel(""))
        item._enable_sorting = True

        return item

    def accept_url(self, url: str) -> bool:
        """
        Check if the url is accepted by the collection.

        Args:
            url (str): Url to check.

        Returns:
            bool: True if the url is accepted, False otherwise.
        """
        try:
            broken_url = omni.client.break_url(url)
            identifier = broken_url.scheme
            return identifier == "file" or identifier is None
        except Exception:
            carb.log_warn(f"Cannot parse url: {url}")
            return False

    async def populate_children_async(self) -> Any:
        try:

            if platform.system().lower() == "linux":
                from .. import disk_partitions
                partitions = disk_partitions.disk_partitions()

                # OM-76424: Pre-filter some of the local directories that are of interest for users
                filtered_partitions = []
                for partition in partitions:
                    if any(x in partition.opts for x in ('nodev', 'nosuid', 'noexec')):
                        continue
                    if partition.fstype in ('tmpfs', 'proc', 'devpts', 'sysfs', 'nsfs', 'autofs', 'cgroup', 'hugetlbfs'):
                        continue
                    filtered_partitions.append(partition)
                partitions = filtered_partitions

                # OM-76424: Ensure that "/" is always there, because disk_partitions() will ignore it sometimes.
                if not any(p.mountpoint == "/" for p in partitions):
                    from types import SimpleNamespace
                    e = SimpleNamespace()
                    e.mountpoint = "/"
                    e.opts = "fixed"
                    partitions.insert(0, e) # first entry

            elif platform.system().lower() == "windows":
                from ctypes import windll
                # GetLocalDrives returns a bitmask with with bit i set meaning that
                # the logical drive 'A' + i is available on the system.
                logicalDriveBitMask = windll.kernel32.GetLogicalDrives()

                from types import SimpleNamespace
                partitions = list()
                # iterate over all letters in the latin alphabet
                for bit in range(0, (ord('Z') - ord('A') + 1)):
                    if logicalDriveBitMask & (1 << bit):
                        e = SimpleNamespace()
                        e.mountpoint = chr(ord('A') + bit) + ":"
                        e.opts = "fixed"
                        partitions.append(e)
            else:
                from . import disk_partitions
                partitions = disk_partitions.disk_partitions()
        except (ImportError, ModuleNotFoundError):
            carb.log_warn("Warning: Could not import disk_partitions")
            return
        except Exception:
            carb.log_warn(traceback.format_exc())
            return
        else:
            # OM-51243: Show OV Drive (O: drive) after refresh in Create
            user_folders = get_user_folders_dict()
            self.mount_user_folders(user_folders)
            # we should check all old Drive at first, but keep the user folder
            old_drives = []
            for name in self._children:
                if name not in user_folders:
                    old_drives.append(name)

            # then check current Drive
            current_drives = []
            for p in partitions:
                if any(x in p.opts for x in ["removable", "fixed", "rw", "ro", "remote"]):
                    mountpoint = p.mountpoint.rstrip("\\")
                    current_drives.append(mountpoint)

            # refresh drives only when there is new drive
            if set(old_drives) != set(current_drives):
                for old_drive in old_drives:
                    self.del_child(old_drive)
                for current_drive in current_drives:
                    self.add_path(current_drive, current_drive)

    def mount_user_folders(self, folders: Dict[str, str]) -> None:
        """
        Mounts given set of user folders under the local collection.

        Args:
            folders (dict): Name, path pairs.

        """
        if not folders:
            return

        for name, path in folders.items():
            if name not in self._children and os.path.exists(path):
                self.add_path(name, path)