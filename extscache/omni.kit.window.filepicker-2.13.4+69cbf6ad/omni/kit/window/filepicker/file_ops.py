# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import sys
import subprocess
import asyncio
import omni.client
import carb.settings
import omni.kit.notification_manager
import omni.kit.app
import omni.ui as ui

from datetime import datetime
from carb import log_warn
from typing import Callable, List, Optional, Dict, Any
from functools import partial
from omni.kit.widget.filebrowser import FileBrowserItem, NucleusConnectionItem
from omni.kit.widget.filebrowser import FileBrowserItemFields
from omni.kit.notification_manager import NotificationStatus
from omni.kit.window.popup_dialog import InputDialog, MessageDialog, FormDialog
from .view import FilePickerView
from .collections.bookmark_collection import BookmarkItem
from .collections.collection_item import CollectionItem
from .versioning_helper import VersioningHelper
from .item_deletion_dialog import ConfirmItemDeletionDialog
from .about_dialog import AboutDialog


async def _check_paths_exist_async(paths: List[str]) -> List[str]:
    """Check if paths already exist."""
    paths_already_exist = []
    for path in paths:
        result, _ = await omni.client.stat_async(path)
        if result == omni.client.Result.OK:
            paths_already_exist.append(path)
    return paths_already_exist


def is_usd_supported() -> bool:
    """
    Check if USD is supported.

    Returns:
        bool: True if support usd or False.
    """
    try:
        from pxr import Usd, Sdf, UsdGeom
    except Exception:
        return False
    return True


async def is_item_checkpointable(context: Dict[str, Any], menu_item: ui.MenuItem):
    """
    Checks if an item is checkpointable. Show the correspond menu item when it's true.

    Args:
        context(Dict[str, Any]): The context of the menu.
        menu_item(:obj:'ui.MenuItem'): The menu item to be shown on
    """
    if "item" in context:
        path = context["item"].path
        if VersioningHelper.is_versioning_enabled():
            if await VersioningHelper.check_server_checkpoint_support_async(
                VersioningHelper.extract_server_from_url(path)
            ):
                menu_item.visible = True


def add_bookmark(item: FileBrowserItem, view: FilePickerView):
    """
    Add a bookmark to the file browser item with a dialog.

    Args:
        item(:obj:'FileBrowserItem'): The item that was selected.
        view(:obj:'FilePickerView'): The view to add the bookmark to.
    """

    def on_okay(dialog: InputDialog, item: FileBrowserItem, view: FilePickerView):
        name = dialog.get_value("name")
        url = dialog.get_value("address")
        try:
            view.add_bookmark(name, url, is_folder=item.is_folder)
        except Exception as e:
            log_warn(f"Error encountered while adding bookmark: {str(e)}")
        finally:
            dialog.hide()

    field_defs = [
        FormDialog.FieldDef("name", "Name:  ", ui.StringField, item.name, True),
        FormDialog.FieldDef("address", "Address:  ", ui.StringField, item.path),
    ]
    dialog = FormDialog(
        title="Add Bookmark",
        width=400,
        ok_handler=lambda dialog: on_okay(dialog, item, view),
        field_defs=field_defs,
    )
    dialog.show()


def edit_bookmark(item: BookmarkItem, view: FilePickerView):
    """
    Edit a bookmark item with a dialog.

    Args:
        item(:obj:'BookmarkItem'): The bookmark item that to be edit.
        view(:obj:'FilePickerView'): The view which own the bookmark.
    """
    def on_okay_clicked(dialog: FormDialog, item: BookmarkItem, view: FilePickerView):
        name = dialog.get_value("name")
        url = dialog.get_value("address")
        try:
            assert(isinstance(item, BookmarkItem))
            view.rename_bookmark(item, name, url)
        except Exception as e:
            log_warn(f"Error encountered while editing bookmark: {str(e)}")

        finally:
            dialog.hide()

    field_defs = [
        FormDialog.FieldDef("name", "Name:  ", ui.StringField, item.name, True),
        FormDialog.FieldDef("address", "Address:  ", ui.StringField, item.path),
    ]
    dialog = FormDialog(
        title="Edit Bookmark",
        width=400,
        ok_handler=lambda dialog: on_okay_clicked(dialog, item, view),
        field_defs=field_defs,
    )
    dialog.show()


def delete_bookmark(item: BookmarkItem, view: FilePickerView):
    """
    Delete a bookmark item with a dialog.

    Args:
        item(:obj:'BookmarkItem'): The bookmark item that to be delete.
        view(:obj:'FilePickerView'): The view which own the bookmark.
    """
    def on_okay_clicked(dialog: MessageDialog, item: BookmarkItem, view: FilePickerView):
        try:
            assert(isinstance(item, BookmarkItem))
            view.delete_bookmark(item)
        except Exception as e:
            log_warn(f"Error encountered while deleting bookmark: {str(e)}")
        finally:
            dialog.hide()

    message = f"Are you sure about deleting the bookmark '{item.name}'?"

    dialog = MessageDialog(
        title="Delete Bookmark",
        width=400,
        message=message,
        ok_handler=lambda dialog: on_okay_clicked(dialog, item, view),
        ok_label="Yes",
        cancel_label="No",
    )
    dialog.show()


def refresh_item(item: FileBrowserItem, view: FilePickerView):
    """
    Refresh the UI for the item.

    Args:
        item(:obj:'FileBrowserItem'): The item to refresh the UI for.
        view(:obj:'FilePickerView'): The view that is own the item.
    """
    try:
        view.refresh_ui(item)
    except Exception as e:
        log_warn(f"Error refreshing the UI: {str(e)}")


def rename_item(item: FileBrowserItem, view: FilePickerView):
    """
    Rename the item with a dialog.

    Args:
        item(:obj:'FileBrowserItem'): The item to rename .
        view(:obj:'FilePickerView'): The view that is own the item.
    """
    def on_okay(dialog: InputDialog, item: FileBrowserItem, view: FilePickerView):
        new_name = dialog.get_value()
        try:
            if view.is_connection_point(item):
                view.rename_server(item, new_name)
            else:
                rename_file(item, view, new_name)
        except Exception as e:
            log_warn(f"Error encountered while renaming item: {str(e)}")
        finally:
            dialog.hide()

    # OM-52387: warn user if we are renaming a file or folder, since it may remove all checkpoints permanently for
    # the orignal file or folder (similar to what we have in Navigator)
    if view.is_connection_point(item):
        dialog = InputDialog(
            title=f"Rename {item.name}",
            width=300,
            pre_label="New Name:  ",
            ok_handler=lambda dialog, item=item: on_okay(dialog, item, view),
        )
    else:
        warning_msg = f"Do you really want to rename \"{item.name}\"?\n\nThis action cannot be undone.\n" + \
            "The folder and the checkpoints will be permanently deleted."
        dialog = InputDialog(
            title=f"Rename {item.name}",
            width=450,
            warning_message=warning_msg,
            ok_handler=lambda dialog, item=item: on_okay(dialog, item, view),
            ok_label="Confirm",
            message="New name:",
            default_value=item.name
        )
    dialog.show()


def rename_file(item: FileBrowserItem, view: FilePickerView, new_name: str):
    """
    Rename the item with a new name.

    Args:
        item(:obj:'FileBrowserItem'): The item to rename .
        view(:obj:'FilePickerView'): The view that is own the item.
        new_name(str): The new name for the item.
    """
    if not (item and new_name):
        return

    try:
        def on_moved(item: FileBrowserItem, view: FilePickerView, results):
            for result in results:
                if isinstance(result, Exception):
                    asyncio.ensure_future(_display_notification_message(
                        f"Error renaming file. Failed with error {str(result)}",
                        NotificationStatus.WARNING
                    ))
            # refresh the parent folder UI to immediately display the renamed item
            refresh_item(item.parent, view)

        new_name = new_name.lstrip("/")
        src_root = os.path.dirname(item.path)
        dst_path = f"{src_root}/{new_name}"
        asyncio.ensure_future(rename_file_async(item.path, dst_path, callback=partial(on_moved, item, view)))
    except Exception as e:
        log_warn(f"Error encountered during move: {str(e)}")


async def rename_file_async(src_path: str, dst_path: str, callback: Callable = None):
    """
    Rename item. Upon success, executes the given callback.

    Args:
        src_path (str): Path of item to rename.
        dst_path (str): Destination path to rename to.
        callback (func): Callback to execute upon success.  Function signature is void callback([str]).

    Raises:
        :obj:`Exception`
    """
    if not (dst_path and src_path):
        return

    # don't rename if src and dst is the same
    if dst_path == src_path:
        return

    async def _rename_path(src_path, dst_path):
        try:
            results = await move_item_async(src_path, dst_path, is_rename=True)
        except Exception:
            raise
        else:
            if callback:
                callback(results)

    src_path = src_path.rstrip("/")
    # check destination existence in batch and ask user for overwrite permission before appending move task
    paths_already_exist = await _check_paths_exist_async([dst_path])
    if paths_already_exist:
        def apply_callback(src_path, dst_path, dialog):
            dialog.hide()
            asyncio.ensure_future(_rename_path(src_path, dst_path))

        _prompt_confirm_items_deletion_dialog(paths_already_exist, partial(apply_callback, src_path, dst_path))
    else:
        await _rename_path(src_path, dst_path)


def add_connection(collection_item: CollectionItem, view: FilePickerView):
    """
    Show the connect dialog for the given view

    Args:
        view (:obj:`FilePickerView`): The FilePickerView to add the connection.
    """
    try:
        view.show_connect_dialog(collection_item.add_new_item)
    except Exception:
        pass


def refresh_connection(item: FileBrowserItem, view: FilePickerView):
    """
    Reconnect current server for the given view

    Args:
        item (:obj:`FileBrowserItem`): The FileBrowserItem to refresh the connection from.
        view (:obj:`FilePickerView`): The FilePickerView own the item.
    """
    try:
        view.reconnect_server(item)
    except Exception:
        pass


def log_out_from_connection(item: NucleusConnectionItem, view: FilePickerView):
    """
    Log out from the Nucleus server from the given connection item

    Args:
        item (:obj:`NucleusConnectionItem`): The NucleusConnectionItem to log out the connection from.
        view (:obj:`FilePickerView`): The FilePickerView own the item.
    """
    try:
        view.log_out_server(item)
    except Exception:
        pass


def remove_connection(item: FileBrowserItem, view: FilePickerView):
    """
    Remove a connection for the file browser item with a confirm dialog.

    Args:
        item (:obj:`FileBrowserItem`): The FileBrowserItem to remove the connection from.
        view (:obj:`FilePickerView`): The FilePickerView own the item.
    """

    def on_okay(dialog: MessageDialog, item: FileBrowserItem, view: FilePickerView):
        try:
            view.delete_server(item)
        except Exception as e:
            log_warn(f"Error encountered while removing connection: {str(e)}")
        finally:
            dialog.hide()

    message = f"Are you sure about removing the connection for '{item.name}'?"

    dialog = MessageDialog(
        title="Remove connection",
        width=400,
        message=message,
        ok_handler=lambda dialog, item=item: on_okay(dialog, item, view),
        ok_label="Yes",
        cancel_label="No",
    )
    dialog.show()

def about_connection(item: FileBrowserItem):
    """
    Show a connection's about info dialog for the connected file browser item.

    Args:
        item (:obj:`FileBrowserItem`): The FileBrowserItem own the connection.
    """
    if not item:
        return

    async def show_dialog():
        server_info = await VersioningHelper.get_server_info_async(item.path)
        if server_info:
            dialog = AboutDialog(
                server_info=server_info,
            )
            dialog.show()

    asyncio.ensure_future(show_dialog())


def create_folder(item: FileBrowserItem):
    """
    Creates folder under given item.

    Args:
        item (:obj:`FileBrowserItem`): Item under which to create the folder.

    """
    def on_okay(dialog: InputDialog, item: FileBrowserItem):
        try:
            assert(item.is_folder)
            item_path = item.path.rstrip("/").rstrip("\\")
            folder_name = dialog.get_value()
            asyncio.ensure_future(omni.client.create_folder_async(f"{item_path}/{folder_name}"))
        except Exception as e:
            log_warn(f"Error encountered while creating folder: {str(e)}")
        finally:
            dialog.hide()

    dialog = InputDialog(
        title="Create folder",
        width=300,
        pre_label="Name:  ",
        ok_handler=lambda dialog, item=item: on_okay(dialog, item),
    )
    dialog.show()


def delete_items(items: List[FileBrowserItem], view: Optional[FilePickerView] = None):
    """
    Deletes given items. Upon success, executes the given callback.

    Args:
        items ([:obj:`FileBrowserItem`]): Items to delete.
        view (Optional[:obj:`FilePickerView`]): The FilePickerView own the item.

    Raises:
        :obj:`Exception`
    """
    if not items:
        return

    def on_deleted(item: FileBrowserItem, view: FilePickerView, results):
        parent_item = item.parent
        if view and parent_item:
            view.select_and_center(parent_item)

    def on_delete_clicked(dialog: ConfirmItemDeletionDialog, items: List[FileBrowserItem]):
        if not items:
            return
        tasks = []
        for item in items:
            item_path = item.path.rstrip("/").rstrip("\\")
            tasks.append(omni.client.delete_async(item_path))
        try:
            asyncio.ensure_future(exec_tasks_async(tasks, callback=partial(on_deleted, items[0], view)))
        except Exception as e:
            log_warn(f"Error encountered during delete: {str(e)}")
        finally:
            dialog.hide()

    # OMFP-2152: To display dialog in external window, must create window immediately
    # And change message later if necessary
    dialog = ConfirmItemDeletionDialog(
        items=items,
        ok_handler=lambda dialog, items=items: on_delete_clicked(dialog, items),
    )

    async def show_dialog():
        checkpoint_support = False
        is_folder = False

        for item in items:
            if item.is_folder:
                is_folder = True
            if await VersioningHelper.check_server_checkpoint_support_async(item.path):
                checkpoint_support = True

        if checkpoint_support:
            if len(items) > 1:
                msg = f"Do you really want to delete these items - including Checkpoints?\n\nThis action cannot be undone. The items and any checkpoints will be permanently deleted."
            elif is_folder:
                name = os.path.basename(items[0].path)
                msg = f"Do you really want to delete \"{name}\" folder and all of its contents - including files and their Checkpoints?\n\nThis action cannot be undone. The folder and all its contents will be permanently deleted."
            else:
                name = os.path.basename(items[0].path)
                msg = f"Do you really want to delete \"{name}\" and all of its checkpoints?\n\nThis action cannot be undone. The file and the checkpoints will be permanently deleted."

            def build_msg():
                with ui.ZStack(height=0):
                    ui.Rectangle(style={"background_color": 0xFFCCCCFF}, height=ui.Percent(100), width=ui.Percent(100))
                    ui.Label(msg, word_wrap=True, style={"margin": 5, "color": 0xFF6D6DD5, "font_size": 16})

            dialog.rebuild_ui(build_msg)

        dialog.show()

    asyncio.ensure_future(show_dialog())

def move_items(dst_item: FileBrowserItem, src_paths: List[str], dst_name: Optional[str] = None, callback: Callable = None):
    """
    Moves items. Upon success, executes the given callback.

    Args:
        dst_item (:obj: 'FileBrowserItem'): Destination item.
        src_paths (List[str]): Paths of items to move.
        dst_name (Optional[str]): Destination item's name.
        callback (Callable): the callback function when move success.Function signature is void callback().
    """
    if not dst_item:
        return

    try:
        from omni.kit.notification_manager import post_notification
    except Exception:
        post_notification = log_warn

    if dst_item and src_paths:
        try:
            def on_moved(results, callback=None):
                for result in results:
                    if isinstance(result, Exception):
                        post_notification(str(result))
                if callback:
                    callback()
            asyncio.ensure_future(
                move_items_async(src_paths, dst_item.path, callback=partial(on_moved, callback=callback)))
        except Exception as e:
            log_warn(f"Error encountered during move: {str(e)}")


async def move_items_async(src_paths: List[str], dst_path: str, callback: Callable = None):
    """
    Moves items. Upon success, executes the given callback.

    Args:
        src_paths ([str]): Paths of items to move.
        dst_path (str): Destination folder.
        callback (func): Callback to execute upon success.  Function signature is void callback([str]).

    Raises:
        :obj:`Exception`
    """
    if not (dst_path and src_paths):
        return

    dst_paths = []
    for src_path in src_paths:
        # use the src_path basename and construct the dst path result
        src_name = os.path.basename(src_path.rstrip("/"))
        dst_paths.append(f"{dst_path}/{src_name}")

    async def _move_paths(src_paths, dst_paths):
        tasks = []
        for src_path, dst_path in zip(src_paths, dst_paths):
            tasks.append(move_item_async(src_path, dst_path))
        try:
            await exec_tasks_async(tasks, callback=callback)
        except Exception:
            raise

    # check destination existence in batch and ask user for overwrite permission before appending move task
    paths_already_exist = await _check_paths_exist_async(dst_paths)
    if paths_already_exist:
        def apply_callback(src_paths, dst_paths, dialog):
            dialog.hide()
            asyncio.ensure_future(_move_paths(src_paths, dst_paths))

        _prompt_confirm_items_deletion_dialog(paths_already_exist, partial(apply_callback, src_paths, dst_paths))
    else:
        await _move_paths(src_paths, dst_paths)


async def move_item_async(src_path: str, dst_path: str, timeout: float = 300.0, is_rename: bool = False) -> str:
    """
    Async function that moves item (recursively) from one path to another.
    Note: this function simply uses the move function from omni.client and makes no attempt to optimize for
    moving from one Omniverse server to another.
    Example usage:
    await move_item_async("C:/tmp/my_file.usd", "omniverse://ov-content/Users/me/moved.usd")

    Args:
        src_root (str): Source path to item being copied.
        dst_root (str): Destination path to move the item.
        timeout (float): Number of seconds to try before erroring out.  Default 10.

    Returns:
        str: Destination path name

    Raises:
        :obj:`RuntimeWarning`: If error or timeout.

    """
    timeout = max(300, timeout)

    try:
        # OM-54464: add source url in moved/renamed item checkpoint
        src_checkpoint = None
        result, entries = await omni.client.list_checkpoints_async(src_path)
        if result == omni.client.Result.OK and entries:
            src_checkpoint = entries[-1].relative_path
        op_str = "Moved"
        if is_rename:
            op_str = "Renamed"
        checkpoint_msg = f"{op_str} from {src_path}"
        if src_checkpoint:
            checkpoint_msg = f"{checkpoint_msg}?{src_checkpoint}"

        result, _ = await asyncio.wait_for(
            omni.client.move_async(src_path, dst_path, behavior=omni.client.CopyBehavior.OVERWRITE, message=checkpoint_msg),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise RuntimeWarning(f"Error unable to move '{src_path}' to '{dst_path}': Timed out after {timeout} secs.")
    except Exception as e:
        raise RuntimeWarning(f"Error moving '{src_path}' to '{dst_path}': {e}")

    if result != omni.client.Result.OK:
        raise RuntimeWarning(f"Error moving '{src_path}' to '{dst_path}': {result}")

    return dst_path

async def obliterate_item_async(path: str, timeout: float = 10.0) -> str:
    """
    Async function.  obliterates the item at the given path name.

    Args:
        path (str): The full path name of a file or folder, e.g. "omniverse://ov-content/Users/me".
        timeout (float): Number of seconds to try before erroring out.  Default 10.

    Returns:
        str: obliterated path name

    Raises:
        :obj:`RuntimeWarning`: If error or timeout.

    """
    try:
        path = path.replace("\\", "/")
        result = await asyncio.wait_for(omni.client.obliterate_async(path, True), timeout=timeout)
    except asyncio.TimeoutError:
        raise RuntimeWarning(f"Error obliterating item '{path}': Timed out after {timeout} secs.")
    except Exception as e:
        raise RuntimeWarning(f"Error obliterating item '{path}': {e}")

    if result != omni.client.Result.OK:
        raise RuntimeWarning(f"Error obliterating item '{path}': {result}")

    return path

def obliterate_items(items: [FileBrowserItem], view: FilePickerView):
    """
    Obliterate given items. Upon success, executes the given callback.

    Args:
        items ([:obj:`FileBrowserItem`]): Items to obliterate.
        callback (Callable): Callback to execute upon success.  Function signature is void callback([str]).

    Raises:
        :obj:`Exception`

    """

    if not items:
        return

    def on_obliterated(item: FileBrowserItem, view: FilePickerView, results):
        for result in results:
            if isinstance(result, Exception):
                asyncio.ensure_future(_display_notification_message(
                    f"Error oblitereate file. Failed with error {str(result)}",
                    NotificationStatus.WARNING
                ))
        # refresh the parent folder UI to immediately display the renamed item
        refresh_item(item.parent, view)

    def on_obliterate_clicked(dialog: ConfirmItemDeletionDialog, items: List[FileBrowserItem]):
        if not items:
            return
        tasks = []
        for item in items:
            item_path = item.path.rstrip("/").rstrip("\\")
            tasks.append(obliterate_item_async(item_path))
        try:
            asyncio.ensure_future(exec_tasks_async(tasks, callback=partial(on_obliterated, items[0], view)))
        except Exception as e:
            log_warn(f"Error encountered during obliterate: {str(e)}")
        finally:
            dialog.hide()

    async def show_dialog():
        checkpoint_support = False
        is_folder = False

        for item in items:
            if item.is_folder:
                is_folder = True
            if await VersioningHelper.check_server_checkpoint_support_async(item.path):
                checkpoint_support = True

        if checkpoint_support:
            if len(items) > 1:
                msg = f"Do you really want to obliterate these items - including Checkpoints?\n\nThis action cannot be undone. The items and any checkpoints will be permanently deleted."
            elif is_folder:
                name = os.path.basename(items[0].path)
                msg = f"Do you really want to obliterate \"{name}\" folder and all of it contents - including files and their Checkpoints?\n\nThis action cannot be undone. The folder and all its contents will be permanently deleted."
            else:
                name = os.path.basename(items[0].path)
                msg = f"Do you really want to obliterate \"{name}\" and all of its checkpoints?\n\nThis action cannot be undone. The file and the checkpoints will be permanently deleted."

            def build_msg():
                with ui.ZStack(height=0):
                    ui.Rectangle(style={"background_color": 0xFFCCCCFF}, height=ui.Percent(100), width=ui.Percent(100))
                    ui.Label(msg, word_wrap=True, style={"margin": 5, "color": 0xFF6D6DD5, "font_size": 16})

            dialog = ConfirmItemDeletionDialog(
                items=items,
                message_fn=build_msg,
                ok_handler=lambda dialog, items=items: on_obliterate_clicked(dialog, items),
            )
        else:
            dialog = ConfirmItemDeletionDialog(
                items=items,
                ok_handler=lambda dialog, items=items: on_obliterate_clicked(dialog, items),
            )
        dialog.show()

    asyncio.ensure_future(show_dialog())

async def restore_item_async(path: str, timeout: float = 10.0) -> str:
    """
    Async function.  restore the item at the given path name.

    Args:
        path (str): The full path name of a file or folder, e.g. "omniverse://ov-content/Users/me".
        timeout (float): Number of seconds to try before erroring out.  Default 10.

    Returns:
        str: restore path name

    Raises:
        :obj:`RuntimeWarning`: If error or timeout.

    """
    try:
        path = path.replace("\\", "/")
        result = await asyncio.wait_for(omni.client.undelete_async(path), timeout=timeout)
    except asyncio.TimeoutError:
        raise RuntimeWarning(f"Error restoring item '{path}': Timed out after {timeout} secs.")
    except Exception as e:
        raise RuntimeWarning(f"Error restoring item '{path}': {e}")

    if result != omni.client.Result.OK:
        raise RuntimeWarning(f"Error restoring item '{path}': {result}")

    return path

def restore_items(items: [FileBrowserItem], view: FilePickerView):
    """
    Restore given items. Upon success, executes the given callback.

    Args:
        items ([:obj:`FileBrowserItem`]): Items to restore.
        callback (Callable): Callback to execute upon success.  Function signature is void callback([str]).

    Raises:
        :obj:`Exception`

    """
    def on_restored(item: FileBrowserItem, view: FilePickerView, results):
        for result in results:
            if isinstance(result, Exception):
                asyncio.ensure_future(_display_notification_message(
                    f"Error restore file. Failed with error {str(result)}",
                    NotificationStatus.WARNING
                ))
        # refresh the parent folder UI to immediately display the renamed item
        refresh_item(item.parent, view)

    if items:
        tasks = []
        for item in items:
            if item.is_deleted:
                item_path = item.path.rstrip("/").rstrip("\\")
                if item.is_folder:
                    item_path = item_path + "/"
                tasks.append(restore_item_async(item_path))
        asyncio.ensure_future(exec_tasks_async(tasks, callback=partial(on_restored, items[0], view)))

def _prompt_confirm_items_deletion_dialog(dst_paths, apply_callback):
    """
    Checks dst_paths existence and prompt user to confirm deletion.

    Args:
        dst_paths (List[str]): The file paths to delete.
        apply_callback (Callable): Function to execute upon clicking the "Yes" button. Function signature:
                    void apply_callback(dialog: :obj:`PopupDialog`)
    """
    items = []
    for dst_path in dst_paths:
        dst_name = os.path.basename(dst_path)
        items.append(
            FileBrowserItem(dst_path, FileBrowserItemFields(dst_name, datetime.now(), 0, 0), is_folder=False))

    dialog = ConfirmItemDeletionDialog(
        title="Confirm File Overwrite",
        message="You are about to overwrite",
        items=items,
        ok_handler=lambda dialog: apply_callback(dialog),
    )
    dialog.show()


def checkpoint_items(items: List[FileBrowserItem], checkpoint_widget):
    """
    Create checkpoint for a list of items.

    Args:
        items(List[:obj:'FileBrowserItem']): List of items to checkpoint.
        checkpoint_widget(:obj:'CheckpointWidget'): Checkpoint widget that is used to list checkpoints.
    """
    if not items:
        return

    paths = [item.path if not item.is_folder else "" for item in items]

    async def checkpoint_items_async(checkpoint_comment: str, checkpoint_widget):
        for path in paths:
            if path and await VersioningHelper.check_server_checkpoint_support_async(
                VersioningHelper.extract_server_from_url(path)
            ):
                result, entry = await omni.client.create_checkpoint_async(path, checkpoint_comment, True)
                if result != omni.client.Result.OK:
                    await _display_notification_message(
                        f"Error creating checkpoint for {path}. Failed with error {result}",
                        NotificationStatus.WARNING
                    )
                elif checkpoint_widget:
                    checkpoint_widget._model.list_checkpoint()

    def on_ok(checkpoint_comment):
        asyncio.ensure_future(checkpoint_items_async(checkpoint_comment, checkpoint_widget))

    VersioningHelper.menu_checkpoint_dialog(ok_fn=on_ok, cancel_fn=None)


def copy_to_clipboard(item: FileBrowserItem):
    """
    Copy a item's path to the clipboard.

    Args:
        item(:obj:'FileBrowserItem'): The item to copy
    """
    try:
        import omni.kit.clipboard
        omni.kit.clipboard.copy(item.path)
    except ImportError:
        log_warn("Warning: Could not import omni.kit.clipboard.")


def open_in_file_browser(item: FileBrowserItem):
    """
    Open the given file item in the OS's native file browser.

    Args:
        item (FileBrowserItem): Selected item of the Content Browser.

    Returns:
        None

    """
    # NOTE: Providing this normalized path as an argument to `subprocess.Popen()` will properly handle the case of
    # the given path containing spaces, and avoids having to parse and surround inputs with double quotation marks.
    normalized_item_path = os.path.normpath(item.path)

    if sys.platform == "win32":
        # On Windows, open the File Explorer view at the parent-level of the given path, with the given file
        # selected. This provides a view similar to what is displayed in the Content browser, and avoids Windows'
        # behavior of either opening the File Explorer *in* the given folder path, or its parent when opening a
        # file.
        #
        # NOTE: The trailing comma character (",") is intentional (see https://ss64.com/nt/explorer.html).
        subprocess.Popen(["explorer", "/select,", normalized_item_path])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", normalized_item_path])
    else:
        subprocess.Popen(["xdg-open", normalized_item_path])


def create_usd_file(item: FileBrowserItem):
    """
    Action executed upon clicking the "New USD File" contextual menu item.

    Args:
        item (FileBrowserItem): Directory item of the File Browser where to create the new USD file.

    Returns:
        None

    """
    async def create_empty_usd_file(usd_file_basename: str) -> None:
        if is_usd_supported():
            from pxr import Usd, Sdf, UsdGeom
        else:
            await _display_notification_message(f"Failed to import USD library.", NotificationStatus.WARNING)
            return
        absolute_usd_file_path = os.path.join(item.path, f"{usd_file_basename}.usd").replace("\\", "/")
        if not await _validate_usd_file_creation(usd_file_basename, absolute_usd_file_path):
            return

        layer = Sdf.Layer.CreateNew(absolute_usd_file_path)
        if not layer:
            await _display_notification_message(
                f"Unable to create USD file at location \"{absolute_usd_file_path}\".",
                NotificationStatus.WARNING)
            return

        stage = Usd.Stage.Open(layer)
        upAxis = carb.settings.get_settings().get_as_string("/persistent/app/stage/upAxis") or ""
        if upAxis == "Z":
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        else:
            UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
        stage.Save()

    def on_okay_clicked(dialog: InputDialog, item: FileBrowserItem) -> None:
        asyncio.ensure_future(create_empty_usd_file(dialog.get_value()))
        dialog.hide()

    dialog = InputDialog(
        title="New USD",
        message="New USD File",
        pre_label="File Name: ",
        post_label=".usd",
        default_value="new_file",
        ok_handler=lambda dialog, item=item: on_okay_clicked(dialog, item),
        ok_label="Create",
    )
    dialog.show()


async def _validate_usd_file_creation(usd_filename: str, absolute_usd_file_path: str) -> bool:
    """
    Check if the given absolute file path for a USD file can be created, based on:
        * Whether or not the given file name is empty.
        * Whether or not the given file path already exists.

    Args:
        usd_filename (str): The name of the USD file to create, as provided by the User (without extension).
        absolute_usd_file_path (str): The absolute file path of a USD file to create.

    Returns:
        bool: `True` if the given absolute file path for a USD file can be created, `False` otherwise.

    """
    # No desired filename was submitted:
    if len(usd_filename) == 0:
        await _display_notification_message("Please provide a name for the USD file.")
        return False

    # A file with the same name already exists:
    usd_file_basename = os.path.basename(absolute_usd_file_path)
    result, _ = await omni.client.stat_async(absolute_usd_file_path)
    if result == omni.client.Result.OK:
        await _display_notification_message(
            f"A file with the same name \"{usd_file_basename}\" already exists in this location.",
            NotificationStatus.WARNING
        )
        return False

    return True


async def _display_notification_message(
        message: str,
        status: NotificationStatus = NotificationStatus.INFO,
    ) -> None:
    """
    Display the given notification message to the User, using the given status.

    Args:
        message (str): Message to display in the notification.
        status (NotificationStatus): Status of the notification (default: `NotificationStatus.INFO`).

    Returns:
        None

    """
    try:
        await omni.kit.app.get_app().next_update_async()
        omni.kit.notification_manager.post_notification(
            text=message,
            status=status,
            hide_after_timeout=False,
        )
    except:
        if status == NotificationStatus.WARNING:
            carb.log_warn(message)
        else:
            carb.log_info(message)


async def exec_tasks_async(tasks, callback: Callable = None):
    """
    Helper function to execute a given list of tasks concurrently.  When done, invokes the callback with the
    list of results. Results can include an exceptions if appropriate.

    Args:
        tasks ([]:obj:`Task`]): List of tasks to execute.
        callback (Callable): Invokes this callback when all tasks are finished. Function signature is
            void callback(results: List[Union[str, Exception]])

    """
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        return
    except Exception:
        # Since we're returning exceptions, we should never hit this case
        return
    else:
        if callback:
            callback(results)
